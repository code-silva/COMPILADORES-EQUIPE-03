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
    #### ***📄MkDocs***          
        