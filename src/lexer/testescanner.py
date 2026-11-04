from src.lexer.scanner import Scanner
from src.lexer.token_type import TokenType


class Main:

    def __init__(self, source_code: str):
        self.scanner = Scanner(source_code)

    def read_token(self):
        print(
            f"{'TIPO':<20} | {'LEXEMA':<15} | {'LITERAL':<15} | {'LINHA':<5} | {'COLUNA':<5}"
        )
        print("-" * 70)

        token = self.scanner.next_token()
        while token.type != TokenType.EOF:
            lexeme_display = repr(token.lexeme)
            # Trocado token.value por token.literal
            literal_display = repr(token.literal) if token.literal is not None else "-"
            
            print(
                f"{token.type.name:<20} | {lexeme_display:<15} | {literal_display:<15} | {token.line:<5} | {token.column:<5}"
            )

            if token.type == TokenType.ERROR:
                print(f"  └─> [ERRO LEXICAL]: {token.literal}")

            token = self.scanner.next_token()

        print(
            f"{token.type.name:<20} | {repr(token.lexeme):<15} | {'-':<15} | {token.line:<5} | {token.column:<5}"
        )

if __name__ == "__main__":
    # Código de teste incluindo blocos indentados, strings, comentários e operadores
    code = (
        'def main():\n'
        '    x = (10 + 10) / 5 * (2 - 3.8)\n'
        '    # Este é um comentário que deve ser ignorado\n'
        '    if x < 1:\n'
        '        mensagem = "Olá, \\"mundo\\"! \\n Teste de string"\n'
        '    else:\n'
        '        string_erro = "esqueci de fechar\n'
        '        caractere_invalido = @\n'
    )

    scanner = Scanner(code)

    print("--- INÍCIO DA TOKENIZAÇÃO ---")
    while True:
        token = scanner.next_token()
        print(token)
        if token.type == TokenType.EOF:
            break
    print("--- FIM DA TOKENIZAÇÃO ---")
