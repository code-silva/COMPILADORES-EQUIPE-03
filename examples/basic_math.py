# examples/basic_math.py
# Arquivo de exemplo para testar o lexer/parser do PyToJava

def soma(a, b):
    return a + b

def eh_par(n):
    if n % 2 == 0:
        return True
    else:
        return False

x = 10
y = 20
resultado = soma(x, y)

for i in range(5):
    if eh_par(i):
        print(i)
    else:
        print(0)
