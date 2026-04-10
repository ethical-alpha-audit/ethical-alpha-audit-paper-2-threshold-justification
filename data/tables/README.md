# Data Tables

This directory contains structured JSON representations of content published in the Paper 3 manuscript and supplementary materials. These files are the deterministic inputs for the Jupyter notebooks.

## Provenance

All files were **manually extracted** from the manuscript text, not computationally derived. The manuscript .docx files do not contain Word table objects; tables are embedded as inline text paragraphs. Each JSON file therefore represents a structured reconstruction of paragraph content.

Every JSON file includes:
- A `_provenance` field citing the exact manuscript location (paragraph numbers or appendix)
- A `_caveat` field (where applicable) reproducing the manuscript's own interpretive caveats

## Files

| File | Manuscript Source | Description |
|------|-------------------|-------------|
| `table1_failure_mechanisms.json` | Results, Table 1 | Six structural failure mechanisms with descriptions, sources, and governance gaps |
| `table2_tjs_specification.json` | Results, Table 2 | TJS six-layer specification with tier requirements and regulatory counterparts |
| `table3_framework_comparison.json` | Results, Table 3 | Comparison matrix: 7 governance frameworks across 8 documentation dimensions |
| `glossary.json` | Throughout manuscript | Consolidated key term definitions |
| `nhs_governance_mapping.json` | Supplementary Appendix G | TJS layer mapping to existing NHS governance artefacts |
| `gaming_resistance_pathways.json` | Supplementary Appendix F | Three concrete gaming exploitation pathways |

## Epistemic status

These files are faithful representations of published manuscript content. They do not introduce new scientific claims. Cross-check against the manuscript .docx files in `manuscript/` for verification.
