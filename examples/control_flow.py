# Exemplo 5: Estruturas de controle de fluxo (if/elif/else e while)
limite = 10
atual = 1
soma_pares = 0
soma_impares = 0

while atual <= limite:
    if atual == 2:
        soma_pares += atual
    elif atual == 4:
        soma_pares += atual
    elif atual == 6:
        soma_pares += atual
    elif atual == 8:
        soma_pares += atual
    elif atual == 10:
        soma_pares += atual
    else:
        soma_impares += atual
    atual += 1

