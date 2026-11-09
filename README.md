<img width="1584" height="396" alt="download" src="https://github.com/user-attachments/assets/829163ec-e84f-457b-a690-30b5bcbae7d9" />

# PyToJava Compiler

> Um compilador/transpilador de subconjunto procedural de Python para código-fonte Java legível e executável.

<p align="center">
  <img src="https://img.shields.io/badge/build-passing-success?style=flat&logo=github-actions&logoColor=white" alt="Build" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Java-17%2B-ED8B00?style=flat&logo=openjdk&logoColor=white" alt="Java" />
  <img src="https://img.shields.io/badge/license-MIT-informational?style=flat" alt="License" />
  <img src="https://img.shields.io/badge/coverage-100%25-success?style=flat" alt="Coverage" />
</p>

---

## Sobre o Projeto

O **PyToJava** é um compilador desenvolvido como parte da disciplina de Compiladores. O objetivo é receber um código-fonte escrito em um subconjunto procedural da linguagem Python e traduzi-lo semanticamente para código Java equivalente, estruturado e executável.

### Pipeline de Compilação
1. **Análise Léxica:** Reconhecimento de tokens e controle de pilha de indentação (*INDENT/DEDENT*).
2. **Análise Sintática:** Construção da Árvore Sintática Abstrata (AST) por descida recursiva e *Precedence Climbing*.
3. **Análise Semântica:** Inferência estática de tipos, checagem de escopo e tabela de símbolos via padrão *Visitor*.
4. **Geração de Código:** Emissão do arquivo final `.java` (`public class Main`) compilável com `javac`.

---

## Integrantes da Equipe

* **Anderson Fernandes da Silva** - Matrícula: `232000679` - [GitHub](https://github.com/code-silva)
* **Pedro Henrique Gomes Rodrigues** - Matrícula: `241025828` - [GitHub](https://github.com/PedroGomes-phgr)
* **Matheus Rodrigues Pontes** - Matrícula: `242024478` - [GitHub](https://github.com/matheus0346)
* **Marcely do Nascimento Silva** - Matrícula: `241025701` - [GitHub](https://github.com/NSMarcely)
* **Sauhan Ferreira Melo** - Matrícula: `242024923` - [GitHub](https://github.com/usuario3)

---

## Estrutura de Pastas

```text
pytojava/
├── docs/                     # Documentação formal e relatórios (MkDocs)
│   ├── arch/
│   │   └── scanner.md
│   ├── codegen/
│   │   ├── architecture.md
│   │   ├── control_flow.md
│   │   └── expressions.md
│   ├── parser/
│   │   ├── ast.md
│   │   ├── errors.md
│   │   ├── grammar.md
│   │   └── index.md
│   ├── semantic/
│   │   ├── analyzer.md
│   │   ├── symbol_table.md
│   │   └── types.md
│   ├── specs/
│   │   └── lexico.md
│   ├── compiladores.md
│   ├── estrutura.md
│   ├── GLOSSARY.md
│   ├── index.md
│   └── usage.md
├── examples/                 # Scripts Python de exemplo (.py)
│   ├── basic_math.py
│   ├── calculator.py
│   ├── control_flow.py
│   ├── factorial.py
│   └── hello.py
├── output/                   # Arquivos .java gerados (ignorados pelo Git)
├── src/                      # Código-fonte do compilador
│   ├── __init__.py
│   ├── cli.py                # Driver e interface de linha de comando (CLI)
│   ├── main.py               # Ponto de entrada alternativo
│   ├── lexer/                # Fase 1: Analisador Léxico
│   ├── parser/               # Fase 2: Analisador Sintático e nós da AST
│   ├── semantic/             # Fase 3: Analisador Semântico e Tabela de Símbolos
│   └── codegen/              # Fase 4: Gerador de Código Java
├── tests/                    # Suíte de testes unitários, de integração e E2E (pytest)
├── .gitignore
├── CONTRIBUTING.md
├── LICENSE
├── mkdocs.yml
├── pyproject.toml
├── README.md
└── requirements.txt
```

## 1. Clonar e Instalar Dependências

```bash
# Clone o repositório
git clone https://github.com/code-silva/COMPILADORES-EQUIPE-03.git
cd COMPILADORES-EQUIPE-03

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instale os pacotes
pip install -r requirements.txt
```

## 2. Compilar um Arquivo Python para Java

```bash
# Compila o arquivo .py gerando automaticamente em output/<nome>.java
python -m src.cli examples/factorial.py

# Ou especifique o caminho do arquivo .java de saída com -o / --output
python -m src.cli examples/calculator.py -o output/Main.java
```

## 3. Executar a Suíte de Testes

```bash
# Executa toda a suíte de testes unitários, de integração e E2E (incluindo validação com javac)
pytest -v
```

## Documentação

Acesse a documentação completa do projeto através do link:
[Clique aqui para acessar a documentação](https://code-silva.github.io/COMPILADORES-EQUIPE-03/)

## Como Executar a Documentação Localmente

Você pode executar o servidor local da documentação de duas formas: **via Docker** (recomendado para evitar divergências de ambiente) ou **localmente via Python/Pipenv**.

---

### Opção 1: Via Docker (Recomendado)

Esta abordagem garante que você rode exatamente a mesma versão do Python e das dependências sem precisar configurar o ambiente na sua máquina.

#### Pré-requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado e em execução.

#### Passos

1. Suba o container da documentação a partir da raiz do projeto:

   ```bash
   docker compose up
   ```

   (Caso queira liberar o terminal, utilize `docker compose up -d`)

2. Acesse a documentação no navegador:

   http://localhost:8000

3. Para parar o servidor:

   ```bash
   docker compose down
   ```

---

### Opção 2: Execução Local (Sem Docker)

Caso prefira rodar a documentação diretamente no seu sistema operacional.

#### Pré-requisitos

- Python 3.10+ (recomendado Python 3.12)
- Pipenv (gerenciador de ambientes virtuais)

#### Passos

1. Instalar o Pipenv (caso ainda não tenha instalado):

   ```bash
   pip install pipenv
   ```

2. Instalar as dependências do projeto na raiz do repositório:

   ```bash
   pipenv install --skip-lock
   ```

3. Iniciar o servidor do MkDocs:

   ```bash
   pipenv run mkdocs serve
   ```

4. Acesse a documentação no navegador:

   http://127.0.0.1:8000

---

> **Nota:** Qualquer alteração nos arquivos da pasta `docs/` ou no `mkdocs.yml` será atualizada automaticamente no navegador em tempo real (hot-reload) em ambos os métodos.

## Licença

Este projeto está licenciado sob a Licença MIT - consulte o arquivo [LICENSE](./LICENSE) para mais detalhes.
