# chess
A minimal chess player, in Python

This is a bare-bones computer-chess player for the terminal, in about 250 lines of code. It doesn't know castling, promotion, or en passant, or do any sort of optimization.

```
% ./chess.py
     a  b  c  d  e  f  g  h
8 : {R}{N}{B}{Q}{K}{B}{N}{R}
7 : {P}{P}{P}{P}{P}{P}{P}{P}
6 :  .  .  .  .  .  .  .  . 
5 :  .  .  .  .  .  .  .  . 
4 :  .  .  .  .  .  .  .  . 
3 :  .  .  .  .  .  .  .  . 
2 :  P  P  P  P  P  P  P  P 
1 :  R  N  B  Q  K  B  N  R 

Your move: a2 a4
     a  b  c  d  e  f  g  h
8 : {R}{N}{B}{Q}{K}{B}{N}{R}
7 : {P}{P}{P}{P}{P}{P}{P}{P}
6 :  .  .  .  .  .  .  .  . 
5 :  .  .  .  .  .  .  .  . 
4 :  P  .  .  .  .  .  .  . 
3 :  .  .  .  .  .  .  .  . 
2 :  .  P  P  P  P  P  P  P 
1 :  R  N  B  Q  K  B  N  R 

     a  b  c  d  e  f  g  h
8 : {R}{N}{B}{Q}{K}{B}{N}{R}
7 : {P}{P}{P} . {P}{P}{P}{P}
6 :  .  .  . {P} .  .  .  . 
5 :  .  .  .  .  .  .  .  . 
4 :  P  .  .  .  .  .  .  . 
3 :  .  .  .  .  .  .  .  . 
2 :  .  P  P  P  P  P  P  P 
1 :  R  N  B  Q  K  B  N  R 
```
