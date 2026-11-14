# Hoja de ruta permanente — Psicohistoria-lab

Versión 1.1 · aprobada por el usuario el 2026-11-11 (v1.0 del mismo día; la v1.1 solo cambia el formato de reporte y agrega el estado verificado). **Norma obligatoria para toda ejecución del laboratorio.** No reemplazarla silenciosamente; cualquier cambio de metas exige aprobación expresa. Consultar este documento al inicio y al cierre de cada ejecución.

## Objetivo científico
Evaluar si modelos matemáticos multivariables, con interacciones económicas, políticas, demográficas, militares e institucionales, pueden anticipar acontecimientos históricos reales mejor que baselines simples. Solo información disponible antes del acontecimiento. Registrar también fallos y resultados negativos. No confundir reconstrucción retrospectiva con pronóstico ex ante.

## Corto plazo: primeros 7 días (desde 2026-11-11)
1. Días 1–2: investigar **5 bases históricas independientes**. Entregar catálogo con URL, procedencia, cobertura temporal/geográfica, variables, licencias, acceso y limitaciones.
2. Días 2–3: **incorporar 3 fuentes nuevas** con datos realmente obtenidos y procesables, hashes y controles; no contar enlaces sin descarga/lectura.
3. Días 3–4: integrar una **matriz país-año multivariable**, documentando identificadores, cambios territoriales, cobertura, ausencias y disponibilidad temporal.
4. Días 4–5: entrenar y evaluar **al menos un modelo que use variables nuevas e interacciones**, comparándolo con baselines simples y respetando la separación temporal.
5. Días 5–7: ejecutar **un experimento histórico real verificable**, inicialmente la disolución de la URSS en 1991, con controles (Estados/crisis sin disolución), variables anteriores a 1991, pronósticos, errores y limitaciones. Si los datos históricos no permiten una evaluación válida, documentar bloqueo y seleccionar un caso alternativo con datos suficientes, sin inventar datos.

**Metas cuantitativas día 7:** 5 bases investigadas; 3 fuentes incorporadas; ≥6 variables explicativas nuevas; 1 matriz multivariable; 1 experimento histórico real; 1 comparación con baselines; 100% de resultados documentados.

## Mediano plazo: días 30–90
- Integrar **10–15 conjuntos de datos** independientes; economía, demografía, política, instituciones y guerras.
- Analizar **interacciones entre variables**, no solo efectos individuales, y comprobar su ganancia fuera de muestra.
- Codificar **≥30 episodios históricos** con períodos comparables sin evento. Casos prioritarios: invasión de Polonia (1939), revolución iraní (1979), caída del Muro de Berlín (1989), además de URSS (1991).
- Evaluación temporal fuera de muestra: Brier, calibración, discriminación, incertidumbre y baselines de frecuencia/persistencia/modelos convencionales.
- Registrar tanto hipótesis descartadas como resultados favorables.

## Largo plazo: meses 6–12
- Ampliar cobertura de países, épocas y variables, según calidad disponible.
- Comparar modelos estadísticos, redes de interdependencia y modelos temporales.
- Evaluar centenares de episodios si existen datos suficientes y comparables.
- Automatizar ingestión, versionado, auditorías y reproducción; crear visualización de variables, pronósticos, errores e incertidumbre.
- GitHub almacena código, protocolos y resultados pequeños; datos voluminosos en almacenamiento externo versionado y referenciado, respetando licencias.

## Reglas innegociables de ejecución
1. Leer esta hoja **antes de cualquier trabajo** en Psicohistoria-lab y verificarla **al terminar**.
2. Priorizar **fuentes y variables nuevas**, excepto bloqueo técnico justificado. No repetir ajustes de COW como sustituto de ampliar datos.
3. Asociar cada experimento con un **acontecimiento histórico real** o familia de eventos definida, y controles negativos.
4. Estudiar **interacciones entre variables** y comprobar si mejoran las predicciones.
5. Separar **hecho verificado / ejecutado / implementado pero no ejecutado / pendiente / bloqueado**. No atribuir resultados inexistentes.
6. Evitar duplicar repositorios, análisis o herramientas. Reutilizar código existente.
7. No filtrar información futura, no inventar datos ni confundir una correlación con causalidad.
8. **Toda ejecución debe terminar con un reporte de cumplimiento de ESTA hoja** (breve por defecto, completo semanal o a pedido), no un informe genérico de actividad. Guardar evidencias en GitHub cuando se modifique el proyecto.

## Formato del reporte (v1.1)

