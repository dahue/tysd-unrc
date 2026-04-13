# Broadcast confiable y atómico

Este repo contiene el proyecto de aprobación final del curso Telecomunicaciones y sistemas distribuidos de la Universidad Nacional de Río Cuarto (UNRC).

## Objetivo

Dados N procesos, implementar una primitiva broadcast(msg) confiable atómico. Esto significa que todos los procesos correctos (sin fallas) coinciden en el conjunto de mensajes recibidos y son entregados (delivered) a la aplicación en el mismo orden (con respecto a otros mensajes de otros broadcasts). Se debe notar que este problema es equivalente a que todos los procesos correctos deban coincidir en la secuencia de mensajes a entregar a la aplicación.

- Documentar la solución, definir sus propiedades (invariantes). 
- Demostrar en forma semi-formal la correctitud de la primitiva.

## Resolución

Cada proceso mantiene un reloj lógico de Lamport. Ante la concurrencia entre procesos, un reloj escalar de Lamport es suficiente para nuestros fines: aunque no caracteriza el orden causal, sí refleja el avance lógico local de cada proceso y permite definir un orden total entre mensajes difundidos en un sistema distribuido.

Los mensajes se encolan en una cola de prioridad ordenada según la clave (timestamp, pid), usando el pid como desempate cuando dos timestamps coinciden.

### Invariante de estabilidad

Un proceso hace **delivery** del mensaje `msg` (el que está a la cabeza de la cola) solo cuando, para **todo** otro proceso $p_i$, ya se recibió al menos un mensaje enviado por $p_i$ cuyo timestamp $ts_i$ cumple $ts_i \geq ts_{\mathrm{msg}}$, donde $ts_{\mathrm{msg}}$ es el timestamp de `msg`. Es decir:

$$
\min_i ts_i \geq ts_{\mathrm{msg}}
$$

donde cada $ts_i$ es el **máximo** timestamp visto hasta entonces en mensajes recibidos del proceso $i$ (en el código, `workers_last_timestamp[i]`).

**Intuición:** en el modelo del protocolo, al cumplirse esa condición se considera seguro avanzar con `msg`: no debería aparecer después un mensaje que deba ir **antes** que `msg` en el orden global inducido por `(timestamp, pid)`.

Gracias a esta invariante y a que todos los procesos usan la **misma** regla de orden y la **misma** condición de entrega, **todos entregan los mensajes a la aplicación en la misma secuencia** (mismo orden global).

### Comunicación

La comunicación usa **ZeroMQ** sobre **TCP**, por lo que se garantiza que los mensajes emitidos llegan a los suscriptores de forma confiable y ordenada (respecto al orden en que los envia cada proceso)