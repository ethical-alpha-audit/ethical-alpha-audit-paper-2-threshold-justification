# Claim Boundary Statement

## What this repository claims

This repository faithfully renders and explains the content of Paper 3: "Beyond 'Magic Numbers': A Threshold Justification Stack for Clinical AI Governance." Specifically:

1. **RC-1:** The three core manuscript tables (failure mechanisms, TJS specification, framework comparison) are rendered as structured CSV files from JSON source data extracted from the manuscript text.
2. **RC-2:** A consolidated glossary of key terms is provided, with all definitions sourced from the manuscript.
3. **RC-3:** TJS layers are mapped to NHS governance artefacts as specified in Supplementary Appendix G.
4. **RC-4:** Two illustrative TJS record structures demonstrate the proposed audit schema, constructed from the manuscript's worked examples.
5. **RC-5:** All notebook outputs are deterministic and hash-locked.

## What this repository does NOT claim

The following results are referenced in the Paper 3 Discussion section as supporting context from companion papers. They are **NOT reproduced, computed, or validated in this repository.**

| ID | Excluded Result | Source Paper | Manuscript Location |
|----|----------------|--------------|---------------------|
| XC-1 | 91.7% sensitivity (11/12 cases rejected) | Paper 4 | Discussion: "Consistent Signals From Historical Replay" |
| XC-2 | 95.8% verdict stability under perturbation (46/48) | Paper 4/5 | Discussion: "Companion studies provide..." |
| XC-3 | 480/480 dual-dataset structural invariance | Paper 4 | Discussion: "Companion studies provide..." |
| XC-4 | TP=20, TN=12 confusion matrix | Paper 4 | Discussion: "Companion studies provide..." |
| XC-5 | Safety gate most frequently binding (83%) | Paper 4 | Discussion: "Consistent Signals From Historical Replay" |
| XC-6 | 0.40–0.45 cliff-edge region for safety gate | Paper 4/5 | Discussion: "Threshold sensitivity analysis" |
| XC-7 | Any empirical validation of the TJS framework | Not performed | Throughout: "normative proposal without empirical validation" |
| XC-8 | Any normative authority of the illustrative JSON schemas | Not claimed | Notebook 03 epistemic notice |

## Why these exclusions matter

Paper 3 is a **conceptual synthesis and normative governance proposal**. It proposes the TJS framework but explicitly states that empirical validation has not been conducted. The companion-paper results cited in the Discussion provide context but are not Paper 3's own scientific contributions. Reproducing them here would misrepresent the epistemic boundaries of the paper.

## Where to find the companion results

- **Paper 4 results (XC-1 through XC-6):** See the Paper 4 reproducibility repository (ethical-alpha-audit-paper-4-historical-replay)
- **Paper 5 results:** See the Paper 5 reproducibility repository (when available)
- **Empirical validation (XC-7):** Requires the pilot study described in the manuscript's Discussion section; this has not been conducted.

## Enforcement mechanisms

- Per-notebook epistemic notices (Notebooks 01, 02, 03)
- Elevated epistemic notice in Notebook 03 for illustrative schemas
- `_epistemic_status` field in all schema JSON files
- `_caveat` field in all interpretive table JSON files
- This document
