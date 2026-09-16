"""
benchmark.py

Script auxiliar para os estudos de caso pedidos no trabalho:
  1. Mede a memória usada pelo processo ao carregar o grafo em cada
     representação (lista vs. matriz de adjacência).
  2. Mede o tempo médio de execução de BFS e de DFS, rodando `--n-buscas`
     buscas (padrão 100) a partir de vértices iniciais distintos,
     sorteados aleatoriamente.

Não substitui o relatório (a montagem das tabelas comparando os grafos é
com vocês) — só automatiza a coleta dos números que o enunciado pede.

Uso:
    python benchmark.py grafos/grafo_1.txt --repr list
    python benchmark.py grafos/grafo_1.txt --repr matrix --n-buscas 100 --seed 42

Requer o pacote 'psutil' (funciona em Windows, Linux e macOS):
    pip install psutil
"""

import argparse
import os
import random
import time

try:
    import psutil
except ImportError:
    raise SystemExit(
        "Este script precisa do pacote 'psutil' para medir memória "
        "(funciona em Windows, Linux e macOS). Instale com:\n"
        "    pip install psutil"
    )

from adjacency_list import AdjacencyListGraph
from adjacency_matrix import AdjacencyMatrixGraph

REPRESENTACOES = {
    "list": AdjacencyListGraph,
    "matrix": AdjacencyMatrixGraph,
}

_PROCESSO = psutil.Process(os.getpid())


def memoria_atual_mb() -> float:
    """
    Retorna a memória residente (RSS) usada pelo processo NESTE instante,
    em megabytes.

    Ao contrário de `resource.getrusage(...).ru_maxrss` (que é cumulativo
    e não existe no Windows), `psutil` dá o uso "agora", então o script
    mede antes e depois de carregar o grafo e reporta a diferença como
    aproximação do custo de memória da representação escolhida.
    """
    return _PROCESSO.memory_info().rss / (1024 * 1024)  # bytes -> MB


def escolher_vertices_iniciais(num_vertices: int, quantidade: int, seed=None) -> list:
    """
    Sorteia `quantidade` vértices iniciais distintos entre 1 e num_vertices.
    Se o grafo tiver menos vértices que `quantidade`, permite repetição
    (não há como sortear mais vértices distintos do que os que existem).
    """
    rng = random.Random(seed)
    if num_vertices >= quantidade:
        return rng.sample(range(1, num_vertices + 1), quantidade)
    return [rng.randint(1, num_vertices) for _ in range(quantidade)]


def tempo_medio_busca(grafo, tipo: str, vertices_iniciais):
    """
    Roda `grafo.bfs` ou `grafo.dfs` uma vez para cada vértice em
    vertices_iniciais, cronometrando cada execução individualmente
    (apenas o algoritmo, sem I/O). Retorna (tempo_medio, tempo_total,
    lista_de_tempos), todos em segundos.
    """
    metodo = grafo.bfs if tipo == "bfs" else grafo.dfs
    tempos = []
    for inicio in vertices_iniciais:
        t0 = time.perf_counter()
        metodo(inicio)
        t1 = time.perf_counter()
        tempos.append(t1 - t0)
    return sum(tempos) / len(tempos), sum(tempos), tempos


def main():
    parser = argparse.ArgumentParser(
        description="Mede memória e tempo médio de BFS/DFS de um grafo (estudo de caso)."
    )
    parser.add_argument("arquivo_entrada", help="Arquivo texto com a descrição do grafo.")
    parser.add_argument(
        "--repr", choices=["list", "matrix"], default="list",
        help="Representação interna do grafo (padrão: list).",
    )
    parser.add_argument(
        "--n-buscas", type=int, default=100,
        help="Quantidade de buscas (BFS e DFS) a executar (padrão: 100).",
    )
    parser.add_argument(
        "--seed", type=int, default=None,
        help="Semente do gerador aleatório, para resultados reprodutíveis.",
    )
    parser.add_argument(
        "--saida", default=None,
        help="Arquivo de saída. Padrão: <grafo>_benchmark_<repr>.txt",
    )
    args = parser.parse_args()

    classe_grafo = REPRESENTACOES[args.repr]

    # Memória antes de carregar o grafo (linha de base do processo).
    memoria_antes = memoria_atual_mb()

    t0 = time.perf_counter()
    grafo = classe_grafo.from_file(args.arquivo_entrada)
    t1 = time.perf_counter()
    tempo_leitura = t1 - t0

    # Pico de memória após carregar o grafo. A diferença para memoria_antes
    # aproxima o custo de armazenar o grafo na representação escolhida.
    memoria_depois = memoria_atual_mb()

    vertices_iniciais = escolher_vertices_iniciais(
        grafo.num_vertices, args.n_buscas, seed=args.seed
    )

    media_bfs, total_bfs, _ = tempo_medio_busca(grafo, "bfs", vertices_iniciais)
    media_dfs, total_dfs, _ = tempo_medio_busca(grafo, "dfs", vertices_iniciais)

    nome_grafo = os.path.splitext(os.path.basename(args.arquivo_entrada))[0]
    saida = args.saida or f"{nome_grafo}_benchmark_{args.repr}.txt"

    linhas = [
        f"Grafo: {args.arquivo_entrada}",
        f"Representação: {args.repr}",
        f"Número de vértices: {grafo.num_vertices}",
        f"Número de arestas: {grafo.num_edges}",
        f"Tempo de leitura do arquivo: {tempo_leitura:.6f} s (não entra nas médias)",
        "",
        f"Memória do processo antes de carregar o grafo: {memoria_antes:.3f} MB",
        f"Memória do processo (pico) após carregar o grafo: {memoria_depois:.3f} MB",
        f"Memória aproximada usada pelo grafo: {memoria_depois - memoria_antes:.3f} MB",
        "",
        f"Quantidade de buscas por algoritmo: {len(vertices_iniciais)}",
        f"Vértices iniciais sorteados: {vertices_iniciais}",
        "",
        f"BFS - tempo total: {total_bfs:.6f} s",
        f"BFS - tempo médio por busca: {media_bfs:.6f} s",
        "",
        f"DFS - tempo total: {total_dfs:.6f} s",
        f"DFS - tempo médio por busca: {media_dfs:.6f} s",
    ]
    texto = "\n".join(linhas) + "\n"

    with open(saida, "w", encoding="utf-8") as f:
        f.write(texto)

    print(texto)
    print(f"Resultados escritos em: {saida}")


if __name__ == "__main__":
    main()
