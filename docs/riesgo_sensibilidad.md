# Índice de exposición al riesgo: variantes y sensibilidad del umbral de inactividad

Generado por `src/analyze/12_riesgo_sensibilidad.py`. No editar a mano. Fórmulas en el docstring del script.

- Población puntuada: 2876 plugins con ≥1 mantenedor; excluidos 12 sin mantenedor (12 de ellos sin dato de instalaciones).
- Plugins puntuados sin dato de instalaciones (tomados como 0): local_accessibilitytoolkit.
- Spearman(in-degree, PageRank) en G_dep = 0.9989 → se usa solo PageRank.
- Plugins ex-núcleo marcados: 22 (evidencia literal en `_ex_core.py`); incorporados al núcleo: 2.

## Escala de cada término (T = 3 años)

Desviación típica y máximo de la contribución de cada término al índice; muestra qué término domina el orden.

| variante   | término            |   desv. típica |   máximo |
|:-----------|:-------------------|---------------:|---------:|
| V0         | z(inst)            |          1.000 |   19.600 |
| V0         | z(indeg+pr)        |          1.000 |   21.404 |
| V0         | SM                 |          0.448 |    1.000 |
| V0         | ST                 |          0.496 |    1.000 |
| V1         | z(log1p inst)      |          1.000 |    3.094 |
| V1         | z(log pr/0,15)     |          1.000 |    9.355 |
| V1         | SM                 |          0.448 |    1.000 |
| V1         | ST                 |          0.496 |    1.000 |
| V2         | mm(log1p inst)/2   |          0.100 |    0.500 |
| V2         | mm(log pr/0,15)/2  |          0.052 |    0.500 |
| V2         | SM/2 (dentro de F) |          0.224 |    0.500 |
| V2         | ST/2 (dentro de F) |          0.248 |    0.500 |

## Composición del top-30 (T = 3 años)

| variante   |   con SM |   con ST |   sin ninguna señal |   ex-núcleo |   mediana instalaciones |
|:-----------|---------:|---------:|--------------------:|------------:|------------------------:|
| V0         |       24 |        5 |                   6 |           2 |                    7704 |
| V1         |       26 |       14 |                   2 |           2 |                     463 |
| V2         |       30 |       27 |                   0 |           3 |                     514 |

## Concordancia entre variantes (T = 3 años)

| par   |   Spearman |   Jaccard top-30 |
|:------|-----------:|-----------------:|
| V0–V1 |      0.827 |            0.395 |
| V0–V2 |      0.749 |            0.132 |
| V1–V2 |      0.767 |            0.333 |

## Sensibilidad al umbral de inactividad (respecto a T = 3 años)

|   T (años) | corte      |   stale |   % stale |   frágiles (SM y ST) |   V0 ρ vs T=3 |   V0 J top-30 vs T=3 |   V1 ρ vs T=3 |   V1 J top-30 vs T=3 |   V2 ρ vs T=3 |   V2 J top-30 vs T=3 |
|-----------:|:-----------|--------:|----------:|---------------------:|--------------:|---------------------:|--------------:|---------------------:|--------------:|---------------------:|
|          2 | 2024-09-10 |    1355 |    47.114 |                 1001 |         0.970 |                0.935 |         0.985 |                0.935 |         0.964 |                0.818 |
|          3 | 2023-09-10 |    1246 |    43.324 |                  930 |         1.000 |                1.000 |         1.000 |                1.000 |         1.000 |                1.000 |
|          5 | 2021-09-10 |    1001 |    34.805 |                  773 |         0.933 |                1.000 |         0.968 |                0.818 |         0.927 |                0.579 |

## Robustez de la variante principal (V2)

|   top-30 V2 estable con T=2, 3 y 5 |   Jaccard top-30 V2 con vs. sin ex-núcleo (sin contar los ex-núcleo) |
|-----------------------------------:|---------------------------------------------------------------------:|
|                             20.000 |                                                                0.900 |

## Top-30 de la variante principal (V2, T = 3 años)

|   rank | component                 |   installations |     I |   E_exposicion |   ex_core |   en_nucleo_robusto |
|-------:|:--------------------------|----------------:|------:|---------------:|----------:|--------------------:|
|      1 | theme_base                |         480.000 | 0.798 |          0.798 |         1 |                   1 |
|      2 | theme_canvas              |         385.000 | 0.753 |          0.753 |         1 |                   1 |
|      3 | local_leeloolxpcontentapi |         117.000 | 0.645 |          0.645 |         0 |                   1 |
|      4 | mod_dataform              |         545.000 | 0.637 |          0.637 |         0 |                   1 |
|      5 | assignsubmission_pdf      |         484.000 | 0.618 |          0.618 |         0 |                   1 |
|      6 | assignfeedback_pdf        |         446.000 | 0.614 |          0.614 |         0 |                   1 |
|      7 | mod_certificate           |        4084.000 | 0.572 |          0.572 |         0 |                   1 |
|      8 | theme_bootstrap           |         805.000 | 0.541 |          0.541 |         0 |                   1 |
|      9 | mod_aulaplaneta           |         331.000 | 0.531 |          0.531 |         0 |                   0 |
|     10 | auth_linkedin             |          27.000 | 0.480 |          0.480 |         0 |                   1 |
|     11 | block_linkedin            |          27.000 | 0.480 |          0.480 |         0 |                   1 |
|     12 | format_flexpage           |          38.000 | 0.476 |          0.476 |         0 |                   1 |
|     13 | mod_externalcontent       |         181.000 | 0.469 |          0.469 |         0 |                   0 |
|     14 | qtype_geogebra            |        1399.000 | 0.455 |          0.455 |         0 |                   0 |
|     15 | block_slider              |        1195.000 | 0.448 |          0.448 |         0 |                   1 |
|     16 | enrol_easy                |         677.000 | 0.420 |          0.420 |         0 |                   1 |
|     17 | filter_cincopa            |         174.000 | 0.420 |          0.420 |         0 |                   0 |
|     18 | qbehaviour_adaptivehints  |         192.000 | 0.418 |          0.418 |         0 |                   1 |
|     19 | block_progress            |        2062.000 | 0.414 |          0.414 |         0 |                   1 |
|     20 | block_user_preferences    |           1.000 | 0.413 |          0.413 |         0 |                   1 |
|     21 | filter_wiris              |        5183.000 | 0.797 |          0.399 |         0 |                   1 |
|     22 | theme_fordson             |        3870.000 | 0.398 |          0.398 |         0 |                   1 |
|     23 | mod_googlemeet            |        3791.000 | 0.397 |          0.397 |         0 |                   0 |
|     24 | theme_klass               |        3436.000 | 0.393 |          0.393 |         0 |                   0 |
|     25 | mod_customcert            |       31808.000 | 0.785 |          0.393 |         0 |                   1 |
|     26 | block_course_overview     |         378.000 | 0.392 |          0.392 |         1 |                   1 |
|     27 | theme_eguru               |        3286.000 | 0.391 |          0.391 |         0 |                   0 |
|     28 | tinymce_mathslate         |         360.000 | 0.390 |          0.390 |         0 |                   0 |
|     29 | report_coursestats        |        2837.000 | 0.383 |          0.383 |         0 |                   0 |
|     30 | booktool_wordimport       |        8282.000 | 0.741 |          0.370 |         0 |                   0 |
