# Claim Traceability Matrix

**Repo:** ethical-alpha-audit-paper-3-framework-comparison  
**Updated:** 2026-04-12 (Engineer session — manuscript text grounded in `inputs/manuscript.pdf` extract + `docs/claim_boundary_statement.md`)  
**Claims:** 20 manuscript- and scope-grounded items | **Verified:** traceability links assigned (execution verified via `python reproduce_all.py`)

This matrix maps **Paper 3 manuscript claims** and **repository fidelity statements** to notebooks, data artefacts, and outputs. It does not restate excluded companion-paper results (see `docs/claim_boundary_statement.md`).

## Manuscript-grounded claims (conceptual / methodological)

| Claim ID | Claim (paraphrase, faithful to manuscript) | Manuscript anchor (section / artefact) | Notebook / code | Output / evidence path | Status |
|----------|---------------------------------------------|----------------------------------------|-----------------|-------------------------|--------|
| P3-C01 | Clinical AI governance often operationalises safety via quantitative thresholds whose methodological rationale is undocumented (“magic numbers”). | Introduction; “What is already known” | `notebooks/01_tjs_framework_and_failure_mechanisms.ipynb` | Narrative setup; `data/tables/table1_failure_mechanisms.json` context | Traced |
| P3-C02 | Conceptual synthesis identified **six** structural failure mechanisms in threshold design (proxy thresholding; context collapse; threshold coupling; boundary gaming; epistemic asymmetry; audit–lifecycle disconnect). | Results; Table 1 | `01_…ipynb` | `outputs/tables/table1_failure_mechanisms.csv` | Traced |
| P3-C03 | Methods combine **conceptual synthesis and regulatory analysis** (targeted searches, Jan 2018–Dec 2025; structural inclusion criterion). | Methods | `01_…ipynb` (epistemic notice); `manuscript/Paper3_Manuscript.docx` | `data/tables/table1_failure_mechanisms.json` (`_caveat`) | Traced |
| P3-C04 | The six mechanisms are argued **structurally distinct** and to cover **major** structural failure modes; **not claimed exhaustive**; inter-rater exercise proposed. | Methods (Reproducibility subsection) | `01_…ipynb` | JSON `_caveat` on interpretive tables | Traced |
| P3-C05 | **Regulatory alignment** assessments are **interpretive inferences** by the author, not statements of regulatory intent or legal requirement. | Methods | `01_…ipynb`; `02_…ipynb` | Table JSON `_caveat` fields | Traced |
| P3-C06 | **Threshold Justification Stack (TJS)** specifies **six documentation layers** with **tiered** requirements: **Primary Safety** (failure can directly harm patients) vs **Secondary Operational**; **Primary** applies by default when uncertain. | Results; Table 2 | `01_…ipynb` | `outputs/tables/table2_tjs_specification.csv` | Traced |
| P3-C07 | Table 2 documents each TJS layer (description, mechanisms addressed, tier requirement, regulatory counterpart). | Table 2 | `01_…ipynb` | `data/tables/table2_tjs_specification.json` → CSV | Traced |
| P3-C08 | Table 3 compares TJS threshold documentation expectations to other governance instruments; **all characterisations interpretive**. | Results; Table 3 | `02_…ipynb` | `outputs/tables/table3_framework_comparison.csv` | Traced |
| P3-C09 | TJS is positioned to **augment** NHS clinical risk management under **DCB0129/0160**, not replace hazard logs. | Discussion / integration | `02_…ipynb` (mappings); `03_…ipynb` | Narrative in notebooks; `outputs/tables/nhs_governance_mapping.csv` | Traced |
| P3-C10 | Hospital integration entails procedural changes (tier classification; populate layers; route record to committee); field mapping to audit schemas in **Supplementary Appendix C** (see supplementary PDF). | Discussion | `02_…ipynb`; `03_…ipynb` | `inputs/supplementary.pdf`; schema demos | Traced |
| P3-C11 | **Gaming resistance** pathways and assessment methodology are detailed in **Supplementary Appendix F**. | Results / Discussion | `02_…ipynb` | `outputs/tables/gaming_resistance_pathways.csv`; `inputs/supplementary.pdf` | Traced |
| P3-C12 | **NHS governance artefact mapping** is specified in **Supplementary Appendix G** (see supplementary PDF). | Supplementary (referenced in manuscript) | `02_…ipynb` | `outputs/tables/nhs_governance_mapping.csv`; `inputs/supplementary.pdf` | Traced |
| P3-C13 | **Full worked examples** for **both** threshold tiers appear in **supplementary appendices**. | Abstract; Methods | `03_…ipynb` | `outputs/schemas/*_rendered.json`; supplementary | Traced |
| P3-C14 | **Empirical validation** (e.g. inter-rater reliability; feasibility pilot with **median completion time** and **kappa** for tier classification) is **required** before scalability claims. | Conclusions; Discussion | `04_…ipynb` (scope checks); `docs/claim_boundary_statement.md` | QA harness; boundary doc XC-7 | Traced |
| P3-C15 | TJS is advanced as a **normative governance proposal**; adoption at scale requires **empirical feasibility** assessment. | Abstract; Discussion | `01_…ipynb`; `03_…ipynb` (epistemic notices) | Schema `_epistemic_status` | Traced |

## Repository fidelity claims (reproduction scope — `docs/claim_boundary_statement.md`)

| Claim ID | Claim | Source doc | Notebook / script | Output / artefact | Status |
|----------|-------|------------|--------------------|-------------------|--------|
| P3-C16 | Manuscript **Tables 1–3** rendered as structured **CSV** from **JSON** sources extracted from the manuscript text. | RC-1 | `01_…ipynb`, `02_…ipynb` | `outputs/tables/table1_failure_mechanisms.csv`, `table2_tjs_specification.csv`, `table3_framework_comparison.csv` | Traced |
| P3-C17 | **Glossary** of key terms consolidated from the manuscript. | RC-2 | `02_…ipynb` | `outputs/tables/glossary.csv` | Traced |
| P3-C18 | **TJS layer → NHS governance artefacts** mapping as specified in **Supplementary Appendix G**. | RC-3 | `02_…ipynb` | `outputs/tables/nhs_governance_mapping.csv` | Traced |
| P3-C19 | **Two illustrative TJS records** (Primary Safety; Secondary Operational) demonstrate the audit schema from worked examples. | RC-4 | `03_…ipynb` | `outputs/schemas/tjs_record_primary_safety_rendered.json`, `tjs_record_secondary_operational_rendered.json` | Traced |
| P3-C20 | Notebook outputs are **deterministic** and **hash-validated** against baselines. | RC-5 | `reproduce_all.py` → `scripts/hash_manifest.py`, `scripts/validate_outputs.py` | `config/expected_outputs.json`, `logs/actual_manifest.json` | Traced |

## Cross-reference: `config/trace_map.json`

Structured output-to-notebook mapping (STM targets) is maintained in `config/trace_map.json` for automation and downstream auditing.

## Exclusions (not P3 claims in this repo)

Companion-paper quantitative results and empirical validation items **XC-1–XC-8** are explicitly out of scope here; see `docs/claim_boundary_statement.md`.
