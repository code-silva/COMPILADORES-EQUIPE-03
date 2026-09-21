Aqui você encontrará a estrutura do nosso projeto detalhadamente, organizada de forma clara para facilitar a navegação e o entendimento de como o PyToJava foi construído. Nesta seção, apresentamos a arquitetura do compilador, a organização dos diretórios e o fluxo de execução. Se você quer entender como as peças se conectam, desde a leitura do código Python até a geração do Java final, este é o lugar certo para começar.

Vamos explorar juntos cada camada do projeto!

---
## 📁 Diretórios 

```text
pytojava/
├── docs/                     
│   ├── arch/
│   │   └── scanner.md
│   ├── specs/
│   │   └── lexico.md
│   └── GLOSSARY.md
├── examples/                 
│   ├── basic_math.py
│   └── control_flow.py
├── output/                   
├── src/                      
│   ├── __init__.py
│   ├── lexer/
│   │   ├── __init__.py
│   │   ├── char_stream.py
│   │   ├── errors.py
│   │   ├── indent_manager.py
│   │   ├── scanner.py
│   │   ├── symbol_table.py
│   │   ├── token.py
│   │   └── token_type.py
│   ├── parser/
│   │   └── __init__.py
│   ├── semantic/
│   │   └── __init__.py
│   ├── codegen/
│   │   └── __init__.py
│   └── main.py               # Ponto de entrada (CLI)
├── tests/                   
│   ├── __init__.py
│   ├── test_lexer_happy_path.py
│   ├── test_lexer_edge_cases.py
│   ├── test_parser.py
│   └── test_codegen.py
├── .gitignore                # Ignora .venv/, __pycache__/, output/
├── CONTRIBUTING.md           # Guia de contribuição da equipe
├── LICENSE
├── mkdocs.yml                # Configuração do site da documentação
├── pyproject.toml            # Configuração do projeto e do pytest
├── README.md
└── requirements.txt          # Dependências (pytest, mkdocs, etc.)
```

---
## 🗂️Pastas
 * docs: Documentação formal e relatórios (MkDocs)
 * examples: Códigos Python de entrada
 * src: Código-fonte do compilador
 * tests: Suíte de testes unitários

