# EXP-006 — Preregistro: V-Dem en lugar de Polity y prueba en 2020–2025

Fecha de registro: 2026-11-17 · Issue #5 (y #4) · Estado: **preespecificado, no ejecutado**. Se publica antes de construir el panel y antes de calcular cualquier predicción.

## Por qué

EXP-005 confirmó la corrección de tasa base en 2012–2019, pero Polity5 termina en 2018 y deja afuera 2020–2025, cuando la tasa de golpes **volvió a subir** (Sahel, Myanmar, Sudán, Gabón, Madagascar). Es la prueba más exigente posible para un modelo que aprendió que los golpes bajan: si la corrección de nivel reacciona tarde, debería perder.

## Fuentes

| Fuente | Versión | SHA-256 | Uso |
|---|---|---|---|
| V-Dem (paquete oficial `vdemdata`, github.com/vdeminstitute/vdemdata) | v16.0, datos 1789–2025 | `39b412d39a061c18f20c98e4ad4d6355b05a0441df31be4ee9aec420dc3d95ea` | P e I |
| Powell & Thyne | V2026.08.29 (en el repo) | `1e8f933b…a9012` | outcome, golpes previos |
| Maddison 2023 | mpd2023_web.xlsx | `ecc5916c…7cbb6` | PIB hasta 2022 |
| Banco Mundial, NY.GDP.PCAP.KD | API, descargado al construir | se registra en el manifiesto | crecimiento 2023–2024 |
| Polity5 | p5v2018 | `f8124856…7a71c` | **solo** para definir el universo de Estados |

Licencia del paquete `vdemdata`: GPL-3 (declarada en su DESCRIPTION); la licencia propia de los datos V-Dem **no verificada** en v-dem.net (host bloqueado).

## Variables (fijadas antes de mirar resultados)

- **Universo:** países-año de Polity5 entre 1960 y 2018; de 2019 a 2025, los países presentes en Polity5 en 2018. Los códigos Polity se traducen a COW con una tabla documentada en el código.
- **E:** idéntica a EXP-003, con crecimiento del PIBpc de Maddison 2023. Para t−1 = 2023 y 2024, crecimiento del Banco Mundial (NY.GDP.PCAP.KD), y nivel = Maddison 2022 encadenado con ese crecimiento.
- **P_v (polarización continua):** `clip((v2cacamps − q05) / (q95 − q05), 0, 1)`, con q05 y q95 calculados sobre las filas de entrenamiento 1960–1989 (un valor más alto es más polarización; verificado: Dinamarca −3,2, EE. UU. 2,0 en 2020).
- **I_v (fragilidad institucional):** `1 − |2·v2x_polyarchy − 1|`: máxima en regímenes intermedios (0,5), mínima en autocracias y democracias plenas. Reemplaza a polity2.
- **T_v = 0,40 E + 0,35 P_v + 0,25 I_v** (pesos de EXP-001, sin ajustar).
- Golpes previos, log PIB y rezagos: como en EXP-005. Todas las explicativas de la fila t son de t−1.
- Se descarta la fila si falta PIB, crecimiento, v2cacamps o v2x_polyarchy en t−1.

## Diseño

- Entrenamiento 1960–1989 del panel nuevo. Modelos: B0, MH, MT, MX y sus versiones corregidas MX_c, MT_c, MH_c (k = 10).
- **Confirmatorio: 2020–2025.**
- Secundario A: 2012–2019 con V-Dem, comparado contra EXP-005 con Polity (¿cambia algo sustituir Polity por V-Dem?).
- Secundario B: 2020–2023 solo (sin el empalme con el Banco Mundial).
- Métricas: Brier, AUC, calibración, IC 95 % del Δ Brier por bootstrap de bloques anuales (1.000 réplicas, semilla 20261111).

## Hipótesis (2020–2025)

- **D1:** Brier(MX_c) < Brier(B0), IC que excluye 0.
- **D2:** Brier(MX_c) < Brier(MH), IC que excluye 0.
- **D3:** Brier(MX_c) < Brier(MH_c), IC que excluye 0.
- **Predicción escrita de antemano:** con la tasa en alza, es plausible que la corrección (que mira 10 años atrás) **subestime** y pierda frente a B0. Si D1 falla, se informa como refutación en el período más reciente.

## Limitaciones declaradas

- Solo 6 años (6 bloques): intervalos poco confiables, y aún menos eventos que en EXP-005.
- V-Dem se codifica retrospectivamente por expertos: la información de 2024 sobre 2023 puede haber sido revisada después.
- El empalme Maddison–Banco Mundial cambia de fuente en los dos últimos años; el secundario B lo controla.
- Sin pronósticos a futuro.
