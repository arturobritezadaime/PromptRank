import re
import spacy
import textstat
from langdetect import detect
from sentence_transformers import SentenceTransformer, util

# ================================
# 🔹 Funciones de evaluación de complejidad del prompt
# ================================
def evaluar_longitud_prompt(prompt: str) -> int:
    """
    Evalúa la complejidad de un prompt basándose en su longitud.

    Args:
        prompt (str): El texto del prompt a evaluar.

    Returns:
        int: Un puntaje de 1 (simple), 2 (moderado) o 3 (complejo).
    """
    palabras = len(prompt.split())

    if palabras < 15:
        # Prompts simples
        return 1
    elif palabras < 40:
        # Prompts medianamente complejos
        return 2
    else:
        # Prompts complejos
        return 3

def evaluar_diversidad_vocabulario(prompt: str) -> int:
    """
    Evalúa la diversidad de vocabulario del prompt mediante la
    proporción de palabras únicas con respecto al total.

    Args:
        prompt (str): El texto del prompt a evaluar.

    Returns:
        int: Un puntaje de 1 (baja), 2 (moderada) o 3 (alta) diversidad.
    """
    palabras = prompt.split()
    total_palabras = len(palabras)
    palabras_unicas = len(set(palabras))

    if total_palabras == 0:
        return 1  # Retorna un valor por defecto para prompts vacíos

    proporcion_diversidad = palabras_unicas / total_palabras

    if proporcion_diversidad < 0.3:
        return 1
    elif proporcion_diversidad < 0.6:
        return 2
    else:
        return 3

def evaluar_deteccion_razonamiento(prompt: str) -> int:
    """
    Evalúa si el prompt contiene elementos de razonamiento usando similitud
    semántica con expresiones predefinidas en español e inglés.

    Args:
        prompt (str): El texto del prompt a evaluar.

    Returns:
        int: Un puntaje de 1 (bajo), 2 (medio) o 3 (alto) para el razonamiento.
    """
    # Modelo de embeddings multilingüe
    modelo_embeddings = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
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

    # Embeddings para las señales
    emb_fuerte = modelo_embeddings.encode(senales_fuertes, convert_to_tensor=True)
    emb_media = modelo_embeddings.encode(senales_medias, convert_to_tensor=True)

    # Calcular similitud coseno
    sim_fuerte = util.cos_sim(prompt_embedding, emb_fuerte).max().item()
    sim_media = util.cos_sim(prompt_embedding, emb_media).max().item()

    # Umbrales de puntuación
    if sim_fuerte >= 0.7:
        return 3
    elif sim_media >= 0.5:
        return 2
    return 1

def cargar_modelo_spacy(prompt: str):
    """
    Detecta el idioma del prompt y carga el modelo spaCy correspondiente.

    Args:
        prompt (str): El texto del prompt.

    Returns:
        spacy.lang: El modelo de spaCy cargado para el idioma detectado.
    """
    idioma = detect(prompt)
    if idioma.startswith("es"):
        return spacy.load("es_core_news_sm")
    elif idioma.startswith("en"):
        return spacy.load("en_core_web_sm")
    else:
        # Por defecto, carga el modelo en español
        return spacy.load("es_core_news_sm")

def evaluar_estructura_gramatical(prompt: str) -> int:
    """
    Evalúa la complejidad de la estructura gramatical del prompt
    contando el número de oraciones complejas.

    Args:
        prompt (str): El texto del prompt a evaluar.

    Returns:
        int: Un puntaje de 1 (simple), 2 (moderado) o 3 (complejo).
    """
    nlp = cargar_modelo_spacy(prompt)
    doc = nlp(prompt)
    oraciones_complejas = sum(1 for sent in doc.sents if sum(1 for tok in sent if tok.dep_ == "mark") > 0)
    total_oraciones = len(list(doc.sents))

    if total_oraciones == 0:
        return 1

    proporcion = oraciones_complejas / total_oraciones

    if proporcion < 0.2:
        return 1
    elif proporcion < 0.5:
        return 2
    return 3

def evaluar_legibilidad(prompt: str) -> int:
    """
    Mide la legibilidad del prompt utilizando la fórmula de Flesch Reading Ease.

    Args:
        prompt (str): El texto del prompt a evaluar.

    Returns:
        int: Un puntaje de 1 (fácil), 2 (moderado) o 3 (difícil/técnico).
    """
    score = textstat.flesch_reading_ease(prompt)
    if score > 70:
        return 1
    elif score > 50:
        return 2
    return 3

def calcular_complejidad_total(prompt: str) -> int:
    """
    Calcula una puntuación de complejidad del prompt en una escala del 1 al 10,
    utilizando una fórmula ponderada.

    Args:
        prompt (str): El texto del prompt a evaluar.

    Returns:
        int: La puntuación final de complejidad, redondeada.
    """
    # Obtener las puntuaciones de cada métrica
    longitud = evaluar_longitud_prompt(prompt)
    vocabulario = evaluar_diversidad_vocabulario(prompt)
    razonamiento = evaluar_deteccion_razonamiento(prompt)
    estructura = evaluar_estructura_gramatical(prompt)
    legibilidad = evaluar_legibilidad(prompt)

    # Fórmula de puntuación ponderada
    raw_score = (longitud * 0.5) + \
                (vocabulario * 2.0) + \
                (razonamiento * 3.5) + \
                (estructura * 1.0) + \
                (legibilidad * 2.0)

    # Normalizar la puntuación a una escala de 1 a 10
    min_raw_score = (1 * 0.5) + (1 * 2.0) + (1 * 3.5) + (1 * 1.0) + (1 * 2.0)
    max_raw_score = (3 * 0.5) + (3 * 2.0) + (3 * 3.5) + (3 * 1.0) + (3 * 2.0)

    normalized_score = 1 + (9 * (raw_score - min_raw_score) / (max_raw_score - min_raw_score))

    final_score = int(round(max(1, min(10, normalized_score))))

    return final_score

# ================================
# 🔹 Programa principal
# ================================
def main():
    """
    Función principal para la ejecución del programa.
    """
    entrada_usuario = input("Introduce tu prompt: ")

    # Evaluar la complejidad del prompt
    longitud = evaluar_longitud_prompt(entrada_usuario)
    complejidad_vocabulario = evaluar_diversidad_vocabulario(entrada_usuario)
    complejidad_razonamiento = evaluar_deteccion_razonamiento(entrada_usuario)
    complejidad_estructura = evaluar_estructura_gramatical(entrada_usuario)
    complejidad_legibilidad = evaluar_legibilidad(entrada_usuario)
    puntuacion_final = calcular_complejidad_total(entrada_usuario)

    print("\n--- Resultados ---")
    print(f"Complejidad por longitud: {longitud}/3")
    print(f"Complejidad por diversidad de vocabulario: {complejidad_vocabulario}/3")
    print(f"Complejidad por razonamiento: {complejidad_razonamiento}/3")
    print(f"Complejidad por estructura gramatical: {complejidad_estructura}/3")
    print(f"Complejidad por legibilidad: {complejidad_legibilidad}/3")
    print(f"\nLa puntuación de complejidad de tu prompt es: {puntuacion_final}/10")

if __name__ == "__main__":
    main()