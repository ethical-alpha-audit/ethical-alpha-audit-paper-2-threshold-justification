# Provenance

## Data files

All structured data in this repository derives from the Paper 2 manuscript and supplementary materials.

| File | Source | Extraction Method |
|------|--------|-------------------|
| `data/tables/table1_failure_mechanisms.json` | Manuscript Results, Table 1 | Manual extraction from paragraph text |
| `data/tables/table2_tjs_specification.json` | Manuscript Results, Table 2 | Manual extraction from paragraph text |
| `data/tables/table3_framework_comparison.json` | Manuscript Results, Table 3 | Manual extraction from paragraph text |
| `data/tables/glossary.json` | Throughout manuscript | Manual consolidation of defined terms |
| `data/tables/nhs_governance_mapping.json` | Supplementary Appendix G | Manual extraction from appendix text |
| `data/tables/gaming_resistance_pathways.json` | Supplementary Appendix F | Manual extraction from appendix text |
| `data/schemas/tjs_record_primary_safety.json` | Committee vignette + Table 2 | Constructed from manuscript descriptions |
| `data/schemas/tjs_record_secondary_operational.json` | Alert system example + Table 2 | Constructed from manuscript descriptions |

## Schema demonstration provenance

The two illustrative TJS record schemas in `data/schemas/` are constructed from the manuscript's worked examples and Table 2 specifications. They are proposed structures demonstrating how TJS documentation might be encoded, not validated or adopted standards. See the `_epistemic_status` field in each file.

## Companion paper cross-references

The Paper 2 Discussion section references numerical results from companion papers. These results are **documented here for context only** and are **not reproduced in this repository**:

- **Paper 1** (Positioning): Evidence enrichment pipeline, canonical dataset construction
- **Paper 4** (Historical Replay): 91.7% sensitivity (11/12), confusion matrix (TP=20, TN=12), perturbation stability, gate ablation
- **Paper 5** (Parameter/Evidence Sensitivity): Simulation results, sensitivity analysis

See `docs/claim_boundary_statement.md` for the full exclusion register.

## Harness scripts provenance

The four scripts in `scripts/` are adopted from the Paper 4 golden exemplar repository (I5) without modification. They implement a generic deterministic notebook execution and validation harness.
