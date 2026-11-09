# Documentação
![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![Language](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Target](https://img.shields.io/badge/Java-17%2B-orange?style=flat-square&logo=openjdk)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen?style=flat-square)

<div class="banner-hero">
  <!-- Imagem de fundo -->
  <img src="img/capa_java_to_python.jpg" class="banner-img" />

  <!-- Camada com o gradiente e os textos sobrepostos -->
  <div class="banner-overlay">
    <div class="banner-content">
      <span class="banner-subtitle">UnB</span>
      <h2 class="banner-title">PyToJava</h2>
    </div>
    <span class="banner-badge">Java</span>
  </div>
</div>

## Sobre o Projeto

O projeto **PyToJava** é desenvolvido como parte da disciplina **Compiladores 1**, ministrada pelo professor **Sergio Freitas**, com o objetivo de construir um compilador funcional que traduza código de um subconjunto procedural da linguagem Python para Java.
Para saber mais sobre compiladores, [clique aqui](compiladores.md).

<div class="grid-cards">

  <!-- Card 1: Analisador Léxico -->
  <div class="card-fases">
    <div>
      <div class="card-header">
        <div class="card-icon">F1</div>
        <span class="badge badge-green">Fase 1</span>
      </div>
      <h3>Analisador Léxico</h3>
      <p>
        Agrupamento de caracteres do código em <strong>Tokens</strong> e controle de pilha de indentação via autômatos finitos.
      </p>
    </div>
    <div class="card-footer-action">
      <div class="progress-bar"><div class="progress-fill green" style="width: 100%;"></div></div>
      <span class="progress-text">Lexer concluído (100%)</span>
      <a href="specs/lexico/" class="btn-card-doc">Ver Documentação -></a>
    </div>
  </div>

  <!-- Card 2: Analisador Sintático -->
  <div class="card-fases">
    <div>
      <div class="card-header">
        <div class="card-icon">F2</div>
        <span class="badge badge-purple">Fase 2</span>
      </div>
      <h3>Analisador Sintático</h3>
      <p>
        Validação dos tokens com a gramática e construção da <strong>Árvore de Sintaxe Abstrata (AST)</strong>.
      </p>
    </div>
    <div class="card-footer-action">
      <div class="progress-bar"><div class="progress-fill green" style="width: 100%;"></div></div>
      <span class="progress-text">Parser AST concluído (100%)</span>
      <a href="parser/" class="btn-card-doc">Ver Documentação -></a>
    </div>
  </div>

  <!-- Card 3: Analisador Semântico -->
  <div class="card-fases">
    <div>
      <div class="card-header">
        <div class="card-icon">F3</div>
        <span class="badge badge-purple">Fase 3</span>
      </div>
      <h3>Analisador Semântico</h3>
      <p>
        Verificação de tipos (<strong>Type Checking</strong>) e gerenciamento de escopos na tabela de símbolos.
      </p>
    </div>
    <div class="card-footer-action">
      <div class="progress-bar"><div class="progress-fill green" style="width: 100%;"></div></div>
      <span class="progress-text">Analisador semântico concluído (100%)</span>
      <a href="semantic/analyzer/" class="btn-card-doc">Ver Documentação -></a>
    </div>
  </div>

  <!-- Card 4: Gerador de Código -->
  <div class="card-fases">
    <div>
      <div class="card-header">
        <div class="card-icon">F4</div>
        <span class="badge badge-purple">Fase 4</span>
      </div>
      <h3>Gerador de Código</h3>
      <p>
        Tradução da AST para código-fonte <strong>Java</strong> estruturado, indentado e compilável com <code>javac</code>.
      </p>
    </div>
    <div class="card-footer-action">
      <div class="progress-bar"><div class="progress-fill green" style="width: 100%;"></div></div>
      <span class="progress-text">Gerador de código concluído (100%)</span>
      <a href="codegen/architecture/" class="btn-card-doc">Ver Documentação -></a>
    </div>
  </div>

</div>

!!! info "Contexto Acadêmico e Arquitetura de Fases [Consultar Teoria de Compiladores](https://github.com/sergioaafreitas/COMP1)"

    Desenvolvido dentro da disciplina de Compiladores 1 do curso de Engenharia de Software. O projeto explora análise léxica por autômatos determinísticos, gramática de precedência para expressões aritméticas, inferência tipada de fluxos de controle e emissão de código Java compilável.

---
## Objetivos

* Implementar as fases de um compilador: análise léxica, sintática, semântica e geração de código
* Aplicar os conceitos teóricos de compiladores na prática
* Gerar código Java executável e compilável via `javac` a partir de código Python procedural
* Compreender a arquitetura interna de um compilador e sua interface de linha de comando (CLI)

---
## Tecnologias Utilizadas

- **Python 3.10+**: Implementação do compilador (Lexer, Parser, Semântico, Codegen e CLI)
- **Java 17+ (`javac`)**: Linguagem alvo e validação do código gerado
- **Pytest**: Suíte de testes unitários e de integração End-to-End (E2E)
- **Flex & Bison**: Modelos teóricos de referência para análise léxica e sintática
- **MkDocs + Material**: Documentação técnica
- **Git & GitHub**: Controle de versão e colaboração
