# Arquitetura do Gerador de Código

O **Gerador de Código** é a fase final do compilador PyToJava. Ele recebe a
Árvore Sintática Abstrata (AST) produzida pelo *Parser* — já validada pelo
*Analisador Semântico* — e emite código-fonte **Java** estruturado e indentado.

---

## Visão Geral

```
AST (ProgramNode)
        │
        ▼
 CodeGenerator.generate()
        │
        ▼
  Código-fonte Java
```

O método principal `generate()` recebe o nó raiz (`ProgramNode`) e devolve uma
`str` com o programa Java. Nesta etapa, ele gera a estrutura estática padrão de
uma classe Java executável e, dentro do método `main`, a tradução de cada
instrução de `ProgramNode.stmts` (veja [Instruções](#instrucoes-atribuicao-e-retorno)).

---

## Estrutura do Módulo

```
src/codegen/
├── __init__.py          # Exporta CodeGenerator
└── code_generator.py    # Implementação principal
```

---

## Classe `CodeGenerator`

### Atributos

| Atributo       | Tipo          | Descrição                                        |
|----------------|---------------|--------------------------------------------------|
| `indent_level` | `int`         | Nível de indentação atual (inicia em `0`)        |
| `code_lines`   | `list[str]`   | Linhas de código Java emitidas durante a geração |
| `INDENT_SIZE`  | `int` (const) | Espaços por nível de indentação (padrão: `4`)    |
| `declared_vars`| `set[str]`    | Variáveis que já receberam declaração Java       |

### Métodos Auxiliares

| Método              | Descrição                                                     |
|---------------------|---------------------------------------------------------------|
| `emit(code)`        | Adiciona `code` à lista com o prefixo de indentação atual     |
| `indent()`          | Incrementa `indent_level` em 1                                |
| `dedent()`          | Decrementa `indent_level` em 1 (levanta `ValueError` se `0`)  |
| `get_code() -> str` | Une `code_lines` com `\n` e retorna a string final            |

### Método Principal

```python
def generate(self, node: ProgramNode) -> str
```

Recebe o nó raiz da AST e devolve o programa Java como string. A cada chamada,
o estado interno (`indent_level`, `code_lines` e `declared_vars`) é reinicializado, garantindo
que chamadas consecutivas produzam o mesmo resultado.

---

## Boilerplate Java Gerado

Para qualquer `ProgramNode`, o gerador emite a estrutura estática padrão de
uma classe Java executável:

```java
public class Main {
    public static void main(String[] args) {
    }
}
```

A indentação segue a convenção Java de **4 espaços** por nível, e as chaves de
abertura e fechamento são sempre balanceadas.

---

## Instruções: Atribuição e Retorno

O método `visit(node)` despacha cada instrução para `visit_<TipoDoNo>`. Um nó
sem gerador de instrução levanta `ValueError`.

### Regras de declaração de variáveis

Java exige que toda variável seja declarada com tipo antes do uso, enquanto em
Python a primeira atribuição já cria a variável. O gerador resolve isso com o
conjunto `declared_vars`:

1. **Primeira atribuição** (`alvo` fora de `declared_vars`): emite
   `tipo alvo = expr;` e adiciona `alvo` ao conjunto.
2. **Atribuições seguintes**: emite `alvo op expr;`, com `op` sendo `=`, `+=`
   ou `-=`.
3. **Atribuição acumulativa sem declaração** (ex.: `x += 1` como primeira
   ocorrência de `x`): levanta `ValueError`, pois não há valor inicial.

O tipo da declaração vem do `SemanticAnalyzer`: o gerador mantém uma instância
própria que visita cada `AssignNode`, inferindo o tipo do valor, registrando o
símbolo e validando reatribuições incompatíveis (que levantam `SemanticError`).

| Tipo semântico | Tipo Java |
|----------------|-----------|
| `int`          | `int`     |
| `float`        | `double`  |
| `String`       | `String`  |
| `boolean`      | `boolean` |
| `None`         | `Object`  |

### Retorno

`ReturnNode` gera `return expr;` quando há valor e `return;` quando não há.

### Exemplo

```python
x = 10
x += 5
media = x / 2.0
aprovado = media >= 7.0
```

```java
public class Main {
    public static void main(String[] args) {
        int x = 10;
        x += 5;
        double media = (x / 2.0);
        boolean aprovado = (media >= 7.0);
    }
}
```

---

## Exemplo de Uso

```python
from src.codegen import CodeGenerator
from src.parser.nodes import ProgramNode

java_code = CodeGenerator().generate(ProgramNode())
print(java_code)
```

Saída:

```java
public class Main {
    public static void main(String[] args) {
    }
}
```