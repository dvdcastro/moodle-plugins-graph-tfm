# Predicción de inactividad: Brier, varios cortes temporales y exposición esperada

Generado por `src/analyze/17_prediccion_brier_cortes.py`. No editar a mano. Diseño en el docstring del script; reutiliza `13_prediccion_inactividad.py` sin modificarlo.

## 1. Brier y calibración (entrenamiento 2020, evaluación 2023)

- Split de 13_: entrenamiento T0 = 2020-09-10 (n = 781, tasa = 0,392); evaluación T0 = 2023-09-10 (n = 974, tasa = 0,360).
- Reproducción de 13_ verificada con asserts: ROC-AUC 0,750 / 0,771 / 0,783 / 0,738 y Brier 0,193 / 0,183 / 0,179 / 0,223.
- Brier de referencia climatológica = ȳ(1 − ȳ) = 0,231; con la tasa de entrenamiento (la única conocida en T0) = 0,231.
- Error de calibración esperado (ECE, deciles) del modelo principal: 0,041.

BSS = 1 − Brier / Brier_ref. Intercepto de calibración: 0 ideal (> 0 = el modelo infraestima la tasa). Pendiente de calibración: 1 ideal (< 1 = predicciones demasiado extremas).

| modelo                                           |   Brier |   BSS (clim. evaluación) |   BSS (clim. entrenamiento) | IC95 Brier     | IC95 BSS        |   prob. media |   intercepto calibración |   pendiente calibración |   ROC-AUC |
|:-------------------------------------------------|--------:|-------------------------:|----------------------------:|:---------------|:----------------|--------------:|-------------------------:|------------------------:|----------:|
| Referencia climatológica (tasa de evaluación)    |   0.231 |                    0.000 |                     nan     | nan            | nan             |       nan     |                  nan     |                 nan     |   nan     |
| Referencia climatológica (tasa de entrenamiento) |   0.231 |                   -0.004 |                       0.000 | nan            | nan             |       nan     |                  nan     |                 nan     |   nan     |
| Línea base (años desde la última versión)        |   0.193 |                    0.163 |                       0.167 | [0,183; 0,202] | [0,125; 0,198]  |         0.383 |                   -0.107 |                   1.414 |     0.750 |
| RL principal (16 variables)                      |   0.183 |                    0.206 |                       0.209 | [0,171; 0,196] | [0,155; 0,255]  |         0.380 |                   -0.109 |                   0.941 |     0.771 |
| RL parsimoniosa (3 variables, exploratoria)      |   0.179 |                    0.224 |                       0.227 | [0,168; 0,190] | [0,177; 0,266]  |         0.376 |                   -0.086 |                   1.082 |     0.783 |
| HistGradientBoosting (16 variables)              |   0.223 |                    0.032 |                       0.036 | [0,204; 0,243] | [-0,057; 0,115] |         0.376 |                   -0.153 |                   0.283 |     0.738 |

### Tabla de fiabilidad por deciles (RL principal)

|   decil |   n |   p_media |   tasa_observada |   diferencia |
|--------:|----:|----------:|-----------------:|-------------:|
|       1 |  98 |     0.045 |            0.071 |        0.027 |
|       2 |  97 |     0.121 |            0.062 |       -0.059 |
|       3 |  97 |     0.188 |            0.258 |        0.070 |
|       4 |  98 |     0.251 |            0.194 |       -0.057 |
|       5 |  97 |     0.322 |            0.289 |       -0.034 |
|       6 |  97 |     0.390 |            0.381 |       -0.008 |
|       7 |  98 |     0.469 |            0.388 |       -0.082 |
|       8 |  97 |     0.560 |            0.567 |        0.007 |
|       9 |  97 |     0.659 |            0.660 |        0.001 |
|      10 |  98 |     0.796 |            0.735 |       -0.061 |

## 2. Robustez a varios cortes (entrena en T0 − 3, evalúa en T0, horizonte 3 años)

- Cohortes de evaluación 2017–2023; la etiqueta de cada cohorte de entrenamiento se cierra exactamente en el T0 de evaluación. Cohortes posteriores a 2023 no tienen la etiqueta completa (cierre 2026-09-07).
- RL principal: ROC-AUC entre 0,733 y 0,793 (media 0,757); BSS entre 0,102 y 0,247; supera a la línea base en 6 de 7 cortes (ΔAUC medio 0,031).

