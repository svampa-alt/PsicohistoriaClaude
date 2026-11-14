# Psicohistoria Lab

> **In English.** An open, recreational lab that tests whether simple mathematical models can anticipate real historical events better than naive baselines — inspired by the fictional psychohistory of Asimov's *Foundation*. Latest result (EXP-003): a hand-weighted "collective tension" index ranks coup risk well out of sample (AUC 0.74; 0.80 with extra variables) but is badly calibrated after 1990, so it does **not** beat the historical base rate on Brier score. Only a "recent coups" count does, slightly. Negative results are published as they are. **[Live demo: El Radiante](https://svampa-alt.github.io/PsicohistoriaClaude/)** · [How to contribute](CONTRIBUTING.md)

**Un laboratorio abierto de exploración matemática de la historia y del comportamiento colectivo, inspirado en la psicohistoria ficticia de la saga *Fundación* de Isaac Asimov.**

## Último hallazgo

**EXP-003 (2026-11-11): el índice T ordena bien el riesgo de golpe de Estado, pero no le gana a la tasa histórica.** Con los pesos de EXP-001 sin ajustar, entrenando con 1960–1989 y pronosticando desde 1990 (3.175 países-año, 74 con intento de golpe):

| Modelo | Brier | vs B0 | AUC |
|---|---|---|---|
| B0 · tasa histórica | 0,02370 | — | 0,640 |
| MH · golpes en los 10 años previos | **0,02313** | **+2,4 %** (IC excluye 0) | 0,687 |
| MT · logística sobre T | 0,02607 | −10,0 % | 0,740 |
| MX · E, P, I, PIB, historia e interacciones | 0,02446 | −3,2 % | **0,801** |

T discrimina (AUC 0,74) pero sobreestima: los golpes cayeron de 6,4 % a 2,3 % de los países por año después de 1990. Es un **resultado negativo en calibración** y no valida la psicohistoria. Salvedades importantes: el PIB termina en 2010 (prueba efectiva 1990–2011) y el evento «URSS 1991» es el intento de golpe, no la disolución.

**Novedad, EXP-004 (2026-11-14):** corrigiendo solo el nivel con la tasa de golpes de los 10 años previos, MX pasa a Brier 0,02227 y supera a B0 y a MH con intervalos que excluyen cero. Pero la misma corrección sobre el modelo de «golpes previos» rinde casi igual: el mérito es de la tasa base, y no está demostrado que el índice aporte precisión extra. La prueba ya era conocida, así que es evidencia débil. [Informe EXP-004](research/EXP-004-tendencia-temporal.md).

