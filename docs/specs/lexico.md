# Analisador Léxico

O **Analisador Léxico** é a **primeira fase** da pipeline do compilador **PyToJava**. Ele lê o código-fonte Python como uma sequência bruta de caracteres e o converte em uma sequência de **tokens** — unidades lexicais mínimas com significado para a linguagem —, cada uma com o seu tipo, o lexema original e a posição (linha e coluna).

Durante a varredura, o léxico **descarta comentários** (tudo a partir de `#` até o fim da linha) e **linhas vazias ou compostas apenas por espaços**, pois não alteram a semântica do programa. Ao mesmo tempo, mantém a emissão dos tokens **sintéticos** `INDENT`, `DEDENT` e `NEWLINE`, de forma análoga ao interpretador Python, permitindo que o Analisador Sintático reconheça os blocos de código sem delimitadores como `{` e `}`.

O resultado dessa fase é o *stream* de tokens consumido pela fase seguinte, que constrói a Árvore de Sintaxe Abstrata (AST).

### O que é um Token? (Entendimento Rápido)

Pense no **Analisador Léxico** como alguém que lê um texto e empacota cada palavra ou símbolo em uma "caixinha" organizada. Essa caixinha é o **Token**, e ela guarda 3 informações principais: o **tipo** (nome do token), o **lexema** (texto original) e a **posição** (linha e coluna).

| Tipo (Nome do Token) | Lexema (Texto) | Posição (Linha, Coluna) |
| :--- | :--- | :--- |
| **KW_IF** | `"if"` | Linha 2, Coluna 4 |
| **IDENTIFIER** | `"total"` | Linha 3, Coluna 5 |
| **INT_LITERAL** | `"42"` | Linha 3, Coluna 11 |

**O que significam estas siglas e termos?**

- **KW_ (Keyword / Palavra Reservada):** É um prefixo usado para identificar palavras que pertencem à própria linguagem Python e não podem ser usadas como nome de variável (ex.: `KW_IF`, `KW_WHILE`, `KW_DEF`).
- **NEWLINE (Fim de Linha Lógica):** Indica ao compilador que uma instrução de código terminou e que a próxima linha executável vai começar.
- **INDENT (Início de Bloco / Entrada de Recuo):** É um token "invisível" gerado quando você dá um Tab ou espaços para entrar em um bloco de código (por exemplo, dentro de um `if` ou `def`).
- **DEDENT (Fim de Bloco / Saída de Recuo):** É o token "invisível" gerado quando você volta a margem do código para a esquerda, indicando que o bloco de código atual terminou.

## Tabela de Tokens

A tokenização segue a regra do **maior casamento** (*maximal munch*): em caso de ambiguidade, vence sempre o padrão mais longo possível. Por isso operadores compostos como `+=`, `-=`, `<=` e `>=` são reconhecidos como um único token (`OP_ADD_ASSIGN`, `OP_SUB_ASSIGN`, `OP_LTE`, `OP_GTE`), e não como a justaposição de dois operadores simples.

