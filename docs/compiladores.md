# Conceitos de Compiladores

## O que é um Compilador?

Um compilador é um programa de computador que atua como um tradutor, convertendo código escrito em uma linguagem de programação de alto nível (como Python) para outra linguagem — seja código de máquina, bytecode ou outra linguagem de alto nível estaticamente tipada (transpilação ou compilação *source-to-source*).

Esse processo preserva a semântica original do programa, permitindo que ele seja executado no ambiente alvo. Além da tradução, o compilador verifica rigorosamente regras léxicas, sintáticas e semânticas, garantindo que o código-fonte esteja livre de erros antes da emissão do código final.

No **PyToJava**, aplicamos esses conceitos traduzindo um subconjunto procedural de Python para código-fonte **Java 17+** (`public class Main`), passando pelas fases clássicas de um compilador.

---

## Quais são as etapas de compilação?

1. **Análise Léxica (`src/lexer/`)**: divide o código-fonte bruto em unidades léxicas chamadas **tokens** (`Token`). Identifica palavras reservadas, identificadores, literais, operadores e delimitadores, descarta comentários (`#`) e converte variações de recuo em tokens sintéticos `INDENT`, `DEDENT` e `NEWLINE` através do `IndentManager`.
2. **Análise Sintática (`src/parser/`)**: valida a sequência linear de tokens contra a gramática livre de contexto da linguagem por descida recursiva e *Precedence Climbing*. Constrói a **Árvore Sintática Abstrata (AST)** encabeçada por `ProgramNode`.
3. **Análise Semântica (`src/semantic/`)**: percorre a AST com o padrão **Visitor** (`SemanticAnalyzer`), gerencia escopos léxicos aninhados na **Tabela de Símbolos** (`SymbolTable`), valida que condições de `if`/`elif`/`while` sejam estritamente booleanas e infere estaticamente os tipos (`int`, `float`, `String`, `boolean`, `None`).
4. **Geração de Código (`src/codegen/`)**: traduz a AST validada para código-fonte Java estruturado e indentado (`CodeGenerator`), mapeando tipos semânticos para tipos Java (`int`, `double`, `String`, `boolean`, `Object`) e emitindo declarações tipadas na primeira atribuição de cada variável em seu escopo.
5. **Orquestração e Interfaces (`src/cli.py` e `src/web.py`)**: o driver conecta as quatro fases tanto pela Interface de Linha de Comando (CLI) quanto pela Interface Web Local com acompanhamento em tempo real das etapas via streaming NDJSON.
