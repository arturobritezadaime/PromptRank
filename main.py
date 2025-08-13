import re
# ================================
# 🔹 Función para detectar complejidad del prompt
# ================================
def evaluar_complejidad_prompt(prompt: str) -> int:
    """
    Evalúa la complejidad de un prompt segun longitud y otros criterios.
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
        
# Solicitar al usuario que introduzca un prompt
entrada_usuario = input("Introduce tu prompt: ")

# Evaluar la complejidad del prompt ingresado
complejidad = evaluar_complejidad_prompt(entrada_usuario)

print(f"La complejidad del prompt es: {complejidad}")