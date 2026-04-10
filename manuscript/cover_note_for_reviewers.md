# Cover Note for Reviewers

## Repository Purpose

This repository accompanies Paper 3: "Beyond 'Magic Numbers': A Threshold Justification Stack for Clinical AI Governance." It provides structured, reproducible renderings of manuscript content to support reviewer assessment and reader understanding.

**This is a conceptual framework repository, not a computational experiment repository.** Paper 3 proposes the tiered Threshold Justification Stack through conceptual synthesis and regulatory analysis. No primary data were generated; no computational experiments were performed.

## What the notebooks do

| Notebook | Function |
|----------|----------|
| 01 | Renders Tables 1 and 2 from structured JSON and walks through the tier classification logic |
| 02 | Renders Table 3 (framework comparison), NHS governance mapping, gaming resistance pathways, and glossary |
| 03 | Displays illustrative TJS record schemas for both threshold tiers |
| 04 | Validates repository structure and output integrity |

## Quick validation (no dependencies required)

```bash
python scripts/validate_outputs.py
```

A result of `VALIDATION PASSED` confirms that checked-in outputs match their pinned SHA-256 hashes.

## Claim boundary

The Discussion section of the manuscript cross-references numerical results from companion papers (Papers 1, 4, and 5). **These results are NOT reproduced in this repository.** See `docs/claim_boundary_statement.md` for the full exclusion register.

## Illustrative schemas

Notebook 03 demonstrates proposed TJS record structures as JSON. These are **illustrative proposed structures** constructed from the manuscript's worked examples. They are not validated standards and should not be interpreted as adopted specifications.
