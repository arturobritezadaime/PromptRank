import re
import spacy
import textstat
from langdetect import detect
from sentence_transformers import SentenceTransformer, util

# ================================
# 🔹 Función para detectar complejidad del prompt
# ================================
def evaluar_longitud_prompt(prompt: str) -> int:
    """
    Evalúa la complejidad de un prompt segun longitud.
    """
    # 1. Analizar la longitud del prompt
    palabras = len(prompt.split())
    
    if palabras < 15:
        # simples
        return 1
    elif palabras < 40:
        # medianamente complejos
        return 2

    else:
        # complejos
        return 3

# ================================
# 🔹 Función para evaluar diversidad de vocabulario
# ================================
def evaluar_diversidad_vocabulario(prompt: str) -> int:
    """
    Evalúa la diversidad de vocabulario del prompt basándose en
    la proporción de palabras únicas respecto al total.
    
    Retorna:
        1 si diversidad baja,
        2 si diversidad moderada,
        3 si diversidad alta.
    """
    palabras = prompt.split()
    total_palabras = len(palabras)
    palabras_unicas = len(set(palabras))
    
    if total_palabras == 0:
        return 1  # Caso de prompt vacío
    
    proporcion_diversidad = palabras_unicas / total_palabras
    
    if proporcion_diversidad < 0.3:
        return 1
    elif proporcion_diversidad < 0.7:
        return 2
    else:
        return 3        

# Modelo de embeddings multilingüe
modelo_embeddings = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def evaluar_deteccion_razonamiento(prompt: str) -> int:
    """
    Evalúa si el prompt contiene razonamiento mediante similitud semántica
    con expresiones en español e inglés (balanceadas).
    """

    prompt_embedding = modelo_embeddings.encode(prompt, convert_to_tensor=True)

    # 🔹 Señales fuertes 
    señales_fuertes = [
        # Español
        "Elabora un plan detallado para resolver el problema",
        "Justifica tu respuesta utilizando argumentos lógicos",
        "Analiza causas y consecuencias del fenómeno descrito",
        "Desarrolla una hipótesis y evalúa su validez",
        "Propón una solución estratégica y argumentada",
        "Explica detalladamente el razonamiento detrás de tu decisión",
        "Evalúa críticamente las opciones disponibles",
        "Argumenta paso a paso cómo llegaste a esa conclusión",

        # Inglés
        "Generate a detailed plan to solve the problem",
        "Justify your response using logical arguments",
        "Analyze the causes and consequences of the situation",
        "Develop a hypothesis and assess its validity",
        "Propose a well-reasoned solution to the issue",
        "Explain in detail the reasoning behind your decision",
        "Critically evaluate the available alternatives",
        "Provide a step-by-step argument for your conclusion"
    ]

    # 🔸 Señales medias 
    señales_medias = [
        # Español 
        "Resume los puntos principales del contenido",
        "Compara dos alternativas posibles",
        "Describe brevemente cómo funciona el proceso",
        "Explica las diferencias entre los casos",
        "¿Por qué crees que ocurre este fenómeno?",
        "Sintetiza la información clave del texto",
        "Haz una descripción breve del procedimiento",
        "Identifica los elementos principales del análisis",

        # Inglés 
        "Summarize the main points of the text",
        "Compare two possible options",
        "Briefly describe how the process works",
        "Explain the differences between the cases",
        "Why do you think this phenomenon occurs?",
        "Synthesize the key information from the text",
        "Give a short description of the procedure",
        "Identify the main elements of the analysis"
    ]

    # Embeddings
    emb_fuerte = modelo_embeddings.encode(señales_fuertes, convert_to_tensor=True)
    emb_media = modelo_embeddings.encode(señales_medias, convert_to_tensor=True)

    # Similitudes
    sim_fuerte = util.cos_sim(prompt_embedding, emb_fuerte).max().item()
    sim_media = util.cos_sim(prompt_embedding, emb_media).max().item()

    # Umbrales
    if sim_fuerte >= 0.7:
        return 3
    elif sim_media >= 0.5:
        return 2
    return 1
def cargar_modelo_spacy(prompt: str):
    """
    Detecta si el texto está en español o inglés y carga el modelo spaCy correspondiente.
    """
    idioma = detect(prompt)
    if idioma.startswith("es"):
        return spacy.load("es_core_news_sm")
    elif idioma.startswith("en"):
        return spacy.load("en_core_web_sm")
    else:
        # Por defecto, español
        return spacy.load("es_core_news_sm")
def evaluar_estructura_gramatical(prompt: str) -> int:
    """Evalúa cuántas oraciones complejas o subordinadas hay."""
    nlp = cargar_modelo_spacy(prompt)
    doc = nlp(prompt)
    oraciones_complejas = sum(1 for sent in doc.sents if sum(1 for tok in sent if tok.dep_ == "mark") > 0)
    total = len(list(doc.sents))
    if total == 0:
        return 1
    proporción = oraciones_complejas / total
    if proporción < 0.2:
        return 1
    elif proporción < 0.5:
        return 2
    return 3

def evaluar_legibilidad(prompt: str) -> int:
    """Usa textstat para medir la legibilidad (Flesch Reading Ease)."""
    score = textstat.flesch_reading_ease(prompt)
    if score > 70:
        return 1  # muy fácil
    elif score > 50:
        return 2  # moderado
    return 3  # difícil o técnico

# Solicitar al usuario que introduzca un prompt
entrada_usuario = input("Introduce tu prompt: ")

# Evaluar la complejidad del prompt ingresado
longitud = evaluar_longitud_prompt(entrada_usuario)
complejidad_vocabulario = evaluar_diversidad_vocabulario(entrada_usuario)
complejidad_razonamiento = evaluar_deteccion_razonamiento(entrada_usuario)
complejidad_estructura = evaluar_estructura_gramatical(entrada_usuario)
complejidad_legibilidad = evaluar_legibilidad(entrada_usuario)

print(f"Complejidad por longitud es: {longitud}")
print(f"Complejidad por diversidad de vocabulario es: {complejidad_vocabulario}")
print(f"Complejidad por razonamiento es: {complejidad_razonamiento}")
print(f"Complejidad por estructura gramatical es: {complejidad_estructura}")
print(f"Complejidad por legibilidad: {complejidad_legibilidad}")