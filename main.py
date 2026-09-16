"""
main.py

Programa de exemplo que usa a biblioteca (graph.py, adjacency_list.py,
adjacency_matrix.py, statistics_report.py) para:
  1. Ler um grafo de um arquivo texto, na representação escolhida;
  2. Escrever, em um único arquivo de saída (--saida): estatísticas do
     grafo, tempos de execução, e (se pedidos) resultado de distância e
     de diâmetro.
  3. Opcionalmente, gerar a árvore de busca (BFS/DFS) em um arquivo
     separado, por ter formato tabular próprio.

Uso:
    python main.py caminho/para/grafo.txt [--repr list|matrix] [--saida relatorio.txt]

Exemplo:
    python main.py grafos/grafo_1.txt --repr list --saida grafo_1_relatorio.txt --busca bfs --inicio 10 --distancia 10 20 --diametro exato
"""

import argparse
import os
import time

from adjacency_list import AdjacencyListGraph
from adjacency_matrix import AdjacencyMatrixGraph
from statistics_report import GraphStatistics

REPRESENTACOES = {
    "list": AdjacencyListGraph,
    "matrix": AdjacencyMatrixGraph,
}


def main():
    parser = argparse.ArgumentParser(description="Análise de estatísticas de um grafo.")
    parser.add_argument("arquivo_entrada", help="Arquivo texto com a descrição do grafo.")
    parser.add_argument(
        "--repr", choices=["list", "matrix"], default="list",
        help="Representação interna do grafo (padrão: list).",
    )
    parser.add_argument(
        "--saida", default="estatisticas.txt",
        help="Arquivo texto de saída com as estatísticas (padrão: estatisticas.txt).",
    )
    parser.add_argument(
        "--busca", choices=["bfs", "dfs"], default=None,
        help="Tipo de busca a executar (bfs ou dfs). Se omitido, não faz busca.",
    )
    parser.add_argument(
        "--inicio", type=int, default=None,
        help="Vértice inicial da busca (obrigatório se --busca for usado).",
    )
    parser.add_argument(
        "--distancia", type=int, nargs=2, metavar=("U", "V"), default=None,
        help="Calcula a distância entre os vértices U e V.",
    )
    parser.add_argument(
        "--diametro", choices=["exato", "aprox"], default=None,
        help="Calcula o diâmetro do grafo (exato ou aproximado).",
    )
    args = parser.parse_args()

    classe_grafo = REPRESENTACOES[args.repr]
    grafo = classe_grafo.from_file(args.arquivo_entrada)
    nome_grafo = os.path.splitext(os.path.basename(args.arquivo_entrada))[0]

    # Um único arquivo de saída (args.saida) recebe estatísticas, tempos de
    # execução, distância e diâmetro. Só a árvore de busca (BFS/DFS) vai
    # para um arquivo separado, por ter formato tabular próprio.
    stats = GraphStatistics(grafo)
    print(stats.as_text())
    stats.write_to_file(args.saida)
    print(f"Estatísticas escritas em: {args.saida}")

    if args.busca is not None:
        if args.inicio is None:
            parser.error("--inicio é obrigatório quando --busca é usado.")

        t0 = time.perf_counter()
        if args.busca == "bfs":
            resultado = grafo.bfs(args.inicio)
        else:
            resultado = grafo.dfs(args.inicio)
        t1 = time.perf_counter()
        tempo_gasto = t1 - t0

        arquivo_busca = f"{nome_grafo}_{args.busca}.txt"
        grafo.write_search_tree(resultado, arquivo_busca)
        print(f"Árvore de {args.busca.upper()} escrita em: {arquivo_busca}")
        print(f"Tempo de execução do {args.busca.upper()}: {tempo_gasto:.6f} segundos")
        stats.registrar_tempo(args.saida, f"{args.busca.upper()} (início={args.inicio})", tempo_gasto)

    if args.distancia is not None:
        u, v = args.distancia
        t0 = time.perf_counter()
        d = grafo.distance(u, v)
        t1 = time.perf_counter()
        tempo_gasto = t1 - t0

        stats.write_distance_report(u, v, d, args.saida)
        stats.registrar_tempo(args.saida, f"Distância({u},{v})", tempo_gasto)
        print(f"Distância entre {u} e {v} escrita em: {args.saida}")
        print(f"Tempo de execução da distância: {tempo_gasto:.6f} segundos")

    if args.diametro is not None:
        t0 = time.perf_counter()
        if args.diametro == "exato":
            d = grafo.diameter()
        else:
            d = grafo.diameter_approx()
        t1 = time.perf_counter()
        tempo_gasto = t1 - t0

        stats.write_diameter_report(d, args.diametro, args.saida)
        stats.registrar_tempo(args.saida, f"Diâmetro ({args.diametro})", tempo_gasto)
        print(f"Diâmetro escrito em: {args.saida}")
        print(f"Tempo de execução do diâmetro ({args.diametro}): {tempo_gasto:.6f} segundos")


if __name__ == "__main__":
    main()
