# Beyond 'Magic Numbers': A Threshold Justification Stack for Clinical AI Governance

[![DOI](https://zenodo.org/badge/1194630564.svg)](https://doi.org/10.5281/zenodo.19499797)

> **Paper 3** of the Ethical Alpha Audit research programme
>
> Author: Walter Brown — Ethical Alpha Audit
> ORCID: [0000-0002-6050-8522](https://orcid.org/0000-0002-6050-8522)

## Reviewer quick validation (no execution required)

```bash
python scripts/validate_outputs.py
```

**Expected result:** `VALIDATION PASSED`

This checks every output file against its pinned SHA-256 digest. No notebook execution, no dependencies beyond Python stdlib. A passing result confirms the checked-in outputs are byte-identical to those produced by the deterministic pipeline.

**To re-execute the full pipeline** (requires dependencies):

```bash
pip install -r requirements.txt
python reproduce_all.py
```

## What this repository contains

This is a **conceptual framework repository**, not a computational experiment repository. Paper 3 proposes the tiered Threshold Justification Stack (TJS) through conceptual synthesis and regulatory analysis. No primary data were generated.

This repository provides:

| Component | Description |
|-----------|-------------|
| 3 manuscript tables | Structured renderings of Tables 1–3 (failure mechanisms, TJS specification, framework comparison) |
| 2 governance mappings | TJS-to-NHS artefact crosswalk and gaming resistance pathways |
| 1 glossary | Consolidated key term definitions from the manuscript |
| 2 illustrative TJS records | Proposed JSON schema for Primary Safety (6-layer) and Secondary Operational (3-layer) threshold documentation |
| 4 Jupyter notebooks | Explanatory notebooks rendering the above from structured JSON source data |
| Deterministic harness | Full execution, hashing, validation, and HTML export pipeline |

## What this repository does NOT contain

- No computational engine (the governance engine belongs to the Paper 4 repository)
- No datasets (no primary data were generated for this conceptual synthesis)
- No figures (the manuscript contains no figures)
- No companion-paper numerical results (see `docs/claim_boundary_statement.md`)
- No simulation or statistical analysis

## Repository structure

```
manuscript/         Canonical manuscript and supplementary materials (.docx)
data/tables/        Structured JSON data extracted from manuscript tables
data/schemas/       Illustrative TJS record structures (proposed, not validated)
notebooks/          4 Jupyter notebooks (explanatory, not experimental)
scripts/            Execution harness (notebook runner, hash validator, HTML export)
config/             Determinism settings, expected outputs, trace map
outputs/            Generated tables (CSV) and rendered schemas (JSON), hash-locked
docs/               Methods, provenance, reproducibility, claim boundary statement
docs/html/          Static HTML exports for reading without code
tests/              Structural and data integrity checks
```

## Notebooks

| # | Notebook | Purpose |
|---|----------|---------|
| 01 | TJS Framework and Failure Mechanisms | Render Table 1 (failure mechanisms), Table 2 (TJS specification), tier classification logic |
| 02 | Framework Comparison and Mappings | Render Table 3 (comparison matrix), NHS governance mapping, glossary |
| 03 | TJS Record Schema Demonstration | Load and display illustrative JSON TJS records for both tiers |
| 04 | Release Validation | Verify repository structure, data integrity, output presence |

For code-free reading, see `docs/html/`.

## Claim boundary

This repository renders and explains the Paper 3 manuscript. It does **not** reproduce numerical results from companion papers (Papers 1, 4, or 5). The Discussion section of the manuscript cross-references companion findings (e.g. 91.7% sensitivity, perturbation stability); these results belong to their respective repositories and are explicitly excluded here. See `docs/claim_boundary_statement.md` for the full exclusion register.

## Citation

See `CITATION.cff` for machine-readable citation metadata.

## Licence

MIT — see `LICENSE`.