→ [Demo interactiva «El Radiante»](https://svampa-alt.github.io/PsicohistoriaClaude/) · [Informe completo](research/EXP-003-golpes-indice-T.md) · [Resultados JSON](research/EXP-003-results.json)

## Empezar en 2 minutos

```bash
git clone https://github.com/svampa-alt/PsicohistoriaClaude.git
cd PsicohistoriaClaude
python -m unittest discover -s tests     # solo biblioteca estándar, Python 3.9+
python src/exp003_model.py               # reproduce la tabla y regenera docs/index.html
```

El panel ya está en `data/exp003_panel.csv`. Para reconstruirlo desde las fuentes (requiere `pyreadr`), ver [el informe](research/EXP-003-golpes-indice-T.md#9-cómo-reproducirlo).

## Cómo participar

- Leé las [reglas de juego](CONTRIBUTING.md): sin fuga de información futura, preespecificado separado de exploratorio, sin datos inventados.
- Elegí una tarea de [research/ISSUES-SUGERIDOS.md](research/ISSUES-SUGERIDOS.md) o de los issues con etiqueta `good first issue`.
- Proponé una [fuente de datos](.github/ISSUE_TEMPLATE/nueva-fuente.md) o un [modelo](.github/ISSUE_TEMPLATE/nuevo-modelo.md) con las plantillas de issue.
- Las metas y el estado verificado están en [HOJA-DE-RUTA.md](HOJA-DE-RUTA.md).

## Objetivo

Explorar, con fines **lúdicos, intelectuales y educativos**, si es posible identificar regularidades estadísticas en la evolución de sociedades humanas y construir modelos matemáticos que describan o anticipen, de forma probabilística y limitada, algunos cambios colectivos.

No pretendemos haber descubierto leyes deterministas de la historia, ni presentar la psicohistoria de ficción como una ciencia establecida. El proyecto es una investigación recreacional abierta a hipótesis refutables, simulaciones, datos históricos, experimentos reproducibles y resultados negativos.

## Principios

- **Curiosidad y rigor:** separar observaciones, supuestos, simulaciones e inferencias.
- **Reproducibilidad:** documentar fuentes, ecuaciones, parámetros, código y resultados.
- **Validación:** contrastar modelos con referencias simples y datos fuera de muestra antes de atribuirles capacidad predictiva.
- **Transparencia:** conservar errores, limitaciones, resultados negativos y correcciones.
- **Persistencia sin duplicación:** un registro canónico por experimento, identificadores estables y actualizaciones trazables mediante commits.
- **Uso responsable:** no utilizar modelos exploratorios como fundamento suficiente para decisiones de alto impacto ni para manipular poblaciones.

## Primer modelo experimental (EXP-001)

Definimos un índice hipotético de tensión colectiva:

```text
T = 0.40 E + 0.35 P + 0.25 I
```

donde E representa tensión económica, P polarización y I fragilidad institucional, normalizadas entre 0 y 1.

Una dinámica inicial de simulación:

```text
T[t+1] = clip(T[t] + alpha*S[t] - beta*R[t], 0, 1)
```

S representa shocks y R capacidad de recuperación. **Los pesos y parámetros son ilustrativos; no han sido estimados ni validados con datos reales.**

Ejemplo simulado: E=0.65, P=0.70, I=0.40 produce T=0.605. Con alpha=0.30, S=0.40, beta=0.20 y R=0.25, el siguiente valor es T=0.675. No constituye una predicción histórica.

## Registro y continuidad

Este repositorio es la fuente de referencia para documentación, datos, experimentos y código. Cada nuevo avance debe revisar el estado existente antes de crear archivos o repetir pruebas. Identificaremos experimentos como `EXP-001`, `EXP-002`, etc., y distinguiremos expresamente **propuesto / implementado / ejecutado / validado**.

El primer avance es conceptual y simulado; la siguiente etapa es operacionalizar variables con datos históricos verificables, definir líneas base y construir pruebas retrospectivas sin fuga de información futura.

## Colaboraciones bienvenidas

**Toda colaboración, fork, propuesta, crítica constructiva o retroalimentación es bienvenida**, siempre que aporte positivamente al proyecto. Nos interesan especialmente las contribuciones que mejoren la calidad de los datos, las formulaciones matemáticas, la reproducibilidad, la validación y la claridad de las conclusiones.

Se puede participar abriendo un *issue*, proponiendo cambios mediante *pull requests*, compartiendo experimentos o creando un *fork* con enfoques alternativos. Las contribuciones se evaluarán por su fundamento y utilidad, no por confirmar nuestras hipótesis.

## Inspiración y alcance

Inspirado en la obra literaria de Isaac Asimov, sin afiliación con sus titulares de derechos. El repositorio no reproduce el texto de las novelas. El proyecto no tiene fines comerciales definidos: su propósito actual es recreacional, intelectual y de aprendizaje colectivo.

## Estado

- EXP-001: formulación matemática inicial y ejemplos simulados; **sin validación empírica**.
- EXP-002: **implementado parcialmente** — lector CSV entidad-año, baselines B0 (tasa histórica global) y B1 (tasa por entidad contraída hacia la global), cálculo Brier y pruebas unitarias; [protocolo de variables y evaluación](research/EXP-002-plan.md). **Sin datos históricos incorporados ni validación empírica**. [Avance 002-B: ecuaciones, pruebas y contraste sintético negativo](research/EXP-002-plan.md#avance-diario-002-b-baseline-por-entidad-2026-11-07). Pruebas automáticas: [ejecución satisfactoria](https://github.com/svampa-alt/Psicohistoria-lab/actions/runs/42207584555).

- EXP-002-C (2026-11-08): puerta de calidad de cobertura explícita en [`src/coverage.py`](src/coverage.py), dos pruebas nuevas y selección documental de COW guerras interestatales v4.0 + membresía estatal como fuentes candidatas. [Protocolo y límites](research/EXP-002-plan.md#avance-diario-002-c-cobertura-explicita-y-seleccion-de-fuente-2026-11-08). **No se descargaron datos reales ni se validaron modelos históricos.**

- EXP-002-D (2026-11-09): [adaptador local COW](src/cow_adapter.py), [pruebas sintéticas](tests/test_cow_adapter.py) y [registro de supuestos y límites](research/EXP-002-plan.md#avance-diario-002-d-adaptador-cow-y-prueba-temporal-sintetica-2026-11-09). **Aún sin datos históricos incorporados, ni validación empírica.**

Los avances futuros deben conservar un historial auditable y evitar duplicar experimentos o repositorios.

- EXP-002-E (2026-11-10): [comparación pareada B0/B1](src/compare_baselines.py), [pruebas sintéticas](tests/test_compare_baselines.py) y [protocolo con bootstrap anual](research/EXP-002-plan.md#avance-diario-002-e-contraste-pareado-reproducible-2026-11-10). **Código implementado; sin datos históricos procesados ni capacidad predictiva validada.** La reconciliación de episodios COW continúa pendiente.

- EXP-002-F (2026-11-10): [ejemplo práctico mínimo y reproducible](research/EXP-002-F-ejemplo-practico.md) con dos entidades sintéticas y corte temporal 2002. Brier B0=0.25, B1=0.0625 con strength=2 **calculados analíticamente**; no son resultados históricos ni validación empírica. No se alteró el modelo EXP-001.

- EXP-002-G (2026-11-10): [descarga reproducible de fuentes oficiales COW](src/cow_official_run.py) y [pruebas del ZIP](tests/test_cow_official_run.py). Genera hashes, audita el panel y ejecuta B0/B1 solo si el adaptador admite los archivos; registra bloqueos. **Aún no se ejecutó sobre datos históricos reales ni existe validación predictiva.** [Protocolo](research/EXP-002-plan.md#avance-002-g--primer-camino-ejecutable-hacia-un-contraste-historico-real-2026-11-10).

- EXP-002-H (2026-11-10): [primer contraste histórico real con COW](research/EXP-002-H-primer-contraste-historico.md): 8.485 Estado-años de prueba (1950–2007), 133 eventos; Brier B0=0,0155789940, B1=0,0155668684. La diferencia es ínfima y su intervalo descriptivo incluye cero; **no se demostró ventaja predictiva robusta**. Los reingresos y episodios secundarios siguen pendientes de auditoría. Se corrigieron los encabezados reales del adaptador.

- EXP-002-I (2026-11-11): [sensibilidad a StartYear2](research/EXP-002-I-sensibilidad-segundos-episodios.md), con [código reproducible](src/cow_second_onset_sensitivity.py) y [resultados JSON](research/EXP-002-I-results.json). Los 19 segundos episodios válidos agregan 5 Estado-años positivos, todos antes de 1950. Test 1950–2007: 8.485 observaciones, 133 eventos; Brier B0=0,0155926964 y B1=0,0155782024 con ambos episodios. **No hay ventaja predictiva robusta demostrada ni validación de EXP-001**. Datos COW originales no incorporados al repositorio.

- EXP-003 (2026-11-11): [índice T frente a golpes de Estado](research/EXP-003-golpes-indice-T.md) — **ejecutado sobre datos reales** (Powell & Thyne, Polity IV, Maddison 2013, V-Dem; 6.848 países-año, 310 eventos). Corte preespecificado 1960–1989 / 1990–2014 (efectivo hasta 2011). Brier B0=0,02370, MH=0,02313, MT=0,02607, MX=0,02446; AUC MT=0,740, MX=0,801. **T discrimina pero no mejora el Brier de B0; solo MH tiene IC que excluye cero.** Variantes expansivas marcadas como exploratorias. [Código](src/exp003_model.py), [panel](data/exp003_panel.csv), [manifiesto con hashes](data/exp003_manifest.json), [pruebas](tests/test_exp003.py), [demo](https://svampa-alt.github.io/PsicohistoriaClaude/). Sin validación causal ni de EXP-001.

- EXP-004 (2026-11-14): [corrección de tasa base](research/EXP-004-tendencia-temporal.md) — **ejecutado**, con [preregistro](research/EXP-004-preregistro.md) previo. MX_c: Brier 0,02227 (+6,0 % vs B0), AUC 0,807; IC vs B0 [−0,00199; −0,00084] y vs MH [−0,00127; −0,00044]. **H3 no cumplida:** MX_c no supera de forma demostrable a MH_c (0,02237). Ventana de prueba ya conocida por EXP-003: evidencia débil, pendiente de confirmar con años nuevos. [Código](src/exp004_tendencia.py), [pruebas](tests/test_exp004.py), [resultados](research/EXP-004-results.json).
