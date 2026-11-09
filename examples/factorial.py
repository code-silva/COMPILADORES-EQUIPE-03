# Exemplo 2: Calculo de fatorial iterativo com validacao condicional
numero = 6
fatorial = 1
valido = True

if numero < 0:
    valido = False
    fatorial = 0
elif numero == 0:
    fatorial = 1
else:
    contador = numero
    while contador > 1:
        fatorial = fatorial * contador
        contador -= 1

