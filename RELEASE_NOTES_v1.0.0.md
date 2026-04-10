# Release Notes v1.0.0

Initial release of the Paper 3 reproducibility repository.

## Contains

- Structured renderings of all 3 manuscript tables (failure mechanisms, TJS specification, framework comparison)
- NHS governance artefact mapping (TJS layers to existing NHS trust processes)
- Gaming resistance pathways (3 exploitation pathways from Supplementary Appendix F)
- Consolidated key term glossary (~20 terms)
- 2 illustrative TJS record schemas (Primary Safety 6-layer, Secondary Operational 3-layer)
- 4 Jupyter notebooks with epistemic notices and manuscript caveat propagation
- Deterministic execution harness with SHA-256 hash-locked outputs
- Code-collapsed HTML exports for academic readers
- Claim boundary statement documenting excluded companion-paper results

## Does not contain

- No computational engine (belongs to Paper 4 repository)
- No benchmark datasets (no primary data generated)
- No figures (manuscript contains no figures)
- No companion-paper numerical results

## Known limitations

- Tables 1–3 were manually reconstructed from manuscript paragraph text (the .docx does not contain Word table objects). Each JSON data file includes a `_provenance` field for cross-checking.
- Illustrative TJS record schemas are proposed structures, not validated or adopted standards. Each schema file includes an `_epistemic_status` field.
- The glossary aims to be comprehensive but may not capture every defined term in the manuscript.
