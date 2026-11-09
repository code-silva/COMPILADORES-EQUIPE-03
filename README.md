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

# Guia de Execução e Homologação do Projeto

Este guia descreve os pré-requisitos e o passo a passo para configurar o ambiente, executar a suíte de testes automatizados e compilar scripts Python procedurais para Java no Windows, Linux e macOS.

---

## 1. Pré-requisitos e Instalação de Ferramentas

O projeto exige **Python 3.10+** (recomendado 3.12) e **OpenJDK 17+** (`javac`).

### Windows (via PowerShell como Administrador)

### 1. Instalar o Python 3.12 (adicionando ao PATH)

```powershell
winget install -e --id Python.Python.3.12 --override "/passive InstallAllUsers=1 PrependPath=1"
```

### 2. Instalar o OpenJDK 17
```powershell
winget install -e --id EclipseAdoptium.Temurin.17.JDK
```

### 3. Feche e reabra o terminal para atualizar as variáveis de ambiente


### Linux (Ubuntu / Debian)

```bash
# 1. Atualizar repositórios e instalar Python, venv e OpenJDK 17
sudo apt update
sudo apt install -y python3 python3-venv python3-pip openjdk-17-jdk

# 2. Confirmar as versões
python3 --version
javac -version
```

### macOS (via Homebrew)

```bash
brew install python@3.12 openjdk@17
sudo ln -sfn $(brew --prefix)/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
export PATH="$(brew --prefix)/opt/openjdk@17/bin:$PATH"
```

---

## 2. Configuração do Ambiente Virtual do Projeto

Em qualquer sistema operacional, navegue até a pasta raiz do repositório clonado:

```bash
python3 -m venv .venv        # Linux / macOS
python -m venv .venv         # Windows

# 2. Ativar o ambiente virtual
source .venv/bin/activate    # Linux / macOS
.\.venv\Scripts\activate     # Windows (PowerShell)

# (No Windows PowerShell, se houver bloqueio de script, execute antes:)
# Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Instalar as dependências do projeto
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

---

## 3. Execução da Suíte de Testes Automatizados

Para homologar as 4 fases da pipeline de compilação (Scanner com pilha de indentação, Parser com *Precedence Climbing*, Analisador Semântico com *Visitor Pattern* e a validação *End-to-End* com o `javac` real via `subprocess`):

```bash
python -m pytest -v
```

> **Resultado Esperado:** 629+ testes aprovados.

---

## 4. Compilação e Execução de um Exemplo (Python → Java)

**Passo A:** Transpilar o código Python procedural para Java

```bash
python -m src.cli examples/calculator.py -o Main.java
```

**Passo B:** Compilar a classe Java emitida usando o `javac`

```bash
javac Main.java
```

**Passo C:** Executar a aplicação na JVM

```bash
java Main
```

---

## 5. Visualização da Documentação Estática (Opcional)

Para visualizar os diagramas da AST em Mermaid.js e os manuais das etapas de compilação:

```bash
python -m mkdocs serve
```

Acesse [http://127.0.0.1:8000](http://127.0.0.1:8000) no navegador.

---

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
