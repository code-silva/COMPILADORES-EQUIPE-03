# Árvore Sintática Abstrata (AST)

A **Árvore Sintática Abstrata** (*Abstract Syntax Tree* — **AST**) é a estrutura de dados central produzida pelo **Analisador Sintático (Parser)** do compilador **PyToJava**. Enquanto a análise léxica converte o código-fonte Python em uma sequência linear de tokens, a AST organiza essas construções em uma hierarquia em árvore que reflete a estrutura gramatical e semântica do programa, abstraindo detalhes puramente sintáticos (como delimitadores, quebras de linha e recuos `INDENT`/`DEDENT`).

Cada nó da árvore é modelado com `@dataclass` no módulo `src/parser/nodes.py` e carrega metadados de rastreabilidade (`line` e `column`) herdados da classe base `Node`, permitindo que as fases seguintes (análise semântica e geração de código Java) reportem diagnósticos precisos no código-fonte original.

---

## Hierarquia da AST

A infraestrutura da AST é composta pela superclasse `Node`, pelo nó raiz `ProgramNode` (que agrupa todas as instruções de nível superior do programa) e pelos nós de expressões, como `BinOpNode`:

```mermaid
classDiagram
    class Node {
        +int line = 0
        +int column = 0
    }
    class ProgramNode {
        +list~Node~ stmts = []
    }
    class BinOpNode {
        +Node | None left = None
        +str op = ""
        +Node | None right = None
    }
    Node <|-- ProgramNode
    Node <|-- BinOpNode
```

Também podemos visualizar como um `ProgramNode` organiza as instruções em tempo de execução na forma de árvore:

```mermaid
flowchart TD
    Root["ProgramNode (line=1, column=1)"] --> S1["Stmt 1: Node (line=1, column=1)"]
    Root --> S2["Stmt 2: Node (line=2, column=1)"]
    Root --> SN["Stmt N: Node (...)"]
```

---

## Especificação dos Nós

### `Node`

Classe base para todos os nós da Árvore Sintática Abstrata.

```python
@dataclass(kw_only=True)
class Node:
    line: int = 0
    column: int = 0
```

| Atributo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `line` | `int` | `0` | Linha no código-fonte onde a construção sintática se inicia (1-based quando preenchida pelo parser, `0` quando não especificada). |
| `column` | `int` | `0` | Coluna no código-fonte onde a construção sintática se inicia (1-based quando preenchida pelo parser, `0` quando não especificada). |

!!! info "Por que `kw_only=True` na classe base?"
    Em Python, `dataclasses` padrão não permitem que subclasses declarem atributos obrigatórios (sem valor padrão) após atributos herdados que já possuem valor padrão (`line: int = 0` e `column: int = 0`).
    Ao declarar `@dataclass(kw_only=True)` em `Node`, `line` e `column` tornam-se parâmetros exclusivamente nomeados (*keyword-only*), permitindo que qualquer subclasse (como `ProgramNode` ou `BinOpNode`) defina livremente atributos posicionais ou com valor padrão sem conflito na ordem de argumentos do `__init__`.

---

### `ProgramNode`

Nó raiz da AST que representa o programa Python completo como uma sequência ordenada de instruções (*statements*).

```python
@dataclass
class ProgramNode(Node):
    stmts: list[Node] = field(default_factory=list)
```

| Atributo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `stmts` | `list[Node]` | `[]` | Lista ordenada de instruções de nível superior que compõem o programa. Inicializada com `field(default_factory=list)` para evitar compartilhamento de estado mutável entre instâncias. |
| `line` | `int` | `0` | Herdado de `Node`. Indica a linha do primeiro elemento do programa. |
| `column` | `int` | `0` | Herdado de `Node`. Indica a coluna do primeiro elemento do programa. |

---

### `BinOpNode` (Expressões Binárias)

Nó responsável por representar operações binárias **aritméticas** (`+`, `-`, `*`, `/`) e **relacionais** (`==`, `!=`, `<`, `<=`, `>`, `>=`) entre dois operandos (`left` e `right`).

```python
@dataclass
class BinOpNode(Node):
    left: Node | None = None
    op: str = ""
    right: Node | None = None
```

| Atributo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `left` | `Node \| None` | `None` | Sub-árvore ou nó folha correspondente ao operando esquerdo. |
| `op` | `str` | `""` | Símbolo textual do operador binário (ex.: `"+"`, `"-"`, `"*"`, `"/"`, `"=="`, `"!="`, `"<"`, `"<="`, `">"`, `">="`). |
| `right` | `Node \| None` | `None` | Sub-árvore ou nó folha correspondente ao operando direito. |
| `line` | `int` | `0` | Herdado de `Node`. Linha no código-fonte onde a operação é avaliada. |
| `column` | `int` | `0` | Herdado de `Node`. Coluna no código-fonte onde a operação é avaliada. |

---

## Representação de Expressões Binárias e Árvore de Precedência

Na AST, a **precedência de operadores** e a **associatividade** são codificadas diretamente pela profundidade dos nós `BinOpNode`:

- Operações de **maior precedência** (como multiplicação `*` e divisão `/`) ficam **mais profundas** na árvore (mais próximas das folhas), sendo avaliadas primeiro.
- Operações de **menor precedência** (como adição `+`, subtração `-` e comparações relacionais `<=`, `==`) ficam **mais próximas da raiz** da expressão, consumindo o resultado das sub-árvores filhas.

### Exemplo Visual 1 — Precedência Aritmética (`2 + 3 * 4`)