|   T0 entrenamiento |   T0 evaluación |   n entrenamiento |   n evaluación |   tasa entrenamiento |   tasa evaluación | modelo                                    |   ROC-AUC | IC95 ROC-AUC   | ΔAUC vs. base [IC95]   |   Brier |   Brier ref. |   BSS |   BSS (clim. entrenamiento) |   prob. media |   intercepto calibración |   pendiente calibración |
|-------------------:|----------------:|------------------:|---------------:|---------------------:|------------------:|:------------------------------------------|----------:|:---------------|:-----------------------|--------:|-------------:|------:|----------------------------:|--------------:|-------------------------:|------------------------:|
|               2014 |            2017 |               681 |            715 |                0.557 |             0.456 | Línea base (años desde la última versión) |     0.702 | [0,664; 0,741] | —                      |   0.236 |        0.248 | 0.048 |                       0.085 |         0.562 |                   -0.591 |                   0.494 |
|               2014 |            2017 |               681 |            715 |                0.557 |             0.456 | RL principal (16 variables)               |     0.733 | [0,697; 0,770] | 0,031 [0,003; 0,061]   |   0.223 |        0.248 | 0.102 |                       0.137 |         0.441 |                    0.098 |                   0.495 |
|               2015 |            2018 |               750 |            754 |                0.509 |             0.462 | Línea base (años desde la última versión) |     0.790 | [0,758; 0,821] | —                      |   0.183 |        0.249 | 0.264 |                       0.270 |         0.439 |                    0.129 |                   0.966 |
|               2015 |            2018 |               750 |            754 |                0.509 |             0.462 | RL principal (16 variables)               |     0.793 | [0,762; 0,823] | 0,003 [-0,021; 0,026]  |   0.187 |        0.249 | 0.247 |                       0.254 |         0.416 |                    0.293 |                   0.745 |
|               2016 |            2019 |               695 |            768 |                0.478 |             0.398 | Línea base (años desde la última versión) |     0.759 | [0,724; 0,794] | —                      |   0.198 |        0.240 | 0.172 |                       0.193 |         0.473 |                   -0.360 |                   1.160 |
|               2016 |            2019 |               695 |            768 |                0.478 |             0.398 | RL principal (16 variables)               |     0.753 | [0,716; 0,788] | -0,006 [-0,041; 0,027] |   0.199 |        0.240 | 0.168 |                       0.189 |         0.458 |                   -0.319 |                   0.838 |
|               2017 |            2020 |               715 |            781 |                0.456 |             0.392 | Línea base (años desde la última versión) |     0.695 | [0,659; 0,733] | —                      |   0.214 |        0.238 | 0.102 |                       0.117 |         0.446 |                   -0.247 |                   1.056 |
|               2017 |            2020 |               715 |            781 |                0.456 |             0.392 | RL principal (16 variables)               |     0.751 | [0,714; 0,785] | 0,055 [0,026; 0,084]   |   0.196 |        0.238 | 0.179 |                       0.193 |         0.407 |                   -0.081 |                   0.915 |
|               2018 |            2021 |               754 |            857 |                0.462 |             0.384 | Línea base (años desde la última versión) |     0.689 | [0,654; 0,726] | —                      |   0.221 |        0.237 | 0.065 |                       0.088 |         0.455 |                   -0.386 |                   0.608 |
|               2018 |            2021 |               754 |            857 |                0.462 |             0.384 | RL principal (16 variables)               |     0.746 | [0,713; 0,780] | 0,057 [0,034; 0,080]   |   0.200 |        0.237 | 0.156 |                       0.177 |         0.424 |                   -0.236 |                   0.680 |
|               2019 |            2022 |               768 |            932 |                0.398 |             0.383 | Línea base (años desde la última versión) |     0.694 | [0,659; 0,728] | —                      |   0.215 |        0.236 | 0.089 |                       0.090 |         0.373 |                    0.052 |                   0.695 |
|               2019 |            2022 |               768 |            932 |                0.398 |             0.383 | RL principal (16 variables)               |     0.751 | [0,720; 0,782] | 0,057 [0,031; 0,081]   |   0.197 |        0.236 | 0.166 |                       0.167 |         0.351 |                    0.185 |                   0.771 |
|               2020 |            2023 |               781 |            974 |                0.392 |             0.360 | Línea base (años desde la última versión) |     0.750 | [0,718; 0,782] | —                      |   0.193 |        0.231 | 0.163 |                       0.167 |         0.383 |                   -0.107 |                   1.414 |
|               2020 |            2023 |               781 |            974 |                0.392 |             0.360 | RL principal (16 variables)               |     0.771 | [0,740; 0,801] | 0,021 [-0,007; 0,051]  |   0.183 |        0.231 | 0.206 |                       0.209 |         0.380 |                   -0.109 |                   0.941 |

## 3. Exposición esperada E = P̂(inactividad a 3 años) × I

- Modelo: RL principal entrenada con la cohorte T0 = 2023-09-10 (n = 974, tasa = 0,360), aplicada a las features en T_now = 2026-09-10.
- Plugins activos en T_now: 1640; con término de impacto I (población P2): 1630 (10 sin mantenedor, fuera de P2). Activos según 12_ (ST = 0): 1630.
- Probabilidad media predicha en T_now: 0,330 (mediana 0,308); inactivos esperados en 2026-2029: 538 de 1630.
- El top-30 de V2 sobre toda la población contiene 27 plugins con ST = 1 (ya inactivos), que por definición no entran en E.
- Top-20 de E con un solo mantenedor (SM = 1): 12; P(inactividad) mediana del top-20: 0,740; I mediano del top-20: 0,395 frente a 0,214 en todos los activos.

