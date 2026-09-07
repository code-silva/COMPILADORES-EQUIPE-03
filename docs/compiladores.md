## Oque é um Compilador?
Um compilador é um programa de computador que atua como um tradutor, convertendo código escrito em uma linguagem de programação de alto nível (como Python) para outra linguagem, geralmente de mais baixo nível, como código de máquina, assembly ou bytecode.

Esse processo mantém o significado original do programa, permitindo que ele seja executado em diferentes ambientes. Além da tradução, o compilador também verifica erros de sintaxe e semântica, garantindo que o código fonte esteja correto antes da geração do código final.

No PyToJava, aplicamos esse conceito traduzindo código Python para Java, passando por todas as fases clássicas de um compilador.
## Quais são as etas de compilação? 
**1) Análise Léxica:** Divide o código-fonte em unidades lexicais chamadas "tokens". Identifica palavras-chave, operadores, identificadores e outros símbolos da linguagem. Garante que o código-fonte esteja bem estruturado e siga as regras básicas da linguagem.

**2) Análise Sintática:** Analisa a estrutura gramatical do código-fonte com base na gramática da linguagem. Verifica se a sequência de tokens forma sentenças válidas de acordo com as regras da linguagem. Constrói uma árvore sintática (parse tree) que representa a hierarquia estrutural do programa.

**3) Geração de Código Intermediário:** Cria uma representação mais abstrata e fácil de manipular do programa. Permite que a lógica seja separada da arquitetura específica da máquina onde será executado. Essa etapa facilita a otimização e o suporte a múltiplas arquiteturas.

**4) Otimização:** Analisa o código intermediário para melhorar o desempenho e a eficiência do programa final. Aplica técnicas como eliminação de código morto, otimização de loops e redução de instruções. Produz um código mais rápido e que consome menos recursos.

**5) Geração do Código Objeto:** Traduz o código intermediário otimizado em instruções de baixo nível compreendidas pelo processador. Gera arquivos executáveis que podem ser executados diretamente pela máquina. Conclui o processo de compilação com o código final pronto para uso.
