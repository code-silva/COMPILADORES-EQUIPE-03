# Documentação
![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square)
![Language](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Target](https://img.shields.io/badge/Java-17%2B-orange?style=flat-square&logo=openjdk)
![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)
![Coverage](https://img.shields.io/badge/coverage-85%25-yellowgreen?style=flat-square)

## 📌Sobre o Projeto

O projeto **PyToJava** é desenvolvido como parte da disciplina **Compiladores 1**, ministrada pelo professor **Sergio Freitas**, com o objetivo de construir um compilador funcional que traduza código da linguagem Python para Java.
Para saber mais sobre compiladores, [clique aqui](compiladores.md).

<div class="grid-cards">

  <!-- Card 1: Analisador Léxico -->
  <div class="card-fases">
    <div>
      <div class="card-header">
        <div class="card-icon">🔤</div>
        <span class="badge badge-green">Fase 1</span>
      </div>
      <h3>Analisador Léxico</h3>
      <p>
        Agrupamento de caracteres do código em <strong>Tokens</strong> e remoção de espaços via autómatos finitos.
      </p>
    </div>
    <div class="card-footer-action">
      <div class="progress-bar"><div class="progress-fill green" style="width: 100%;"></div></div>
      <span class="progress-text">Lexer ativo (100%)</span>
      <a href="../compiladores/#analisador-lexico" class="btn-card-doc">Ver Documentação ➔</a>
    </div>
  </div>

  <!-- Card 2: Analisador Sintático -->
  <div class="card-fases">
    <div>
      <div class="card-header">
        <div class="card-icon">🌳</div>
        <span class="badge badge-purple">Fase 2</span>
      </div>
      <h3>Analisador Sintático</h3>
      <p>
        Validação dos tokens com a gramática e construção da <strong>Árvore de Sintaxe Abstrata (AST)</strong>.
      </p>
    </div>
    <div class="card-footer-action">
      <div class="progress-bar"><div class="progress-fill purple" style="width: 100%;"></div></div>
      <span class="progress-text">Parser AST concluído</span>
      <a href="../compiladores/#analisador-sintatico" class="btn-card-doc">Ver Documentação ➔</a>
    </div>
  </div>

  <!-- Card 3: Analisador Semântico -->
  <div class="card-fases">
    <div>
      <div class="card-header">
        <div class="card-icon">🛡️</div>
        <span class="badge badge-purple">Fase 3</span>
      </div>
      <h3>Analisador Semântico</h3>
      <p>
        Verificação de tipos (<strong>Type Checking</strong>) e gerenciamento de escopos na tabela de símbolos.
      </p>
    </div>
    <div class="card-footer-action">
      <div class="progress-bar"><div class="progress-fill purple" style="width: 85%;"></div></div>
      <span class="progress-text">Checagem de tipos em progresso</span>
      <a href="../compiladores/#analisador-semantico" class="btn-card-doc">Ver Documentação ➔</a>
    </div>
  </div>

</div>

!!! info "🎓 Contexto Acadêmico & Arquitetura de Fases [Consultar Teoria de Compiladores ↗](https://github.com/sergioaafreitas/COMP1)"

    Desenvolvido dentro da disciplina de Compiladores 1 do curso de Engenharia de Software. O projeto explora análise léxica por autómatos determinísticos, gramática de precedência para expressões aritméticas e inferência tipada de fluxos de controle, gerando artefatos compiláveis.

---
## 🎯Objetivos

* implementar as fases de um compilador: análise léxica, sintática, semântica e geração de código
* Aplicar os conceitos teóricos de compiladores na prática
* Gerar código Java executável a partir de código Python
* Compreender a arquitetura interna de um compilador
---
## 📊Tecnológias Utilizadas

- **Flex**: Análise Léxica (gerador de lexer)
- **Bison**: Análise Sintática (gerador de parser)
- **MkDocs + Material**: Documentação
- **Git**: Controle de versão
- **GitHub**: Repositório e colaboração