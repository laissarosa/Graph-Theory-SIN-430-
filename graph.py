"""
graph.py

Define a classe abstrata Graph, que representa um grafo não-direcionado
e implementa tudo que não depende de como o grafo é armazenado
internamente: leitura de arquivo (from_file), BFS, DFS, cálculo de graus
e componentes conexas.

As classes concretas (AdjacencyListGraph e AdjacencyMatrixGraph) só
precisam implementar add_edge, has_edge e neighbors e o resto da
biblioteca funciona automaticamente para as duas.
"""

from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, List, Optional, Set


class Graph(ABC):
    """
    Classe abstrata para um grafo não-direcionado.

    Vértices são numerados de 1 a num_vertices (1-indexado), seguindo
    o formato do arquivo de entrada da disciplina.
    """

    def __init__(self, num_vertices: int):
        if num_vertices < 0:
            raise ValueError("Número de vértices não pode ser negativo.")
        self.num_vertices = num_vertices
        self.num_edges = 0

    # ---- Métodos que cada representação concreta deve implementar ----

    @abstractmethod
    def add_edge(self, u: int, v: int) -> None:
        """Adiciona uma aresta {u, v} ao grafo (sem duplicar arestas)."""
        raise NotImplementedError

    @abstractmethod
    def has_edge(self, u: int, v: int) -> bool:
        """Retorna True se existe aresta entre u e v."""
        raise NotImplementedError

    @abstractmethod
    def neighbors(self, v: int) -> List[int]:
        """Retorna a lista de vizinhos do vértice v."""
        raise NotImplementedError

    def _check_vertex(self, v: int) -> None:
        if not (1 <= v <= self.num_vertices):
            raise ValueError(f"Vértice {v} fora do intervalo [1, {self.num_vertices}].")

    # ---- Construtor alternativo: lê o grafo de um arquivo texto ----

    @classmethod
    def from_file(cls, filepath: str) -> "Graph":
        """
        Lê um grafo de um arquivo texto e retorna uma instância da classe
        concreta a partir da qual este método foi chamado.

        Exemplo de uso:
            grafo = AdjacencyListGraph.from_file("grafo_1.txt")
            grafo = AdjacencyMatrixGraph.from_file("grafo_1.txt")


        Formato esperado do arquivo:
            linha 1: número de vértices (n)
            linhas seguintes: uma aresta por linha, no formato "u v"
        """
        with open(filepath, "r", encoding="utf-8") as f:
            raw_lines = (line.strip() for line in f)
            lines = (line for line in raw_lines if line)  

            try:
                num_vertices = int(next(lines))
            except StopIteration:
                raise ValueError("Arquivo de entrada vazio.")

            graph = cls(num_vertices)
            self_loops_ignorados = 0

            for line_num, line in enumerate(lines, start=2):
                parts = line.split()
                if len(parts) != 2:
                    raise ValueError(
                        f"Linha {line_num} inválida: esperado 'u v', obtido {line!r}."
                    )
                u, v = int(parts[0]), int(parts[1])
                if u == v:
                    # Laços (u == v) são ignorados silenciosamente, assim como
                    # arestas duplicadas — não interrompem a leitura do arquivo.
                    self_loops_ignorados += 1
                    continue
                graph.add_edge(u, v)

            if self_loops_ignorados > 0:
                print(
                    f"Aviso: {self_loops_ignorados} laço(s) (aresta 'u u') "
                    f"encontrado(s) em {filepath!r} foram ignorados."
                )

        return graph

    # ---- Funcionalidades comuns, implementadas em termos de neighbors() ----

    def degree(self, v: int) -> int:
        """Retorna o grau do vértice v."""
        self._check_vertex(v)
        return len(self.neighbors(v))

    def all_degrees(self) -> List[int]:
        """Retorna a lista de graus de todos os vértices, na ordem 1..n."""
        return [self.degree(v) for v in range(1, self.num_vertices + 1)]

    def bfs(self, start: int) -> Dict[str, Dict[int, Optional[int]]]:
        """
        Busca em largura (BFS) a partir do vértice start.

        Retorna um dicionário com:
            - 'parent': mapa vértice -> pai na árvore de busca (None para a raiz)
            - 'level' : mapa vértice -> nível/distância a partir de start
        Apenas os vértices alcançáveis a partir de start são incluídos.
        """
        self._check_vertex(start)
        parent: Dict[int, Optional[int]] = {start: None}
        level: Dict[int, int] = {start: 0}
        queue = deque([start])

        while queue:
            u = queue.popleft()
            for w in self.neighbors(u):
                if w not in level:
                    level[w] = level[u] + 1
                    parent[w] = u
                    queue.append(w)

        return {"parent": parent, "level": level}

    def dfs(self, start: int) -> Dict[str, Dict[int, Optional[int]]]:
        """
        Busca em profundidade (DFS), implementada de forma iterativa para
        evitar estourar o limite de recursão do Python em grafos grandes.

        Retorna um dicionário com:
            - 'parent': mapa vértice -> pai na árvore de busca (None para a raiz)
            - 'level' : mapa vértice -> nível na árvore de busca
        """
        self._check_vertex(start)
        parent: Dict[int, Optional[int]] = {start: None}
        level: Dict[int, int] = {start: 0}
        visited: Set[int] = set()
        stack = [start]

        while stack:
            u = stack.pop()
            if u in visited:
                continue
            visited.add(u)
            for w in self.neighbors(u):
                if w not in parent:
                    parent[w] = u
                    level[w] = level[u] + 1
                if w not in visited:
                    stack.append(w)

        return {"parent": parent, "level": level}

    def connected_components(self) -> List[List[int]]:
        """
        Retorna a lista de componentes conexas do grafo.

        Cada componente é representada como uma lista de vértices. A lista
        de componentes é ordenada da maior para a menor.
        """
        visited: Set[int] = set()
        components: List[List[int]] = []

        for v in range(1, self.num_vertices + 1):
            if v not in visited:
                result = self.bfs(v)
                component = list(result["level"].keys())
                visited.update(component)
                components.append(component)

        components.sort(key=len, reverse=True)
        return components

    def write_search_tree(self, result, filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("vertice pai nivel\n")
            parent = result["parent"]
            level = result["level"]

            for v in sorted(parent.keys()):
                pai = parent[v] if parent[v] is not None else "-"
                f.write(f"{v} {pai} {level[v]}\n")

            
    def distance(self, u: int, v: int) -> Optional[int]:
        """
        Retorna a distância (número de arestas no caminho mínimo) entre
        os vértices u e v. Retorna None se não houver caminho entre eles
        (grafo desconexo).
        """
        self._check_vertex(u)
        self._check_vertex(v)
        result = self.bfs(u)
        return result["level"].get(v)


    def diameter(self) -> int:
        """
        Retorna o diâmetro do grafo: a maior distância entre qualquer par
        de vértices alcançáveis entre si.
        """
        maior = 0
        for v in range(1, self.num_vertices + 1):
            result = self.bfs(v)
            maior_local = max(result["level"].values())
            maior = max(maior, maior_local)
        return maior


    def diameter_approx(self) -> int:
        """
        Versão aproximada do diâmetro, usando a técnica de "double sweep":
        duas BFS ao invés de uma por vértice. Não garante o valor exato,
        mas é muito mais rápida em grafos grandes.
        """
        vertice_inicial = 1
        result_a = self.bfs(vertice_inicial)
        a = max(result_a["level"], key=result_a["level"].get)

        result_b = self.bfs(a)
        b = max(result_b["level"], key=result_b["level"].get)

        return result_b["level"][b]


    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(num_vertices={self.num_vertices}, "
                f"num_edges={self.num_edges})")
