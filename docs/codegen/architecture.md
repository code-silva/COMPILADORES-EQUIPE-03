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
uma classe Java executável; a tradução das instruções da AST é adicionada nas
etapas seguintes.

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
o estado interno (`indent_level` e `code_lines`) é reinicializado, garantindo
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