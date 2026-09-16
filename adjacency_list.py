"""
adjacency_list.py

Implementação de grafo não-direcionado usando lista de adjacência.
"""

from typing import List, Set
from graph import Graph


class AdjacencyListGraph(Graph):
    """Representação de grafo por lista de adjacência (um set por vértice)."""

    def __init__(self, num_vertices: int):
        super().__init__(num_vertices)
        # _adj[v] é o conjunto de vizinhos de v (índice 0 não é usado,
        # pois os vértices são numerados de 1 a num_vertices).
        self._adj: List[Set[int]] = [set() for _ in range(num_vertices + 1)]

    def add_edge(self, u: int, v: int) -> None:
        self._check_vertex(u)
        self._check_vertex(v)
        if u == v:
            raise ValueError("Laços (self-loops) não são permitidos.")
        if v not in self._adj[u]:
            self._adj[u].add(v)
            self._adj[v].add(u)
            self.num_edges += 1

    def has_edge(self, u: int, v: int) -> bool:
        self._check_vertex(u)
        self._check_vertex(v)
        return v in self._adj[u]

    def neighbors(self, v: int) -> List[int]:
        self._check_vertex(v)
        return list(self._adj[v])
