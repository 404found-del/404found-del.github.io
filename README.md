# dataarchitect.studio

Source for **[dataarchitect.studio](https://dataarchitect.studio)** — essays and
field notes on data architecture: dimensional modelling, the lakehouse, open
table formats, data contracts, and the craft of making information trustworthy.

A Jekyll site on GitHub Pages. No theme gem, no JavaScript framework, no
tracking beyond privacy-friendly page counts.

## Layout

| Path | What it is |
|---|---|
| `_posts/` | Essays. `YYYY-MM-DD-slug.md`, served at `/essays/:slug/` |
| `_patterns/` | Architecture patterns catalog, `/patterns/:name/` |
| `_glossary/` | Term definitions, `/glossary/:name/` |
| `benchmarks/` | Reproducible benchmark scripts and their raw results |
| `_layouts/`, `_includes/` | Templates |
| `llms.txt`, `llms-full.txt` | Machine-readable index and full text, for AI retrieval |

## Benchmarks

Numbers published on the site come from scripts in `benchmarks/`, committed
alongside the raw results file each one produced. The datasets are generated
from fixed seeds, so a rerun operates on identical bytes.

```bash
pip install pyarrow fastavro duckdb cramjam
python3 benchmarks/file-format-benchmark.py --rows 3000000 --trials 3
```

If you rerun one and get materially different results, that is worth knowing —
please [open an issue](https://github.com/404found-del/404found-del.github.io/issues).
One published essay already corrects an earlier claim on this site because
measurement contradicted it; that is the intended failure mode, not an
embarrassment.

## Building locally

```bash
bundle install
bundle exec jekyll serve
```

**Note on Jekyll versions.** `Gemfile` targets Jekyll 4.x. Confirm which
pipeline is actually deploying before assuming local output matches production:
GitHub Pages' legacy branch build pins Jekyll 3.x via the `github-pages` gem,
while `.github/workflows/pages.yml` builds with the Gemfile's version. Check
the `generator` meta tag on a live page to see which one is in force.

## Contributing

Corrections are genuinely welcome, especially factual ones —
[open an issue](https://github.com/404found-del/404found-del.github.io/issues).
Essays get corrected in place with the change noted, rather than quietly edited.

## Licence

Two different terms, see [LICENSE](LICENSE): the code is MIT, so you can run and
modify the benchmarks freely. The essays are copyright — quote them with
attribution, but please don't republish them wholesale.
