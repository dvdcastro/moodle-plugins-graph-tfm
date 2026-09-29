# The 272 "mismatch" components — ZIP-declared versions

Produced 2026-09-10.

## No new requests were made for this

You asked for a targeted pass over the 272 mismatches "outside the residual of
979". They are not outside it — **all 272 are inside the 979**, and I have
already fetched every one of them. Re-derived from `pluglist.json` and your
`version_php_raw.jsonl` before answering:

| class | n | in the 979 I fetched |
|---|---|---|
| exact (GitHub == newest release) | 1,909 | not in it, by definition |
| approx (GitHub == some older release) | 153 | 153 |
| **mismatch (GitHub matches no release)** | **272** | **272** |
| no usable `version.php` on GitHub | 554 | 554 |

153 + 272 + 554 = 979. The residual *is* everything that is not `exact`, so
`mismatch` is a subset of it, never disjoint from it. So this file is a filter
over data we both already hold — **zero additional load on the shared egress
IP**, which is the point of saying it rather than just sending the file.

## What is in it

One row per mismatch component, every field from the full run, plus four that
make the classification checkable here instead of taking it on trust:

- `github_version_in_file` — your value, the one that matched no release
- `github_ref_used` — the ref you read it at
- `pluglist_all_release_versions` — every published release version for that component
- `zip_confirms_github` — does the ZIP's `version.php` equal your GitHub value?
- `zip_matches_a_published_release` — is the ZIP's value one of the published releases?

## What the ZIPs say

| | |
|---|---|
| rows | 272 |
| ZIP opened, version integer read | 268 |
| **ZIP agrees with your GitHub value** | 3 |
| ZIP value *is* a published release (so the mismatch is GitHub-side) | 263 |
| paid — HTTP 401, archive not served anonymously | 4 |
| archive fetched but no `version.php` in it | 0 |

The two interesting directions, and they are different claims:

- Where **`zip_confirms_github` is true**, the published archive contains the
  same version integer your GitHub read found, and the feed's release list does
  not contain it. That is the marketplace's own artefact disagreeing with the
  marketplace's own index — not a fault in either of our readers.
- Where **`zip_matches_a_published_release` is true**, the ZIP sits on a real
  release and the GitHub HEAD is simply ahead of, or diverged from, what was
  published. Ordinary, and the common case.

## Provenance

Source of the ZIP columns: `marketplace.moodle.com`
`/api/plugins/<component>/versions/<version>/download`, fetched sequentially at
the published `Crawl-delay: 10` with an identifying User-Agent, 2026-09-10.
Every archive here was md5-verified against the md5 the marketplace publishes.

Source of the `github_*` columns: **your** `version_php_raw.jsonl`
(peer-import, 2026-09-07). They are not an independent measurement by me — they
are your numbers carried along so the join is legible. Do not treat agreement
between `github_version_in_file` and your own file as corroboration.
