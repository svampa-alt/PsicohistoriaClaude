# EXP-012 — Panel de caídas por protesta popular o rebelión (paso de datos)

Fecha: 2026-11-26 · Estado: **panel construido; modelos no ejecutados**. La evaluación está [preregistrada](EXP-012-preregistro.md) (commit `dcf3933`) y queda para la próxima corrida.

## Nueva familia de eventos

Gobernantes que dejaron el cargo por **protesta popular** o **rebelión armada**, según Archigos (leído del paquete AuthoritarianismBook, en el commit fijado). Es distinta de los golpes militares que estudiaron EXP-003 a 011.

- **57 episodios desde 1960**, de los cuales **47 entran al panel** (46 años-país con evento).
- Entrenamiento 1960–1989: 18 años-país con evento. Prueba 1990–2014: 28.
- Quedan fuera por falta de datos de PIB o de V-Dem: Zanzibar 1964, Vietnam, Republic of 1964, Pakistan 1969, Yemen, People's Republic of 1978, Somalia 1991, Afghanistan 1992, Afghanistan 1996, Fiji 2000, Solomon Islands 2000, Solomon Islands 2006.

Con esto el laboratorio pasa de 3 a **50 episodios históricos individuales** codificados, contando las 3 disoluciones de EXP-008. La meta de mediano plazo es ≥30.

## Episodios en el panel

| Año | País | Gobernante | Causa |
|---|---|---|---|
| 1960 | Korea, Republic of | Rhee | protesta popular |
| 1963 | Congo | Youlou | protesta popular |
| 1964 | Sudan | Abboud | protesta popular |
| 1966 | Ecuador | Castro | protesta popular |
| 1970 | Poland | Gomulka | protesta popular |
| 1972 | Madagascar (Malagasy) | Tsiranana | protesta popular |
| 1973 | Thailand | Thanon Kittakachorn | protesta popular |
| 1975 | Laos | Souvanna Phouma | rebeldes (con apoyo extranjero) |
| 1975 | Cambodia (Kampuchea) | Lon Nol | rebeldes |
| 1975 | Comoros | Abdallah | rebeldes |
| 1979 | Nicaragua | Anastasio Somoza Debayle | rebeldes (con apoyo extranjero) |
| 1979 | Chad | Malloum | rebeldes (con apoyo extranjero) |
| 1979 | Iran (Persia) | Mohammad Reza | protesta popular |
| 1982 | Chad | Oueddei | rebeldes |
| 1986 | Philippines | Marcos | protesta popular |
| 1986 | Uganda | Okello | rebeldes |
| 1989 | Rumania | Ceausescu | protesta popular |
| 1989 | Lebanon | Moawad | rebeldes |
| 1990 | Bangladesh | Ershad | protesta popular |
| 1990 | Chad | Habre | rebeldes |
| 1990 | Haiti | Avril | protesta popular |
| 1990 | Liberia | Doe | rebeldes |
| 1991 | Ethiopia | Gebre Kidan | rebeldes |
| 1991 | Ethiopia | Mengistu Marriam | rebeldes |
| 1992 | Azerbaijan | Mutalibov | protesta popular |
| 1992 | Georgia | Gamsakhurdia | rebeldes |
| 1992 | Algeria | Boudiaf | rebeldes |
| 1992 | Tajikistan | Nabiyev | rebeldes |
| 1993 | Azerbaijan | Abulfaz Elchibey | rebeldes |
| 1997 | Congo | Lissouba | rebeldes (con apoyo extranjero) |
| 1997 | Congo, Democratic Republic of (Zaire) | Mobutu | rebeldes |
| 2000 | Cote D’Ivoire | Guei | protesta popular |
| 2000 | Ecuador | Mahuad | protesta popular |
| 2001 | Afghanistan | Mullah Omar | rebeldes (con apoyo extranjero) |
| 2003 | Central African Republic | Patasse | rebeldes |
| 2003 | Georgia | Shevardnadze | protesta popular |
| 2004 | Haiti | Aristide | rebeldes (con apoyo extranjero) |
| 2004 | Kyrgyz Republic | Akayev | protesta popular |
| 2006 | Nepal | Gyanendra | protesta popular |
| 2007 | Bangladesh | Iajuddin | protesta popular |
| 2007 | Georgia | Saakashvili | protesta popular |
| 2010 | Kyrgyz Republic | Bakiyev | protesta popular |
| 2011 | Tunisia | Zine Al-Abidine Ben Ali | protesta popular |
| 2011 | Libya | Qaddafi | rebeldes (con apoyo extranjero) |
| 2011 | Egypt | Mubarak | protesta popular |
| 2013 | Central African Republic | Francois Bozize | rebeldes |
| 2013 | Egypt | Morsi | protesta popular |

## Panel ([data/exp012_panel.csv](../data/exp012_panel.csv), [manifiesto](../data/exp012_manifest.json))

7521 filas, 1960–2014, sobre la base del panel de EXP-011. `outcome` es ahora el nuevo evento. El golpe queda en `coup_outcome`, y `rev_prev10` cuenta los años con evento en los 10 anteriores.

## Límites

- Archigos termina en 2014. Su licencia **no está verificada** en origen.
- La equivalencia Gleditsch-Ward→COW se hizo a mano en tres casos (Serbia, Yemen, Alemania).
- Pakistán 1969 queda fuera porque Polity usa un código distinto para el Pakistán anterior a 1971.
