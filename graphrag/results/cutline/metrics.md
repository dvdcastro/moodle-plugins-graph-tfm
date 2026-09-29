# Métricas — modo `cutline` (vectorial, GraphRAG)

Gold: `gold/questions.jsonl` (sha256 `95cf7b4a51bece06…`), 15 preguntas. K = 20 fichas en los tres sistemas. Modelos: `gemini-embedding-001` (768 d), `gemini-2.5-flash` (temperature 0, thinkingBudget 0). Bootstrap 10000 remuestreos, IC 95 %: pareado (preguntas i.i.d.), estratificado por tipo y por conglomerados en dos etapas (plantilla, luego pregunta). Wilcoxon exacto de rangos con signo sobre las diferencias no nulas.

## Titular: tipos relacionales con lista gold (T1–T4, n = 10)

| Sistema | F1 citas | Recall@20 | Precisión citas | Recall citas |
|---|---|---|---|---|
| vectorial | 0,30 | 0,53 | 0,40 | 0,27 |
| GraphRAG | 1,00 | 1,00 | 1,00 | 1,00 |

Contrastes pareados en T1–T4 (Δ = segundo − primero):

| Contraste | Métrica | Δ | IC pareado | IC estratificado | IC conglomerados | Wilcoxon exacto p | G/E/P |
|---|---|---|---|---|---|---|---|
| GraphRAG − vectorial | F1 | +0,70 | [+0,42; +0,93] | [+0,45; +0,93] | [+0,35; +1,00] | 0,008 | 8/2/0 |
| GraphRAG − vectorial | Recall@20 | +0,47 | [+0,21; +0,74] | [+0,35; +0,57] | [+0,00; +1,00] | 0,031 | 6/4/0 |
| GraphRAG − vectorial | Precisión | +0,60 | [+0,30; +0,90] | [+0,30; +0,90] | [+0,20; +1,00] | 0,031 | 6/4/0 |

## Medias por tipo y sistema

| Tipo | n | Sistema | Recall@20 | P citas | R citas | F1 citas | Cumplim. T5 | Fidelidad (n def.) | Sin citas | Tokens prompt |
|---|---|---|---|---|---|---|---|---|---|---|
| T1 Dependientes | 5 | vectorial | 0,93 | 0,60 | 0,43 | 0,45 | — | 1,00 (3) | 0 | 2645 |
| T1 Dependientes | 5 | GraphRAG | 1,00 | 1,00 | 1,00 | 1,00 | — | 1,00 (5) | 0 | 2717 |
| T3 Co-mantenimiento | 5 | vectorial | 0,12 | 0,20 | 0,12 | 0,15 | — | 1,00 (1) | 0 | 2793 |
| T3 Co-mantenimiento | 5 | GraphRAG | 1,00 | 1,00 | 1,00 | 1,00 | — | 1,00 (5) | 0 | 3069 |
| T6 Semántica (control) | 5 | vectorial | 0,86 | 0,66 | 0,75 | 0,67 | — | 1,00 (5) | 0 | 2780 |
| T6 Semántica (control) | 5 | GraphRAG | 0,82 | 0,66 | 0,69 | 0,64 | — | 1,00 (5) | 0 | 2954 |
| T1–T4 | 10 | vectorial | 0,53 | 0,40 | 0,27 | 0,30 | — | 1,00 (4) | 0 | 2719 |
| T1–T4 | 10 | GraphRAG | 1,00 | 1,00 | 1,00 | 1,00 | — | 1,00 (10) | 0 | 2893 |
| Todas | 15 | vectorial | 0,64 | 0,49 | 0,43 | 0,42 | — | 1,00 (9) | 0 | 2739 |
| Todas | 15 | GraphRAG | 0,94 | 0,89 | 0,90 | 0,88 | — | 1,00 (15) | 0 | 2913 |

## Contrastes por tipo (F1 de citas; T5: cumplimiento, NO comparable)

| Tipo | Contraste | n | Media 1º | Media 2º | Δ | IC pareado | Wilcoxon exacto p | G/E/P |
|---|---|---|---|---|---|---|---|---|
| T1 Dependientes | GraphRAG − vectorial | 5 | 0,45 | 1,00 | +0,55 | [+0,15; +0,95] | 0,250 | 3/2/0 |
| T3 Co-mantenimiento | GraphRAG − vectorial | 5 | 0,15 | 1,00 | +0,85 | [+0,55; +1,00] | 0,062 | 5/0/0 |
| T6 Semántica (control) | GraphRAG − vectorial | 5 | 0,67 | 0,64 | −0,03 | [−0,13; +0,05] | 1,000 | 2/0/3 |

## Longitud del contexto (tokens de prompt según `usageMetadata`)

- vectorial: media 2739 tokens (T1–T4: 2719)
- GraphRAG: media 2913 tokens (T1–T4: 2893)
- GraphRAG vs. vectorial, exceso por pregunta: mediana 6 %, rango [1 %; 16 %]
- Enlazado de entidades (GraphRAG): 10/10
- T3, fracción de mantenedores gold nombrados: vectorial 1,00, GraphRAG 1,00

Gasto API acumulado estimado (todo el proyecto): US$ 0.282
