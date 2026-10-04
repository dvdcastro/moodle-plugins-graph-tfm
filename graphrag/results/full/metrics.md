# Métricas — modo `full` (vectorial, vectorial + relaciones, KG-RAG)

Gold: `gold/questions.jsonl` (sha256 `95cf7b4a51bece06…`), 30 preguntas. K = 20 fichas en los tres sistemas. Modelos: `gemini-embedding-001` (768 d), `gemini-2.5-flash` (temperature 0, thinkingBudget 0). Bootstrap 10000 remuestreos, IC 95 %: pareado (preguntas i.i.d.), estratificado por tipo y por conglomerados en dos etapas (plantilla, luego pregunta). Wilcoxon exacto de rangos con signo sobre las diferencias no nulas.

## Titular: tipos relacionales con lista gold (T1–T4, n = 20)

| Sistema | F1 citas | Recall@20 | Precisión citas | Recall citas |
|---|---|---|---|---|
| vectorial | 0,32 | 0,44 | 0,38 | 0,30 |
| vectorial + relaciones | 0,47 | 0,44 | 0,55 | 0,44 |
| KG-RAG | 0,96 | 0,93 | 1,00 | 0,93 |

Contrastes pareados en T1–T4 (Δ = segundo − primero):

| Contraste | Métrica | Δ | IC pareado | IC estratificado | IC conglomerados | Wilcoxon exacto p | G/E/P |
|---|---|---|---|---|---|---|---|
| KG-RAG − vectorial | F1 | +0,64 | [+0,45; +0,82] | [+0,49; +0,79] | [+0,34; +0,90] | 3,1·10^-5 | 16/4/0 |
| KG-RAG − vectorial | Recall@20 | +0,49 | [+0,32; +0,67] | [+0,40; +0,58] | [+0,14; +0,84] | 1,2·10^-4 | 14/6/0 |
| KG-RAG − vectorial | Precisión | +0,62 | [+0,40; +0,82] | [+0,47; +0,78] | [+0,30; +0,95] | 2,4·10^-4 | 13/7/0 |
| vectorial + relaciones − vectorial | F1 | +0,15 | [+0,01; +0,32] | [+0,03; +0,28] | [−0,04; +0,42] | 0,094 | 5/14/1 |
| vectorial + relaciones − vectorial | Recall@20 | +0,00 | [+0,00; +0,00] | [+0,00; +0,00] | [+0,00; +0,00] | 1,000 | 0/20/0 |
| vectorial + relaciones − vectorial | Precisión | +0,17 | [+0,00; +0,38] | [+0,00; +0,35] | [−0,03; +0,42] | 0,125 | 4/15/1 |
| KG-RAG − vectorial + relaciones | F1 | +0,49 | [+0,31; +0,67] | [+0,39; +0,58] | [+0,11; +0,85] | 1,2·10^-4 | 14/6/0 |
| KG-RAG − vectorial + relaciones | Recall@20 | +0,49 | [+0,32; +0,66] | [+0,40; +0,58] | [+0,14; +0,84] | 1,2·10^-4 | 14/6/0 |
| KG-RAG − vectorial + relaciones | Precisión | +0,45 | [+0,25; +0,65] | [+0,30; +0,60] | [+0,10; +0,85] | 0,004 | 9/11/0 |

## Medias por tipo y sistema

