"""
main.py

Programa de exemplo que usa a biblioteca (graph.py, adjacency_list.py,
adjacency_matrix.py, statistics_report.py) para:
  1. Ler um grafo de um arquivo texto, na representação escolhida;
  2. Calcular e escrever estatísticas do grafo em um arquivo de saída.

Uso:
    python main.py caminho/para/grafo.txt [--repr list|matrix] [--saida estatisticas.txt]

Exemplo:
    python main.py grafos/grafo_1.txt --repr list --saida estatisticas.txt
"""

import argparse

from adjacency_list import AdjacencyListGraph
from adjacency_matrix import AdjacencyMatrixGraph
from statistics_report import GraphStatistics

# Mapa usado apenas para traduzir a opção de linha de comando (uma string)
# na classe correspondente. O usuário da biblioteca, ao chamar o código
# diretamente, nunca precisa disso: basta escrever
#   AdjacencyListGraph.from_file(caminho)
# ou
#   AdjacencyMatrixGraph.from_file(caminho)
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
    args = parser.parse_args()

    classe_grafo = REPRESENTACOES[args.repr]
    grafo = classe_grafo.from_file(args.arquivo_entrada)

    stats = GraphStatistics(grafo)
    print(stats.as_text())
    stats.write_to_file(args.saida)
    print(f"Estatísticas escritas em: {args.saida}")


if __name__ == "__main__":
    main()