Na expressão `2 + 3 * 4`, a multiplicação tem precedência sobre a soma. Portanto, o nó `BinOpNode(op="+")` ocupa a raiz da expressão e seu campo `right` aponta para outro `BinOpNode(op="*")`:

```mermaid
flowchart TD
    Add["BinOpNode (op='+')"] -->|"left"| N2["Operando (2)"]
    Add -->|"right"| Mul["BinOpNode (op='*')"]
    Mul -->|"left"| N3["Operando (3)"]
    Mul -->|"right"| N4["Operando (4)"]
```

### Exemplo Visual 2 — Expressão Aritmética e Relacional Combinada (`2 + 3 * 4 <= 15`)

Quando combinamos operadores aritméticos com um operador relacional (`<=`), o operador relacional possui a menor precedência e torna-se o nó superior da expressão:

```mermaid
flowchart TD
    Rel["BinOpNode (op='<=')"] -->|"left"| Add["BinOpNode (op='+')"]
    Rel -->|"right"| N15["Operando (15)"]
    Add -->|"left"| N2["Operando (2)"]
    Add -->|"right"| Mul["BinOpNode (op='*')"]
    Mul -->|"left"| N3["Operando (3)"]
    Mul -->|"right"| N4["Operando (4)"]
```

---

## Exemplos de Uso

```python
from src.parser import BinOpNode, Node, ProgramNode

# 1. Instanciação padrão (programa vazio)
empty_program = ProgramNode()
assert empty_program.stmts == []
assert (empty_program.line, empty_program.column) == (0, 0)

# 2. Construção de sub-árvore aninhada para "2 + 3 * 4"
mult_expr = BinOpNode(
    left=Node(line=1, column=5),
    op="*",
    right=Node(line=1, column=9),
    line=1,
    column=7,
)
add_expr = BinOpNode(
    left=Node(line=1, column=1),
    op="+",
    right=mult_expr,
    line=1,
    column=3,
)

assert add_expr.op == "+"
assert add_expr.right.op == "*"
```

---

## 🪢Nós de Controle de Fluxo

Esta seção documenta os nós que representam as estruturas condicionais e de repetição do subconjunto Python suportado pelo PyToJava.

---🔨

### `IfNode`

Representa uma estrutura condicional completa, podendo conter cláusulas `elif` e `else`.

| Atributo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `condition` | `Node \| None` | `None` | Expressão avaliada como condição do `if`. |
| `then_body` | `list[Node]` | `[]` | Lista de instruções executadas quando a condição é verdadeira. |
| `elif_clauses` | `list[ElifClauseNode]` | `[]` | Lista de cláusulas `elif` associadas ao bloco. |
| `else_body` | `list[Node]` | `[]` | Lista de instruções executadas quando nenhuma condição anterior é verdadeira. |
| `line` | `int` | `0` | Herdado de `Node`. |
| `column` | `int` | `0` | Herdado de `Node`. |

---

### `ElifClauseNode`

Representa uma cláusula `elif` dentro de uma estrutura condicional.

| Atributo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `condition` | `Node \| None` | `None` | Expressão avaliada como condição do `elif`. |
| `body` | `list[Node]` | `[]` | Lista de instruções executadas quando a condição é verdadeira. |
| `line` | `int` | `0` | Herdado de `Node`. |
| `column` | `int` | `0` | Herdado de `Node`. |

---

### `ElseClauseNode`

Representa a cláusula `else` dentro de uma estrutura condicional.

| Atributo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `body` | `list[Node]` | `[]` | Lista de instruções executadas quando nenhuma condição anterior é verdadeira. |
| `line` | `int` | `0` | Herdado de `Node`. |
| `column` | `int` | `0` | Herdado de `Node`. |

---

### `WhileNode`

Representa um laço de repetição `while`.

| Atributo | Tipo | Padrão | Descrição |
| :--- | :--- | :--- | :--- |
| `condition` | `Node \| None` | `None` | Expressão avaliada a cada iteração do laço. |
| `body` | `list[Node]` | `[]` | Lista de instruções executadas enquanto a condição for verdadeira. |
| `line` | `int` | `0` | Herdado de `Node`. |
| `column` | `int` | `0` | Herdado de `Node`. |

### 👀Exemplo Visual

Dado o seguinte trecho de código Python:

```python
if x > 0:
    resultado = 1
elif x == 0:
    resultado = 0
else:
    resultado = -1
```

A AST correspondente gerada pelos nós seria:

```mermaid
flowchart TD
    If["IfNode (line=1)"] --> Cond["condition: BinOpNode '>'"]
    If --> Then["then_body"]
    If --> Elif["elif_clauses"]
    If --> Else["else_body"]

    Then --> T1["AssignNode 'resultado = 1' (line=2)"]

    Elif --> E1["ElifClauseNode (line=3)"]
    E1 --> EC["condition: BinOpNode '=='"]
    E1 --> EB["body"]
    EB --> EB1["AssignNode 'resultado = 0' (line=4)"]

    Else --> EL1["AssignNode 'resultado = -1' (line=6)"]
```

E para um laço `while`:

```python
while contador <= 10:
    contador += 1
```

```mermaid
flowchart TD
    While["WhileNode (line=1)"] --> WCond["condition: BinOpNode '<='"]
    While --> WBody["body"]
    WBody --> WB1["AssignNode 'contador += 1' (line=2)"]
```

---
## 🚀Validação e Testes

Para executar a suíte de testes unitários da AST:

```bash
pytest tests/test_ast_nodes.py -v
```