### Top-20 por exposición esperada

|   rank_E | component                                  |   installations |   SM |   recency_y |   releases_2y |     I |   p_inactividad |   E_esperada |    V2 |   rank_V2 |   ex_core |
|---------:|:-------------------------------------------|----------------:|-----:|------------:|--------------:|------:|----------------:|-------------:|------:|----------:|----------:|
|        1 | qtype_poasquestion                         |             212 |    0 |       2.583 |             0 | 0.509 |           0.730 |        0.372 | 0.000 |      2597 |         0 |
|        2 | local_aws                                  |            1859 |    1 |       2.340 |             0 | 0.581 |           0.596 |        0.346 | 0.290 |       112 |         0 |
|        3 | block_dedication                           |            7466 |    0 |       2.135 |             0 | 0.601 |           0.546 |        0.328 | 0.000 |      2372 |         0 |
|        4 | assignsubmission_estream                   |             147 |    1 |       2.126 |             0 | 0.491 |           0.624 |        0.306 | 0.245 |       206 |         0 |
|        5 | atto_fontsize                              |            3991 |    0 |       2.974 |             0 | 0.400 |           0.759 |        0.304 | 0.000 |      2390 |         0 |
|        6 | mod_via                                    |              82 |    0 |       2.508 |             0 | 0.384 |           0.786 |        0.302 | 0.000 |      2674 |         0 |
|        7 | block_znanium_com                          |             100 |    1 |       2.428 |             0 | 0.389 |           0.762 |        0.297 | 0.195 |       425 |         0 |
|        8 | local_yukaltura                            |              49 |    1 |       1.685 |             1 | 0.436 |           0.669 |        0.291 | 0.218 |       308 |         0 |
|        9 | theme_roshnilite                           |             590 |    1 |       2.471 |             0 | 0.308 |           0.945 |        0.291 | 0.154 |       715 |         0 |
|       10 | qtype_ordering                             |            1211 |    1 |       2.948 |             0 | 0.448 |           0.632 |        0.283 | 0.224 |       286 |         0 |
|       11 | enrol_apply                                |            2265 |    0 |       2.892 |             0 | 0.373 |           0.750 |        0.279 | 0.000 |      2416 |         0 |
|       12 | qbehaviour_regexpadaptivewithhelp          |            1129 |    0 |       1.920 |             1 | 0.516 |           0.527 |        0.272 | 0.000 |      2455 |         0 |
|       13 | local_clickview                            |             148 |    1 |       1.607 |             2 | 0.496 |           0.535 |        0.265 | 0.248 |       200 |         0 |
|       14 | qbehaviour_adaptiveexternalgrading         |              82 |    1 |       1.806 |             1 | 0.376 |           0.697 |        0.262 | 0.188 |       469 |         0 |
|       15 | customfield_file                           |             284 |    1 |       2.739 |             0 | 0.273 |           0.955 |        0.260 | 0.136 |       915 |         0 |
|       16 | theme_boosted                              |             251 |    0 |       2.867 |             0 | 0.267 |           0.967 |        0.258 | 0.000 |      2584 |         0 |
|       17 | paygw_bank                                 |             232 |    1 |       2.460 |             0 | 0.263 |           0.935 |        0.246 | 0.131 |       968 |         0 |
|       18 | profilefield_file                          |             716 |    1 |       2.424 |             0 | 0.317 |           0.774 |        0.246 | 0.159 |       685 |         0 |
|       19 | qbehaviour_regexpadaptivewithhelpnopenalty |            1113 |    0 |       1.920 |             1 | 0.410 |           0.582 |        0.239 | 0.000 |      2456 |         0 |
|       20 | block_iprbookshop_ru                       |              35 |    1 |       2.673 |             0 | 0.279 |           0.852 |        0.237 | 0.139 |       879 |         0 |

### Comparación con el índice V2

| comparación                                 | solapamiento   |   Jaccard |   Spearman (activos) |
|:--------------------------------------------|:---------------|----------:|---------------------:|
| top-30 E vs. top-30 V2 (población completa) | 0              |     0.000 |              nan     |
| top-20 E vs. top-30 V2 (población completa) | 0              |     0.000 |              nan     |
| top-30 E vs. top-30 V2 (solo activos)       | 3              |     0.053 |                0.088 |
| E vs. impacto I (activos)                   | —              |   nan     |                0.191 |
| E vs. P(inactividad) (activos)              | —              |   nan     |                0.620 |
| top-30 E principal vs. E parsimoniosa       | 23             |     0.622 |                0.924 |
