import re
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

def evaluar_deteccion_razonamiento(prompt: str) -> int:
    """Detecta señales de pensamiento crítico, planificación o lógica."""
    señales = ["plan", "analyze", "analizar", "think", "pensar", "reason", "razonar"]
    if any(pal in prompt.lower() for pal in señales):
        return 3
    elif "why" in prompt.lower() or "how" in prompt.lower():
        return 2
    return 1
# Solicitar al usuario que introduzca un prompt
entrada_usuario = input("Introduce tu prompt: ")

# Evaluar la complejidad del prompt ingresado
longitud = evaluar_longitud_prompt(entrada_usuario)
complejidad_vocabulario = evaluar_diversidad_vocabulario(entrada_usuario)
complejidad_razonamiento = evaluar_deteccion_razonamiento(entrada_usuario)

print(f"La longitud del prompt es: {longitud}")
print(f"Complejidad por diversidad de vocabulario: {complejidad_vocabulario}")
print(f"Complejidad por razonamiento: {complejidad_razonamiento}")