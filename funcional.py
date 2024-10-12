import re
import ast
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict

# Definición de los tokens
TOKENS = [
    ("CLAVES", r'\b(if|else|while|for|return|break|continue|def|class|print|int|float)\b'),  # Palabras clave de Python
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

        try:
            tree = ast.parse(code)
            print("El análisis sintáctico fue exitoso. El código es sintácticamente correcto.")
            return tree
        except SyntaxError as e:
            print("El análisis sintáctico falló debido a un error de sintaxis.")
            print(f"Detalles del error: {e}")
            return None

    def visualize_ast(self, node):
        """Función para generar el gráfico del árbol AST usando matplotlib y networkx"""
        G = nx.DiGraph()  # Grafo dirigido para representar el AST

        def add_edges(graph, node, parent=None):
            """Función recursiva que añade los nodos y aristas al grafo"""
            node_id = str(id(node))
            label = self.get_node_label(node)  # Obtener solo el valor para mostrar
            graph.add_node(node_id, label=label)
            
            if parent:
                parent_id = str(id(parent))
                graph.add_edge(parent_id, node_id)
            
            for field, value in ast.iter_fields(node):
                if isinstance(value, ast.AST):
                    add_edges(graph, value, node)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, ast.AST):
                            add_edges(graph, item, node)
        
        add_edges(G, node)
        
        # Layout jerárquico
        pos = self.hierarchical_layout(G, str(id(node)))
        labels = nx.get_node_attributes(G, 'label')
        
        plt.figure(figsize=(10, 6))  # Tamaño de la figura ajustado
        nx.draw(G, pos, labels=labels, with_labels=True, node_size=2000, 
                node_color='lightblue', font_size=12, font_weight='bold', edge_color='gray', arrows=True)
        plt.title("Árbol de Sintaxis Abstracta (AST)")
        plt.show()

    def get_node_label(self, node):
        """Devuelve una etiqueta para el nodo, basada en su valor"""
        if isinstance(node, ast.Constant):
            return str(node.value)  # Mostrar el valor para constantes
        elif isinstance(node, ast.Name):
            return node.id  # Mostrar el nombre de la variable
        elif isinstance(node, ast.BinOp):
            return self.get_operator_symbol(node.op)  # Mostrar el símbolo del operador
        elif isinstance(node, ast.UnaryOp):
            return self.get_operator_symbol(node.op)  # Mostrar el símbolo del operador unario
        return type(node).__name__  # Por defecto, usar el tipo

    def get_operator_symbol(self, operator):
        """Devuelve el símbolo del operador en formato de cadena"""
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
        return operator_mapping.get(type(operator), type(operator).__name__)  # Retornar el símbolo o el nombre

    def hierarchical_layout(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5):
        """Función para crear un layout jerárquico para un grafo dirigido."""
        pos = self._hierarchical_pos(G, root, width, vert_gap, vert_loc, xcenter)
        return pos

    def _hierarchical_pos(self, G, root=None, width=1., vert_gap=0.2, vert_loc=0, xcenter=0.5, pos=None, parent=None, parsed=[]):
        """Función recursiva para generar un layout jerárquico para el grafo."""
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

    # Análisis sintáctico
    analyzer = SyntaxAnalyzer()
    tree = analyzer.analyze(codigo_fuente)

    if tree is not None:  # Solo genera el gráfico si el análisis fue exitoso
        print("Generando gráfico del árbol sintáctico...")
        analyzer.visualize_ast(tree)

if __name__ == "__main__":
    main()

