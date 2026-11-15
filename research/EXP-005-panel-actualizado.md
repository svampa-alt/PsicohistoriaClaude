# EXP-005 — Panel actualizado (paso de datos)

Fecha: 2026-11-15 · Issue #1 · Estado: **panel construido y verificado; modelos no ejecutados**. La evaluación confirmatoria está [preregistrada](EXP-005-preregistro.md) (commit `9aa2763`, anterior a la construcción del panel) y queda para la próxima corrida.

## Qué cambia respecto de EXP-003

| | EXP-003 | EXP-005 |
|---|---|---|
| Golpes | Powell & Thyne V2015 (vía AuthoritarianismBook) | **Powell & Thyne V2026.08.29**, original |
| PIB | Maddison 2013, hasta 2010 | **Maddison 2023**, hasta 2022 |
| Régimen | Polity IV (paquete de 2015) | **Polity5** p5v2018, hasta 2018 |
| Unión | nombre de país | **código Polity** + tabla ISO3 documentada |
| Años con dato | 1960–2011 | **1960–2019** |

Todas las fuentes se leen de su origen oficial, con SHA-256 en [data/exp005_manifest.json](../data/exp005_manifest.json). El problema de PIB duplicado de URSS/Yugoslavia/Checoslovaquia de EXP-003 desaparece: Maddison 2023 trae series propias (SUN, YUG, CSK) y la unión es por código.

## Panel

- **8197 filas, 327 años-país con intento de golpe, 163 países** ([data/exp005_panel.csv](../data/exp005_panel.csv)).
- 1960–1989: 3649 filas, 233 eventos · 1990–2011: 3303 filas, 80 eventos · **2012–2019: 1245 filas, 14 eventos** (el conjunto confirmatorio nunca evaluado).
- Descartadas: 584 sin PIB en t−1, 162 sin polity2 en t−1, 22 sin ambos; contenían 26 años-país con golpe. EXP-003 descartaba 1.281 filas; ahora 768.
- Países sin serie de PIB comparable: Guyana (110), Suriname (115), Germany West (260), Germany East (265), Serbia and Montenegro (347), Yugoslavia (347), Somalia (520), South Sudan (525), Eritrea (531), Yemen North (678), Yemen South (680), Bhutan (760), Pakistan (769), South Vietnam (817), Timor Leste (860), Papua New Guinea (910), Solomon Islands (940), Fiji (950).
- Intentos de golpe en microestados que Polity5 no cubre (Dominica, Granada, Santo Tomé, Seychelles, Maldivas): 7, fuera del panel.
- 2019 no está en Polity5: un país entra en 2019 si estaba en 2018 (todas sus explicativas son de 2018).

## Control contra el panel de EXP-003 ([data/exp005_control.json](../data/exp005_control.json))

Sobre 6640 países-año comunes (1960–2011):

| Variable | Coincidencia |
|---|---|
| outcome (golpe sí/no) | 6635 de 6640; las 5 diferencias son fechas corregidas por Powell & Thyne |
| polity2 en t−1 | 5901 iguales (89 %): revisiones de Polity5 |
| P (faccional) | 6491 iguales (98 %) |
| log PIB en t−1 | correlación 0.983 |
| crecimiento en t−1 | correlación 0.752 |
| índice T | correlación 0.926 |

El crecimiento es lo que más cambia (0,75): Maddison 2023 revisó a fondo las series y cambió de base de precios. Como E depende del crecimiento, **el índice T de EXP-005 no es idéntico al de EXP-003** (correlación 0,93). Por eso el preregistro reentrena todos los modelos sobre el panel nuevo.

## Límites

- Confirmatorio con solo 14 eventos en 8 años: poca potencia, declarada de antemano.
- Polity5 se discontinuó en 2018; 2020–2026 (incluidos los golpes del Sahel) siguen fuera hasta sustituir polity2 y polcomp (issue #5).
- Licencia de Powell & Thyne no verificada (redistribución aprobada por el usuario); Maddison 2023 es CC BY 4.0 según dataverse.nl **(no verificado en esta corrida)**; Polity5 permite uso académico con cita **(no verificado)**. Maddison y Polity no se redistribuyen: se descargan con el script.
- Codificación retrospectiva de Polity y revisiones del PIB: no es información estrictamente disponible en t−1.

## Reproducir

```bash
pip install -r requirements-data.txt
curl -L -o _fuentes/maddison2023/mpd2023_web.xlsx https://dataverse.nl/api/access/datafile/421302
curl -L -o _fuentes/polity5/p5v2018.xls https://www.systemicpeace.org/inscr/p5v2018.xls
python src/exp005_build_panel.py    # verificá los SHA-256 contra el manifiesto
python src/exp005_control.py        # opcional, requiere la fuente de EXP-003
```
