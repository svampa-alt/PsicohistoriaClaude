# EXP-009 — Preregistro: recalibración más rápida del nivel (issue #4)

Fecha de registro: 2026-11-21 · Estado: **preespecificado, no ejecutado**. Se publica antes de calcular cualquier predicción de los modelos nuevos.

## Problema

EXP-006 mostró que la corrección de tasa base (tasa global de los 10 años previos) **subestima** cuando los golpes vuelven a subir: en 2021, MX_c predijo 1,1 % y hubo 3,8 %. La corrección mira solo la tasa global y reacciona con demora.

## Propuesta

**Recalibración del intercepto con los errores recientes del propio modelo.** Para cada año t:

1. Se toman las filas de los años t−5 a t−1, con la probabilidad cruda del modelo y el resultado observado (ambos conocidos antes de t).
2. Se estima un único desplazamiento `a_t` en escala logit, por máxima verosimilitud con ridge 1 (Newton), de modo que `σ(logit(p) + a_t)` ajuste esos resultados.
3. La predicción del año t es `σ(logit(p_t) + a_t)`.

A diferencia de la corrección de EXP-004, usa la composición real de países en riesgo y el error del modelo, no solo el cociente de tasas globales. Con 5 años debería reaccionar antes.

Modelo base: **MXs** (sin interacciones, el mejor según EXP-007), entrenado en 1960–1989 sobre `data/exp006_panel.csv` (V-Dem), sin cambios.

| Modelo | Nivel |
|---|---|
| MXs_c10 (referencia) | corrección de EXP-004, k = 10 |
| **MXs_r5** (principal) | recalibración del intercepto, últimos 5 años |
| MXs_c5 (secundario) | corrección de EXP-004, k = 5 |

MXs_c5 es secundario porque EXP-004 ya mostró, como exploratorio, que k = 5 rendía algo mejor: no sería una prueba limpia.

## Hipótesis (prueba 1990–2025, 36 bloques anuales)

- **K1 (primaria):** Brier(MXs_r5) < Brier(MXs_c10), IC 95 % del Δ (bootstrap de bloques anuales, 1.000 réplicas, semilla 20261111) que excluye 0.
- **K2:** Brier(MXs_r5) < Brier(B0) y < Brier(MH), con IC que excluye 0.
- **K3 (descriptiva):** en 2020–2025, la brecha |p̄ − tasa observada| de MXs_r5 es menor que la de MXs_c10.

## Límites declarados

- **Datos no vírgenes:** 1990–2025 se usó en EXP-004 a 007. El diseño nuevo no se probó nunca, pero se eligió conociendo el problema que esos datos revelaron. Un resultado favorable es evidencia débil hasta probarlo en años nuevos (2026 en adelante, cuando haya datos).
- La recalibración de 1990 usa 1985–1989, todavía dentro del entrenamiento: es legítimo (anterior a t) pero optimista para los primeros años.
- Sin pronósticos a futuro.

## Bloqueo registrado hoy

Se intentó ampliar las bases con UCDP (conflictos armados, otra familia de eventos): `ucdp.uu.se` y `ucdpapi.pcr.uu.se` están bloqueados por la red de la sesión, igual que `correlatesofwar.org`. Queda pendiente.
