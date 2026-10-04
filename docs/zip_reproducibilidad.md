# Reproducibilidad de la fuente ZIP (residual de 979 plugins)

_Generado por `src/collect/06b_compare_zip.py` el 2026-10-04 11:07 UTC. No editar a mano._

## Que se compara

- **Original:** `data/processed/version_php_zip_residual979.jsonl`, de la descarga original del 2026-09-10. Es el archivo usado en **todos** los resultados de la memoria y no se modifica.
- **Reproducido:** `data/processed/version_php_zip_residual979_reproducido.jsonl`, generado con `src/collect/06_zip_version_php.py` desde fuentes publicas: el snapshot `data/raw/pluglist_20260907.json` (URL de descarga y md5 por version) y el ZIP que sirve hoy el directorio de plugins de Moodle.
- La poblacion se re-deriva con `--population derive` y coincide exactamente con los 979 componentes del original (residual definido el 2026-09-08: plugins sin coincidencia exacta entre el `version.php` de GitHub y la version mas nueva del feed).

## Resultado

| | original | reproducido |
|---|---|---|
| filas | 979 | 979 |
| HTTP 200 (ZIP descargado) | 913 | 912 |
| HTTP 401 (plugin de pago, no descargable anonimo) | 66 | 67 |
| otros codigos HTTP | 0 | 0 |
| md5 coincide con el publicado en el feed | 913 | 912 |
| version leida del version.php | 902 | 901 |
| dependencias declaradas (pares) | 282 | 280 |

- **Filas identicas en todos los campos que importan aguas abajo** (`version_in_zip`, `requires_in_zip`, `dependencies_in_zip`, `maturity_in_zip`, `release_in_zip`, `component_in_zip`, `zip_sha256`, `zip_md5_matched_published`, `http_status`, `agrees_with_pluglist`): **939 / 979** (95.9%).
- Identicas tambien en los campos secundarios (`version_php_path`, `version_php_sha256`, `zip_bytes`, `note`): 939 / 979.
- Mismo archivo byte a byte (`zip_sha256` igual) en 912 de los 913 ZIP descargados en la descarga original.

### Diferencias por campo

| campo | filas distintas |
|---|---|
| `version_in_zip` | 1 |
| `requires_in_zip` | 1 |
| `dependencies_in_zip` | 3 |
| `maturity_in_zip` | 27 |
| `release_in_zip` | 4 |
| `component_in_zip` | 33 |
| `zip_sha256` | 1 |
| `zip_md5_matched_published` | 1 |
| `http_status` | 1 |
| `agrees_with_pluglist` | 1 |
| `version_php_path` (secundario) | 1 |
| `version_php_sha256` (secundario) | 1 |
| `zip_bytes` (secundario) | 1 |
| `note` (secundario) | 1 |

### Categorias de diferencia

#### parser_module_legacy (36)

Mismo ZIP byte a byte. El version.php usa la convencion pre-2.0 `$module->` para `component`, `maturity` o `dependencies`. En 03_version_php.py solo VERSION_RE y REQUIRES_RE aceptan `$module->` (fix del 2026-09-10); MATURITY_RE, COMPONENT_RE y DEP_RE siguen exigiendo `$plugin->`, asi que el reproducido deja esos campos en null (o `{}`). version_in_zip y requires_in_zip coinciden. `component_in_zip` y `maturity_in_zip` no los consume 09_merge_zip_residual.py; el caso de `dependencies_in_zip`, si aparece, se discute aparte en la seccion de impacto.

