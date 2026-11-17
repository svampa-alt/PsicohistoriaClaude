# EXP-006 — Panel con V-Dem (paso de datos)

Fecha: 2026-11-17 · Issue #5 · Estado: **panel construido; modelos no ejecutados**. La evaluación está [preregistrada](EXP-006-preregistro.md) (commit `8f1e144`, anterior a este panel) y queda para la próxima corrida.

## Qué cambia respecto de EXP-005

- **I** pasa de polity2 a V-Dem: `I_v = 1 − |2·v2x_polyarchy − 1|`.
- **P** pasa de un indicador binario de Polity a la polarización continua de V-Dem (`v2cacamps`), reescalada con los cuantiles 5 % y 95 % del entrenamiento (q05 = -2.351, q95 = 2.237).
- **Cobertura hasta 2025.** El PIB de 2023 y 2024 se encadena con el crecimiento del Banco Mundial (312 país-años). Polity5 solo define qué países forman el universo.

## Panel ([data/exp006_panel.csv](../data/exp006_panel.csv), [manifiesto](../data/exp006_manifest.json))

**9248 filas, 345 años-país con intento de golpe, 163 países.**

| Período | Filas | Eventos | Rol |
|---|---|---|---|
| 1960–1989 | 3689 | 236 | entrenamiento |
| 1990–2011 | 3369 | 78 | — |
| 2012–2019 | 1256 | 14 | secundario A (comparación con EXP-005) |
| 2020–2023 | 628 | 12 | confirmatorio (y secundario B) |
| 2024–2025 | 306 | 5 | confirmatorio, con PIB del Banco Mundial |

Descartadas: 674 filas sin PIB en t−1 y 45 sin V-Dem en t−1; contenían 25 eventos.

La tasa observada en 2020–2025 es 1.8 %, contra 1.1 % en 2012–2019: los golpes volvieron a subir, como anticipaba el preregistro.

## Fuentes nuevas

- V-Dem v16 (datos 1789–2025), del paquete oficial `vdemdata` del V-Dem Institute (GitHub). El paquete declara licencia GPL-3; la licencia de los datos en v-dem.net **no se verificó** porque el host está bloqueado. Archivo no redistribuido.
- Banco Mundial, NY.GDP.PCAP.KD 2020–2024, API pública (los datos del Banco Mundial son CC BY 4.0 según su política general; **no verificado** en esta corrida). Archivo no redistribuido.

## Límites

- 2020–2025 tiene 17 eventos en 6 años: potencia todavía menor que en EXP-005.
- V-Dem se codifica retrospectivamente: los valores de t−1 pueden incluir revisiones posteriores a t.
- En 2024–2025 se mezclan dos fuentes de PIB; el secundario B (2020–2023) lo controla.
- Los países que nacieron después de 2018 no entran en el universo.

## Reproducir

```bash
pip install -r requirements-data.txt
curl -L -o _fuentes/vdem16/vdem.RData https://raw.githubusercontent.com/vdeminstitute/vdemdata/master/data/vdem.RData
curl -L -o _fuentes/worldbank/NY.GDP.PCAP.KD_2020_2024.json "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.KD?format=json&date=2020:2024&per_page=20000"
python src/exp006_build_panel.py   # requiere también las fuentes de EXP-005
```

El archivo del Banco Mundial cambia con cada actualización de la API: el hash del manifiesto identifica la versión usada.
