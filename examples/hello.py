# Exemplo 1: Manipulacao de strings, booleanos e saudacao condicional
saudacao = "Ola"
destinatario = "Mundo"
mensagem = saudacao + ", " + destinatario + "!"
ativo = True
codigo_status = 0

if ativo == True:
    codigo_status = 200
    mensagem = mensagem + " Bem-vindo ao PyToJava."
else:
    codigo_status = 400
    mensagem = "Sistema inativo."

