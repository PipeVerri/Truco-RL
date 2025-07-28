# Version 1
Va a ser un MLP el cual evolucione a traves de un algoritmo genetico. Los inputs van a ser:

1. Cartas que tengo mias ordenadas de mayor a menor(3 neuronas)
2. Cartas jugada mia(3 neuronas)
2. Carta jugada oponente(3 neuronas)

- Los valores para eso van a ser las cartas ordenadas desde el mayor numero(el macho) hasta el menor numero(el 4). 
- Le voy a meter info sobre el palo de la carta(2 neuronas por carta, una de valor otra de palo) pero me gustaria 
- Si la carta aun no fue jugada o ya la gaste, su valor se vuelve 0
- Hago de que si jugaste la primera carta, despues en la siguiente iteracion tengas en 0 ese espacio asi logra entender mas el modelo sobre los turnos, pero las ordeno de mayor a menor ya que "macho-hembra-4" es lo mismo que "4-macho-hembra", pero **tengo que probar si hago de que tengan "los agujeros" o si siempre las corro para atras**

3. Estado de las manos(3 neuronas)
- 0 si no se jugo
- 1 si la gane yo
- -1 si la gano el otro
- 0.5 si empardo
4. Si la mano es "critica" o no(2 neuronas para la mano 2 y 3)

Si en esa mano se determina quien gana o no, se le pone un 1, si no, un 0

5. Puntos de envido(1 neurona)
6. Puntos a ganar si se cantara real envido(1 neurona)
7. Puntos que ganaria el oponente si ganara el real envido(1 neurona)
8. Puntos que me faltan para los 30(1)
9. Puntos que le faltan al oponente para los 30(1)
10. Diferencia de puntos entre yo - oponente

- La razon por la que puse puntos para los 30 en vez de simplemente los puntos que tengo es porque es mas importante cuanto nos faltan que cuanto tenemos
- Los puntos a ganar del falta envido es lo que ganaria por si solo, sin contar nada stackeado

10. Puedo cantar truco
11. Puedo cantar retruco
12. Puedo cantar vale 4
13. Estado actual del truco

Los estados de si puedo o no va a ser un one-hot. 1 para si, 0 para no
- 0 si nadie canto
- 1 truco
- 2 retruco
- 3 vale 4

14. Puedo cantar envido
15. Puedo cantar doble-envido
16. Puedo cantar real envido
17. Puedo cantar falta envido
18. Puntos actuales del envido

En si puedo cantar o no lo mismo, uso un one-hot. En los puntos actuales del envido lo que hago es sumar todo lo que se viene cantando(si se canto envido-envido, entonces esta neurona = 4)

19. Si el envido lo rechaze yo, lo rechazo el oponente, lo gane yo o lo gano el oponente
20. Cuantos puntos de envido tiene el oponente(0 si no los dijo)

***Al final voy a usar vectores one-hot para todo excepto las cartas***