"""
statistics_report.py

Cálculo e escrita de estatísticas de um grafo: número de vértices,
número de arestas, graus (mínimo, máximo, médio, mediana) e informações
sobre as componentes conexas.

Observação: este arquivo não se chama "statistics.py" para não colidir
com o módulo "statistics" da biblioteca padrão do Python (usado aqui
apenas para calcular a mediana).
"""

from statistics import median as _median
from typing import List

from graph import Graph


class GraphStatistics:
    """Calcula e formata estatísticas de um objeto Graph."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self._degrees: List[int] = graph.all_degrees()
        self._components: List[List[int]] = graph.connected_components()

    # ---- Estatísticas de grau ----

    @property
    def num_vertices(self) -> int:
        return self.graph.num_vertices

    @property
    def num_edges(self) -> int:
        return self.graph.num_edges

    @property
    def min_degree(self) -> int:
        return min(self._degrees) if self._degrees else 0

    @property
    def max_degree(self) -> int:
        return max(self._degrees) if self._degrees else 0

    @property
    def avg_degree(self) -> float:
        return sum(self._degrees) / len(self._degrees) if self._degrees else 0.0

    @property
    def median_degree(self) -> float:
        return _median(self._degrees) if self._degrees else 0.0

    # ---- Componentes conexas ----

    @property
    def num_components(self) -> int:
        return len(self._components)

    @property
    def component_sizes(self) -> List[int]:
        """Tamanhos das componentes conexas, em ordem decrescente."""
        return [len(c) for c in self._components]

    def as_text(self) -> str:
        """Monta o relatório de estatísticas como uma string formatada."""
        lines = [
            f"Número de vértices: {self.num_vertices}",
            f"Número de arestas: {self.num_edges}",
            f"Grau mínimo: {self.min_degree}",
            f"Grau máximo: {self.max_degree}",
            f"Grau médio: {self.avg_degree:.4f}",
            f"Mediana de grau: {self.median_degree}",
            "",
            f"Número de componentes conexas: {self.num_components}",
        ]
        for i, size in enumerate(self.component_sizes, start=1):
            lines.append(f"  Componente {i}: {size} vértice(s)")
        lines.append("")
        return "\n".join(lines)

    def write_to_file(self, filepath: str) -> None:
        """Escreve o relatório de estatísticas em um arquivo texto."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.as_text())
