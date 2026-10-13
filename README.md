# Côte d'Ivoire (CI) — législation en Markdown

Part of [LawCodex](https://github.com/LawCodex): the legislation of every country as plain Markdown in git.

Constitutions and laws of the Republic of Côte d'Ivoire, in **French** (official language), from official
sources: the **Conseil constitutionnel** (constitutions) and the **Assemblée nationale** (laws published in the
"LOIS" section of www.assnat.ci). Texts are as enacted / as published (not consolidated).

Retrieved 2026-10-13.

<!-- COUNTS -->
| Directory | Files |
|---|---|
| `constitution/` | 3 |
| `lois/` | 68 |
| **Total** | **71** |
<!-- /COUNTS -->

## Structure

```
constitution/constitution-2016.md   Constitution of 8 November 2016 (loi n° 2016-886) — in force
constitution/constitution-2000.md   Constitution of 1 August 2000 (loi n° 2000-513) — historical
constitution/constitution-1960.md   Constitution of 3 November 1960 — historical
lois/<year>/loi-<number>.md          laws (year of the law; `undated` when neither the page nor the PDF gives a number/date)
lois/undated/<slug>.md               laws whose number could not be determined (slug of the title given by the Assemblée)
```

Front matter: `identifier` = law number when known; `date` = date of the law when it could be parsed;
`source` = PDF URL; `record` = Assemblée nationale page of the law; `status` is `unknown` for laws (the source does
not say whether a law is still in force).

Headings: TITRE / CHAPITRE / SECTION → `##`…; articles are headings (`Article N`). Text is extracted from PDFs with
poppler; scanned pages are OCRed with tesseract (French) and marked `OCR` in `note`.

## Sources

| Source | URL | Used for |
|---|---|---|
| Conseil constitutionnel de Côte d'Ivoire | https://www.conseil-constitutionnel.ci/lois-et-decrets/la-constitution | the three constitutions (PDF) |
| Assemblée nationale de Côte d'Ivoire — rubrique LOIS | https://www.assnat.ci/?-lois-82- | laws (one page per law with a PDF) |

## Not covered / known gaps

* **Partial corpus.** The Assemblée nationale publishes only ~130 laws (mostly 2011–2020, many being laws
  authorising ratification of treaties or ratifying ordinances); about 50 law pages have no PDF attached and are
  missing. There is no official online consolidated database of Ivorian legislation reachable from outside the
  country: the Journal officiel website (journal-officiel.ci / jo.gouv.ci) did not answer, and the Secrétariat
  général du Gouvernement "documenthèque" (www.sgg.gouv.ci) offers only a few dozen decrees/ordinances with many broken
  links, so it was not used.
* The 2016 Constitution text is the original version; the constitutional revision of 2020 (loi constitutionnelle
  n° 2020-348 du 19 mars 2020) is not incorporated. The Assemblée's own constitution link (CONSTITUTION.pdf) and the
  Code électoral link are broken (HTTP 404).
* Codes (civil, pénal, travail, OHADA uniform acts...), ordinances and decrees are not included except where the
  Assemblée published a ratification law with the text annexed.

## Copyright

Official texts (laws, constitution) of Côte d'Ivoire are published by public institutions for public information;
the sites used state no restriction on reuse. The Markdown conversion is provided as is; the authoritative texts are
those published in the Journal officiel de la République de Côte d'Ivoire.

## Regenerating

```sh
python3 -m pip install -r scripts/requirements.txt   # plus poppler-utils and tesseract (+ fra traineddata)
python3 scripts/ci_fetch.py      # downloads to ../_raw/ci/ (cached) and writes the Markdown
python3 scripts/ci_readme.py     # updates the counts table
```
