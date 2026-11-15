# EXP-005 — Preregistro: confirmación sobre años nuevos con fuentes actualizadas

Fecha de registro: 2026-11-15 · Issues: #1 y #4 · Estado: **preespecificado, no ejecutado**. Este archivo se publica antes de construir el panel nuevo y antes de calcular cualquier predicción sobre los años de prueba.

## Por qué

EXP-004 mostró que la corrección de tasa base (MX_c) supera a B0 y a MH, pero sobre una ventana que ya conocíamos. Con fuentes actualizadas hay años que **ningún experimento evaluó**: EXP-003 terminó en 2011 porque el PIB de Maddison 2013 llegaba a 2010. Esos años son la confirmación genuina.

## Fuentes (originales, no intermediarios)

| Fuente | Versión | SHA-256 | Uso |
|---|---|---|---|
| Powell & Thyne, golpes | V2026.08.29 (`data/fuentes/`) | `1e8f933b22f4b9a77d0ba5eb59bf0d8158adcaab27746adcf345195be87a9012` | outcome y golpes previos |
| Maddison Project Database | 2023 (`mpd2023_web.xlsx`, dataverse.nl doi:10.34894/INZBF2) | `ecc5916ca12789b983fc4be437f8a354bbf4291323605324ac3e0aea4c57cbb6` | PIB per cápita y crecimiento |
| Polity5 | p5v2018 (systemicpeace.org) | `f81248561cb4fd884b0a439c7c0af298bc7f81b993bcd42e006988cb6d37a71c` | universo, polity2, polcomp |

## Panel (fijado antes de construirlo)

- Universo: filas país-año de Polity5 con año t entre 1960 y 2019 (Polity5 llega a 2018, así que t−1 ≤ 2018).
- Unión: P&T → Polity por `ccode_polity` si existe, si no `ccode`. Maddison (ISO3) → código Polity con tabla de equivalencias documentada en el código; los casos sin equivalencia se listan en el manifiesto.
- `growth_lag` = PIBpc(t−1)/PIBpc(t−2) − 1; `loggdp_lag` = log PIBpc(t−1). Se descarta la fila si falta alguno o falta polity2(t−1).
- P = 1 si `polcomp`(t−1) ∈ {6, 7, 8} (Factional/Restricted, Factional, Electoral Transition: Persistent Conflict). Equivalencia numérica verificada contra las etiquetas de la copia de EXP-003.
- E, I, T, `coups_prev10`: definiciones idénticas a EXP-003 (años con ≥1 intento en t−10..t−1).

## Diseño

- Entrenamiento 1960–1989 sobre el panel nuevo; coeficientes fijos después.
- Modelos: B0, MH, MT, MX (EXP-003) y MX_c, MH_c, MT_c (EXP-004, k = 10).
- **Conjunto confirmatorio: años 2012–2019** (solo filas que ningún experimento anterior evaluó).
- Secundario: 1990–2011 sobre el panel nuevo, para comparar con EXP-003/004 (no confirmatorio).
- Métricas: Brier, AUC, calibración en quintiles, IC 95 % del Δ Brier por bootstrap de bloques anuales (1.000 réplicas, semilla 20261111).

## Hipótesis (sobre 2012–2019)

- **C1:** Brier(MX_c) < Brier(B0), IC del Δ que excluye 0.
- **C2:** Brier(MX_c) < Brier(MH), IC que excluye 0.
- **C3:** Brier(MX_c) < Brier(MH_c), IC que excluye 0.
- Si C1 no se cumple, la ventaja de EXP-004 queda **no confirmada**. Se publica cualquiera sea el resultado.

## Limitaciones declaradas de antemano

- **Poca potencia:** 8 años y, probablemente, pocas decenas de eventos. Un IC que incluya 0 es el resultado más probable aunque el efecto exista.
- Cambio de escala del PIB (dólares de 2011 en vez de 1990 GK): los modelos se reentrenan sobre el panel nuevo, no se reutilizan coeficientes de EXP-003.
- Polity5 termina en 2018: 2020–2026 quedan fuera hasta reemplazar polity2/polcomp (issue #5).
- Sin pronósticos a futuro.