### Reporte breve — formato por defecto de cada ejecución
Máximo **10 líneas**:
- Fecha, qué se ejecutó y commits; si se verificó GitHub.
- **Una sola línea con los 7 indicadores** de corto plazo: bases investigadas (x/5) · fuentes incorporadas (x/3) · variables nuevas (x/≥6) · matriz (x/1) · experimento real (x/1) · comparación con baselines (x/1) · documentación (x %).
- Resultado concreto principal (métricas reales) y qué es exploratorio.
- Pendientes, desvíos o bloqueos, y plazos incumplidos si los hay. Si no hubo avances, escribir **0** y por qué.

### Reporte completo — semanal o a pedido del usuario
- **Fecha, ejecución, commits y archivos examinados**; indicar si se verificó GitHub.
- Tabla **Compromiso de la hoja de ruta | Meta y vencimiento | Cumplido hoy (evidencia concreta) | Acumulado verificado | Falta/bloqueo | Estado**.
- Los 7 indicadores de corto plazo y los hitos de mediano/largo plazo que correspondan.
- **Resultados concretos:** fuentes con URL, cantidad de filas/variables, nombres de eventos, métricas y artefactos/commits.
- **Pendientes y desvíos:** qué obligación falta, cuánto falta, por qué y si se incumplió un plazo.
- **Conclusión:** grado de cumplimiento; no confundir actividad con avance científico.

Ambos formatos obedecen las mismas reglas: nada se declara cumplido sin evidencia; «implementado, no ejecutado» y «no verificado» se dicen expresamente.

El estado no se autodeclara como cumplido sin evidencia verificable. Las metas no son garantías de factibilidad; los bloqueos se registran y no se ocultan.

## Estado verificado tras EXP-003 (2026-11-11)

Evidencia: [research/EXP-003-golpes-indice-T.md](research/EXP-003-golpes-indice-T.md), [data/exp003_manifest.json](data/exp003_manifest.json), [research/EXP-003-results.json](research/EXP-003-results.json).

| Indicador (día 7) | Meta | Acumulado | Estado y salvedad |
|---|---|---|---|
| Bases investigadas | 5 | 5 | COW (EXP-002), Powell & Thyne, Polity IV, Maddison 2013, V-Dem. Las cuatro nuevas se leyeron de **una** fuente secundaria (AuthoritarianismBook); licencias originales **no verificadas** en origen. |
| Fuentes incorporadas | 3 | 4 | Leídas, con hash SHA-256 y commit fijado. |
| Variables explicativas nuevas | ≥6 | 7 | growth, loggdp, polity2, factional, polyarchy, execorr, coups_prev10. polyarchy y execorr están en el panel pero **no se usaron** en modelos. |
| Matriz país-año multivariable | 1 | 1 | 6.848 filas, 156 países, 1960–2011 efectivos. Cambios territoriales documentados solo parcialmente (duplicados URSS/Yugoslavia/Checoslovaquia). |
| Experimento histórico real | 1 | 1 (parcial) | Familia de eventos: 74 años-país con intento de golpe en la prueba. **La disolución de la URSS no fue evaluada**: el evento de 1991 en los datos es el intento de golpe de agosto. |
| Comparación con baselines | 1 | 1 | B0, B1, MH frente a MT y MX, con IC por bloques anuales. |
| Documentación | 100 % | 100 % de EXP-003 | Incluye resultado negativo: T no mejora el Brier de B0. |

Pendiente de corto plazo: experimento específico sobre disolución de Estados (URSS 1991) con controles, o registro formal del bloqueo; verificar licencias en las fuentes originales; comprobar la ganancia fuera de muestra de las interacciones (EXP-003 no la aísla). Mediano plazo: 5 de 10–15 conjuntos de datos; 0 de ≥30 episodios históricos codificados individualmente.

### Actualización 2026-11-14 (EXP-004)

Evidencia: [research/EXP-004-tendencia-temporal.md](research/EXP-004-tendencia-temporal.md). Los 7 indicadores no cambian (5/5 · 4/3 · 7/≥6 · 1/1 · 1/1 parcial · 1/1 · 100 %). Se agrega una segunda comparación con baselines: MX_c supera a B0 y a MH en Brier con IC que excluye cero, pero no a MH_c, y sobre una ventana de prueba ya conocida. Bloqueo registrado: la red de la sesión no permite descargar las fuentes actualizadas del issue #1 (www.uky.edu, dataverse.nl, www.rug.nl, api.worldbank.org, www.systemicpeace.org). Siguen pendientes la disolución de la URSS, la verificación de licencias en origen y el aporte aislado de las interacciones (issue #3).
