# Broadcast confiable y atómico

Este repo contiene el proyecto de aprobación final del curso Telecomunicaciones y sistemas distribuidos de la Universidad Nacional de Río Cuarto (UNRC).

## Objetivo

Dados N procesos, implementar una primitiva broadcast(msg) confiable atómico. Esto significa que todos los procesos correctos (sin fallas) coinciden en el conjunto de mensajes recibidos y son entregados (delivered) a la aplicación en el mismo orden (con respecto a otros mensajes de otros broadcasts). Se debe notar que este problema es equivalente a que todos los procesos correctos deban coincidir en la secuencia de mensajes a entregar a la aplicación.
* Documentar la solución, definir sus propiedades (invariantes). 
* Demostrar en forma semi-formal la correctitud de la primitiva.
