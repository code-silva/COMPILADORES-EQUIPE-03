# Árvore Sintática Abstrata (AST)

A **Árvore Sintática Abstrata (AST)** é a representação estruturada em árvore do código-fonte gerada pelo Analisador Sintático (Parser). Ela remove detalhes sintáticos superficiais (como parênteses e pontuações irrelevantes para a semântica) e organiza as instruções e expressões em nós hierárquicos.

Todos os nós da AST herdam da classe base `Node`, que armazena metadados de localização (`line` e `column`) para permitir relatórios precisos de erros nas fases seguintes do compilador.

---

## Estrutura Base

### `Node`
A classe base imutável (`frozen=True`) para todos os nós da árvore.

- **Atributos:**
  - `line` (`int`): Linha no código-fonte onde o elemento se inicia (padrão: `0`).
  - `column` (`int`): Coluna no código-fonte onde o elemento se inicia (padrão: `0`).

### `ProgramNode`
O nó raiz que representa um programa completo.

- **Atributos:**
  - `stmts` (`list[Node]`): Lista contendo todas as instruções de nível superior executadas no programa.

---

## Instruções Imperativas

As instruções imperativas representam comandos de mutação de estado e controle de fluxo linear. Na versão atual do PyToJava, destacam-se o comando de atribuição e o comando de retorno.

### `AssignNode`
Representa comandos de atribuição de valores a variáveis, suportando tanto atribuições simples quanto operações aritméticas acumulativas.

- **Atributos:**
  - `target` (`str`): O identificador (nome da variável) que recebe o valor atribuído (ex.: `"x"`).
  - `op` (`str`): O operador de atribuição utilizado. Pode ser `" = "` (atribuição simples), `" += "` (soma e atribuição) ou `" -= "` (subtração e atribuição).
  - `value` (`Node | None`): O sub-nó da AST que representa a expressão avaliada cujo resultado será armazenado em `target`.

#### Exemplos Práticos

1. **Atribuição Simples:**
   * **Código Python:**
     ```python
     x = 10
     ```
   * **Estrutura na AST:**
     ```text
     AssignNode(target="x", op="=", value=IntLiteralNode(value=10))
     ```

2. **Atribuição Acumulativa (Adição):**
   * **Código Python:**
     ```python
     x += 1
     ```
   * **Estrutura na AST:**
     ```text
     AssignNode(target="x", op="+=", value=IntLiteralNode(value=1))
     ```

3. **Atribuição Acumulativa (Subtração):**
   * **Código Python:**
     ```python
     x -= 5
     ```
   * **Estrutura na AST:**
     ```text
     AssignNode(target="x", op="-=", value=IntLiteralNode(value=5))
     ```

---

### `ReturnNode`
Representa a instrução de retorno de uma função ou escopo executável.

- **Atributos:**
  - `value` (`Node | None`): O sub-nó da AST que representa a expressão cujo valor retornado é devolvido pelo escopo. Quando a instrução é um retorno vazio (`return` sem expressão), o atributo assume o valor `None`.

#### Exemplos Práticos

1. **Retorno com Expressão:**
   * **Código Python:**
     ```python
     return x
     ```
   * **Estrutura na AST:**
     ```text
     ReturnNode(value=IdentifierNode(name="x"))
     ```

2. **Retorno Vazio (Void):**
   * **Código Python:**
     ```python
     return
     ```
   * **Estrutura na AST:**
     ```text
     ReturnNode(value=None)
     ```
