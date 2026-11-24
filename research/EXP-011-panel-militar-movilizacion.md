# EXP-011 — Panel con poder militar y movilización masiva (paso de datos)

Fecha: 2026-11-24 · Estado: **panel construido; modelos no ejecutados**. La evaluación está [preregistrada](EXP-011-preregistro.md) (commit `9acd7f8`) y queda para la próxima corrida.

## Qué se agregó

Al panel V-Dem de EXP-006 se le suman dos variables de V-Dem v16, ambas de t−1:

- `mil_lag` = `v2x_ex_military`: cuánto depende el poder ejecutivo de los militares (0–1).
- `mob_lag` = `v2cagenmob` (movilización masiva) reescalado a [0, 1] con los cuantiles del entrenamiento (q05 = −2,435; q95 = 1,905). La versión sin reescalar queda en `mob_raw_lag`.

Es información de otro tipo que la ya usada: mide el papel de los militares y la protesta en la calle, dos mecanismos directos de un golpe. La fuente es la misma V-Dem v16 ya verificada (SHA-256 en [data/exp011_manifest.json](../data/exp011_manifest.json)); no hay archivos nuevos que redistribuir.

## Panel ([data/exp011_panel.csv](../data/exp011_panel.csv))

**9.240 filas y 345 eventos**: solo se pierden 8 filas (Afganistán, sin dato de movilización) y ningún evento.

| Período | Filas | Eventos |
|---|---|---|
| 1960–1989 | 3.689 | 236 |
| 1990–2019 | 4.617 | 92 |
| 2020–2025 | 934 | 17 |

## Límites

- El poder militar puede reflejar golpes ya ocurridos: se solapa con «golpes previos».
- V-Dem se codifica retrospectivamente.

## Reproducir

```bash
python src/exp011_build_panel.py   # requiere _fuentes/vdem16/vdem.RData (ver EXP-006)
```
