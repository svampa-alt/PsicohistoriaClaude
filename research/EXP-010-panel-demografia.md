# EXP-010 — Panel con población y urbanización (paso de datos)

Fecha: 2026-11-22 · Estado: **panel construido; modelos no ejecutados**. La evaluación está [preregistrada](EXP-010-preregistro.md) (commit `68eedfb`) y queda para la próxima corrida.

## Qué se agregó

Al panel V-Dem de EXP-006 se le suman dos variables demográficas del Banco Mundial, ambas de t−1:

- `lpop_lag`: logaritmo de la población total (`SP.POP.TOTL`).
- `urb_lag`: proporción de población urbana (`SP.URB.TOTL.IN.ZS` / 100).

Archivos de la API descargados el 2026-11-22 y no redistribuidos; hashes y URL en [data/exp010_manifest.json](../data/exp010_manifest.json). La inflación (`FP.CPI.TOTL.ZG`) también se descargó, pero se descartó antes de mirar resultados: solo 103 países tienen datos en los años sesenta.

## Panel ([data/exp010_panel.csv](../data/exp010_panel.csv))

**8.991 filas y 335 eventos** (EXP-006 tenía 9.248 y 345).

| Período | Filas | Eventos |
|---|---|---|
| 1960–1989 | 3.473 | 227 |
| 1990–2019 | 4.588 | 91 |
| 2020–2025 | 930 | 17 |

Se pierden 257 filas con 10 eventos:

- **1960** (100 filas): el Banco Mundial empieza en 1960, así que no hay dato de 1959.
- **Taiwán** (63): el Banco Mundial no lo publica.
- **URSS, Yugoslavia y Checoslovaquia** (94): no hay series de esos Estados como agregados.

Para la evaluación, todos los modelos (también B0, MH y MXs_c) se recalculan sobre estas mismas 8.991 filas, así que sus números no serán idénticos a los de EXP-006 y 007.

## Límites

- Población y urbanización se miden con método uniforme recién en décadas recientes; las primeras cifras son estimaciones del Banco Mundial y de la ONU.
- Licencia de los datos del Banco Mundial: CC BY 4.0 según su política general, **no verificada** en esta corrida.
- Perder la URSS, Yugoslavia y Checoslovaquia saca del panel casos con golpes relevantes (URSS 1991).

## Reproducir

```bash
for ind in SP.POP.TOTL SP.URB.TOTL.IN.ZS; do
  curl -L -o _fuentes/worldbank/$ind.json "https://api.worldbank.org/v2/country/all/indicator/$ind?format=json&date=1958:2024&per_page=20000"
done
python src/exp010_build_panel.py
```

La API cambia con cada actualización: el hash del manifiesto identifica la versión usada.