| Tipo | n | Sistema | Recall@20 | P citas | R citas | F1 citas | Cumplim. T5 | Fidelidad (n def.) | Sin citas | Tokens prompt |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 Dependientes | 5 | vectorial | 0,93 | 0,60 | 0,43 | 0,45 | — | 1,00 (3) | 0 | 2645 |
| T1 Dependientes | 5 | vectorial + relaciones | 0,93 | 1,00 | 0,93 | 0,96 | — | 1,00 (5) | 0 | 3649 |
| T1 Dependientes | 5 | KG-RAG | 1,00 | 1,00 | 1,00 | 1,00 | — | 1,00 (5) | 0 | 2717 |
| T2 Dependencias | 5 | vectorial | 0,65 | 0,70 | 0,65 | 0,67 | — | 0,88 (4) | 0 | 2718 |
| T2 Dependencias | 5 | vectorial + relaciones | 0,65 | 0,80 | 0,65 | 0,70 | — | 1,00 (4) | 0 | 3568 |
| T2 Dependencias | 5 | KG-RAG | 0,90 | 1,00 | 0,90 | 0,93 | — | 1,00 (5) | 0 | 2763 |
| T3 Co-mantenimiento | 5 | vectorial | 0,12 | 0,20 | 0,12 | 0,15 | — | 1,00 (1) | 0 | 2793 |
| T3 Co-mantenimiento | 5 | vectorial + relaciones | 0,12 | 0,20 | 0,12 | 0,15 | — | 1,00 (1) | 0 | 3383 |
| T3 Co-mantenimiento | 5 | KG-RAG | 1,00 | 1,00 | 1,00 | 1,00 | — | 1,00 (5) | 0 | 3069 |
| T4 Comunidad frágil | 5 | vectorial | 0,04 | 0,00 | 0,00 | 0,00 | — | 1,00 (1) | 0 | 2830 |
| T4 Comunidad frágil | 5 | vectorial + relaciones | 0,04 | 0,20 | 0,04 | 0,07 | — | 1,00 (2) | 1 | 3389 |
| T4 Comunidad frágil | 5 | KG-RAG | 0,82 | 1,00 | 0,82 | 0,89 | — | 1,00 (5) | 0 | 3915 |
| T5 Alternativas | 5 | vectorial | — | — | — | — | 0,52 | 1,00 (3) | 0 | 2842 |
| T5 Alternativas | 5 | vectorial + relaciones | — | — | — | — | 0,80 | 1,00 (4) | 0 | 3536 |
| T5 Alternativas | 5 | KG-RAG | — | — | — | — | 1,00 | 1,00 (5) | 0 | 3544 |
| T6 Semántica (control) | 5 | vectorial | 0,86 | 0,66 | 0,75 | 0,67 | — | 1,00 (5) | 0 | 2780 |
| T6 Semántica (control) | 5 | vectorial + relaciones | 0,86 | 0,67 | 0,72 | 0,66 | — | 1,00 (5) | 0 | 3366 |
| T6 Semántica (control) | 5 | KG-RAG | 0,80 | 0,61 | 0,67 | 0,61 | — | 1,00 (5) | 0 | 3371 |
| T1–T4 | 20 | vectorial | 0,44 | 0,38 | 0,30 | 0,32 | — | 0,94 (9) | 0 | 2747 |
| T1–T4 | 20 | vectorial + relaciones | 0,44 | 0,55 | 0,44 | 0,47 | — | 1,00 (12) | 1 | 3497 |
| T1–T4 | 20 | KG-RAG | 0,93 | 1,00 | 0,93 | 0,96 | — | 1,00 (20) | 0 | 3116 |
| Todas | 30 | vectorial | 0,52 | 0,43 | 0,39 | 0,39 | 0,52 | 0,97 (17) | 0 | 2768 |
| Todas | 30 | vectorial + relaciones | 0,52 | 0,57 | 0,49 | 0,51 | 0,80 | 1,00 (21) | 1 | 3482 |
| Todas | 30 | KG-RAG | 0,90 | 0,92 | 0,88 | 0,89 | 1,00 | 1,00 (30) | 0 | 3230 |

## Contrastes por tipo (F1 de citas; T5: cumplimiento, NO comparable)

