# EXP-003 — ¿El índice T anticipa golpes de Estado?

Fecha: 2026-11-11 · Estado: **ejecutado** sobre datos reales · Resultado principal: **negativo para el índice T en calibración, positivo en ordenamiento**.

## 1. Pregunta

El índice de tensión colectiva de EXP-001, `T = 0.40 E + 0.35 P + 0.25 I`, con sus pesos ilustrativos **sin ajustar**, medido en el año t−1, ¿anticipa intentos de golpe de Estado en el año t mejor que baselines simples, fuera de muestra?

Familia de eventos: intentos de golpe (exitosos o fallidos). Controles negativos: todos los países-año del mismo panel sin intento.

## 2. Datos y licencias

Todas las tablas se leen del paquete R [AuthoritarianismBook](https://github.com/xmarquez/AuthoritarianismBook) de Xavier Márquez (licencia del paquete: GPL-3), fijado en el commit `51716224a08674b956a6434b0d18cd761311efde`. Es una **fuente secundaria**: los datos pertenecen a sus autores originales y deben citarse así.

| Tabla (.rda) | Fuente original | Uso | Cobertura en el archivo | Condiciones |
|---|---|---|---|---|
| `powell_thyne` | Powell & Thyne (2011), *Global Instances of Coups from 1950 to 2010*, JPR 48(2) | outcome, golpes previos | 1950–2015, 474 intentos | Uso académico con cita |
| `polity_annual` | Polity IV, Marshall, Gurr & Jaggers (Center for Systemic Peace) | universo, polity2, polcomp | hasta 2015 | Uso académico con cita; sin redistribución comercial |
| `economic_data` | Maddison Project (Bolt & van Zanden, 2013) | PIB per cápita y crecimiento | **hasta 2010** | Uso libre con cita |
| `vdem` | V-Dem (Coppedge et al.), versión incluida en el paquete | polyarchy, execorr | hasta 2015 | Uso libre con cita |

Los `.rda` no se redistribuyen: se clonan en `_fuentes/` (ignorado por git). El repositorio guarda el panel derivado ([data/exp003_panel.csv](../data/exp003_panel.csv), 6.848 filas) y el [manifiesto](../data/exp003_manifest.json) con los SHA-256 de cada `.rda` y del panel. Las licencias de las fuentes originales **no fueron verificadas en sus sitios oficiales** en esta ejecución; la columna «Condiciones» refleja su uso habitual declarado y queda como «no verificado».

## 3. Operacionalización

Unidad: país-año. Universo: filas de `polity_annual` con `in_system=True`, 1960–2014 (8.129). Unión por `country_name` + `year`.

- `outcome(t)` = 1 si hubo al menos un intento de golpe en t.
- Todas las explicativas son de **t−1**:
  - `growth_lag`: crecimiento del PIB per cápita (Maddison). `loggdp_lag`: log del nivel.
  - `polity2_lag`; `factional_lag` = 1 si `polcomp` es «Factional», «Factional/Restricted» o «Electoral Transition: Persistent Conflict/Coercion».
  - `polyarchy_lag`, `execorr_lag` (V-Dem): incluidas en el panel, **no usadas** en los modelos de este experimento.
  - `coups_prev10`: cantidad de años con al menos un intento en t−10..t−1 (misma unidad que el outcome).
- Índice (pesos de EXP-001, no estimados):
  - `E = clip(0.5 − growth/0.2, 0, 1)` · `P = factional` · `I = clip(1 − |polity2|/10, 0, 1)` · `T = 0.40E + 0.35P + 0.25I`.

Filas descartadas: 1.281 (1.115 sin PIB en t−1, 132 sin polity2 en t−1, 34 sin ambos); en ellas había 34 años-país con golpe. Panel final: **6.848 filas, 310 eventos, 156 países**.

## 4. Diseño

**Preespecificado** (fijado antes de evaluar):

- Corte temporal: entrenamiento 1960–1989 (3.673 obs, 236 eventos), prueba 1990–2014 (3.175 obs, 74 eventos). Todos los modelos sobre las mismas filas.
- B0: tasa histórica global expansiva. B1: tasa por país contraída hacia la global (strength=5). Ambos reutilizados de `src/psicohistoria.py`.
- MT: logística sobre T. MH: logística sobre `coups_prev10`. MX: logística sobre E, P, I, `loggdp_lag`, `coups_prev10`, E×I, P×I.
- Logística por Newton con ridge=1; variables estandarizadas con media y desvío del entrenamiento.
- Métricas: Brier, skill vs B0, AUC, calibración en 5 quintiles, IC 95 % del Δ Brier vs B0 por bootstrap de bloques anuales (1.000 réplicas, semilla 20261111).

**Exploratorio** (no cuenta como prueba): `MT_expansivo` y `MX_expansivo`, reajustados en cada año de prueba con todos los años anteriores; y la sensibilidad a PIB duplicado (§7).

## 5. Resultados (prueba, 3.175 obs, 74 eventos)

| Modelo | Tipo | Brier | Skill vs B0 | AUC | IC 95 % Δ Brier vs B0 |
|---|---|---|---|---|---|
| B0 | preespecificado | 0,02370 | — | 0,640 | — |
| B1 | preespecificado | 0,02469 | −4,2 % | 0,774 | [+0,00026; +0,00178] |
| MT | preespecificado | 0,02607 | −10,0 % | 0,740 | [+0,00148; +0,00325] |
| **MH** | preespecificado | **0,02313** | **+2,4 %** | 0,687 | **[−0,00096; −0,00019]** |
| MX | preespecificado | 0,02446 | −3,2 % | **0,801** | [−0,00038; +0,00194] |
| MT_expansivo | *exploratorio* | 0,02408 | −1,6 % | 0,756 | [−0,00017; +0,00103] |
| MX_expansivo | *exploratorio* | 0,02339 | +1,3 % | 0,815 | [−0,00125; +0,00070] |

Valores completos, coeficientes y calibración: [EXP-003-results.json](EXP-003-results.json).

## 6. Interpretación

1. **T ordena bien el riesgo.** Con pesos que nadie ajustó, MT alcanza AUC 0,740; agregar PIB, historia e interacciones (MX) lo lleva a 0,801. Los países-año que el índice señala son, en promedio, donde más golpes hubo.
2. **Pero sobreestima después de 1990.** La tasa de golpes cayó de 6,4 % (1960–1989) a 2,3 % (1990–2014). Un modelo ajustado en el primer período predice en promedio 7,7 % (MT) o 5,7 % (MX) cuando lo observado es 2,3 %. En su quintil más alto MT predice 16,0 % y se observa 5,5 %. Por eso su Brier es **peor** que el de B0, y el intervalo de MT excluye el cero del lado malo.
3. **El único modelo cuyo intervalo excluye el cero a favor es MH**, que solo cuenta golpes recientes. La mejora es pequeña (2,4 %).
4. **Las interacciones no demostraron ganancia.** MX mejora el AUC pero no el Brier; el experimento no separa el aporte de E×I y P×I del de las demás variables (pendiente, ver issues).
5. Las variantes expansivas se acercan a B0 porque van absorbiendo la caída de la tasa; es coherente con el diagnóstico de calibración, pero es **exploratorio**.

Nada de esto es causal ni valida la psicohistoria. Es una asociación predictiva en un panel con sesgos conocidos.

## 7. Caso URSS 1991

En `powell_thyne`, «Russia (Soviet Union)» tiene outcome=1 en 1991. **Ese evento es el intento de golpe de agosto de 1991 contra Gorbachov, no la disolución de la URSS** (diciembre de 1991). EXP-003 no pronostica disoluciones de Estados; la meta de la hoja de ruta sobre la disolución sigue pendiente.

Pronóstico para 1991 con datos de 1990: T=0,65; MT=14,1 % (puesto 15 de 131); MX=6,5 % (puesto 44 de 131); B0=6,3 %. MT lo ubicó en el 12 % superior; MX, apenas sobre la tasa base, porque la URSS no tenía golpes previos ni competencia «faccional».

**Advertencia sobre este caso.** Maddison trae dos series superpuestas bajo «Russia (Soviet Union)» desde 1990 (ex URSS y Federación Rusa) y el crecimiento que publica el paquete está calculado entre filas intercaladas: para 1990 figura −12,1 % o +9,0 % según la fila. La regla fija del constructor (conservar la última fila) toma −12,1 %, lo que da E=1. Con los niveles de la propia fuente para la serie continua de la ex URSS (7.112 → 6.894) el crecimiento sería ≈ −3,1 %, E≈0,66 y T≈0,51 en vez de 0,65. El T de la URSS en 1991 está, entonces, **inflado por un defecto de la fuente**. Lo mismo afecta a Yugoslavia y Checoslovaquia: 71 filas en total, marcadas con `gdp_lag_duplicado=1`.

Sensibilidad (exploratoria): excluyendo esas 71 filas, las conclusiones no cambian — B0 0,02371; MT 0,02603 (AUC 0,741); MH 0,02312, con IC [−0,00099; −0,00020]; MX 0,02444 (AUC 0,802).

## 8. Límites

- **El PIB termina en 2010**: no hay filas de 2012–2014. La prueba «1990–2014» cubre de hecho **1990–2011** (2010 y 2011 con ~112 países en vez de ~150).
- **Sesgo por datos faltantes**: se descartó el 15,8 % del universo, con 34 años-país con golpe. Los países sin PIB suelen ser pobres, nuevos o en conflicto: justo donde hay más golpes.
- **P es binario** y proviene de la misma codificación Polity que I; no mide polarización social.
- **Fuentes hasta 2015** y versiones antiguas (Polity IV, Maddison 2013, V-Dem de la época). Las revisiones posteriores pueden cambiar valores.
- **Disponibilidad ex ante**: se usan valores de t−1 tal como se publicaron años después. Polity y V-Dem se codifican retrospectivamente; no es un pronóstico ex ante estricto.
- Nombres y fronteras siguen la codificación del paquete (Gleditsch-Ward); los Estados sucesores heredan series de forma imperfecta (§7).
- Un solo corte temporal; la incertidumbre del bootstrap por años no cubre dependencia entre países.
- `coups_prev10` cuenta años con intento, no intentos. Contar intentos da MH=0,02329 y MX AUC=0,803; la conclusión es la misma.

## 9. Cómo reproducirlo

```bash
# 1) Solo modelo, pruebas y demo (biblioteca estándar, usa el panel versionado)
python -m unittest discover -s tests
python src/exp003_model.py

# 2) Reconstruir el panel desde la fuente
pip install -r requirements-data.txt
git clone https://github.com/xmarquez/AuthoritarianismBook.git _fuentes/AuthoritarianismBook
git -C _fuentes/AuthoritarianismBook checkout 51716224a08674b956a6434b0d18cd761311efde
python src/exp003_build_panel.py     # verifica el commit, escribe panel y manifiesto
python src/exp003_model.py
```

Valores de control: 6.848 filas, 310 eventos; prueba 3.175 obs y 74 eventos; Brier B0 0,02370, MH 0,02313, MT 0,02607; AUC MT 0,740, MX 0,801. SHA-256 del panel en `data/exp003_manifest.json`.

Artefactos: `src/exp003_build_panel.py`, `src/exp003_model.py`, `tests/test_exp003.py`, `research/EXP-003-results.json`, `docs/exp003_demo.json`, `docs/index.html` (generado desde `docs/_plantilla.html`).