| Nome do Token | Padrão Regex / Regra Formal | Exemplo Válido | Exemplo Inválido |
| :--- | :--- | :--- | :--- |
| **KW_CLASS** | `\bclass\b` | `class` | `classic`, `Class` |
| **KW_DEF** | `\bdef\b` | `def` | `define`, `DEF` |
| **KW_SELF** | `\bself\b` | `self` | `selfie`, `Self` |
| **KW_IF** | `\bif\b` | `if` | `iff`, `IF` |
| **KW_ELIF** | `\belif\b` | `elif` | `elseif`, `ELIF` |
| **KW_ELSE** | `\belse\b` | `else` | `els`, `ELSE` |
| **KW_WHILE** | `\bwhile\b` | `while` | `whiles`, `WHILE` |
| **KW_RETURN** | `\breturn\b` | `return` | `returns`, `RETURN` |
| **KW_TRUE** | `\bTrue\b` | `True` | `true`, `TRUE` |
| **KW_FALSE** | `\bFalse\b` | `False` | `false`, `FALSE` |
| **KW_NONE** | `\bNone\b` | `None` | `none`, `null` |
| **IDENTIFIER** | `[a-zA-Z_][a-zA-Z0-9_]*` | `total_1`, `_init`, `valor` | `1total`, `valor-total`, `taxa$` |
| **INT_LITERAL** | `[0-9]+` | `0`, `42`, `1000` | `01a`, `12_000` |
| **FLOAT_LITERAL**| `[0-9]+\.[0-9]+` | `0.5`, `3.1415`, `10.0` | `.5`, `3.`, `3..14` |
| **STRING_LITERAL**| `"([^"\n\\]|\\.)*" \| '([^'\n\\]|\\.)*'` | `"olá"`, `'texto'`, `"com \"escape\""` | `"texto não terminado`, `'misto"` |
| **OP_PLUS** | `\+` | `+` | `++` |
| **OP_MINUS** | `-` | `-` | `--` |
| **OP_MULT** | `\*` | `*` | `**` |
| **OP_DIV** | `/` | `/` | `//` |
| **OP_ASSIGN** | `=` | `=` | `:=` |
| **OP_ADD_ASSIGN**| `\+=` | `+=` | `+ =` |
| **OP_SUB_ASSIGN**| `-=` | `-=` | `- =` |
| **OP_EQ** | `==` | `==` | `===` |
| **OP_NEQ** | `!=` | `!=` | `<>` |
| **OP_LT** | `<` | `<` | |
| **OP_LTE** | `<=` | `<=` | `< =` |
| **OP_GT** | `>` | `>` | |
| **OP_GTE** | `>=` | `>=` | `> =` |
| **COLON** | `:` | `:` | `;` |
| **LPAREN** | `\(` | `(` | `[` |
| **RPAREN** | `\)` | `)` | `]` |
| **NEWLINE** | `\r?\n` | `\n` | Espaço simples |
| **INDENT** | *Sintético (Pilha de recuo)* | Aumento de recuo de bloco | Desalinhamento da pilha |
| **DEDENT** | *Sintético (Pilha de recuo)* | Redução de recuo de bloco | Nível inexistente na pilha |
| **EOF** | *Fim de arquivo (`\0`)* | Fim do fluxo lido | Caractere intermediário |

## Regras Especiais

### Descarte de Comentários

Toda ocorrência do caractere `#` inicia um comentário que se estende até o fim da linha física. O léxico ignora integralmente o trecho comentado, seja ele uma linha inteira:

```python
# este comentário é descartado
```

seja um comentário ao final de uma linha de código:

```python
total = total + 1  # soma uma unidade
```

Após remover o comentário, o restante da linha é tokenizado normalmente. Uma linha que continha apenas um comentário é tratada como linha vazia e não gera token algum.

### Descarte de Linhas Vazias

Linhas vazias ou compostas apenas por espaços em branco (e tabs) são descartadas e **não** geram tokens. Consequentemente, elas não produzem `INDENT`, `DEDENT` ou `NEWLINE`, evitando que a estrutura de blocos seja alterada por espaçamento irrelevante.

### Pilha de Indentação

O léxico mantém uma **pilha de níveis de recuo**, inicializada com o nível `0`. Para cada linha lógica remanescente (após o descarte de comentários e linhas vazias), calcula-se a quantidade de recuo à esquerda e aplica-se o algoritmo:

1. Se o recuo for **igual** ao topo da pilha, nada é emitido e a linha é tokenizada normalmente.
2. Se o recuo for **maior** que o topo da pilha, empilha-se o novo nível e emite-se **um** token `INDENT`.
3. Se o recuo for **menor** que o topo da pilha, desempilha-se enquanto o topo for maior que o recuo, emitindo **um** `DEDENT` para cada nível removido.
4. Se, ao final do passo anterior, o recuo **não coincidir** com o topo da pilha, a indentação é considerada desalinhada e gera-se um erro léxico.
5. Ao atingir o fim do arquivo, emite-se **um** `DEDENT` para cada nível restante na pilha (acima de `0`) e, por fim, o token `EOF`.

Dessa forma, o alinhamento dos blocos é validado contra níveis previamente estabelecidos, impedindo recuos arbitrários que não correspondam a nenhum nível da pilha.

## Padrão de Erro Léxico

