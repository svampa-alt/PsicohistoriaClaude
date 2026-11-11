# Cómo participar / How to contribute

*English below.*

## Español

Psicohistoria Lab es un proyecto recreativo y abierto. No hace falta ser especialista: hace falta respetar las reglas de juego.

### Reglas de juego

1. **Sin fuga de información futura.** Para predecir el año t solo se usa lo disponible hasta t−1. Si agregás una variable, decí de qué año es.
2. **Preespecificado ≠ exploratorio.** Lo que se decide antes de ver los resultados de prueba (corte, variables, hiperparámetros, semilla) es preespecificado. Todo lo demás se rotula «exploratorio» y no cuenta como evidencia.
3. **No inventar datos.** Cada fuente lleva URL, versión o commit, licencia y hash. Si falta un dato, se declara faltante.
4. **Siempre contra un baseline.** Un modelo nuevo se compara con B0 y MH sobre las mismas filas, con Brier, AUC e intervalo.
5. **Los resultados negativos se publican.** Un modelo que pierde contra el baseline es un aporte.
6. **Reproducible o no ocurrió.** Código en `src/`, pruebas sintéticas en `tests/`, informe en `research/`. `python -m unittest discover -s tests` tiene que pasar.
7. **Sin afirmaciones causales ni de «validación científica»** que los datos no sostengan. No usar esto para decisiones reales.
8. **No duplicar.** Antes de empezar, leé [HOJA-DE-RUTA.md](HOJA-DE-RUTA.md) y los experimentos existentes.

### Formas de aportar

- **Una fuente de datos**: abrí un issue con la plantilla «Nueva fuente».
- **Un modelo o variable**: abrí un issue con la plantilla «Nuevo modelo» antes de programar, así queda preespecificado.
- **Una crítica**: errores de método, de datos o de interpretación son bienvenidos como issue.
- **Ideas para empezar**: [research/ISSUES-SUGERIDOS.md](research/ISSUES-SUGERIDOS.md) y la etiqueta `good first issue`.

### Pull requests

Una rama por cambio, mensaje de commit claro, pruebas incluidas. El modelo y las pruebas usan solo la biblioteca estándar de Python; las dependencias de datos van en `requirements-data.txt`.

---

## English

Psicohistoria Lab is an open, recreational project. You don't need to be an expert; you need to play by the rules.

### Ground rules

1. **No future leakage.** Forecasts for year t use only information available up to t−1. State the year of every new variable.
2. **Pre-specified ≠ exploratory.** Anything decided before looking at test results (split, variables, hyperparameters, seed) is pre-specified. Everything else is labelled "exploratory" and is not evidence.
3. **No invented data.** Every source needs a URL, version or commit, licence and hash. Missing data is reported as missing.
4. **Always against a baseline.** New models are compared with B0 and MH on the same rows, with Brier, AUC and an interval.
5. **Negative results get published.** A model that loses to the baseline is a contribution.
6. **Reproducible or it didn't happen.** Code in `src/`, synthetic tests in `tests/`, write-up in `research/`. `python -m unittest discover -s tests` must pass.
7. **No causal or "scientifically validated" claims** the data cannot support. Do not use this for real-world decisions.
8. **Don't duplicate.** Read [HOJA-DE-RUTA.md](HOJA-DE-RUTA.md) and the existing experiments first.

### Ways to help

- **A data source**: open an issue with the "Nueva fuente" template.
- **A model or variable**: open an issue with the "Nuevo modelo" template before coding, so it is pre-specified.
- **A critique**: methodological, data or interpretation errors are welcome as issues.
- **Starter ideas**: [research/ISSUES-SUGERIDOS.md](research/ISSUES-SUGERIDOS.md) and the `good first issue` label.

Issues and pull requests are welcome in Spanish or English.
