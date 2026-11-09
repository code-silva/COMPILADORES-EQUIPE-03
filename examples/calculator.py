# Exemplo 3: Calculadora procedural com precedencia de operadores e controle de fluxo
operando_a = 20.0
operando_b = 4.0
operacao = 4
resultado = 0.0
erro_divisao = False

if operacao == 1:
    resultado = operando_a + operando_b
elif operacao == 2:
    resultado = operando_a - operando_b
elif operacao == 3:
    resultado = operando_a * operando_b
elif operacao == 4:
    if operando_b == 0.0:
        erro_divisao = True
        resultado = 0.0
    else:
        resultado = operando_a / operando_b
else:
    resultado = 0.0

expressao_complexa = (operando_a + operando_b) * 2.0 - 10.0 / 2.0
resultado += expressao_complexa

