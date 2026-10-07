# Modelo nulo de dilución para la pérdida de cuota de instalaciones

Generado por `src/analyze/16_dilucion_modelo_nulo.py`. No editar a mano. Diseño en el docstring del script.

- Plugins con ≥24 meses de serie: N = 2145; pierden cuota (métrica de 05): 91,9%.
- Total del ecosistema: 26.751 (sep 2012) → 1.229.754 (ago 2026), ×46,0.
- Semillas: 20261004 (A4, 200 réplicas), 20261005 (B1, 1000 permutaciones), 20261006 (sensibilidad, 1000 permutaciones).

## A. ¿De dónde sale el 91,9%? (misma métrica, mismos plugins)

| escenario | % de plugins con diferencia negativa |
|:--|--:|
| A0 observado | 91,9% |
| A1 cada plugin crece al ritmo del total (cuota constante, analítico) | 0,0% |
| A2 instalaciones congeladas en su nivel de pico (solo crece el denominador) | 95,4% |
| A3 cuota sobre su cohorte de entrada y anteriores (sin dilución por entrantes) | 88,2% |
| A4 serie de cuota permutada en el tiempo (solo artefacto de selección del pico) | 57,0% [54,7%; 59,1%] |
| A4 sobre la cuota de cohorte de A3 | 56,9% [55,0%; 59,2%] |

### Descomposición del crecimiento del total (A5)

- Base: media mensual sep 2012 – ago 2013 = 55.905; reciente: media de los últimos 12 meses = 1.186.601 (×21,2).
- Incumbentes (algún reporte en la ventana base): 716 plugins; aportan 393.717 (34,8%) del crecimiento neto.
- Entrantes posteriores: 2102 plugins activos hoy; aportan 736.978 (65,2%) del crecimiento neto y suponen el 62,1% del total actual.
- Plugins con <24 meses de serie (fuera de N, dentro del denominador): 2,4% del total actual y 2,5% del crecimiento neto.
- Plugins activos en los últimos 12 meses: 2776.

## B. Concentración del crecimiento absoluto

### B principal: N = 2.145, historia propia (primeros 12 meses frente a últimos 12)

- Ganancia neta total: 1.002.070 instalaciones; plugins con ganancia positiva: 73,2%; plugins que multiplican por ≥10: 23,8%.
- Tasa anualizada común del nulo proporcional: r* = 0,1980 (×1,219 por año).
- Spearman(log tamaño inicial, tasa anualizada) = −0,120.
- Top 1% (22 plugins) por ganancia absoluta: mod_customcert, mod_hvp, theme_moove, mod_attendance, format_tiles, block_completion_progress, block_configurable_reports, mod_questionnaire, local_mailtest, block_xp, theme_academi, mod_zoom, format_onetopic, tool_certificate, auth_oidc, format_remuiformat, mod_coursecertificate, booktool_wordimport, mod_game, mod_checklist, theme_boost_union, mod_choicegroup.

| métrica | observado | nulo proporcional (B0) | nulo Gibrat (B1): mediana [IC 95%] | p (más concentrado que B1) | p (menos concentrado que B1) |
|:--|--:|--:|--:|--:|--:|
| ganancia neta captada por el top 1% | 29,9% | 20,4% | 81,1% [64,6%; 93,6%] | 1,000 | 0,001 |
| ganancia neta captada por el top 5% | 62,0% | 53,0% | 94,0% [88,3%; 98,0%] | 1,000 | 0,001 |
| ganancia neta captada por el top 10% | 78,8% | 68,2% | 97,1% [94,4%; 99,1%] | 1,000 | 0,001 |
| fracción mínima de plugins con el 50% de la ganancia | 3,1% | 4,4% | 0,2% [0,0%; 0,5%] | 1,000 | 0,001 |
| Gini de la ganancia absoluta | 0,920 | 0,790 | 0,979 [0,963; 0,993] | 1,000 | 0,001 |

