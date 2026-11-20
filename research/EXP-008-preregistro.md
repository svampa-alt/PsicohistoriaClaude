# EXP-008 — Preregistro: disolución de la URSS (1991) y casos comparables

Fecha de registro: 2026-11-20 · Estado: **preespecificado, no ejecutado**. Se publica antes de calcular cualquier percentil o puntaje de los casos.

## Por qué ahora

La hoja de ruta fijó como experimento histórico de los primeros 7 días la **disolución de la URSS en 1991**, con controles. El plazo venció el 2026-11-18. EXP-003 aclaró que el evento de 1991 en los datos de golpes es el intento de golpe de agosto, no la disolución. Este experimento evalúa la disolución en sí.

## Pregunta

Con datos disponibles al cierre de 1990, ¿el índice de tensión (en su versión V-Dem de EXP-006) ubicaba a la URSS entre los Estados de mayor tensión del mundo? ¿Y a los otros Estados que se disolvieron en esos años?

## Casos (definidos antes de mirar)

Disoluciones: un Estado que desaparece al partirse en sucesores, según el último año de su código en Polity5.

| Caso | Código Polity | Año del evento t | Datos usados |
|---|---|---|---|
| URSS | 364 | 1991 | 1990 |
| Yugoslavia (RFSY) | 345 | 1991 | 1990 |
| Checoslovaquia | 315 | 1992 | 1991 |

**Excluidos y por qué:** unificaciones (las dos Alemanias en 1990, los dos Yemen en 1990), porque son el fenómeno inverso; conquista (Vietnam del Sur, 1975); Serbia y Montenegro (2006), porque no hay PIB comparable. Ninguno de estos tiene filas en el panel de todos modos.

**Controles negativos:** todos los demás Estados del panel en el mismo año, ninguno de los cuales se disolvió.

## Medidas

Sobre `data/exp006_panel.csv` (sin cambios), en la fila del año del evento (con explicativas de t−1):

- Percentil del caso dentro de su año para **T_v**, y para cada componente: **E** (tensión económica), **P_v** (polarización), **I_v** (fragilidad institucional). Percentil = proporción de Estados de ese año con valor estrictamente menor, más la mitad de los empates.
- Puesto (ranking) de T_v dentro del año.
- Riesgo de golpe según MXs_c (el mejor modelo de EXP-007), como información adicional, sin hipótesis.

## Hipótesis

- **U1:** la URSS en 1991 tiene T_v en el percentil ≥ 75 de su año.
- **U2:** el percentil medio de T_v de los tres casos es ≥ 75.
- **U3:** la probabilidad de que tres Estados elegidos al azar de sus años tengan un percentil medio igual o mayor que el observado es < 0,05 (prueba de permutación, 100.000 sorteos, semilla 20261120).

Si U1 falla, el índice **no anticipaba** la disolución de la URSS, y se informa así.

## Límites declarados

- Solo 3 casos: esto es un estudio de casos, no una estimación estadística. U3 tiene muy poca potencia.
- El índice T se diseñó como «tensión colectiva», no para disoluciones; tampoco se entrenó con ellas. Es una prueba de validez de criterio, no de pronóstico.
- Los datos de 1990 de V-Dem y Maddison se codificaron mucho después, con conocimiento de lo que pasó: riesgo de sesgo retrospectivo.
- Ser de alta tensión es compatible con muchos desenlaces (golpes, guerras, reformas); un percentil alto no implica que el índice «predijo» la disolución.
