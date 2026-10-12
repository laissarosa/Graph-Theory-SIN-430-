"""
estudo_de_caso.py

Estudos de caso da parte de grafos com pesos.

  1. Distância e caminho mínimo entre o vértice 10 e os vértices
     20, 30, 40, 50 e 60 (Dijkstra com heap) -> uma tabela por grafo.
  2. Tempo médio para calcular as distâncias de um vértice a todos os
     outros, para Dijkstra sem heap (vetor) e com heap -> uma tabela
     comparando os grafos. São sorteados k vértices iniciais (os MESMOS
     para as duas implementações), mede-se o tempo total e divide-se
     por k (média amostral).

Uso:
    python estudo_de_caso.py grafos/W_1.txt grafos/W_2.txt grafos/W_3.txt --k 100 --saida estudo_de_caso.md

Observação: o Dijkstra sem heap é O(n^2) por execução; em grafos grandes
use um k menor (ex.: --k 10) e informe isso no relatório.
"""

import argparse
import os
import random
import time

from adjacency_list import AdjacencyListGraph
from adjacency_matrix import AdjacencyMatrixGraph

REPRESENTACOES = {"list": AdjacencyListGraph, "matrix": AdjacencyMatrixGraph}


def fmt_dist(d):
    return "sem caminho" if d is None else f"{d:.6g}"


def tabela_md(cabecalho, linhas):
    out = ["| " + " | ".join(cabecalho) + " |",
           "|" + "|".join("---" for _ in cabecalho) + "|"]
    for linha in linhas:
        out.append("| " + " | ".join(str(c) for c in linha) + " |")
    return "\n".join(out)


def pergunta_1(grafo, nome, origem, destinos):
    if grafo.has_negative_weight:
        return f"Grafo {nome}: possui pesos negativos; Dijkstra não aplicável.\n"
    if not (1 <= origem <= grafo.num_vertices):
        return f"Grafo {nome}: vértice de origem {origem} inexistente.\n"
    resultado = grafo.dijkstra_heap(origem)  # uma execução serve para todos os destinos
    linhas = []
    for dest in destinos:
        if not (1 <= dest <= grafo.num_vertices):
            linhas.append((dest, "vértice inexistente", "-"))
            continue
        d = resultado["dist"].get(dest)
        caminho = grafo.path_from_parents(resultado["parent"], dest)
        linhas.append((dest, fmt_dist(d), " -> ".join(map(str, caminho)) if caminho else "-"))
    return (f"**Grafo {nome}** — origem {origem}\n\n"
            + tabela_md(["Destino", "Distância", "Caminho mínimo"], linhas) + "\n")


def pergunta_2(grafo, k, rng):
    """Retorna (tempo médio vetor, tempo médio heap, k efetivo) ou None."""
    if grafo.has_negative_weight:
        return None
    k = min(k, grafo.num_vertices)
    inicios = rng.sample(range(1, grafo.num_vertices + 1), k)

    t0 = time.perf_counter()
    for s in inicios:
        grafo.dijkstra_vector(s)
    t_vetor = time.perf_counter() - t0

    t0 = time.perf_counter()
    for s in inicios:
        grafo.dijkstra_heap(s)
    t_heap = time.perf_counter() - t0

    return t_vetor / k, t_heap / k, k


def main():
    parser = argparse.ArgumentParser(description="Estudos de caso - grafos com pesos.")
    parser.add_argument("arquivos", nargs="+", help="Arquivos de grafos com pesos.")
    parser.add_argument("--repr", choices=["list", "matrix"], default="list",
                        help="Representação interna (padrão: list).")
    parser.add_argument("--k", type=int, default=100,
                        help="Quantidade de vértices iniciais sorteados (padrão: 100).")
    parser.add_argument("--seed", type=int, default=42, help="Semente aleatória (padrão: 42).")
    parser.add_argument("--origem", type=int, default=10, help="Vértice de origem (padrão: 10).")
    parser.add_argument("--destinos", type=int, nargs="+", default=[20, 30, 40, 50, 60],
                        help="Vértices de destino (padrão: 20 30 40 50 60).")
    parser.add_argument("--saida", default="estudo_de_caso.md", help="Arquivo de saída (markdown).")
    args = parser.parse_args()

    classe = REPRESENTACOES[args.repr]
    rng = random.Random(args.seed)
    blocos_q1, linhas_q2 = [], []

    for caminho_arq in args.arquivos:
        nome = os.path.splitext(os.path.basename(caminho_arq))[0]
        print(f"Lendo {caminho_arq} ...")
        grafo = classe.from_file(caminho_arq)

        blocos_q1.append(pergunta_1(grafo, nome, args.origem, args.destinos))

        print(f"  Medindo tempos de Dijkstra (k={args.k}) ...")
        res = pergunta_2(grafo, args.k, rng)
        if res is None:
            linhas_q2.append((nome, grafo.num_vertices, grafo.num_edges, "-", "-", "-", "-"))
        else:
            t_vetor, t_heap, k_ef = res
            speedup = t_vetor / t_heap if t_heap > 0 else float("inf")
            linhas_q2.append((nome, grafo.num_vertices, grafo.num_edges, k_ef,
                              f"{t_vetor:.6f}", f"{t_heap:.6f}", f"{speedup:.1f}x"))

    texto = ["# Estudos de caso — grafos com pesos\n",
             f"Representação: `{args.repr}` | semente: {args.seed}\n",
             "## 1. Distância e caminho mínimo\n", *blocos_q1,
             "\n## 2. Tempo médio de Dijkstra (um vértice → todos)\n",
             tabela_md(["Grafo", "n", "m", "k", "Sem heap (s)", "Com heap (s)", "Speedup"], linhas_q2),
             "\nTempos em segundos por execução (tempo total de k execuções / k).\n"]
    saida = "\n".join(texto)
    print("\n" + saida)
    with open(args.saida, "w", encoding="utf-8") as f:
        f.write(saida)
    print(f"Resultados escritos em: {args.saida}")


if __name__ == "__main__":
    main()
