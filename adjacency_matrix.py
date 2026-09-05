"""
adjacency_matrix.py

Implementação de grafo não-direcionado usando matriz de adjacência.
"""

from typing import List
from graph import Graph

class AdjacencyMatrixGraph(Graph):
    """Representação de grafo por matriz de adjacência."""

    def __init__(self, num_vertices: int):
        super().__init__(num_vertices)
        n = num_vertices + 1
        # _matrix[u][v] == 1 se existe aresta {u, v}, 0 caso contrário.
        self._matrix: List[bytearray] = [bytearray(n) for _ in range(n)]

    def add_edge(self, u: int, v: int) -> None:
        self._check_vertex(u)
        self._check_vertex(v)
        if u == v:
            raise ValueError("Laços (self-loops) não são permitidos.")
        if not self._matrix[u][v]:
            self._matrix[u][v] = 1
            self._matrix[v][u] = 1
            self.num_edges += 1

    def has_edge(self, u: int, v: int) -> bool:
        self._check_vertex(u)
        self._check_vertex(v)
        return bool(self._matrix[u][v])

    def neighbors(self, v: int) -> List[int]:
        self._check_vertex(v)
        row = self._matrix[v]
        return [w for w in range(1, self.num_vertices + 1) if row[w]]
