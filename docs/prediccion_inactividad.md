# Predicción de inactividad de publicación (experimento supervisado)

Generado por `src/analyze/13_prediccion_inactividad.py`. No editar a mano. Diseño y limitaciones en el docstring del script.

- Cohorte de entrenamiento T0 = 2020-09-10: n = 781, tasa de inactividad = 0,392
- Cohorte de evaluación T0 = 2023-09-10: n = 974, tasa de inactividad = 0,360
- Plugins presentes en ambas cohortes: 475
- Evidencia de fuga en supportedmoodles: 61 versiones publicadas antes de 2020-09-10 declaran soporte para Moodle ≥ 4.0 (publicado en 2022)
- Instalaciones en T0 tomadas del mes anterior al corte (Aug 2023 para la cohorte de evaluación)

## Resultados (evaluación fuera de tiempo sobre la cohorte 2023)

| modelo                                                       |   variables |   ROC-AUC |   PR-AUC |   Brier |   precisión top-10% |   prob. media |   ROC-AUC CV-5 dentro de 2023 | IC95 ROC-AUC   | ΔAUC vs. baseline [IC95]   |   P(Δ ≤ 0) |
|:-------------------------------------------------------------|------------:|----------:|---------:|--------:|--------------------:|--------------:|------------------------------:|:---------------|:---------------------------|-----------:|
| Línea base: años desde la última versión                     |       1.000 |     0.750 |    0.619 |   0.193 |               0.722 |         0.383 |                         0.749 | [0,719; 0,781] | —                          |    nan     |
| Regresión logística principal (16 variables fechadas ≤ T0)   |      16.000 |     0.771 |    0.654 |   0.183 |               0.732 |         0.380 |                         0.786 | [0,741; 0,801] | 0,021 [-0,008; 0,050]      |      0.076 |
| Regresión logística parsimoniosa (3 variables, exploratoria) |       3.000 |     0.783 |    0.663 |   0.179 |               0.753 |         0.376 |                         0.786 | [0,753; 0,810] | 0,033 [0,006; 0,060]       |      0.009 |
| Regresión logística + variables con fuga (sensibilidad)      |      20.000 |     0.765 |    0.644 |   0.198 |               0.722 |         0.464 |                         0.776 | [0,734; 0,794] | 0,015 [-0,015; 0,044]      |      0.176 |
| HistGradientBoosting (referencia no lineal)                  |      16.000 |     0.738 |    0.571 |   0.223 |               0.649 |         0.376 |                         0.806 | [0,704; 0,768] | -0,013 [-0,044; 0,021]     |      0.768 |
| Índice de exposición V2 en T0 (sin entrenamiento)            |     nan     |     0.456 |    0.311 | nan     |               0.155 |       nan     |                       nan     | [0,421; 0,491] | -0,294 [-0,340; -0,247]    |      1.000 |
| Índice literal V0 en T0 (sin entrenamiento)                  |     nan     |     0.402 |    0.295 | nan     |               0.175 |       nan     |                       nan     | [0,363; 0,439] | -0,348 [-0,396; -0,298]    |      1.000 |

## Coeficientes del modelo principal (entrenado en la cohorte 2020)

Las variables de tipo son indicadoras con referencia «resto de tipos»; `age_y`, `n_versions` y `releases_2y` son colineales, por lo que solo se interpreta el signo de las variables con IC que no cruza el 0.

| variable        |   coef |   IC95 inf |   IC95 sup |   odds ratio por 1 DE |
|:----------------|-------:|-----------:|-----------:|----------------------:|
| age_y           |  0.117 |     -0.098 |      0.415 |                 1.125 |
| recency_y       |  0.463 |      0.252 |      0.663 |                 1.589 |
| n_versions      | -0.065 |     -0.594 |      0.243 |                 0.937 |
| releases_2y     | -0.439 |     -0.861 |     -0.087 |                 0.645 |
| log_installs    | -0.561 |     -0.794 |     -0.324 |                 0.570 |
| installs_growth | -0.144 |     -0.394 |      0.035 |                 0.866 |
| type_mod        | -0.089 |     -0.273 |      0.114 |                 0.914 |
| type_block      |  0.240 |      0.059 |      0.425 |                 1.271 |
| type_local      |  0.133 |     -0.046 |      0.318 |                 1.142 |
| type_theme      |  0.008 |     -0.219 |      0.171 |                 1.008 |
| type_qtype      | -0.250 |     -0.795 |     -0.049 |                 0.779 |
| type_format     |  0.087 |     -0.060 |      0.210 |                 1.091 |
| type_auth       | -0.099 |     -0.307 |      0.054 |                 0.906 |
| type_filter     |  0.135 |     -0.045 |      0.314 |                 1.145 |
| type_report     | -0.000 |     -0.233 |      0.180 |                 1.000 |
| type_tool       |  0.110 |     -0.036 |      0.280 |                 1.117 |

## Coeficientes del modelo parsimonioso

| variable     |   coef |   IC95 inf |   IC95 sup |   odds ratio por 1 DE |
|:-------------|-------:|-----------:|-----------:|----------------------:|
| recency_y    |  0.485 |      0.277 |      0.680 |                 1.624 |
| log_installs | -0.592 |     -0.765 |     -0.432 |                 0.553 |
| releases_2y  | -0.528 |     -0.873 |     -0.278 |                 0.590 |

## Deriva de variables entre cohortes

| variable        |   media 2020 |   media 2023 |   diferencia estandarizada |
|:----------------|-------------:|-------------:|---------------------------:|
| support_lag     |       11.932 |        7.084 |                     -1.377 |
| installs_growth |        0.379 |        0.204 |                     -0.328 |
| age_y           |        3.847 |        4.422 |                      0.184 |
| n_versions      |        7.421 |        9.049 |                      0.150 |
| releases_2y     |        2.663 |        3.099 |                      0.116 |
| n_supported     |        5.636 |        6.131 |                      0.108 |
| type_block      |        0.192 |        0.155 |                     -0.098 |
| type_mod        |        0.160 |        0.182 |                      0.057 |
| recency_y       |        1.009 |        0.966 |                     -0.052 |
| log_installs    |        5.031 |        5.100 |                      0.035 |
| type_filter     |        0.042 |        0.037 |                     -0.027 |
| n_maintainers   |        1.627 |        1.653 |                      0.025 |
| type_qtype      |        0.045 |        0.049 |                      0.021 |
| type_theme      |        0.027 |        0.024 |                     -0.021 |
| type_report     |        0.029 |        0.033 |                      0.020 |
| type_auth       |        0.027 |        0.025 |                     -0.014 |
| type_local      |        0.118 |        0.121 |                      0.010 |
| type_format     |        0.022 |        0.023 |                      0.006 |
| type_tool       |        0.069 |        0.068 |                     -0.005 |
| log_indeg_dep   |        0.136 |        0.137 |                      0.002 |
