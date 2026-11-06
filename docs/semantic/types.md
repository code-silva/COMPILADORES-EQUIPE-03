# Tipos e Compatibilidade Semântica

O analisador semântico do **PyToJava** infere e valida tipos para expressões e
atribuições. Esta página documenta os tipos primitivos reconhecidos, a matriz de
compatibilidade de operações binárias (`BinOpNode`) e as regras de registro e
coerção em atribuições (`AssignNode`).

A implementação fica em `src/semantic/analyzer.py`, com apoio da
[`SymbolTable`](symbol_table.md) para resolução de identificadores.

---

## Tipos primitivos

| Tipo | Origem principal | Observação |
| :--- | :--- | :--- |
| `int` | `IntLiteralNode`, operações aritméticas inteiras | Inteiros. |
| `float` | `FloatLiteralNode`, promoção numérica e divisão | Ponto flutuante. |
| `String` | `StringLiteralNode` e concatenação | Texto; o nome do tipo é `String`, com `S` maiúsculo. |
| `boolean` | `BoolLiteralNode` e comparações | Resultado de comparações; o nome é `boolean`, não `bool`. |
| `None` | `NoneLiteralNode` e `return` sem valor | Tipo especial, sem operações aritméticas ou relacionais. |

A inferência é centralizada em `SemanticAnalyzer.infer_type()`, que delega ao
visitor do nó. Literais retornam diretamente seu tipo; identificadores são
resolvidos na tabela de símbolos ativa.

```python
x = 10          # int
y = 2.5         # float
nome = "Ana"    # String
ativo = True    # boolean
vazio = None    # None
```

Um identificador não declarado gera erro com a posição do próprio nó:

```text
Erro Semântico [Linha 2, Coluna 5]: Variável 'origem' não declarada
```

---

## Operações binárias (`BinOpNode`)

`visit_BinOpNode()` infere o tipo dos operandos com `infer_type()` e aplica a
matriz de compatibilidade abaixo. O resultado é sempre um nome de tipo textual
ou um `SemanticError` com a linha e a coluna do operador.

### Operadores aritméticos

Operadores: `+`, `-`, `*`, `/`, `%`.

| Operando esquerdo | Operando direito | Resultado |
| :--- | :--- | :--- |
| `int` | `int` | `int` |
| `int` | `int` com `/` | `float` |
| `float` | `float` | `float` |
| `int` | `float` | `float` |
| `float` | `int` | `float` |
| `String` | `String` com `+` | `String` |

Regras complementares:

- A divisão `/` sempre produz `float` quando os operandos são numéricos.
- `%` segue a promoção numérica: `int % int` produz `int`; qualquer operando
  `float` produz `float`.
- A concatenação é permitida apenas para `String + String`.
- `String - String`, `String * String` e demais combinações com `String` são
  incompatíveis.

### Operadores de comparação

Operadores: `==`, `!=`, `<`, `>`, `<=`, `>=`.

| Operando esquerdo | Operando direito | Resultado |
| :--- | :--- | :--- |
| `int` | `int` | `boolean` |
| `float` | `float` | `boolean` |
| `int` | `float` | `boolean` |
| `float` | `int` | `boolean` |
| `boolean` | `boolean` | `boolean` |

Comparações entre `String`, entre tipos não relacionados ou entre `boolean` e
tipos numéricos são incompatíveis nesta etapa.

### Erros de operação binária

Operações incompatíveis informam os dois tipos e o operador:

```text
Erro Semântico [Linha 1, Coluna 12]: Operação binária incompatível: int + String
```

Outros diagnósticos:

| Situação | Mensagem |
| :--- | :--- |
| Operador desconhecido | `Operador binário não suportado: '<op>'` |
| Operando ausente | `Expressão binária com operando ausente` |

> O analisador semântico reconhece `%` em `BinOpNode`, mas o lexer/parser atual
> ainda não tokeniza esse operador. O suporte léxico/sintático pode ser
> habilitado em uma etapa futura.

---

## Atribuições (`AssignNode`)

`visit_AssignNode()` executa a seguinte sequência:

1. Valida que existe uma expressão de valor; caso contrário, lança
   `Atribuição sem expressão de valor`.
2. Infere o tipo do lado direito com `infer_type(node.value)`.
3. Procura o identificador de destino com `current_scope.lookup(node.target)`,
   considerando o escopo atual e seus escopos pais.
4. Se o identificador não existir, registra um novo `Symbol` no escopo atual,
   com o tipo inferido e a posição do nó.
5. Se já existir, valida a compatibilidade com `_is_assignable`.

### Regras de `_is_assignable`

| Tipo do alvo | Tipo do valor | Permitido |
| :--- | :--- | :--- |
| `int` | `int` | Sim |
| `float` | `float` | Sim |
| `float` | `int` | Sim, por coerção/promoção |
| `int` | `float` | Não |
| `String` | `String` | Sim |
| `boolean` | `boolean` | Sim |
| `None` | `None` | Sim |
| `int` | `String` | Não |
| `boolean` | `int` | Não |
| `None` | `boolean` | Não |

Resumo:

- Mesmo tipo é sempre aceito.
- A única coerção implícita permitida é `int` para `float`.
- `float` para `int`, tipos textuais, booleanos e `None` exigem equivalência
  exata.
- Atribuições a símbolos visíveis em escopos pais são validadas contra o tipo
  do símbolo encontrado; não há criação de um símbolo local por sombreamento.

### Erro de atribuição incompatível

```text
Erro Semântico [Linha 2, Coluna 1]: Tipo incompatível na atribuição: variável 'idade' é 'int', mas recebeu 'String'
```

A posição reportada é sempre a do nó `AssignNode`, preservando a linha e a
coluna do alvo da atribuição.

---

## Exemplos

### Código válido

```python
idade = 18              # registra idade: int
altura = 1.75           # registra altura: float
media = idade + altura  # int + float -> float
nome = "Ana"            # registra nome: String
saudacao = nome + "!"   # String + String -> String
maior_de_idade = idade >= 18  # comparação numérica -> boolean

ticket = 10
ticket = ticket + 2     # int + int -> int
saldo = 100.0
saldo = 99.5            # float atribuído a float: permitido
```

Tipos registrados ao final:

| Variável | Tipo |
| :--- | :--- |
| `idade` | `int` |
| `altura` | `float` |
| `media` | `float` |
| `nome` | `String` |
| `saudacao` | `String` |
| `maior_de_idade` | `boolean` |
| `ticket` | `int` |
| `saldo` | `float` |

### Coerção permitida

```python
preco = 10.0
preco = 5       # int atribuído a float: permitido, preco continua float
```

### Operação binária incompatível

```python
total = 10 + "texto"
```

```text
Erro Semântico [Linha 1, Coluna 12]: Operação binária incompatível: int + String
```

### Comparação incompatível

```python
resultado = 10 > "5"
```

```text
Operação binária incompatível: int > String
```

### Atribuição incompatível

```python
idade = 18
idade = "dezoito"
```

```text
Erro Semântico [Linha 2, Coluna 1]: Tipo incompatível na atribuição: variável 'idade' é 'int', mas recebeu 'String'
```

### Identificador não declarado

```python
destino = origem + 1
```

```text
Erro Semântico [Linha 1, Coluna 11]: Variável 'origem' não declarada
```

---

## Validação

```bash
python -m pytest tests/ -v
mkdocs build --strict
```
