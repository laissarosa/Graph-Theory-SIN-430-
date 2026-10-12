"""
adjacency_list.py

Implementação de grafo não-direcionado (com ou sem pesos) usando lista de adjacência.
"""

from typing import Dict, List, Optional, Tuple
from graph import Graph


class AdjacencyListGraph(Graph):
    """Representação de grafo por lista de adjacência.
    Uma lista em que cada posição contém um dicionário {vizinho: peso}.
    (Um dicionário mantém a unicidade das arestas, como o set anterior,
    e guarda o peso de cada aresta.)"""

    def __init__(self, num_vertices: int):
        super().__init__(num_vertices)
        # _adj[v] mapeia cada vizinho de v ao peso da aresta (índice 0 não
        # é usado, pois os vértices são numerados de 1 a num_vertices).
        self._adj: List[Dict[int, float]] = [dict() for _ in range(num_vertices + 1)]

    def add_edge(self, u: int, v: int, weight: Optional[float] = None) -> None:
        self._check_vertex(u)
        self._check_vertex(v)
        if u == v:
            raise ValueError("Laços (self-loops) não são permitidos.")
        if v not in self._adj[u]:
            peso = self._register_weight(weight)
            self._adj[u][v] = peso
            self._adj[v][u] = peso
            self.num_edges += 1

    def neighbors(self, v: int) -> List[int]:
        self._check_vertex(v)
        return list(self._adj[v])

    def weighted_neighbors(self, v: int) -> List[Tuple[int, float]]:
        self._check_vertex(v)
        return list(self._adj[v].items())

    def get_weight(self, u: int, v: int) -> Optional[float]:
        self._check_vertex(u)
        self._check_vertex(v)
        return self._adj[u].get(v)