| Tipo | Contraste | n | Media 1º | Media 2º | Δ | IC pareado | Wilcoxon exacto p | G/E/P |
|---|---|---|---|---|---|---|---|---|
| T1 Dependientes | KG-RAG − vectorial | 5 | 0,45 | 1,00 | +0,55 | [+0,15; +0,95] | 0,250 | 3/2/0 |
| T1 Dependientes | vectorial + relaciones − vectorial | 5 | 0,45 | 0,96 | +0,51 | [+0,15; +0,87] | 0,250 | 3/2/0 |
| T1 Dependientes | KG-RAG − vectorial + relaciones | 5 | 0,96 | 1,00 | +0,04 | [+0,00; +0,12] | 1,000 | 1/4/0 |
| T2 Dependencias | KG-RAG − vectorial | 5 | 0,67 | 0,93 | +0,26 | [+0,03; +0,63] | 0,250 | 3/2/0 |
| T2 Dependencias | vectorial + relaciones − vectorial | 5 | 0,67 | 0,70 | +0,03 | [−0,30; +0,40] | 1,000 | 1/3/1 |
| T2 Dependencias | KG-RAG − vectorial + relaciones | 5 | 0,70 | 0,93 | +0,23 | [+0,03; +0,47] | 0,250 | 3/2/0 |
| T3 Co-mantenimiento | KG-RAG − vectorial | 5 | 0,15 | 1,00 | +0,85 | [+0,55; +1,00] | 0,062 | 5/0/0 |
| T3 Co-mantenimiento | vectorial + relaciones − vectorial | 5 | 0,15 | 0,15 | +0,00 | [+0,00; +0,00] | 1,000 | 0/5/0 |
| T3 Co-mantenimiento | KG-RAG − vectorial + relaciones | 5 | 0,15 | 1,00 | +0,85 | [+0,55; +1,00] | 0,062 | 5/0/0 |
| T4 Comunidad frágil | KG-RAG − vectorial | 5 | 0,00 | 0,89 | +0,89 | [+0,81; +0,98] | 0,062 | 5/0/0 |
| T4 Comunidad frágil | vectorial + relaciones − vectorial | 5 | 0,00 | 0,07 | +0,07 | [+0,00; +0,20] | 1,000 | 1/4/0 |
| T4 Comunidad frágil | KG-RAG − vectorial + relaciones | 5 | 0,07 | 0,89 | +0,83 | [+0,68; +0,96] | 0,062 | 5/0/0 |
| T5 Alternativas | KG-RAG − vectorial | 5 | 0,52 | 1,00 | +0,48 | [+0,08; +0,88] | 0,250 | 3/2/0 |
| T5 Alternativas | vectorial + relaciones − vectorial | 5 | 0,52 | 0,80 | +0,28 | [+0,00; +0,68] | 0,500 | 2/3/0 |
| T5 Alternativas | KG-RAG − vectorial + relaciones | 5 | 0,80 | 1,00 | +0,20 | [+0,00; +0,60] | 1,000 | 1/4/0 |
| T6 Semántica (control) | KG-RAG − vectorial | 5 | 0,67 | 0,61 | −0,06 | [−0,15; +0,01] | 0,250 | 1/1/3 |
| T6 Semántica (control) | vectorial + relaciones − vectorial | 5 | 0,67 | 0,66 | −0,01 | [−0,06; +0,04] | 0,750 | 1/2/2 |
| T6 Semántica (control) | KG-RAG − vectorial + relaciones | 5 | 0,66 | 0,61 | −0,05 | [−0,09; −0,02] | 0,125 | 0/1/4 |

## Longitud del contexto (tokens de prompt según `usageMetadata`)

- vectorial: media 2768 tokens (T1–T4: 2747)
- vectorial + relaciones: media 3482 tokens (T1–T4: 3497)
- KG-RAG: media 3230 tokens (T1–T4: 3116)
- vectorial + relaciones vs. vectorial, exceso por pregunta: mediana 25 %, rango [11 %; 58 %]
- KG-RAG vs. vectorial, exceso por pregunta: mediana 15 %, rango [−1 %; 60 %]
- Enlazado de entidades (vectorial + relaciones): 25/25
- Enlazado de entidades (KG-RAG): 25/25
- T3, fracción de mantenedores gold nombrados: vectorial 1,00, vectorial + relaciones 1,00, KG-RAG 1,00
- T2, recall en contexto de las dependencias sin release >3 años: vectorial 0,70, vectorial + relaciones 0,70, KG-RAG 0,90

Gasto API acumulado estimado (todo el proyecto): US$ 0.282
