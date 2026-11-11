# Publication and BibTeX workflow

`data/publications.json` is the single source of truth for BibTeX records. Do not edit `bibtex.html` or `publications.bib` directly; they are generated files.

## Add a new paper

For a paper with a DOI:

```bash
python3 scripts/add_publication.py --category journal --doi 10.xxxx/xxxxx
```

For an arXiv preprint:

```bash
python3 scripts/add_publication.py --category conference --arxiv 2604.05704
```

Use `--category journal` for the next permanent `J` number and `--category conference` for the next permanent `C` number. The script retrieves available metadata, assigns the next identifier, updates `data/publications.json`, and regenerates both visitor-facing BibTeX files.

## Regenerate BibTeX after a manual correction

```bash
python3 scripts/generate_bibtex.py
```

The generated [BibTeX page](bibtex.html) supports copying individual records and links to `publications.bib` for downloading all records.

Review new metadata before committing, especially authors, venue, volume, pages, and publication year. DOI records are retrieved from Crossref; arXiv records are retrieved from arXiv.
