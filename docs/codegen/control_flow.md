# Geração de Código para Estruturas de Controle de Fluxo

O módulo `src/codegen/code_generator.py` traduz as estruturas de controle procedurais da AST (`IfNode`, `ElifClauseNode`, `ElseClauseNode` e `WhileNode`) para blocos equivalentes em **Java**, substituindo a delimitação por recuo (`INDENT`/`DEDENT`) do Python por blocos explícitos delimitados por chaves `{}` e indentados em múltiplos de 4 espaços.

---

## Regras de Tradução (Python -> AST -> Java)

| Estrutura em Python | Nó da AST | Estrutura Emitida em Java |
| :--- | :--- | :--- |
| `if cond:` | `IfNode` | `if (<cond>) { ... }` |
| `elif cond:` | `ElifClauseNode` | `} else if (<cond>) { ... }` |
| `else:` | `ElseClauseNode` / `IfNode.else_body` | `} else { ... }` |
| `while cond:` | `WhileNode` | `while (<cond>) { ... }` |

### Escopo de Variáveis e Alinhamento de Chaves

1. **Validação Booleana:** Antes de emitir a condição de `if`, `elif` ou `while`, o `CodeGenerator` valida no `SemanticAnalyzer` que a expressão condicional possui tipo `boolean`.
2. **Pilha de Escopos de Bloco:** Ao entrar em cada corpo (`then_body`, `elif`, `else` ou `while`), o gerador empilha um novo escopo léxico tanto no `SemanticAnalyzer` quanto na pilha de variáveis declaradas (`_scope_stack`). Variáveis já declaradas no escopo externo são reutilizadas sem redeclaração, enquanto variáveis criadas localmente dentro de um bloco recebem sua própria declaração tipada em Java (sem conflitar com blocos irmãos).
3. **Formatação de Chaves (`{}`):** A abertura `{` permanece na mesma linha do comando (`if (...) {`, `} else if (...) {`, `} else {`, `while (...) {`), o corpo interno é recuado em `+4` espaços (`indent()`), e o fechamento `}` retorna ao nível da estrutura (`dedent()`).

---

## Exemplos Comparativos (Python vs. Java Gerado)

### 1. Condicional Completa (`if / elif / else`)

=== "Python (Entrada)"

    ```python
    nota = 8
    conceito = ""
    if nota >= 9:
        conceito = "A"
    elif nota >= 7:
        conceito = "B"
    elif nota >= 5:
        conceito = "C"
    else:
        conceito = "D"
    ```

=== "Java (Saída do CodeGenerator)"

    ```java
    public class Main {
        public static void main(String[] args) {
            int nota = 8;
            String conceito = "";
            if ((nota >= 9)) {
                conceito = "A";
            } else if ((nota >= 7)) {
                conceito = "B";
            } else if ((nota >= 5)) {
                conceito = "C";
            } else {
                conceito = "D";
            }
        }
    }
    ```

---

### 2. Laço de Repetição (`while`)

=== "Python (Entrada)"

    ```python
    n = 5
    fatorial = 1
    while n > 1:
        fatorial = fatorial * n
        n -= 1
    ```

=== "Java (Saída do CodeGenerator)"

    ```java
    public class Main {
        public static void main(String[] args) {
            int n = 5;
            int fatorial = 1;
            while ((n > 1)) {
                fatorial = (fatorial * n);
                n -= 1;
            }
        }
    }
    ```

---

### 3. Estruturas Aninhadas (`while` + `if / else`)

=== "Python (Entrada)"

    ```python
    i = 0
    menores = 0
    while i < 10:
        if i < 5:
            menores += 1
        else:
            if i == 7:
                return
        i += 1
    ```

=== "Java (Saída do CodeGenerator)"

    ```java
    public class Main {
        public static void main(String[] args) {
            int i = 0;
            int menores = 0;
            while ((i < 10)) {
                if ((i < 5)) {
                    menores += 1;
                } else {
                    if ((i == 7)) {
                        return;
                    }
                }
                i += 1;
            }
        }
    }
    ```

---

## Validação e Testes

```bash
pytest tests/test_codegen_control_flow.py -v
mkdocs build --strict
```
