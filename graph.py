"""
graph.py

Define a classe abstrata Graph, que representa um grafo não-direcionado
(com ou sem pesos nas arestas) e implementa tudo que não depende de como
o grafo é armazenado internamente: leitura de arquivo (from_file), BFS,
DFS, cálculo de graus, componentes conexas, diâmetro e caminhos mínimos
(Dijkstra com e sem heap).

As classes concretas (AdjacencyListGraph e AdjacencyMatrixGraph) só
precisam implementar add_edge, neighbors e weighted_neighbors; o resto da
biblioteca funciona automaticamente para as duas.

Grafos sem pesos continuam funcionando normalmente: toda aresta sem peso
explícito recebe peso 1.0.
"""

import heapq
from abc import ABC, abstractmethod
from collections import deque
from typing import Dict, Iterator, List, Optional, Set, Tuple

INF = float("inf")


class Graph(ABC):
    """
    Classe abstrata para um grafo não-direcionado, opcionalmente ponderado.

    Vértices são numerados de 1 a num_vertices (1-indexado), seguindo
    o formato do arquivo de entrada da disciplina.

    Atributos de peso:
        is_weighted         -> True se alguma aresta foi inserida com peso explícito.
        has_negative_weight -> True se alguma aresta tem peso negativo
                               (nesse caso Dijkstra não pode ser usado).
    """

    def __init__(self, num_vertices: int):
        if num_vertices < 0:
            raise ValueError("Número de vértices não pode ser negativo.")
        self.num_vertices = num_vertices
        self.num_edges = 0
        self.is_weighted = False
        self.has_negative_weight = False

    # ---- Métodos que cada representação concreta deve implementar ----

    @abstractmethod
    def add_edge(self, u: int, v: int, weight: Optional[float] = None) -> None:
        """
        Adiciona uma aresta {u, v} ao grafo (sem duplicar arestas).
        Se weight for None, a aresta recebe peso 1.0 (grafo sem pesos).
        Implementações devem chamar self._register_weight(weight) ao
        inserir uma aresta nova e armazenar o valor retornado.
        """
        raise NotImplementedError

    @abstractmethod
    def neighbors(self, v: int) -> List[int]:
        """Retorna a lista de vizinhos do vértice v."""
        raise NotImplementedError

    @abstractmethod
    def weighted_neighbors(self, v: int) -> List[Tuple[int, float]]:
        """Retorna a lista de pares (vizinho, peso da aresta) do vértice v."""
        raise NotImplementedError

    def get_weight(self, u: int, v: int) -> Optional[float]:
        """Retorna o peso da aresta {u, v}, ou None se ela não existir."""
        self._check_vertex(u)
        self._check_vertex(v)
        for w, peso in self.weighted_neighbors(u):
            if w == v:
                return peso
        return None

    def _check_vertex(self, v: int) -> None:
        if not (1 <= v <= self.num_vertices):
            raise ValueError(f"Vértice {v} fora do intervalo [1, {self.num_vertices}].")

    def _register_weight(self, weight: Optional[float]) -> float:
        """
        Valida o peso de uma aresta nova, atualiza os indicadores
        is_weighted / has_negative_weight e devolve o peso a armazenar.
        """
        if weight is None:
            return 1.0
        weight = float(weight)
        if weight != weight or weight in (INF, -INF):
            raise ValueError("Peso de aresta deve ser um número real finito.")
        self.is_weighted = True
        if weight < 0:
            self.has_negative_weight = True
        return weight

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
                              (sem pesos) ou "u v peso" (com pesos, onde
                              peso é qualquer número em ponto flutuante).
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
                if len(parts) not in (2, 3):
                    raise ValueError(
                        f"Linha {line_num} inválida: esperado 'u v' ou 'u v peso', "
                        f"obtido {line!r}."
                    )
                u, v = int(parts[0]), int(parts[1])
                peso = float(parts[2]) if len(parts) == 3 else None
                if u == v:
                    # Laços (u == v) são ignorados silenciosamente, assim como
                    # arestas duplicadas — não interrompem a leitura do arquivo.
                    self_loops_ignorados += 1
                    continue
                graph.add_edge(u, v, peso)

            if self_loops_ignorados > 0:
                print(
                    f"Aviso: {self_loops_ignorados} laço(s) (aresta 'u u') "
                    f"encontrado(s) em {filepath!r} foram ignorados."
                )

        return graph

    # ---- Funcionalidades comuns, implementadas em termos de neighbors() ----

    def edges(self) -> Iterator[Tuple[int, int, float]]:
        """Gera cada aresta uma única vez, como (u, v, peso) com u < v."""
        for u in range(1, self.num_vertices + 1):
            for v, peso in self.weighted_neighbors(u):
                if u < v:
                    yield (u, v, peso)

    def degree(self, v: int) -> int:
        """Retorna o grau do vértice v."""
        self._check_vertex(v)
        return len(self.neighbors(v))

    def all_degrees(self) -> List[int]:
        """Retorna a lista de graus de todos os vértices, na ordem 1..n."""
        return [self.degree(v) for v in range(1, self.num_vertices + 1)]

    def bfs(self, start: int) -> Dict:
        """
        Busca em largura (BFS) a partir do vértice start.

        Retorna um dicionário com:
            - 'parent': mapa vértice -> pai na árvore de busca (None para a raiz)
            - 'level' : mapa vértice -> nível/distância a partir de start
        Apenas os vértices alcançáveis a partir de start são incluídos.
        (Ignora os pesos: o nível é o número de arestas.)
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

    def dfs(self, start: int) -> Dict:
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
        os vértices u e v, ignorando pesos. Retorna None se não houver
        caminho entre eles (grafo desconexo).
        Para a distância ponderada, use weighted_distance / shortest_path.
        """
        self._check_vertex(u)
        self._check_vertex(v)
        result = self.bfs(u)
        return result["level"].get(v)

    def diameter(self) -> int:
        """
        Retorna o diâmetro do grafo: a maior distância (em número de arestas)
        entre qualquer par de vértices alcançáveis entre si.
        """
        maior = 0
        for v in range(1, self.num_vertices + 1):
            result = self.bfs(v)
            maior_local = max(result["level"].values())
            maior = max(maior, maior_local)
        return maior

    def diameter_approx(self) -> int:
        """
        Versão aproximada do diâmetro:
        duas BFS ao invés de uma por vértice. Não garante o valor exato,
        mas é muito mais rápida em grafos grandes.
        """
        vertice_inicial = 1
        result_a = self.bfs(vertice_inicial)
        a = max(result_a["level"], key=result_a["level"].get)

        result_b = self.bfs(a)
        b = max(result_b["level"], key=result_b["level"].get)

        return result_b["level"][b]

    # ---- Caminhos mínimos em grafos com pesos (Dijkstra) ----

    def _check_dijkstra(self, start: int) -> None:
        self._check_vertex(start)
        if self.has_negative_weight:
            raise ValueError(
                "O grafo possui arestas com peso negativo: o algoritmo de "
                "Dijkstra não é aplicável (a biblioteca não implementa "
                "caminhos mínimos com pesos negativos)."
            )

    def dijkstra_vector(self, start: int) -> Dict:
        """
        Dijkstra SEM heap: a cada iteração, o vértice não visitado de menor
        distância é encontrado por varredura linear do vetor de distâncias.
        Complexidade: O(n^2 + m).

        Retorna {'dist': {v: distância}, 'parent': {v: pai}} apenas com os
        vértices alcançáveis a partir de start.
        """
        self._check_dijkstra(start)
        n = self.num_vertices
        dist = [INF] * (n + 1)
        parent: List[Optional[int]] = [None] * (n + 1)
        done = [False] * (n + 1)
        dist[start] = 0.0

        for _ in range(n):
            u = -1
            melhor = INF
            for v in range(1, n + 1):
                if not done[v] and dist[v] < melhor:
                    melhor = dist[v]
                    u = v
            if u == -1:  # restantes são inalcançáveis
                break
            done[u] = True
            for w, peso in self.weighted_neighbors(u):
                if not done[w]:
                    nova = melhor + peso
                    if nova < dist[w]:
                        dist[w] = nova
                        parent[w] = u

        return self._pack_dijkstra(dist, parent)

    def dijkstra_heap(self, start: int) -> Dict:
        """
        Dijkstra COM heap (heapq, remoção preguiçosa de entradas obsoletas).
        Complexidade: O((n + m) log n).

        Retorna {'dist': {v: distância}, 'parent': {v: pai}} apenas com os
        vértices alcançáveis a partir de start.
        """
        self._check_dijkstra(start)
        n = self.num_vertices
        dist = [INF] * (n + 1)
        parent: List[Optional[int]] = [None] * (n + 1)
        done = [False] * (n + 1)
        dist[start] = 0.0
        heap: List[Tuple[float, int]] = [(0.0, start)]

        while heap:
            d, u = heapq.heappop(heap)
            if done[u]:
                continue
            done[u] = True
            for w, peso in self.weighted_neighbors(u):
                if not done[w]:
                    nova = d + peso
                    if nova < dist[w]:
                        dist[w] = nova
                        parent[w] = u
                        heapq.heappush(heap, (nova, w))

        return self._pack_dijkstra(dist, parent)

    def dijkstra(self, start: int, use_heap: bool = True) -> Dict:
        """Executa Dijkstra a partir de start, com heap (padrão) ou sem."""
        if use_heap:
            return self.dijkstra_heap(start)
        return self.dijkstra_vector(start)

    @staticmethod
    def _pack_dijkstra(dist: List[float], parent: List[Optional[int]]) -> Dict:
        alc = {v: d for v, d in enumerate(dist) if v >= 1 and d < INF}
        return {"dist": alc, "parent": {v: parent[v] for v in alc}}

    @staticmethod
    def path_from_parents(parent: Dict[int, Optional[int]], target: int) -> Optional[List[int]]:
        """Reconstrói o caminho start -> target a partir do mapa de pais."""
        if target not in parent:
            return None
        caminho = []
        atual: Optional[int] = target
        while atual is not None:
            caminho.append(atual)
            atual = parent[atual]
        caminho.reverse()
        return caminho

    def shortest_path(self, u: int, v: int, use_heap: bool = True) -> Tuple[Optional[float], Optional[List[int]]]:
        """
        Retorna (distância, caminho) mínimo ponderado entre u e v, onde
        caminho é a lista de vértices de u até v. Retorna (None, None) se
        não houver caminho.
        """
        self._check_vertex(v)
        result = self.dijkstra(u, use_heap)
        if v not in result["dist"]:
            return None, None
        return result["dist"][v], self.path_from_parents(result["parent"], v)

    def weighted_distance(self, u: int, v: int, use_heap: bool = True) -> Optional[float]:
        """Distância mínima ponderada entre u e v (None se não houver caminho)."""
        return self.shortest_path(u, v, use_heap)[0]

    def __repr__(self) -> str:
        return (f"{self.__class__.__name__}(num_vertices={self.num_vertices}, "
                f"num_edges={self.num_edges})")