### Sensibilidad: cohorte fija con reporte en los 12 meses 09/2012 – 08/2013

- 413 plugins; factor agregado de la cohorte ×6,31; con ganancia positiva: 59,6%; ganancia neta total: 273.922; Spearman(log tamaño base, factor) = +0,011.
- Factor del ecosistema completo en las mismas ventanas: ×21,2; plugins de la cohorte que crecen al menos ese factor: 15,5%; factor de los plugins: mediana ×1,75, percentil 90 ×29,13, percentil 99 ×487,5.

| métrica | observado | nulo proporcional (B0) | nulo Gibrat (B1): mediana [IC 95%] | p (más concentrado que B1) | p (menos concentrado que B1) |
|:--|--:|--:|--:|--:|--:|
| ganancia neta captada por el top 1% | 19,6% | 18,9% | 60,1% [38,3%; 83,6%] | 1,000 | 0,001 |
| ganancia neta captada por el top 5% | 49,7% | 41,3% | 85,8% [74,1%; 94,8%] | 1,000 | 0,001 |
| ganancia neta captada por el top 10% | 70,1% | 57,1% | 94,0% [88,4%; 97,7%] | 1,000 | 0,001 |
| fracción mínima de plugins con el 50% de la ganancia | 5,3% | 7,7% | 1,0% [0,2%; 2,2%] | 1,000 | 0,001 |
| Gini de la ganancia absoluta | 0,899 | 0,690 | 0,973 [0,950; 0,990] | 1,000 | 0,001 |
| plugins que crecen menos que el agregado de su cohorte | 72,2% | 0,0% | 83,3% [78,2%; 93,5%] | 1,000 | 0,001 |

### Sensibilidad: cohorte fija con reporte en los 12 meses 09/2015 – 08/2016

- 1003 plugins; factor agregado de la cohorte ×2,04; con ganancia positiva: 39,1%; ganancia neta total: 320.240; Spearman(log tamaño base, factor) = +0,104.
- Factor del ecosistema completo en las mismas ventanas: ×3,8; plugins de la cohorte que crecen al menos ese factor: 17,5%; factor de los plugins: mediana ×0,56, percentil 90 ×6,71, percentil 99 ×97,1.

| métrica | observado | nulo proporcional (B0) | nulo Gibrat (B1): mediana [IC 95%] | p (más concentrado que B1) | p (menos concentrado que B1) |
|:--|--:|--:|--:|--:|--:|
| ganancia neta captada por el top 1% | 41,2% | 18,0% | 75,4% [57,4%; 91,4%] | 1,000 | 0,001 |
| ganancia neta captada por el top 5% | 89,2% | 43,0% | 100,1% [96,4%; 104,5%] | 1,000 | 0,001 |
| ganancia neta captada por el top 10% | 113,1% | 58,5% | 107,2% [102,5%; 115,8%] | 0,075 | 0,926 |
| fracción mínima de plugins con el 50% de la ganancia | 1,6% | 7,2% | 0,4% [0,1%; 0,9%] | 1,000 | 0,001 |
| Gini de la ganancia absoluta | 1,521 | 0,724 | 1,181 [1,065; 1,387] | 0,002 | 0,999 |
| plugins que crecen menos que el agregado de su cohorte | 72,6% | 0,0% | 85,1% [77,3%; 94,2%] | 1,000 | 0,001 |

## Lectura

- p empíricos unilaterales frente a B1, en las dos direcciones: proporción de permutaciones tan concentradas o más que lo observado, y tan poco concentradas o menos (para la fracción del 50%, el sentido se invierte: menor = más concentrado).
- B1 principal permuta las tasas anualizadas dentro de cada año de entrada (estratos de duración comparable).
- Con ganancias negativas la ganancia neta captada por el top puede superar el 100% y el Gini puede superar 1; solo se usan para comparar observado con nulo.