Todo erro léxico é reportado com a **posição exata** (linha e coluna, ambas contadas a partir de `1`). As mensagens seguem três categorias formais:

| Categoria | Formato da Mensagem |
| :--- | :--- |
| Caractere Inválido | `Erro Léxico [Linha X, Coluna Y]: caractere inválido '<c>'` |
| String Não Terminada | `Erro Léxico [Linha X, Coluna Y]: literal de string não terminado` |
| Indentação Desalinhada | `Erro Léxico [Linha X, Coluna Y]: recuo desalinhado com a pilha de indentação` |

| Campo | Descrição |
| :--- | :--- |
| `Erro Léxico` | Prefixo fixo que identifica a fase em que o erro ocorreu. |
| `Linha X` | Número da linha (`X`) onde o erro foi detectado. |
| `Coluna Y` | Número da coluna (`Y`), contado a partir do primeiro caractere da linha. |
| Mensagem | Descrição da categoria, com o caractere ofensivo entre aspas simples quando aplicável. |

Ao encontrar o primeiro erro léxico, o analisador **interrompe a compilação**, não produz tokens parciais e não avança para as fases seguintes.

## Exemplos Práticos

### Códigos Válidos

**Exemplo 1 — Comentários descartados:**

```python
# calcula o dobro de um número
def dobro(x):
    return x * 2  # ignora este comentário
```

O primeiro comentário e o comentário ao final da linha são descartados, restando a sequência:

```
KW_DEF, IDENTIFIER, LPAREN, IDENTIFIER, RPAREN, COLON, NEWLINE,
INDENT, KW_RETURN, IDENTIFIER, OP_MULT, INT_LITERAL, NEWLINE, DEDENT, EOF
```

**Exemplo 2 — Operadores compostos (`+=` e `<=`):**

```python
while total <= 100:
    total += 1
```

O `<=` é reconhecido como `OP_LTE` e o `+=` como `OP_ADD_ASSIGN` (maior casamento), e não como pares de operadores simples:

```
KW_WHILE, IDENTIFIER, OP_LTE, INT_LITERAL, COLON, NEWLINE,
INDENT, IDENTIFIER, OP_ADD_ASSIGN, INT_LITERAL, NEWLINE, DEDENT, EOF
```

**Exemplo 3 — Sequência de tokens completa:**

```python
def saudacao(nome):
    mensagem = "olá"
    if nome == None:
        return "anônimo"
    return mensagem
```

```
KW_DEF, IDENTIFIER, LPAREN, IDENTIFIER, RPAREN, COLON, NEWLINE,
INDENT, IDENTIFIER, OP_ASSIGN, STRING_LITERAL, NEWLINE,
KW_IF, IDENTIFIER, OP_EQ, KW_NONE, COLON, NEWLINE,
INDENT, KW_RETURN, STRING_LITERAL, NEWLINE, DEDENT,
KW_RETURN, IDENTIFIER, NEWLINE, DEDENT, EOF
```

### Códigos Inválidos

**Exemplo 1 — Caractere inválido `@`:**

```python
def main():
    a = 10
    b = a @ 2
    return b
```

Mensagem de erro gerada:

```
Erro Léxico [Linha 3, Coluna 11]: caractere inválido '@'
```

O caractere `@` (coluna `11`) não pertence ao alfabeto de operadores definido na tabela de tokens.

**Exemplo 2 — String não terminada:**

```python
def mensagem():
    texto = "olá
    return texto
```

Mensagem de erro gerada:

```
Erro Léxico [Linha 2, Coluna 13]: literal de string não terminado
```

A aspa que abre a string na coluna `13` nunca é fechada antes do fim da linha, configurando a categoria *String Não Terminada*.

**Exemplo 3 — Recuo desalinhado com a pilha:**

```python
def teste():
    if True:
        return 1
      return 0
```

Mensagem de erro gerada:

```
Erro Léxico [Linha 4, Coluna 7]: recuo desalinhado com a pilha de indentação
```

Na linha `4`, o recuo de 6 espaços não coincide com nenhum nível da pilha `[0, 4, 8]`, gerando a categoria *Indentação Desalinhada*.
