<img width="1584" height="396" alt="capa_compiladores (3)" src="https://github.com/user-attachments/assets/e1bbe697-07e6-43d0-a963-72d915920563" />

---

# COMPILADORES-EQUIPE-03

# PyToJava Compiler 🐍 ➔ ☕

> Um compilador/transpilador de subconjunto de Python para código-fonte Java legível e executável.

<!-- Badges Sugeridas -->
![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![Language](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Target](https://img.shields.io/badge/Java-17%2B-orange?style=flat-square&logo=openjdk)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen?style=flat-square)

---

## 📌 Sobre o Projeto

O **PyToJava** é um compilador desenvolvido como parte da disciplina de Compiladores. O objetivo é receber um código-fonte escrito em um subconjunto da linguagem Python e traduzi-lo semanticamente para código Java equivalente e executável.

### Pipeline de Compilação
1. **Análise Léxica:** Reconhecimento de tokens e indentação (*INDENT/DEDENT*).
2. **Análise Sintática:** Construção da Árvore Sintática Abstrata (AST).
3. **Análise Semântica:** Inferência de tipos, checagem de escopo e tabela de símbolos.
4. **Geração de Código:** Emissão do arquivo final `.java`.

---

## 👥 Integrantes da Equipe

* **Anderson Fernandes da Silva** - Matrícula: `232000679` - [GitHub](https://github.com/code-silva)
* **Pedro Henrique Gomes Rodrigues** - Matrícula: `241025828` - [GitHub](https://github.com/usuario2)
* **Nome do Integrante 3** - Matrícula: `000000000` - [GitHub](https://github.com/usuario3)
* **Nome do Integrante 4** - Matrícula: `000000000` - [GitHub](https://github.com/usuario3)
* **Nome do Integrante 5** - Matrícula: `000000000` - [GitHub](https://github.com/usuario3)



---

## 📁 Estrutura de Pastas (sujeita a alterações)

```text
pytojava/
├── docs/                 # Documentação formal e relatórios
├── examples/             # Códigos Python de teste (.py)
│   ├── basic_math.py
│   └── control_flow.py
├── src/                  # Código-fonte do compilador
│   ├── lexer/            # Analisador léxico
│   ├── parser/           # Analisador sintático e gramáticas (ex: ANTLR/Lark/PLY)
│   ├── semantic/         # Tabela de símbolos e verificação de tipos
│   ├── codegen/          # Gerador de código Java
│   └── main.py           # Ponto de entrada (CLI)
├── tests/                # Suíte de testes unitários e de integração
│   ├── test_lexer.py
│   ├── test_parser.py
│   └── test_codegen.py
├── output/               # Arquivos .java gerados pela compilação
├── requirements.txt      # Dependências do projeto
├── README.md
└── LICENSE
```

## 1. Clonar e Instalar Dependências

```bash
# Passos sujeito a alterações

# Clone o repositório
git clone link-do-repositorio

# Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
# .venv\Scripts\activate    # Windows

# Instale os pacotes
pip install -r requirements.txt
```
# 2. Compilar um arquivo Python para Java

```bash
# Passos a definir
```

# 📄 Licença

A definir

---
