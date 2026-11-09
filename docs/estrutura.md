# Estrutura do Projeto

Aqui você encontrará a estrutura do nosso projeto detalhadamente, organizada de forma clara para facilitar a navegação e o entendimento de como o **PyToJava** foi construído. Nesta seção, apresentamos a arquitetura do compilador, a organização dos diretórios e o fluxo de execução. Se você quer entender como as peças se conectam, desde a leitura do código Python até a geração do Java final, este é o lugar certo para começar.

---

## Diretórios

```text
pytojava/
├── docs/                                # Documentação formal e especificações (MkDocs)
│   ├── arch/
│   │   └── scanner.md                   # Arquitetura do Scanner léxico
│   ├── codegen/
│   │   ├── architecture.md              # Arquitetura do Gerador de Código
│   │   ├── control_flow.md              # Tradução de if/elif/else e while
│   │   └── expressions.md               # Tradução de literais e expressões
│   ├── parser/
│   │   ├── ast.md                       # Nós da Árvore Sintática Abstrata (AST)
│   │   ├── errors.md                    # Erros sintáticos e casos de borda
│   │   ├── grammar.md                   # Gramática formal e precedência
│   │   └── index.md                     # Visão geral e API do Parser
│   ├── semantic/
│   │   ├── analyzer.md                  # Analisador Semântico e padrão Visitor
│   │   ├── symbol_table.md              # Tabela de Símbolos e escopos
│   │   └── types.md                     # Regras de tipos e compatibilidade
│   ├── specs/
│   │   └── lexico.md                    # Especificação léxica e tabela de tokens
│   ├── compiladores.md                  # Conceitos gerais de compiladores
│   ├── estrutura.md                     # Estrutura de diretórios do projeto
│   ├── GLOSSARY.md                      # Glossário de termos técnicos
│   ├── index.md                         # Página inicial da documentação
│   └── usage.md                         # Guia de uso da CLI (Driver)
├── examples/                            # Scripts Python procedurais de exemplo (.py)
│   ├── basic_math.py                    # Operações aritméticas e atribuições
│   ├── calculator.py                    # Calculadora procedural com controle de fluxo
│   ├── control_flow.py                  # Laços while e condicionais aninhadas
│   ├── factorial.py                     # Cálculo iterativo de fatorial
│   └── hello.py                         # Manipulação de strings e booleanos
├── output/                              # Diretório padrão para arquivos .java gerados
├── src/                                 # Código-fonte do compilador PyToJava
│   ├── __init__.py
│   ├── cli.py                           # Driver e CLI do pipeline completo
│   ├── main.py                          # Ponto de entrada principal (delega para cli.py)
│   ├── lexer/                           # Fase 1: Analisador Léxico
│   │   ├── __init__.py
│   │   ├── char_stream.py
│   │   ├── errors.py
│   │   ├── indent_manager.py
│   │   ├── scanner.py
│   │   ├── symbol_table.py
│   │   ├── token.py
│   │   └── token_type.py
│   ├── parser/                          # Fase 2: Analisador Sintático e AST
│   │   ├── __init__.py
│   │   ├── errors.py
│   │   ├── nodes.py
│   │   └── parser.py
│   ├── semantic/                        # Fase 3: Analisador Semântico
│   │   ├── __init__.py
│   │   ├── analyzer.py
│   │   ├── errors.py
│   │   └── symbol_table.py
│   └── codegen/                         # Fase 4: Gerador de Código Java
│       ├── __init__.py
│       └── code_generator.py
├── tests/                               # Suíte de testes unitários e E2E (pytest)
│   ├── __init__.py
│   ├── parser_helpers.py
│   ├── test_ast_nodes.py
│   ├── test_codegen.py
│   ├── test_codegen_control_flow.py
│   ├── test_codegen_expressions.py
│   ├── test_codegen_statements.py
│   ├── test_compiler_pipeline.py
│   ├── test_e2e_javac.py
│   ├── test_indent_manager.py
│   ├── test_lexer_edge_cases.py
│   ├── test_lexer_happy_path.py
│   ├── test_parser_control_flow.py
│   ├── test_parser_edge_cases.py
│   ├── test_parser_expressions.py
│   ├── test_parser_integration.py
│   ├── test_parser_statements.py
│   ├── test_scanner.py
│   ├── test_semantic_analyzer_base.py
│   ├── test_semantic_assignment.py
│   ├── test_semantic_binop_inference.py
│   ├── test_semantic_control_flow.py
│   ├── test_symbol_table.py
│   └── test_symbol_table_and_errors.py
├── .gitignore
├── CONTRIBUTING.md
├── docker-compose.yml
├── Dockerfile
├── LICENSE
├── mkdocs.yml
├── pyproject.toml
├── README.md
└── requirements.txt
```

---

## Pastas Principais

* **docs**: Documentação formal, relatórios e especificações técnicas (MkDocs)
* **examples**: Scripts Python procedurais prontos para compilação de ponta a ponta
* **output**: Diretório de saída onde os arquivos `.java` gerados são armazenados
* **src**: Código-fonte modularizado das quatro fases do compilador e da CLI
* **tests**: Suíte de testes unitários, de integração e de validação E2E com `javac`
