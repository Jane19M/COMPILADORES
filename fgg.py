import ast
import matplotlib.pyplot as plt
import networkx as nx

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
            graph.add_node(node_id, label=type(node).__name__)
            
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
        
        # Definir un layout jerárquico manual
        pos = self.hierarchical_layout(G, str(id(node)))
        labels = nx.get_node_attributes(G, 'label')
        
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, labels=labels, with_labels=True, node_size=2000, 
                node_color='lightblue', font_size=10, font_weight='bold', edge_color='gray', arrows=True)
        plt.title("Árbol de Sintaxis Abstracta (AST)")
        plt.show()

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

    analyzer = SyntaxAnalyzer()
    tree = analyzer.analyze(codigo_fuente)

    if tree is not None:  # Solo genera el gráfico si el análisis fue exitoso
        print("Generando gráfico del árbol sintáctico...")
        analyzer.visualize_ast(tree)

if __name__ == "__main__":
    main()
