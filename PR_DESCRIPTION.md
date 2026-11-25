# Pull Request — Otimização do Compilador, Interface Web Local e Documentação

> **Branch:** `perf/otimizacao-compilador-e-docs`  
> **Escopo:** Otimização das 4 fases do compilador, correção de regressão em literais de string longos após benchmark, aprimoramento da interface web local, revisão da suíte de testes e alinhamento completo da documentação técnica.

---

## Resumo

Este Pull Request consolida melhorias de **desempenho**, **usabilidade** e **documentação** no **PyToJava**, mantendo 100% de compatibilidade com os contratos existentes da CLI, da API Python (`compile_source`) e dos testes automatizados.

Após a rodada de benchmarks comparativos (`pr64.json`), foi revertida a troca de `str.replace` por `str.translate` na geração de strings Java e aplicadas otimizações adicionais de despacho no nível da classe e varredura por fatias (*slices*) no `Scanner`.

---

## Principais Alterações e Correções Pós-Benchmark

### 1. Correção da Regressão em Strings Longas e Otimizações Adicionais

- **Reversão de `str.translate` para `str.replace` encadeado (`src/codegen/code_generator.py`)**:
  - Em CPython, `str.translate(dict)` realiza um lookup em dicionário Python para cada caractere individual da string, enquanto `str.replace(old, new)` utiliza busca vetorizada em C (`fastsearch`/`memchr`) e retorna a própria referência sem alocação quando o caractere de controle não está presente. Reverter para a cadeia `.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")` eliminou integralmente a regressão de ~5,7x observada no cenário `strings_400`.
- **Tabelas de Despacho no Nível da Classe (`_VISITOR_DISPATCH`)**:
  - Em `SemanticAnalyzer` e `CodeGenerator`, o cache de despacho por instância (`self._visitor_cache = {}`) foi substituído por tabelas estáticas no nível da classe (`_VISITOR_DISPATCH: dict[type[Node], Callable]`), preservando o fallback `getattr()` para subclasses instrumentadas nos testes. Isso eliminou a alocação de dois dicionários por compilação (reduzindo o pico de memória no cenário `small`) e removeu o custo de *warm-up* na primeira visita de cada tipo de nó.
- **Fast-path por Identidade de Tipo em `CodeGenerator.gen_expression()`**:
  - Reordenação dos ramos pelos nós mais frequentes (`IdentifierNode`, `IntLiteralNode`, `BinOpNode`) utilizando verificação rápida `type(node) is ...` antes do fallback `isinstance()`.
- **Varredura por Fatias Contínuas nos Laços Internos do `Scanner` (`src/lexer/scanner.py`)**:
  - `_scan_string()`, `_scan_number()`, `_scan_identifier()`, `_skip_whitespace()`, `_skip_comment()` e `_process_line_indentation()` agora percorrem o buffer `source_code` com cursor local em vez de invocar `stream.is_at_end()`, `stream.peek()` e `stream.advance()` a cada caractere. Em `_scan_string()`, strings sem sequências de escape são extraídas em uma única operação de *slice* (`source[chunk_start:cursor]`).

| Fase | Arquivos | Otimizações Consolidadas |
| :--- | :--- | :--- |
| **Léxico** | `src/lexer/char_stream.py`, `token.py`, `symbol_table.py`, `scanner.py` | `__slots__` em `CharStream`; `slots=True` em `Token` e `Symbol`; varredura direta no buffer e fatiamento (`source[start:cursor]`) para strings, números, identificadores, comentários e indentação; constantes `frozenset`/`dict` para operadores e delimitadores. |
| **Sintático** | `src/parser/parser.py` | Conjuntos de operadores e terminadores convertidos para `frozenset`; `_tokenize_source()` delegando diretamente para `Scanner(source_code).scan()`. |
| **Semântico** | `src/semantic/symbol_table.py`, `analyzer.py` | `slots=True` em `Symbol` e `__slots__` em `SymbolTable`; cálculo iterativo de `depth`; tabela de despacho de classe `_VISITOR_DISPATCH`. |
| **Codegen** | `src/codegen/code_generator.py` | Cache pré-alocado de prefixos de indentação (`_INDENT_PREFIXES`); escape de strings Java via `.replace()` nativo em C; tabela de despacho de classe `_VISITOR_DISPATCH`; fast-path em `gen_expression()`; docstrings padronizadas (PEP 257). |

---

### 2. Interface Web Local (`src/web.py` e `src/static/`)

- **Experiência de Uso**:
  - Layout responsivo com alternância entre **tema claro e escuro** (persistido em `localStorage`).
  - Modo **Arquivo `.py`** (*drag-and-drop* e seletor local) e modo **Editor** integrado com atalho `Ctrl+Enter`.
  - Carregamento rápido dos scripts oficiais de `examples/` via `GET /api/examples`.
  - Visualizador de saída `Main.java` com numeração de linhas, realce de sintaxe Java, tempo de compilação, botão de cópia e download direto.
- **Servidor HTTP (`src/web.py`)**:
  - Cache em memória dos assets estáticos com `functools.lru_cache`.
  - Tratamento de rotas com query string via `urllib.parse.urlsplit`.
  - Suporte a `HEAD`, entrega de `/favicon.svg` e cabeçalhos de segurança (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`).

---

### 3. Documentação Técnica (`docs/` e `README.md`)

- **`docs/compiladores.md`**: corrigido título e alinhadas as etapas teóricas aos módulos reais do PyToJava.
- **`docs/estrutura.md`** e **`README.md`**: atualizada a árvore de diretórios com `src/web.py`, `src/static/`, `examples/teste_interface.py` e `tests/test_web.py`.
- **`docs/usage.md`**: documentados o callback `on_stage` de `compile_source()` e os endpoints/argumentos da interface web local.
- **`docs/GLOSSARY.md`**: adicionados termos das fases posteriores (`AST`, `Precedence Climbing`, `Tabela de Símbolos`, `Padrão Visitor`, `Coerção / Promoção Numérica`, `Transpilação`, `NDJSON`).
- **`docs/semantic/symbol_table.md`** e **`docs/index.md`**: alinhados os nomes de tipos (`"String"`, `"boolean"`) e a descrição das tecnologias.

---

### 4. Testes Automatizados (`tests/`)

- Novo teste em `tests/test_compiler_pipeline.py` validando a ordem exata dos eventos do callback `on_stage` em `compile_source()`.
- Cobertura HTTP em `tests/test_web.py` para `/favicon.svg`, query strings, `HEAD` com cabeçalhos de segurança e `GET /api/examples`.
- **Resultado da execução das 23 suítes**: `691` aprovados, `0` falhas (`8` testes dependentes do binário externo `javac` pulados automaticamente quando `javac` não está no `PATH`).

---

## Como Executar Localmente

```bash
# Iniciar a interface web local
python -m src.web

# Compilar um arquivo via CLI
python -m src.cli examples/basic_math.py

# Executar a suíte de testes
python -m pytest -v
```

---

## Checklist do PR

- [x] Regressão de `str.translate` em `strings_400` corrigida e validada em benchmark
- [x] Otimizações aplicadas sem quebra de contrato nas 4 fases do compilador
- [x] Suíte completa de testes validada (`691` aprovados, `0` falhas)
- [x] Documentação técnica atualizada e sem emojis
- [x] Branch e commits seguindo o padrão do `CONTRIBUTING.md`
