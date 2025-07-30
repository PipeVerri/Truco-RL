# Version 1
Va a ser un MLP el cual evolucione a traves de un algoritmo genetico. **Solo va a jugar lo mejor posible la mano, no la partida entera** ya que siento que se me van a ir al carajo las entradas si no las hago bien(lo cual aun no se). Los inputs van a ser:
## Inputs
1. Cartas que tengo mias ordenadas de mayor a menor(3 neuronas)
2. Cartas jugada mia(3 neuronas)
2. Carta jugada oponente(3 neuronas)

- Los valores para eso van a ser las cartas ordenadas desde el mayor numero(el macho) hasta el menor numero(el 4). 
- Le voy a meter info sobre el palo de la carta(2 neuronas por carta, una de valor otra de palo) pero me gustaria 
- Si la carta aun no fue jugada o ya la gaste, su valor se vuelve 0
- Hago de que si jugaste la primera carta, despues en la siguiente iteracion tengas en 0 ese espacio asi logra entender mas el modelo sobre los turnos, pero las ordeno de mayor a menor ya que "macho-hembra-4" es lo mismo que "4-macho-hembra", pero **tengo que probar si hago de que tengan "los agujeros" o si siempre las corro para atras**

3. Estado de las manos(3 neuronas one hot)
- La primera en 1 si la gane yo
- La segunda en 1 si la gano el otro
- Las tercera prendida si se empardo
- Ninguna prendida si no se jugo
4. Si la mano es "critica" o no(2 neuronas one hot para la mano siendo jugada)

Las 2 ultimas manos tienen neuronas one hot que
- 1 dice si puedo empardar(y no perder)
- La otra dice si puedo perder(solo para la mano 2, ya que si puedo perder tercera sin que pase nada tuve que haber definido en segunda)

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
13. Estado actual del truco(parece redundante pero no lo es, ya que si no puedo cantar retruco, puede ser porque el otro lo tenga, o porque nunca se canto. Es medio redundante, pero para que no tenga que intuir)

El estado del truco va a ser un unico numero de cuantos puntos estan en juego

14. Puedo cantar envido
15. Puedo cantar doble-envido
16. Puedo cantar real envido
17. Puedo cantar falta envido
18. Puntos actuales del envido

En si puedo cantar o no lo mismo, uso un one-hot. En los puntos actuales del envido lo que hago es sumar todo lo que se viene cantando(si se canto envido-envido, entonces esta neurona = 4)

19. Si el envido lo rechaze yo, lo rechazo el oponente, lo gane yo o lo gano el oponente
20. Cuantos puntos de envido tiene el oponente(0 si no los dijo)

***Al final voy a usar vectores one-hot para todo excepto los valores de  cartas***
## Salidas
Va a ser una salida softmax pasada por una mascara asi no toma acciones incorrectas
1. Jugar la primera carta
2. Jugar la segunda carta
3. Jugar la tercera carta
4. Cantar truco, retruco...(1 neurona por accion)
5. Cantar envido, doble envido...(1 neurona por accion)
6. Quiero truco
7. No quiero truco
8. Quiero envido
9. No quiero envido
8. Me voy al mazo

## Returns de la funcion de process_action
0. Perdio el agente 1
1. Gano el agente 1