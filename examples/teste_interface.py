# Arquivo de teste para enviar na interface local do PyToJava.
# Exercita variaveis, operacoes, repeticao e condicoes.

aluno = "Professor"
nota_1 = 8.0
nota_2 = 6.0
media = (nota_1 + nota_2) / 2.0
aprovado = False
situacao = "Pendente"

if media >= 7.0:
    aprovado = True
    situacao = "Aprovado"
elif media >= 5.0:
    situacao = "Recuperacao"
else:
    situacao = "Reprovado"

contador = 1
soma = 0
while contador <= 5:
    soma += contador
    contador += 1
