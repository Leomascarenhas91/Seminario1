#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OBST SIMPLES – Exemplo didático
-----------------------------------------------------------------
    keys = ["Ana", "Bruno", "Carla", "Diego"]
    p    = [0.35, 0.25, 0.25, 0.15]
    q    = [0.02, 0.02, 0.02, 0.02, 0.02]

O script:
  1) Mostra as chaves e probabilidades de entrada.
  2) Normaliza p+q para 1.0 se necessário e valida o formato.
  3) Executa a OBST por programação dinâmica.
  4) Exibe o custo mínimo esperado e as raízes escolhidas por intervalo.
  5) Exibe a **ordem escolhida** (pré-ordem, em-ordem, pós-ordem) derivando da tabela root.
"""

from typing import List, Any
import sys

# ---------------------------
# Validação de p e q
# ---------------------------
def validate_probabilities(p: List[float], q: List[float]) -> None:
    if len(q) != len(p) + 1:
        raise ValueError("q deve ter tamanho len(p)+1 (há n+1 gaps para n chaves).")
    if any(x < 0 for x in p + q):
        raise ValueError("Probabilidades negativas não são permitidas.")
    s = sum(p) + sum(q)
    if abs(s - 1.0) > 1e-6:
        raise ValueError(f"As probabilidades devem somar 1.0 (atual: {s:.6f}).")

# ---------------------------
# Núcleo: OBST (DP clássica)
# ---------------------------

#Implementa a OBST por programação dinâmica e devolve três tabelas:
def optimal_bst(p: List[float], q: List[float], keys: List[Any]):
    n = len(p)
    if len(keys) != n:
        raise ValueError("keys e p devem ter o mesmo tamanho.")
    #menor custo esperado para as chaves do intervalo i..j;
    e = [[0.0]*(n+2) for _ in range(n+2)]
    #peso (soma das probabilidades p e q) no intervalo i..j;
    w = [[0.0]*(n+2) for _ in range(n+2)]
    #índice da raiz ótima escolhida para i..j.
    root = [[0]*(n+2) for _ in range(n+2)]

    #Inicializa os casos-base (intervalo vazio i..i-1):
    #custo = q[i-1], peso = q[i-1].
    #Isto modela a chance de “não encontrar” entre as chaves.
    for i in range(1, n+2):
        e[i][i-1] = q[i-1]
        w[i][i-1] = q[i-1]
    for L in range(1, n+1):
        for i in range(1, n-L+2):
            j = i + L - 1
            #Inicializa o custo do intervalo com infinito
            e[i][j] = float("inf")
            #Atualiza o peso do intervalo i..j a partir do peso i..j-1:
            #adiciona p[j-1] (prob. da chave j) e q[j] (gap após j).

            w[i][j] = w[i][j-1] + p[j-1] + q[j]
            melhor_r, melhor_custo = None, float("inf")
            #Testa cada chave r em i..j como candidata a raiz do intervalo.
            for r in range(i, j+1):

                #Calcula o custo se r for raiz:
                #custo da subárvore esquerda e[i][r-1] +
                # custo da subárvore direita e[r+1][j] +
                #w[i][j] (todo mundo do intervalo fica um nível mais fundo quando escolhemos uma raiz).

                custo = e[i][r-1] + e[r+1][j] + w[i][j]
                if custo < melhor_custo:
                    melhor_custo, melhor_r = custo, r
            e[i][j] = melhor_custo
            root[i][j] = melhor_r
    return e, w, root

# ---------------------------
# Ordens (percursos) a partir da tabela root
#Essas três funções percorrem recursivamente os intervalos indicados pela tabela root para gerar, sem construir a árvore, as listas de chaves em pré-ordem, em-ordem e 
# pós-ordem.
# ---------------------------
def preorder_from_root(root, keys, i, j):
    if j < i:
        return []
    r = root[i][j]
    return [keys[r-1]] + preorder_from_root(root, keys, i, r-1) + preorder_from_root(root, keys, r+1, j)

def inorder_from_root(root, keys, i, j):
    if j < i:
        return []
    r = root[i][j]
    return inorder_from_root(root, keys, i, r-1) + [keys[r-1]] + inorder_from_root(root, keys, r+1, j)

def postorder_from_root(root, keys, i, j):
    if j < i:
        return []
    r = root[i][j]
    return postorder_from_root(root, keys, i, r-1) + postorder_from_root(root, keys, r+1, j) + [keys[r-1]]

# ---------------------------
# Programa principal
# ---------------------------
def main():
    # Exemplo visível de entrada:
    keys = ["Ana", "Bruno", "Carla", "Diego"]
    p    = [0.35, 0.25, 0.25, 0.15]
    q    = [0.02, 0.02, 0.02, 0.02, 0.02]

    print(">>> EXEMPLO UTILIZADO:")
    print(f"    keys = {keys}")
    print(f"    p    = {p}")
    print(f"    q    = {q}\n")

    # Normaliza p+q para 1.0 (mantém proporções) — evita erro de soma
    total = sum(p) + sum(q)
    if abs(total - 1.0) > 1e-9:
        esc = 1.0 / total
        p = [round(x*esc, 10) for x in p]
        q = [round(x*esc, 10) for x in q]

    # Validação final
    validate_probabilities(p, q)

    print(">>> Executando OBST (programação dinâmica)...")
    e, w, root = optimal_bst(p, q, keys)
    n = len(keys)

    # Custo
    cost_dp = e[1][n]
    print(f">>> Custo mínimo esperado (DP): {cost_dp:.6f}\n")

    # Raízes por intervalo (decisões do algoritmo)
    print(">>> Raízes escolhidas por intervalo:")
    for L in range(1, n+1):
        for i in range(1, n-L+2):
            j = i + L - 1
            r = root[i][j]
            print(f"    Intervalo [{i},{j}] → chaves {keys[i-1:j]} | raiz = '{keys[r-1]}'")

    # Ordem escolhida (percursos)
    pre  = preorder_from_root(root, keys, 1, n)
    ino  = inorder_from_root(root, keys, 1, n)
    post = postorder_from_root(root, keys, 1, n)

    print("\n>>> Ordem escolhida (percursos da OBST):")
    print("    Pré-ordem (raiz → esquerda → direita):", pre)
    print("    Em-ordem  (esquerda → raiz → direita):", ino, "  (deve sair ordenada)")
    print("    Pós-ordem (esquerda → direita → raiz):", post)

    print("\n>>> FIM – A OBST minimiza o número médio de comparações considerando as probabilidades.")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("Erro ao executar:", exc, file=sys.stderr)
        sys.exit(1)
