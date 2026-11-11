# Issues sugeridos tras EXP-003

Seis tareas concretas, ordenadas de más accesible a más exigente. Todas deben respetar [CONTRIBUTING.md](../CONTRIBUTING.md).

## 1. Actualizar los golpes de Estado a 2025
Etiquetas: `datos`, `good first issue`

El panel usa la copia de Powell & Thyne incluida en AuthoritarianismBook (hasta 2015) y el PIB de Maddison 2013 (hasta 2010), por lo que no hay pronósticos después de 2011. Tarea: incorporar la versión vigente de Powell & Thyne y una serie de PIB actualizada (p. ej. Maddison Project 2023), con URL, licencia y hashes, y extender la prueba. Los años nuevos son una prueba genuinamente fuera de muestra: no tocar la especificación de los modelos.

## 2. Graficar la tasa anual de golpes
Etiquetas: `good first issue`

La clave de EXP-003 es la caída de la tasa de 6,4 % (1960–1989) a 2,3 % (1990–2014). Tarea: un gráfico (SVG o script de biblioteca estándar) de la tasa anual observada 1960–2011 junto con la probabilidad media predicha por B0, MT y MX, a partir de `data/exp003_panel.csv` y `docs/exp003_demo.json`. Puede sumarse a la demo.

## 3. ¿Aportan algo las interacciones fuera de muestra?
Etiquetas: `modelo`

MX incluye E×I y P×I, pero EXP-003 no separa su aporte. Tarea: comparar MX contra el mismo modelo sin interacciones, sobre las mismas filas, con Δ Brier, ΔAUC e IC por bloques anuales. Preespecificar en el issue antes de ejecutar. La hoja de ruta exige comprobar la ganancia de las interacciones.

## 4. Tendencia temporal
Etiquetas: `modelo`

Los modelos sobreestiman porque no saben que la tasa base baja. Tarea: evaluar una variante con tendencia (año, o tasa global de los últimos k años, usando solo años anteriores) y ver si corrige la calibración sin perder AUC. Comparar con MT_expansivo y MX_expansivo. Declarar k antes de evaluar.

## 5. Polarización de V-Dem en lugar de P
Etiquetas: `modelo`, `datos`

P es un indicador binario de competencia «faccional» de Polity. Tarea: reemplazarlo por una medida continua de polarización de V-Dem (p. ej. `v2cacamps` o `v2smpolsoc`, que no están en el paquete actual: requiere incorporar V-Dem completo), reescalada a [0,1] con parámetros del entrenamiento, y repetir MT y MX. Documentar cobertura y faltantes.

## 6. Traducir la demo
Etiquetas: `good first issue`

«El Radiante» (`docs/_plantilla.html`) está solo en español y muestra los nombres de país de la fuente, en inglés. Tarea: agregar un selector ES/EN, traducir los textos y los nombres de país, sin dependencias externas y manteniendo la página autocontenida. Regenerar con `python src/exp003_model.py`.
