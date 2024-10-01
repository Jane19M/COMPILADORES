import re
from collections import defaultdict
import ast

# Lista de tokens con su respectiva expresión regular para identificar diferentes componentes del código
TOKENS = [
    ("CLAVES", r'\b(if|else|while|for|return|break|continue|def|class|print|int)\b'),  # Palabras clave de Python
    ("IDENTIFICADORES", r'\b[a-zA-Z_]\w*\b'),                                # Identificadores válidos
    ("NUMEROS", r'\b\d+(\.\d+)?\b'),                                         # Números enteros y decimales
    ("OPERADORES", r'[+\-*/%=<>!&|^~]'),                                     # Operadores aritméticos y lógicos
    ("STRING", r'"[^"\\]*(\\.[^"\\]*)*"'),                                   # Cadenas de texto con escapado
    ("SALTOS DE LINEA", r'\n'),                                              # Saltos de línea
    ("ESPACIOS", r'[ \t]+'),                                                 # Espacios y tabulaciones
    ("COMENTARIOS", r'#.*'),                                                 # Comentarios de línea
    ("DELIMITADORES", r'[(){}[\],.;:]'),                                     # Delimitadores como paréntesis y comas
]

def tokenize(code):
    tokens = defaultdict(list)  # Diccionario que almacenará los tokens categorizados
    position = 0  # Posición actual en el código fuente

    while position < len(code):
        match = None
        for token_type, token_regex in TOKENS:
            regex = re.compile(token_regex)
            match = regex.match(code, position)
            if match:
                if token_type not in ["ESPACIOS"]:
                    tokens[token_type].append(match.group(0))
                position = match.end(0)
                break

        if not match:
            print(f"Error: Token desconocido en la posición {position}")
            break
    
    return tokens

class SyntaxAnalyzer:
    def __init__(self):
        pass

    def analyze(self, code):
        print("Iniciando el análisis sintáctico...")

        steps = [
            "Paso 1: Se verifica la estructura general del código.",
            "Paso 2: Se analizan las declaraciones de funciones y clases.",
            "Paso 3: Se evalúan las expresiones y los argumentos.",
            "Paso 4: Se comprueba la correcta utilización de los delimitadores.",
            "Paso 5: Se construye el árbol de sintaxis abstracta (AST).",
            "Paso 6: Se valida que el código sea sintácticamente correcto."
        ]

        try:
            for step in steps:
                print(step)  # Muestra cada paso del análisis
                # Simulación de la lógica de análisis en cada paso
                if step == "Se verifica la estructura general del código.":
                    print("  - Verificando si el código tiene una estructura válida.")
                elif step == "Se analizan las declaraciones de funciones y clases.":
                    print("  - Identificando funciones y clases definidas.")
                elif step == "Se evalúan las expresiones y los argumentos.":
                    print("  - Analizando las llamadas a funciones y sus argumentos.")
                elif step == "Se comprueba la correcta utilización de los delimitadores.":
                    print("  - Asegurando que todos los paréntesis y llaves están correctamente cerrados.")
                elif step == "Se construye el árbol de sintaxis abstracta (AST).":
                    print("  - Generando la representación interna del código.")
                elif step == "Se valida que el código sea sintácticamente correcto.":
                    print("  - Comprobando que no haya errores de sintaxis.")

            tree = ast.parse(code)
            print("El análisis sintáctico fue exitoso. El código es sintácticamente correcto.")
            return tree  # Retorna el árbol para su uso posterior
        except SyntaxError as e:
            print("El análisis sintáctico falló debido a un error de sintaxis.")
            print(f"Detalles del error: {e}")
            return None

def main():
    print("Por favor, ingrese el código fuente a analizar (deje una línea vacía para finalizar):")
    lineas = []

    while True:
        linea = input()
        if linea == "":
            break
        lineas.append(linea)

    codigo_fuente = "\n".join(lineas)

    tokens = tokenize(codigo_fuente)

    print("\nTokens identificados agrupados por categoría:")
    for token_type, token_values in tokens.items():
        print(f"{token_type}: {', '.join(token_values)}")

    # Análisis sintáctico
    analyzer = SyntaxAnalyzer()
    tree = analyzer.analyze(codigo_fuente)

    if tree is not None:  # Solo muestra el árbol si el análisis fue exitoso
        print("El árbol generado es:")
        print(ast.dump(tree, indent=4))

if __name__ == "__main__":
    main()
