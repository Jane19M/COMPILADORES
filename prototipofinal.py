import re
import ast
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

# Definición de los tokens
TOKENS = [
    ("CLAVES", r'\b(if|else|while|for|return|break|continue|def|class|print|int|float|input)\b'),  # Palabras clave de Python
    ("IDENTIFICADORES", r'\b[a-zA-Z_]\w*\b'),                                # Identificadores válidos
    ("NUMEROS", r'\b\d+(\.\d+)?\b'),                                         # Números enteros y decimales
    ("OPERADORES", r'[+\-*/%=<>!&|^~]'),                                     # Operadores aritméticos y lógicos
    ("STRING", r'"[^"\\]*(\\.[^"\\]*)*"'),                                   # Cadenas de texto con escapado
    ("SALTOS_DE_LINEA", r'\n'),                                              # Saltos de línea
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
                # No ignoramos ningún token, incluso los ESPACIOS
                tokens[token_type].append(match.group(0))
                position = match.end(0)
                break

        if not match:
            print(f"Error: Token desconocido en la posición {position}")
            break
    
    return tokens

class SyntaxTreeVisualizer:
    def __init__(self):
        pass

    def analyze_and_visualize(self, code):
        # Convertir el código fuente en un árbol de sintaxis abstracta (AST)
        try:
            tree = ast.parse(code)
            print("\nIniciando el análisis sintáctico...")
            print("El análisis sintáctico fue exitoso. El código es sintácticamente correcto.\n")
            print("Árbol de Sintaxis Abstracta (AST) en formato de texto:")
            self.print_ast(tree)
            self.visualize_ast(tree, code)
        except SyntaxError as e:
            print(f"Error de sintaxis: {e}")

    def print_ast(self, node, indent=""):
        """Imprimir el AST de forma jerárquica."""
        print(f"{indent}{type(node).__name__}")
        indent += "  "
        for field, value in ast.iter_fields(node):
            if isinstance(value, ast.AST):
                print(f"{indent}{field}:")
                self.print_ast(value, indent + "  ")
            elif isinstance(value, list):
                print(f"{indent}{field}: [")
                for item in value:
                    if isinstance(item, ast.AST):
                        self.print_ast(item, indent + "  ")
                print(f"{indent}]")
            else:
                print(f"{indent}{field}: {value}")

    def visualize_ast(self, tree, code):
        # Grafo dirigido para representar el árbol sintáctico
        G = nx.DiGraph()

        # Función recursiva para recorrer el árbol AST y añadir nodos y aristas
        def add_edges(node, parent_name=None):
            node_name = self.get_node_label(node, code)  # Obtener el label con el valor del token ingresado
            if node_name:
                G.add_node(node_name, label=node_name)
            
            if parent_name and node_name:  # Solo agregar la arista si el nodo tiene un label válido
                G.add_edge(parent_name, node_name)

            for child in ast.iter_child_nodes(node):
                add_edges(child, node_name)

        # Iniciar la construcción del árbol desde la raíz
        add_edges(tree)

        # Dibujar el árbol sintáctico
        pos = self.hierarchical_layout(G, list(G.nodes)[0])  # Tomar el primer nodo como raíz
        labels = nx.get_node_attributes(G, 'label')
        
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, labels=labels, with_labels=True, node_size=2000, 
                node_color='pink', font_size=10, font_weight='bold', edge_color='gray', arrows=True)
        plt.title("Árbol Sintáctico (AST)")
        plt.show()

    def get_node_label(self, node, code):
        """Obtener una etiqueta del nodo que refleje el token ingresado por el usuario."""
        if isinstance(node, ast.Constant):
            return str(node.value)  # Mostrar el valor de la constante
        elif isinstance(node, ast.Name):
            return node.id  # Mostrar el identificador de la variable
        elif isinstance(node, ast.BinOp):
            return self.get_operator_symbol(node.op)  # Mostrar el símbolo del operador
        elif isinstance(node, ast.UnaryOp):
            return self.get_operator_symbol(node.op)  # Mostrar el símbolo del operador unario
        return ""  # No mostrar etiquetas para nodos sin interés

    def get_operator_symbol(self, operator):
        """Obtener el símbolo del operador en formato de cadena."""
        operator_mapping = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.Div: '/',
            ast.Mod: '%',
            ast.Pow: '**',
            ast.LShift: '<<',
            ast.RShift: '>>',
            ast.BitOr: '|',
            ast.BitXor: '^',
            ast.BitAnd: '&',
            ast.FloorDiv: '//',
        }
        return operator_mapping.get(type(operator), '')

    def hierarchical_layout(self, G, root, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        """Layout jerárquico para dibujar el árbol."""
        pos = self._hierarchical_pos(G, root, width, vert_gap, vert_loc, xcenter)
        return pos

    def _hierarchical_pos(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
        """Función recursiva para crear la posición jerárquica."""
        if pos is None:
            pos = {root: (xcenter, vert_loc)}
        else:
            pos[root] = (xcenter, vert_loc)
        
        children = list(G.successors(root))
        if not children:
            return pos
        
        dx = width / len(children)
        nextx = xcenter - width/2 - dx/2

        for child in children:
            nextx += dx
            pos = self._hierarchical_pos(G, child, width=dx, vert_gap=vert_gap, 
                                         vert_loc=vert_loc-vert_gap, xcenter=nextx, pos=pos, 
                                         parent=root, parsed=parsed)

        return pos

def main():
    print("Por favor, ingrese el código fuente a analizar (deje una línea vacía para finalizar):")
    lineas = []

    while True:
        linea = input()
        if linea == "":
            break
        lineas.append(linea)

    codigo_fuente = "\n".join(lineas)

    # Análisis léxico
    tokens = tokenize(codigo_fuente)

    print("\nTokens identificados agrupados por categoría:")
    for token_type, token_values in tokens.items():
        print(f"{token_type}: {', '.join(token_values)}")

    # Análisis sintáctico y visualización
    visualizer = SyntaxTreeVisualizer()
    visualizer.analyze_and_visualize(codigo_fuente)

if __name__ == "__main__":
    main()
