# graph_lib — Biblioteca de Grafos (COS242 — Trabalho, Parte 1)

Biblioteca orientada a objetos, em Python, para representar e analisar
grafos **não-direcionados**, conforme o enunciado da Parte 1.

## Estrutura

```
graph_lib/
├── __init__.py          # API pública do pacote
├── graph.py              # classe abstrata Graph: BFS, DFS, componentes conexas
├── adjacency_list.py      # AdjacencyListGraph  (representação por lista de adjacência)
├── adjacency_matrix.py    # AdjacencyMatrixGraph (representação por matriz de adjacência)
├── reader.py              # leitura do arquivo texto de entrada
└── statistics.py          # cálculo/escrita das estatísticas do grafo

main.py                   # programa de exemplo (linha de comando)
grafo_exemplo.txt         # grafo da Figura 1 do enunciado (5 vértices)
```

## Design

- **`Graph`** (classe abstrata, `abc.ABC`) define o contrato comum
  (`add_edge`, `has_edge`, `neighbors`) e implementa, em cima desse
  contrato, tudo que não depende da representação interna: `degree`,
  `all_degrees`, `bfs`, `dfs` e `connected_components`. Isso evita
  duplicar esses algoritmos nas duas representações.
- **`AdjacencyListGraph`** guarda, para cada vértice, um `set` com seus
  vizinhos. Uso de memória `O(V + E)` — ideal para grafos esparsos.
- **`AdjacencyMatrixGraph`** guarda uma matriz `V × V`, implementada
  como uma lista de `bytearray` (1 byte por posição, em vez dos ~28
  bytes que um `int` do Python ocupa em uma lista comum). Uso de
  memória `O(V²)`.
- Vértices são numerados de **1 a n** (1-indexado), seguindo o formato
  do arquivo de entrada da disciplina. Arestas duplicadas no arquivo
  são ignoradas (não incrementam `num_edges` nem duplicam o vizinho);
  laços (`u == v`) são rejeitados com `ValueError`.
- O usuário da biblioteca escolhe a representação através do parâmetro
  `representation` de `read_graph_from_file` (`"list"` ou `"matrix"`),
  sem precisar conhecer as classes concretas — troca de representação
  não muda nenhum código que use o grafo depois de criado, pois ambas
  implementam a mesma interface `Graph`.

## Formato do arquivo de entrada

```
n
u1 v1
u2 v2
...
```

A primeira linha tem o número de vértices `n`; cada linha seguinte
descreve uma aresta `u v`. Exemplo (`grafo_exemplo.txt`, Figura 1 do
enunciado):

```
5
1 2
2 5
5 3
4 5
1 5
```

## Uso como biblioteca

```python
from graph_lib import read_graph_from_file, GraphStatistics

# escolha a representação: "list" (padrão) ou "matrix"
grafo = read_graph_from_file("grafo_1.txt", representation="list")

print(grafo.num_vertices, grafo.num_edges)
print(grafo.degree(1))
print(grafo.neighbors(1))

busca = grafo.bfs(1)          # {'parent': {...}, 'level': {...}}
componentes = grafo.connected_components()   # lista de listas de vértices

stats = GraphStatistics(grafo)
print(stats.as_text())
stats.write_to_file("estatisticas.txt")
```

## Uso pela linha de comando

```bash
python main.py grafo_exemplo.txt --repr list --saida estatisticas.txt
python main.py grafo_exemplo.txt --repr matrix --saida estatisticas.txt
```

O arquivo de saída (`estatisticas.txt`) contém: número de vértices,
número de arestas, grau mínimo, grau máximo, grau médio, mediana de
grau e informações sobre as componentes conexas (quantidade e tamanho
de cada uma, em ordem decrescente).

Saída para `grafo_exemplo.txt`:

```
Número de vértices: 5
Número de arestas: 5
Grau mínimo: 1
Grau máximo: 4
Grau médio: 2.0000
Mediana de grau: 2

Número de componentes conexas: 1
  Componente 1: 5 vértice(s)
```

## Testes realizados

- Grafo do exemplo do enunciado (Figura 1): estatísticas conferem à mão.
- Grafo desconexo (3 componentes de tamanhos 3, 2 e 2): resultado correto.
- Rejeição de laços (`u == v`) com mensagem de erro clara.
- Grafo grande (n = 10 000, 30 000 arestas, como no exemplo do enunciado):
  as duas representações produzem exatamente o mesmo resultado; a lista
  de adjacência é bem mais rápida (~0,15 s) que a matriz (~6 s) para
  calcular as componentes conexas, o que é esperado dado o custo
  `O(V)` de `neighbors(v)` na matriz contra `O(deg(v))` na lista.
