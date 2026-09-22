# 🌟Página de Contribuição do **PyToJava**!

Se você chegou até aqui, é porque quer entender como o projeto funciona por dentro ou ajudar a fazê-lo crescer, e ficamos felizes com isso.
Nesta seção você vai encontrar as tecnologias que sustentam o **PyToJava** (Flex, Bison, Git e companhia) e um guia passo a passo de como contribuir e configurar seu ambiente de desenvolvimento, tanto no Windows quanto no Linux.
---
## 🪛Tecnológias Utilizadas
- **Flex**: Análise Léxica (gerador de lexer)
- **Bison**: Análise Sintática (gerador de parser)
- **MkDocs + Material**: Documentação
- **Git**: Controle de versão
- **GitHub**: Repositório e colaboração

    ### ⭐Configuração e Instalação de dependências
    Para o funcionamento do PyToJava é necessário instalar e configurar algumas dependências. O processo pode variar conforme o sistema operacional utilizado, mas não se preocupe aqui vc encontrar passo a passo.

    #### ***⚡Flex e Bison***
    === "Windows"
        1. **Instalar WSL (Windows Subsystem for Linux)**

            * Abra o PowerShell no modo administrador e execute o seguinte comando pra a instalação da wsl:
            
                ```py title="PowerShell" linenums="1" hl_lines="2-3"
                wsl --install
                ```
                Após a instalação ser concluída, reinicie sua máquina.
        
                ***ATENÇÃO*** Recomenda-se ler a documentação oficial do WSL para mais detalhes:
                [Documentação da WLS](https://learn.microsoft.com/en-us/windows/wsl/install)

        2. **Instalar Flex e Bison**
            * Após ligar sua máquina, abra o terminal do Ubuntu (WSL) e execute:

                ```py title="Ubuntu" linenums="1"
                sudo apt update
                sudo apt install flex bison build-essential git -y  
                ```
        3. **Testar instalação**
            * Depois que a instalação for concluída, teste rodando:
                ```py title=" bash" linenums="1"
                flex --version
                bison --version
                ```
            * Deve aparecer algo como:
                ```py title=" bash" linenums="1"
                flex 2.6.4
                bison (GNU Bison) 3.8.2
                ```

    === "Linux" 
        1. **Instalar Flex e Bison**
            *  Abra o  bash e execute o seguinte comando pra a instalação:
                ```py title="Ubuntu" linenums="1"
                sudo apt update
                sudo apt install flex bison build-essential git -y  
                ```
            

        3. **Testar instalação**
            * Depois que a instalação for concluída, teste rodando:
                ```py title=" bash" linenums="1"
                flex --version
                bison --version
                ```
            * Deve aparecer algo como:
                ```py title=" bash" linenums="1"
                flex 2.6.4
                bison (GNU Bison) 3.8.2
                ```
    ---        
    #### ***🐈‍⬛Git***
    1. Acesse o [site oficial](https://git-scm.com/install) do Git pra a instalação.

    2. ***Testar instalação***
        
        * Depois que a instalação for concluída, teste rodando:

            ```bash title="bash" linenums="1"
            git --version
            ```
            Deve aparecer algo como:

            ```bash title="bash" linenums="1"
            git version 2.43.0    
            ```

    3. ***Configurar o Git***  
        ```bash title="bash" linenums="1" 
        git config --global user.name "Coloque seu nome do GitHub aqui"
        git config --global user.email "Coloque seu email do GitHub aqui"
        ```
    ---
    #### ***🪞Clonar Repositório*** 
    1. ***Clonar***
        * Abra o terminal no diretório onde deseja salvar a pasta do projeto e execute o seguinte comando:
        ```bash title="bash" linenums="1" 
        git clone https://github.com/code-silva/COMPILADORES-EQUIPE-03.git
        ```
    2. ***Acessar a pasta***:
        * Execute o seguinte comando:
        ```bash title="bash" linenums="1" 
        cd COMPILADORES-EQUIPE-03
        ```
    3. ***Verificar os arquivos***:
        * Execute o seguinte comando:
        ```bash title="bash" linenums="1" 
        ls
        ```
    ---   

## ***📚Padronizações***   
Padronização é o conjunto de regras e convenções que o projeto adota para manter o código, a documentação e o fluxo de trabalho consistentes. Ela existe para que qualquer pessoa do time saiba como nomear branches, escrever commits, organizar arquivos e contribuir de forma alinhada. Sem padronização, cada um faz de um jeito, o que gera confusão, retrabalho e dificulta a manutenção. Com ela, o repositório se torna mais legível, previsível e fácil de revisar, por isso abaixo segue-se alguns padrões dotados: 

### ***🗄️Padrão de branches***     
Uma branch permite trabalhar em uma mudança sem afetar o código principal. Nomear branches de forma padronizada ajuda a equipe a entender rapidamente o que está sendo feito e isso organiza o repositório, evita conflitos e facilita a revisão.

Vale salientar que os nomes de branches são compostos de **2 partes**:

```linenums="1" 
<prefixo>/<descrição-curta>
```

---

=== "docs"

    - **Quando usar:** Apenas mudanças de documentação, como por exemplo, arquivos `.md`, comentários, README, guias, glossário.

    **Exemplos:**

    ```linenums="1" 
    docs/padronizacao-commits-branches-git
    docs/atualizar-glossario-lexico
    ```

=== "feature"

    - **Quando usar:** Uma nova feature que será adicionada ao projeto, como por exemplo, componente, funcionalidade, módulo novo.

    **Exemplos:**

    ```linenums="1" 
    feature/analisador-lexico
    feature/parser-operadores-logicos
    ```

=== "fix"

    - **Quando usar:** Correção de um bug identificado.

    **Exemplos:**

    ```linenums="1" 
    fix/leitura-indentacao-bloco-if
    fix/reconhecimento-numeros-decimais
    ```

=== "perf"

    - **Quando usar:** Mudança de código focada em melhorar performance, velocidade, uso de memória, tamanho.

    **Exemplos:**

    ```linenums="1" 
    perf/tokenizacao-expressoes-grandes
    perf/otimizar-busca-tokens
    ```

=== "refactor"

    - **Quando usar:** Mudança de código que **não adiciona funcionalidade** e **não corrige bug** só reorganiza.

    **Exemplos:**

    ```linenums="1" 
    refactor/separar-logica-tokens
    refactor/extrair-classe-scanner
    ```

=== "test"

    - **Quando usar:** Adicionar ou corrigir testes.

    **Exemplos:**

    ```linenums="1" 
    test/casos-indent-dedent
    test/cobertura-parser-expressoes
    ```

=== "improvement"

    - **Quando usar:** Melhoria em algo **já existente**, como por exemplo, performance, escrita, layout, usabilidade.

    **Exemplos:**

    ```linenums="1" 
    improvement/glossario-tabela-termos
    improvement/mensagens-erro-sintatico
    ```
 ----

#### ***✅Boas práticas***

| Regra | Certo | Errado |
| :--- | :--- | :--- |
| Letras **minúsculas** | `feature/nova-funcionalidade` | `Feature/Nova-Funcionalidade` |
| **Hífen** entre palavras | `fix/leitura-indentacao` | `fix/leitura_indentacao` |
| **Sem acentos** | `docs/atualizar-glossario` | `docs/atualizar-glossário` |
| **Sem espaços** | `test/casos-indent` | `test/casos indent` |
| **Curto e descritivo** | `fix/leitura-indentacao-bloco-if` | `fix/corrige-aquele-bug` |    

#### ***🔨Como criar a branch na prática***

- 1° Atualize a dev:

    ```bash linenums="1" 
    git checkout dev
    git pull origin dev
    ```

- 2° Crie a branch seguindo o padrão:

    ```bash linenums="1"
    git checkout -b feature/analisador-lexico
    ```

- 3° Listar branches locais e remotas:    
    
    ```bash linenums="1"
    git branch -a
    ```

### ***🚀Convenção de commits***
Um commit é como uma anotação no caderno do projeto: ele diz o que mudou e por quê. Para que essas anotações fiquem fáceis de ler, o projeto usa o padrão **Conventional Commits**, que coloca um prefixo no início da mensagem indicando o tipo da mudança. Cada tipo ainda pode ganhar um **emoji**, que ajuda a identificar visualmente do que se trata. Assim, qualquer pessoa da equipe entende o histórico rapidamente e ferramentas conseguem gerar changelogs sozinhas. Por isso, o projeto segue o padrão descrito abaixo.

---

####  ***🧷Tipo e descrição***

-   ***feat***

    Indica que o trecho de código está incluindo um **novo recurso**.

    **Exemplo:** `feat: adiciona analisador léxico`

    - O emoji que representa esse tipo é o ✨ (`:sparkles:`).

        **Exemplo com emoji:** `✨ feat: adiciona analisador léxico`

-   ***fix***

    Indica que o trecho de código commitado está **solucionando um problema** (bug fix).

    **Exemplo:** `fix: corrige leitura de indentação`

    - O emoji que representa esse tipo é o 🐛 (`:bug:`).

        **Exemplo com emoji:** `🐛 fix: corrige leitura de indentação`

-   ***docs***

    Indica que houveram **mudanças na documentação**, como por exemplo no README do repositório.

    **Exemplo:** `docs: atualiza glossário de termos`

    - O emoji que representa esse tipo é o 📚 (`:books:`).

        **Exemplo com emoji:** `📚 docs: atualiza glossário de termos`

-   ***test***

    Utilizado quando são realizadas **alterações em testes**, seja criando, alterando ou excluindo testes unitários.

    **Exemplo:** `test: adiciona casos para INDENT e DEDENT`

    - O emoji que representa esse tipo é o 🧪 (`:test_tube:`).

        **Exemplo com emoji:** `🧪 test: adiciona casos para INDENT e DEDENT`

-   ***build***

    Utilizado quando são realizadas **modificações em arquivos de build e dependências**.

    **Exemplo:** `build: atualiza dependências do projeto`

    - O emoji que representa esse tipo é o 📦 (`:package:`).

        **Exemplo com emoji:** `📦 build: atualiza dependências do projeto`

-   ***perf***

    Serve para identificar quaisquer **alterações de código relacionadas a performance**.

    **Exemplo:** `perf: otimiza tokenização de expressões`

    - O emoji que representa esse tipo é o ⚡ (`:zap:`).

        **Exemplo com emoji:** `⚡ perf: otimiza tokenização de expressões`

-   ***style***

    Indica que houveram **alterações referentes a formatações de código**, como semicolons, trailing spaces e lint.

    **Exemplo:** `style: aplica formatação PEP 8 no lexer`
 
    - O emoji que representa esse tipo é o 💄 (`:lipstick:`).

        **Exemplo com emoji:** `💄 style: aplica formatação PEP 8 no lexer`

-   ***refactor***

    Refere-se a mudanças devido a **refatorações que não alteram a funcionalidade**.

    **Exemplo:** `refactor: separa lógica de tokens`

    - O emoji que representa esse tipo é o ♻️ (`:recycle:`).

        **Exemplo com emoji:** `♻️ refactor: separa lógica de tokens`

-   ***chore***

    Indica **atualizações de tarefas de build, configurações de administrador, pacotes**.

    **Exemplo:** `chore: adiciona pasta output ao gitignore`

    - O emoji que representa esse tipo é o 🔧 (`:wrench:`).

        **Exemplo com emoji:** `🔧 chore: adiciona pasta output ao gitignore`

-   ***ci***

    Indica **mudanças relacionadas a integração contínua** (continuous integration).

    **Exemplo:** `ci: configura pipeline no GitHub Actions`

    - O emoji que representa esse tipo é o 🧱 (`:bricks:`).

        **Exemplo com emoji:** `🧱 ci: configura pipeline no GitHub Actions`

-   ***raw***

    Indica **mudanças relacionadas a arquivos de configurações, dados, features, parâmetros**.

    **Exemplo:** `raw: ajusta parâmetros do parser`

    - O emoji que representa esse tipo é o 🗃️ (`:card_file_box:`).

        **Exemplo com emoji:** `🗃️ raw: ajusta parâmetros do parser`

-   ***cleanup***

    Utilizado para **remover código comentado, trechos desnecessários** ou qualquer outra forma de limpeza do código-fonte.

    **Exemplo:** `cleanup: remove código comentado do scanner`

    - O emoji que representa esse tipo é o 🧹 (`:broom:`).

        **Exemplo com emoji:** `🧹 cleanup: remove código comentado do scanner`

-   ***remove***

    Indica a **exclusão de arquivos, diretórios ou funcionalidades obsoletas** ou não utilizadas.

    **Exemplo:** `remove: exclui função obsoleta de tokenização`

    - O emoji que representa esse tipo é o 🗑️ (`:wastebasket:`).

        **Exemplo com emoji:** `🗑️ remove: exclui função obsoleta de tokenização`

---

#### ***🔨Como fazer commit na prática***

- 1° Verifique o que foi alterado

    ```bash linenums="1"
    git status
    ```

- 2° Adicione os arquivos e faça o commit com uma descrição clara

    ```bash linenums="1"
    git add .
    git commit -m "feat: adiciona analisador léxico para expressões aritméticas"
    ```

- 3° Envie para o remoto
```bash linenums="1"
git push origin feature/analisador-lexico
```
---

#### 🪄Recomendações

- Utilize um tipo que esteja de acordo com o conteúdo do commit.
- Na primeira linha, use no máximo **4 palavras**.
- Para detalhar melhor, utilize a **descrição do commit**.
- O uso de **emoji** no início da mensagem é **opcional**, mas ajuda a identificar visualmente o tipo.afiliados**.

---

### ***🎯Fluxo de Pull Request***
O Pull Request é a etapa em que o código desenvolvido é revisado antes de ser integrado à branch principal. Ele permite que outros membros da equipe analisem as mudanças, sugiram ajustes e garantam que tudo esteja de acordo com o padrão do projeto. Para que o PR seja aceito, é necessário cumprir o seguinte checklist antes de solicitar a revisão.

#### ***📋 Checklist obrigatório antes do merge***

Antes de solicitar revisão, confirme que:

- [ ] O código **compila** sem erros.
- [ ] Todos os **testes unitarios passam**.
- [ ] As **mudanças foram explicadas** e os **critérios de conclusão** foram atendidos.
- [ ] Se novos termos foram introduzidos, não esqueça de indicar para o **glossário** ser atualizado.
- [ ] A branch está **atualizada com a `main`** (sem conflitos).
- [ ] A **descrição do PR** explica o que foi feito e **como rodar**.
- [ ] Foi solicitada **revisão de pelo menos 1 membro** da equipe.

***✅ Após o merge*** vá até a **issue designada** e **feche-a**.