| componente | campo | original | reproducido |
|---|---|---|---|
| `mod_alternative` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_alternative` | `component_in_zip` | "mod_alternative" | null |
| `mod_amvonetroom` | `maturity_in_zip` | "MATURITY_RC" | null |
| `mod_babelroom` | `maturity_in_zip` | "MATURITY_RC" | null |
| `mod_babelroom` | `component_in_zip` | "mod_babelroom" | null |
| `mod_cooradbridge` | `maturity_in_zip` | "MATURITY_RC" | null |
| `mod_cooradbridge` | `component_in_zip` | "mod_cooradbridge" | null |
| `mod_courseprovider` | `component_in_zip` | "mod_courseprovider" | null |
| `mod_customlesson` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_customlesson` | `component_in_zip` | "mod_customlesson" | null |
| `mod_dinsysconnect` | `maturity_in_zip` | "MATURITY_RC" | null |
| `mod_dinsysconnect` | `component_in_zip` | "mod_dinsysconnect" | null |
| `mod_ecampusbookpage` | `dependencies_in_zip` | {"block_ecampus_tbird": "2013120900"} | {} |
| `mod_ecampusbookpage` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_ecampusbookpage` | `component_in_zip` | "mod_ecampusbookpage" | null |
| `mod_eduvision` | `component_in_zip` | "mod_eduvision" | null |
| `mod_engagement` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_engagement` | `component_in_zip` | "mod_engagement" | null |
| `mod_ensemblecontent` | `maturity_in_zip` | "MATURITY_BETA" | null |
| `mod_ensemblecontent` | `component_in_zip` | "mod_ensemblecontent" | null |
| `mod_etherpad` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_etherpad` | `component_in_zip` | "mod_etherpad" | null |
| `mod_flax` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_flax` | `component_in_zip` | "mod_flax" | null |
| `mod_forumanon` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_furnace` | `component_in_zip` | "mod_furnace" | null |
| `mod_guidedquiz` | `maturity_in_zip` | "MATURITY_RC" | null |
| `mod_kitmoo` | `component_in_zip` | "mod_kitmoo" | null |
| `mod_languagelab` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_languagelab` | `component_in_zip` | "mod_languagelab" | null |
| `mod_linkbazaar` | `maturity_in_zip` | "MATURITY_ALPHA" | null |
| `mod_linkbazaar` | `component_in_zip` | "mod_linkbazaar" | null |
| `mod_livestreaming` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_livestreaming` | `component_in_zip` | "mod_livestreaming" | null |
| `mod_mdid` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_mdid` | `component_in_zip` | "mod_mdid" | null |
| `mod_media` | `component_in_zip` | "mod_media" | null |
| `mod_mythtranscode` | `component_in_zip` | "mod_mythtranscode" | null |
| `mod_offlinesession` | `component_in_zip` | "mod_offlinesession" | null |
| `mod_pdfpager` | `component_in_zip` | "mod_pdfpager" | null |
| `mod_pdfparts` | `maturity_in_zip` | "MATURITY_RC" | null |
| `mod_pdfparts` | `component_in_zip` | "mod_pdfparts" | null |
| `mod_playlist` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_playlist` | `component_in_zip` | "mod_playlist" | null |
| `mod_poasassignment` | `maturity_in_zip` | "MATURITY_RC" | null |
| `mod_sookooroo` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_sookooroo` | `component_in_zip` | "mod_sookooroo" | null |
| `mod_tiplayer` | `component_in_zip` | "mod_tiplayer" | null |
| `mod_videochat` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_videochat` | `component_in_zip` | "mod_videochat" | null |
| `mod_videoconference` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_videoconference` | `component_in_zip` | "mod_videoconference" | null |
| `mod_videoconsultation` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_videoconsultation` | `component_in_zip` | "mod_videoconsultation" | null |
| `mod_videofile` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `mod_videofile` | `component_in_zip` | "mod_videofile" | null |
| `mod_webex` | `component_in_zip` | "mod_webex" | null |
| `mod_znanja` | `dependencies_in_zip` | {"mod_scorm": "ANY_VERSION"} | {} |
| `mod_znanja` | `maturity_in_zip` | "MATURITY_BETA" | null |
| `mod_znanja` | `component_in_zip` | "mod_znanja" | null |

#### release_no_literal (3)

Mismo ZIP byte a byte. `$plugin->release` no es un literal entre comillas: o es una expresion PHP concatenada (ej. `'2.3 (Build: '.$plugin->version.')'`, donde la descarga original guardo solo el primer fragmento) o un numero sin comillas (ej. `0.2`). El reproducido solo acepta literales entre comillas y lo deja en null. release_in_zip es informativo y no se usa aguas abajo.

| componente | campo | original | reproducido |
|---|---|---|---|
| `block_bfwpub` | `release_in_zip` | "2.3 (Build: " | null |
| `local_confseed` | `release_in_zip` | "0.2" | null |
| `repository_typo3` | `release_in_zip` | "0.0.1 (Build: " | null |

#### acceso_cambiado (1)

Cambio el codigo HTTP para la misma URL (por ejemplo un plugin de pago que paso a ser gratuito, o un artefacto retirado). Depende del servidor, no del procedimiento.

| componente | campo | original | reproducido |
|---|---|---|---|
| `format_periods` | `version_in_zip` | 2017102700 | null |
| `format_periods` | `requires_in_zip` | 2017050300 | null |
| `format_periods` | `dependencies_in_zip` | {} | null |
| `format_periods` | `maturity_in_zip` | "MATURITY_STABLE" | null |
| `format_periods` | `release_in_zip` | "3.3.1" | null |
| `format_periods` | `component_in_zip` | "format_periods" | null |
| `format_periods` | `zip_sha256` | "dd46a83d4ee2e69728f77227da630a9d6692e59df3439565804f15e0... | null |
| `format_periods` | `zip_md5_matched_published` | true | null |
| `format_periods` | `http_status` | 200 | 401 |
| `format_periods` | `agrees_with_pluglist` | true | null |

## Impacto aguas abajo

09_merge_zip_residual.py solo escribe la fuente ZIP en el grafo para los plugins en los que GitHub no encontro ningun `version.php` (`dep_source_ref IS NULL`), y de cada fila usa `version_in_zip`, `requires_in_zip`, `agrees_with_pluglist`, `http_status`, `note`, `dependencies_in_zip`. Para cada fila con diferencias:

| componente | categoria | GitHub encontro version.php | la fusion usa la fila ZIP | campos de la fusion que difieren |
|---|---|---|---|---|
| `format_periods` | acceso_cambiado | si | no | `version_in_zip`, `requires_in_zip`, `agrees_with_pluglist`, `http_status`, `note`, `dependencies_in_zip` |
| `mod_alternative` | parser_module_legacy | no | si | - |
| `mod_amvonetroom` | parser_module_legacy | no | si | - |
| `mod_babelroom` | parser_module_legacy | no | si | - |
| `mod_cooradbridge` | parser_module_legacy | no | si | - |
| `mod_courseprovider` | parser_module_legacy | no | si | - |
| `mod_customlesson` | parser_module_legacy | si | no | - |
| `mod_dinsysconnect` | parser_module_legacy | no | si | - |
| `mod_ecampusbookpage` | parser_module_legacy | si | no | `dependencies_in_zip` |
| `mod_eduvision` | parser_module_legacy | no | si | - |
| `mod_engagement` | parser_module_legacy | si | no | - |
| `mod_ensemblecontent` | parser_module_legacy | no | si | - |
| `mod_etherpad` | parser_module_legacy | no | si | - |
| `mod_flax` | parser_module_legacy | no | si | - |
| `mod_forumanon` | parser_module_legacy | no | si | - |
| `mod_furnace` | parser_module_legacy | no | si | - |
| `mod_guidedquiz` | parser_module_legacy | no | si | - |
| `mod_kitmoo` | parser_module_legacy | no | si | - |
| `mod_languagelab` | parser_module_legacy | si | no | - |
| `mod_linkbazaar` | parser_module_legacy | si | no | - |
| `mod_livestreaming` | parser_module_legacy | no | si | - |
| `mod_mdid` | parser_module_legacy | si | no | - |
| `mod_media` | parser_module_legacy | no | si | - |
| `mod_mythtranscode` | parser_module_legacy | si | no | - |
| `mod_offlinesession` | parser_module_legacy | si | no | - |
| `mod_pdfpager` | parser_module_legacy | no | si | - |
| `mod_pdfparts` | parser_module_legacy | si | no | - |
| `mod_playlist` | parser_module_legacy | si | no | - |
| `mod_poasassignment` | parser_module_legacy | no | si | - |
| `mod_sookooroo` | parser_module_legacy | si | no | - |
| `mod_tiplayer` | parser_module_legacy | no | si | - |
| `mod_videochat` | parser_module_legacy | no | si | - |
| `mod_videoconference` | parser_module_legacy | no | si | - |
| `mod_videoconsultation` | parser_module_legacy | no | si | - |
| `mod_videofile` | parser_module_legacy | si | no | - |
| `mod_webex` | parser_module_legacy | no | si | - |
| `mod_znanja` | parser_module_legacy | no | si | `dependencies_in_zip` |
| `block_bfwpub` | release_no_literal | no | si | - |
| `local_confseed` | release_no_literal | si | no | - |
| `repository_typo3` | release_no_literal | no | si | - |

**Filas cuya diferencia llegaria al grafo si se usara el reproducido en lugar del original: 1.** El original sigue siendo el archivo de todos los resultados.

## Como reproducir

```bash
python3 src/collect/06_zip_version_php.py          # ~3 h: 979 peticiones a 10 s (Crawl-delay del robots.txt)
python3 src/collect/06b_compare_zip.py             # escribe este documento
```

Los ZIP quedan en `data/raw/zips/cache/` (fuera de git); una segunda ejecucion lee de la cache y no vuelve a pedir nada al servidor (`--offline` lo garantiza).
