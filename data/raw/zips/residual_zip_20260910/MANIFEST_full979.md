# ZIP-declared version.php facts — full run, 2026-09-10

This is the **second source** we
agreed on: values read out of the plugin archives published by the
marketplace, not another read of the GitHub tree, so it does not share the
provenance of either of our earlier measurements.

This supersedes the 100-row pilot (`zip_version_php.jsonl`, sha256
`eeb4cd61…45b7`, sent earlier today). Same fields, same method, whole
population.

## Population

**All 979** of the residual plugins we reconciled to on 2026-09-08 — the ones
with no exact match between a GitHub `version.php` and the newest published
release. Not a sample.

Source host: `marketplace.moodle.com`, path
`/api/plugins/<component>/versions/<version>/download`.
Its robots.txt is `User-agent: *` + `Crawl-delay: 10` with no `Disallow`;
fetched **sequentially at 10 s spacing** with an identifying User-Agent, on
the shared egress IP 200.118.16.101. Total transfer **0.82 GB**; wall clock
**2.9 hours**, which is almost entirely the mandated pacing (979 x 10 s) —
actual fetch time was under 15 minutes.

## Numbers

| | |
|---|---|
| rows | 979 |
| `version.php` found **and** a version integer read from it | 901 |
| ZIP version **equals** the pluglist newest version | 884 |
| ZIP version **differs** from pluglist | 17 |
| valid ZIP with **no `version.php` at all** | 10 |
| **paid/private** — HTTP 401, archive not served anonymously | 66 |
| other HTTP or transport error | 0 |
| archive over the 250 MB per-file cap, not opened | 0 |
| md5 matched the published md5 | 913 |

**The residual does not close to zero, and the two reasons are structural.**

1. **Paid plugins return HTTP 401.** They are listed in the feed with a
   downloadurl and a published md5, but the archive is entitlement-walled.
   Not retryable, not a pacing problem.
2. **Pre-2.0 plugins ship no `version.php`.** The Moodle 1.9 convention put
   the version inside the block/module class, and old themes put it in
   `config.php`. `block_amazon` (2008120401) and `theme_allc` are the worked
   examples — valid archives, md5 verified, no such file anywhere in them.

**Measured ceiling: 92.0%** of the 979 (paid archives and the pre-2.0 ones
account for the rest). The pilot's projection of "96-99%" was optimistic — it
extrapolated 2 paid plugins in 100 to ~20 in 979, and the real figure is 66.
Quote the measured number, not the projection.

## Fields

Every row carries the source of its own claim:

- `zip_sha256` — checksum of the archive the values were read from
- `version_php_sha256` — checksum of the `version.php` blob itself
- `version_php_path` — where in the archive it was found
- `zip_md5_matched_published` — whether the archive matched the md5 the
  marketplace publishes for that version (`null` when not checked)
- `agrees_with_pluglist` — `version_in_zip == pluglist_declared_version`;
  `null` when there was nothing to compare
- `note` — why a row has no parsed version, when it has none

**A bug we found and fixed before sending this.** The file picker tested
`name.endswith("version.php")`, which also matches `check_conversion.php`,
`package_version.php` and `get_version.php`. Four archives
(`local_yukaltura`, `local_yumymedia`, `local_zilink`, `mod_amvonetroom`)
picked one of those, found no `$plugin->version` in it, and were recorded as
"declares no version" — a wrong fact manufactured out of a substring match.
All four do ship a real `version.php`. The picker now requires the basename to
be exactly `version.php`, and those four archives were re-fetched and re-read.
If you ran the same suffix test anywhere, it has the same four false
negatives.

**One field renamed since the pilot:** `zip_truncated_at_60mb_cap` is now
`zip_truncated_at_cap`. The per-file cap was raised from 60 MB to 250 MB for
this run (the pilot truncated one archive), so the old name would have been a
lie about which threshold applied. Nothing else changed shape.

## Standing figures

Residual **979** newest-exact / **826** any-release, as reconciled 2026-09-08.
Earlier totals of 2.2 GB and 670 MB for this run were **void** — both were
extrapolated from a mean over a distribution one outlier dominates. The
measured total is in the Population section above; quote that, not an
extrapolation.
