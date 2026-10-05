# Especificação sintática inicial

Esta página registra o primeiro incremento do analisador sintático. O objetivo
atual é reconhecer expressões e atribuições simples a partir dos tokens gerados
pelo analisador léxico.

## Gramática

```ebnf
programa       ::= (quebra_linha | instrucao quebra_linha?)* EOF ;
instrucao      ::= IDENTIFIER op_atribuicao expressao | expressao ;
op_atribuicao  ::= "=" | "+=" | "-=" ;
expressao      ::= comparacao ;
comparacao     ::= adicao (("==" | "!=" | "<" | "<=" | ">" | ">=") adicao)* ;
adicao         ::= multiplicacao (("+" | "-") multiplicacao)* ;
multiplicacao  ::= unario (("*" | "/") unario)* ;
unario         ::= ("+" | "-") unario | primario ;
primario       ::= INT_LITERAL
                 | FLOAT_LITERAL
                 | STRING_LITERAL
                 | "True"
                 | "False"
                 | "None"
                 | IDENTIFIER
                 | "(" expressao ")" ;
quebra_linha   ::= NEWLINE ;
```

As regras em níveis separados definem a precedência. Multiplicação e divisão
são reconhecidas antes de soma e subtração; comparações possuem precedência
menor. Parênteses permitem alterar essa ordem.

## Estado da implementação

O parser descendente recursivo atual:

- consome diretamente os tokens produzidos pelo `Scanner`;
- reconhece literais, identificadores, operadores unários e binários;
- reconhece atribuições simples e compostas (`=`, `+=` e `-=`);
- aceita múltiplas instruções simples separadas por quebra de linha;
- informa erros sintáticos com linha, coluna e token encontrado.

Este é um incremento inicial. Ainda não fazem parte desta gramática:

- comandos compostos (`if`, `elif`, `else` e `while`);
- declarações de funções e `return`;
- blocos delimitados por `INDENT` e `DEDENT`;
- construção da árvore sintática abstrata (AST);
- recuperação após um erro sintático.
