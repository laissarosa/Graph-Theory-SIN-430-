"""
statistics_report.py

Cálculo e escrita de estatísticas de um grafo: número de vértices,
número de arestas, graus (mínimo, máximo, médio, mediana), informações
sobre as componentes conexas, e formatação/escrita de resultados de
consultas pontuais (distância entre dois vértices, diâmetro).

Observação: este arquivo não se chama "statistics.py" para não colidir
com o módulo "statistics" da biblioteca padrão do Python (usado aqui
apenas para calcular a mediana).
"""

from statistics import median as _median
from typing import List, Optional

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

    @property
    def components(self) -> List[List[int]]:
        """Lista de vértices de cada componente conexa, em ordem decrescente de tamanho."""
        return self._components

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
        for i, componente in enumerate(self.components, start=1):
            vertices_str = ", ".join(str(v) for v in sorted(componente))
            lines.append(f"  Componente {i}: {len(componente)} vértice(s) — [{vertices_str}]")
        lines.append("")
        return "\n".join(lines)

    def write_to_file(self, filepath: str) -> None:
        """Escreve o relatório de estatísticas em um arquivo texto."""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.as_text())

    # ---- Distância entre dois vértices ----
    #
    # O valor de `d` já vem calculado de fora (main.py cronometra apenas a
    # chamada a graph.distance(u, v)); aqui só formatamos e ACRESCENTAMOS
    # o resultado ao arquivo de saída consolidado (mesmo arquivo das
    # estatísticas), mantendo a escrita em disco fora da medição de tempo.

    def distance_text(self, u: int, v: int, d: Optional[int]) -> str:
        """Formata o resultado de uma consulta de distância entre u e v."""
        if d is None:
            return f"Não há caminho entre {u} e {v} (vértices em componentes diferentes).\n"
        return f"Distância entre {u} e {v}: {d}\n"

    def write_distance_report(self, u: int, v: int, d: Optional[int], filepath: str) -> None:
        """Acrescenta ao arquivo de saída o resultado de uma consulta de distância entre u e v."""
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(self.distance_text(u, v, d))

    # ---- Diâmetro ----
    #
    # Mesmo esquema: `diametro` já vem calculado (exato ou aproximado);
    # o método só formata e acrescenta ao arquivo de saída consolidado.

    def diameter_text(self, diametro: int, tipo: str) -> str:
        """Formata o resultado do cálculo do diâmetro ('exato' ou 'aprox')."""
        return f"Diâmetro ({tipo}): {diametro}\n"

    def write_diameter_report(self, diametro: int, tipo: str, filepath: str) -> None:
        """Acrescenta ao arquivo de saída o resultado do cálculo do diâmetro."""
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n")
            f.write(self.diameter_text(diametro, tipo))

    # ---- Log de tempos de execução ----

    @staticmethod
    def registrar_tempo(filepath: str, descricao: str, tempo_gasto: float) -> None:
        """Acrescenta ao arquivo de saída uma linha com o tempo de execução de uma operação."""
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(f"{descricao}: {tempo_gasto:.6f} segundos\n")
