# Claim Traceability Matrix

**Repo:** ethical-alpha-audit-paper-3-framework-comparison  
**Updated:** 2026-04-12 (Engineer traceability draft + **P3 QA session**: independent `pytest`, `reproduce_all.py`, hash validation, and tabular artefact checks)  
**Claims:** 35 (P3-C01–P3-C35) manuscript- and scope-grounded items | **VERIFIED** in the matrix below applies only where this repo session produced direct evidence (see status column); Narrative wording re-extracted from inputs/manuscript.docx (2026-04-19 baseline) from `inputs/manuscript.pdf` in the QA session.

This matrix maps **Paper 3 manuscript claims** and **repository fidelity statements** to notebooks, data artefacts, and outputs. It does not restate excluded companion-paper results (see `docs/claim_boundary_statement.md`).

## Manuscript-grounded claims (conceptual / methodological)

| Claim ID | Claim (paraphrase, faithful to manuscript) | Manuscript anchor (section / artefact) | Notebook / code | Output / evidence path | Status |
|----------|---------------------------------------------|----------------------------------------|-----------------|-------------------------|--------|
| P3-C01 | Clinical AI governance often operationalises safety via quantitative thresholds whose methodological rationale is undocumented (“magic numbers”). | Introduction; “What is already known” | `notebooks/01_tjs_framework_and_failure_mechanisms.ipynb` | Narrative setup; `data/tables/table1_failure_mechanisms.json` context | Traced |
| P3-C02 | Conceptual synthesis identified **six** structural failure mechanisms in threshold design (proxy thresholding; context collapse; threshold coupling; boundary gaming; epistemic asymmetry; audit–lifecycle disconnect). | Results; Table 1 | `01_…ipynb` | `outputs/tables/table1_failure_mechanisms.csv`; `data/tables/table1_failure_mechanisms.json` (6 `data` rows) | **VERIFIED** (QA 2026-04-12: tabular row count + repro pipeline) |
| P3-C03 | Methods combine **conceptual synthesis and regulatory analysis** (targeted searches, Jan 2018–Dec 2025; structural inclusion criterion). | Methods | `01_…ipynb` (epistemic notice); `manuscript/Paper3_Manuscript.docx` | `data/tables/table1_failure_mechanisms.json` (`_caveat`) | Traced |
| P3-C04 | The six mechanisms are argued **structurally distinct** and to cover **major** structural failure modes; **not claimed exhaustive**; inter-rater exercise proposed. | Methods (Reproducibility subsection) | `01_…ipynb` | JSON `_caveat` on interpretive tables | Traced |
| P3-C05 | **Regulatory alignment** assessments are **interpretive inferences** by the author, not statements of regulatory intent or legal requirement. | Methods | `01_…ipynb`; `02_…ipynb` | Table JSON `_caveat` fields | Traced |
| P3-C06 | **Threshold Justification Stack (TJS)** specifies **six documentation layers** with **tiered** requirements: **Primary Safety** (failure can directly harm patients) vs **Secondary Operational**; **Primary** applies by default when uncertain. | Results; Table 2 | `01_…ipynb` | `outputs/tables/table2_tjs_specification.csv`; `data/tables/table2_tjs_specification.json` (6 `data` rows; tier fields) | **VERIFIED** (QA 2026-04-12: tabular structure + repro pipeline) |
| P3-C07 | Table 2 documents each TJS layer (description, mechanisms addressed, tier requirement, regulatory counterpart). | Table 2 | `01_…ipynb` | `data/tables/table2_tjs_specification.json` → CSV | **VERIFIED** (QA 2026-04-12: same artefact as C06) |
| P3-C08 | Table 3 compares TJS threshold documentation expectations to other governance instruments; **all characterisations interpretive**. | Results; Table 3 | `02_…ipynb` | `outputs/tables/table3_framework_comparison.csv` | **VERIFIED** (QA 2026-04-12: artefact + hash manifest; interpretive caveat retained) |
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
| P3-C16 | Manuscript **Tables 1–3** rendered as structured **CSV** from **JSON** sources extracted from the manuscript text. | RC-1 | `01_…ipynb`, `02_…ipynb` | `outputs/tables/table1_failure_mechanisms.csv`, `table2_tjs_specification.csv`, `table3_framework_comparison.csv` | **VERIFIED** (QA 2026-04-12: `python reproduce_all.py` + `VALIDATION PASSED`; hashes match `config/expected_outputs.json`) |
| P3-C17 | **Glossary** of key terms consolidated from the manuscript. | RC-2 | `02_…ipynb` | `outputs/tables/glossary.csv` | **VERIFIED** (QA 2026-04-12: same validation pass) |
| P3-C18 | **TJS layer → NHS governance artefacts** mapping as specified in **Supplementary Appendix G**. | RC-3 | `02_…ipynb` | `outputs/tables/nhs_governance_mapping.csv` | **VERIFIED** (QA 2026-04-12: same validation pass) |
| P3-C19 | **Two illustrative TJS records** (Primary Safety; Secondary Operational) demonstrate the audit schema from worked examples. | RC-4 | `03_…ipynb` | `outputs/schemas/tjs_record_primary_safety_rendered.json`, `tjs_record_secondary_operational_rendered.json` | **VERIFIED** (QA 2026-04-12: same validation pass) |
| P3-C20 | Notebook outputs are **deterministic** and **hash-validated** against baselines. | RC-5 | `reproduce_all.py` → `scripts/hash_manifest.py`, `scripts/validate_outputs.py` | `config/expected_outputs.json`, `logs/actual_manifest.json` | **VERIFIED** (QA 2026-04-12: `VALIDATION PASSED`; manifests aligned in session) |

## Cross-reference: `config/trace_map.json`

Structured output-to-notebook mapping (STM targets) is maintained in `config/trace_map.json` for automation and downstream auditing.

## Exclusions (not P3 claims in this repo)

Companion-paper quantitative results and empirical validation items **XC-1–XC-8** are explicitly out of scope here; see `docs/claim_boundary_statement.md`.

## P3 Stage 1 — Claim Extraction (UPDATED)

**Source:** `inputs/manuscript.docx` (engineering re-extraction pass, **2026-04-19**). Extraction method: read `word/document.xml` inside the DOCX package and concatenate `w:t` text runs per paragraph (styles recorded where present). **No manuscript file edits** were performed.

**Relationship to the matrix above:** Identifiers **P3-C01–P3-C20** and their rows in the tables above are **preserved** as the baseline catalogue. This stage **adds** **P3-C21–P3-C35** as additional **atomic** claims surfaced by the refreshed manuscript text (including Discussion, Data Availability, supplementary pointers, and multimedia appendix material present in the DOCX body).

| Claim ID | Atomic claim (neutral paraphrase faithful to manuscript wording) | Manuscript section / anchor (DOCX paragraph / heading cue) | Supporting logic or reference (in-manuscript or repo) |
|----------|-------------------------------------------------------------------|------------------------------------------------------------|--------------------------------------------------------|
| P3-C21 | The FUTURE-AI consensus guideline is described as defining many trustworthy-AI practice expectations while **not** specifying how **quantitative thresholds** that operationalise those practices should be **justified or documented**. | Introduction / related governance context (body paragraph referencing FUTURE-AI `[26]`) | Citation `[26]` in manuscript; conceptual contrast supporting the “magic numbers” problem framing (see also P3-C01). |
| P3-C22 | FDA **January 2025** draft guidance on AI-enabled device software functions is described as articulating **total product lifecycle** expectations while **not** mandating a **structured threshold-justification documentation architecture** analogous to TJS. | Introduction / regulatory context (body paragraph referencing FDA draft guidance `[27]`) | Citation `[27]` in manuscript; interpretive regulatory comparison (see P3-C05, P3-C08 caveats). |
| P3-C23 | Because the work is a **conceptual synthesis** rather than a systematic review, the literature identification process is **not fully reproducible** in the systematic-review sense; nonetheless the targeted strategy, **search dates**, databases, and inclusion criterion are described, and **Table 1** documents provenance for each listed mechanism. | Methods — **Reproducibility** subsection (runs immediately before Results material in extracted paragraph order) | Combines methodological limitation statement with provenance commitment to Table 1 (`data/tables/table1_failure_mechanisms.json` / notebook 01). |
| P3-C24 | **Table 3** is used to compare TJS threshold documentation expectations to other governance instruments to **illustrate** that TJS addresses **gaps not covered** by current practice in the compared instruments. | Results — “Comparison With Existing Governance Approaches” (Table 3 lead-in) | Same interpretive epistemic status as P3-C08; table artefacts in `outputs/tables/table3_framework_comparison.csv`. |
| P3-C25 | An **illustrative** NHS committee vignette is presented for a **Primary Safety** TJS record for an **AI-assisted chest X-ray triage** tool with an **AUROC ≥ 0.85** example threshold, describing compatibility with a **standing monthly meeting** cadence and a conditional approval outcome. | Discussion narrative block titled “Illustrative Committee Vignette” (extracted as a single long paragraph in DOCX) | Explicitly illustrative; not claimed as empirical evaluation; numeric example appears **only** as vignette text in the extracted manuscript body. |
| P3-C26 | The six structural failure mechanisms are argued to converge on two fundamental **sensitivity dimensions** (**parameter calibration**; **evidence calibration**), with further detail deferred to **Supplementary Appendix D**. | Discussion / synthesis paragraph immediately following the vignette | Pointer to supplementary appendix (see `inputs/supplementary.pdf` as manuscript-indicated artefact; not re-opened in this pass). |
| P3-C27 | The manuscript defends **documentation burden** for **Primary Safety** thresholds as proportionate to **irreversibility** of failure consequences, and draws comparability to burdens already associated with **EU AI Act Article 9** risk management language and the **FDA PCCP** framework. | Discussion — “Documentation Burden: Addressing the Proportionality Objection” | Normative argument + regulatory references as stated in manuscript; interpretive mapping (aligned with P3-C05/P3-C08 epistemic posture). |
| P3-C28 | The manuscript states that the governance thresholds in scope have **direct patient-level consequences** (too low permits harm; too high blocks benefit) and links risk management to requiring documented **harm-control pathways** (TJS **Layer 1**) and **sensitivity / cliff-edge** style analysis (TJS **Layer 4**). | Discussion — “Patient-Level Consequence Pathway” | Conceptual chain within manuscript; aligns with tier logic in P3-C06/P3-C14. |
| P3-C29 | The manuscript states that evidence supporting the **non-compensatory gate architecture** currently spans **Tier 4** (computational simulation) and **Tier 3** (structured retrospective replay), and notes **Tier 2** real-world observational evaluation as **not yet executed** in the described programme framing. | Discussion — “Validation Hierarchy” | Depends on the portfolio empirical programme and companion papers (see `docs/claim_boundary_statement.md` XC items for numeric exclusions). |
| P3-C30 | **Companion studies** are described as providing **preliminary**, **context-specific** empirical signals that are **consistent with** the proposed governance framework, including **specific quantitative statements** appearing in the Discussion text (historical replay sensitivity; simulation phrasing; verdict stability percentage; dual-dataset invariance counts; confusion-matrix shape; binding-frequency percentage; cliff-edge numeric band language as stated). | Discussion — companion-evidence paragraph(s) | **Manuscript narrative referencing companion empirical programme; explicit citations added in current revision to Paper 4 and Paper 5 (see references [32,33]).**; numeric verification is **upstream** (Paper 4 / Paper 5 repos per boundary doc), not P3 reproduction scope. |
| P3-C31 | The manuscript reports **perturbation testing** outcomes (**~90% ranking stability** under **±20% variation**), identifies a **threshold-sensitive region (~0.40–0.45)** associated with **binary outcome reversals**, and labels these observations **dataset-specific** and **non-generalised**. | Discussion paragraph adjacent to companion methodological claims in extracted order | Same upstream boundary as XC-6-style claims; manuscript includes explicit non-generalisation qualifier. |
| P3-C32 | **Scope boundaries** are stated: the gate architecture addresses governance evidence assessment within **five specified domains** and does **not** address several enumerated classes of deployment / sociotechnical / procurement / trial-substitution / workflow / trust / human-factors risks. | Discussion — “Scope Boundaries” | Definitions are manuscript-local; trace to repo notebooks is indirect (epistemic scoping). |
| P3-C33 | The manuscript describes a reproducibility posture where **re-execution from identical inputs produces identical outputs**, characterises an **archived reference implementation** as a **deterministic transformation** of a **canonical governance engine**, and notes a historical issue where an **earlier public engine implementation** had drifted from canonical logic (described as an incorrect compensatory formula / profile misalignment) later corrected toward canonical behaviour. | Late manuscript reproducibility / governance-engine disclosure paragraph(s) in extracted DOCX order (pre–Data Availability) | **Not** mapped in `config/trace_map.json` (which covers P3 tabular/schema artefacts). Treat as **portfolio engine / shared-core** lineage for verification outside this repo. |
| P3-C34 | **PhysioNet-derived** threshold sensitivity patterns are invoked as **empirical motivation** for the tiered requirement that **Primary Safety** thresholds receive **all six** TJS layers, explicitly tying **Layer 3** calibration evidence and **Layer 4** cliff-edge analysis to sensitivity of governance outcomes to small threshold changes at the **safety gate**. | “Multimedia Appendix: PhysioNet Threshold Sensitivity” (Heading2 in DOCX) + following paragraph | Manuscript argument; empirical detail is manuscript/supplementary-indicated, not recomputed here. |
| P3-C35 | **Data availability** statement: **no primary data** were generated; the analytical framework is described as fully specified in the manuscript; worked examples are stated to appear in **Supplementary Appendices A and B**. | “Data Availability” (Heading1) + following paragraph | Aligns with P3-C13 and repository reproduction scope (`docs/claim_boundary_statement.md` RC items). |

## P3 Stage 2 — Traceability Mapping (UPDATED)

**Traceability classes (applied as a single primary class per claim; notes capture secondary nuance):** `TRACED_REPO`, `TRACED_UPSTREAM`, `TRACED_MANUSCRIPT_ONLY`, `GAP`, `TO_VERIFY_LATER`.

### A) Retro-mapping for the preserved baseline (`P3-C01–P3-C20`)

For governance automation purposes, interpret the prior matrix’s **`VERIFIED`** rows as **`TRACED_REPO`** (direct QA evidence in-repo) and the remaining **`Traced`** rows as **`TRACED_REPO`** where a notebook/CSV/JSON path is listed, because each baseline row already maps to an in-repo notebook and/or structured artefact path.

**Baseline distribution (counting each baseline claim once):** `TRACED_REPO` = 20; `TRACED_UPSTREAM` = 0; `TRACED_MANUSCRIPT_ONLY` = 0; `GAP` = 0; `TO_VERIFY_LATER` = 0.

> **Note:** Discussion text in the refreshed manuscript now contains companion-paper quantitative narration (see **P3-C29–P3-C31**). Those quantitative statements are **not** part of **P3-C01–P3-C20** as previously enumerated; they are handled as **incremental claims** below and/or as **XC exclusions** in `docs/claim_boundary_statement.md`.

### B) Incremental claims (`P3-C21–P3-C35`)

| Claim ID | Traceability class | Mapping / evidence |
|----------|--------------------|--------------------|
| P3-C21 | `TRACED_MANUSCRIPT_ONLY` | Manuscript text + cited guideline source; not independently reproduced in this repo beyond the conceptual notebooks’ framing. |
| P3-C22 | `TRACED_MANUSCRIPT_ONLY` | Manuscript text + cited FDA draft guidance; not independently reproduced as legal/regulatory fact here. |
| P3-C23 | `TRACED_MANUSCRIPT_ONLY` | Primary content is the **non-systematic-review reproducibility** limitation; **subordinate provenance** for mechanisms is `TRACED_REPO` via Table 1 artefacts (`notebooks/01_tjs_framework_and_failure_mechanisms.ipynb`, `data/tables/table1_failure_mechanisms.json`). |
| P3-C24 | `TRACED_REPO` | `outputs/tables/table3_framework_comparison.csv` / `notebooks/02_framework_comparison_and_mappings.ipynb` / `config/trace_map.json` STM-T3. |
| P3-C25 | `TRACED_MANUSCRIPT_ONLY` | Illustrative vignette narrative; not represented as a separate quantitative reproduction target in `config/trace_map.json`. |
| P3-C26 | `TRACED_MANUSCRIPT_ONLY` | Pointer to Supplementary Appendix D (manuscript-indicated). |
| P3-C27 | `TRACED_MANUSCRIPT_ONLY` | Normative proportionality argument with regulatory references; interpretive (consistent with P3-C05). |
| P3-C28 | `TRACED_MANUSCRIPT_ONLY` | Conceptual patient-harm pathway statement; aligns logically with tier definitions (P3-C06) but not a separate tabular artefact. |
| P3-C29 | `TRACED_UPSTREAM` | Validation tier programme and companion evidence bases (Paper 4 / Paper 5 family per `docs/claim_boundary_statement.md`; portfolio graph shows P3 tier-2 upstream includes **P4** in `eaa_system/dependency_graph.json`). |
| P3-C30 | `TRACED_UPSTREAM` | Quantitative companion statements require upstream repos for independent recomputation/verification; manuscript remains the **authoritative wording** for what is claimed in Paper 3 Discussion. |
| P3-C31 | `TRACED_UPSTREAM` | Perturbation / cliff-edge numeric statements are manuscript-reported companion-context; treat recomputation as upstream. |
| P3-C32 | `TRACED_MANUSCRIPT_ONLY` | Scope boundary list is manuscript-local governance scoping text. |
| P3-C33 | `TO_VERIFY_LATER` | Determinism / canonical-engine lineage is **not** covered by `config/trace_map.json`; portfolio **shared-core** / engine archives would be the appropriate verification locus (outside this repo’s hash-locked notebook tables). |
| P3-C34 | `TRACED_MANUSCRIPT_ONLY` | Argumentative link from PhysioNet sensitivity narrative to tiered documentation requirements; multimedia appendix content not in trace map outputs. |
| P3-C35 | `TRACED_MANUSCRIPT_ONLY` | Data availability statement; consistent with RC scope framing, but the claim itself is manuscript metadata. |

**Incremental distribution:** `TRACED_REPO` **1**; `TRACED_UPSTREAM` **3**; `TRACED_MANUSCRIPT_ONLY` **10**; `GAP` **0**; `TO_VERIFY_LATER` **1**.

**Combined catalogue (P3-C01–P3-C35):** `TRACED_REPO` **21**; `TRACED_UPSTREAM` **3**; `TRACED_MANUSCRIPT_ONLY` **10**; `GAP` **0**; `TO_VERIFY_LATER` **1**.

## P3 — Risk register (refresh-derived)

- **Over-claim / interpretive comparison risk (regulatory & framework):** P3-C21–P3-C22, P3-C24, P3-C27 retain the manuscript’s explicit **interpretive** posture (consistent with P3-C05/P3-C08); readers should not treat table mappings as regulatory intent.
- **Unsupported *numerical generalisation* risk:** P3-C30–P3-C31 bundle **dataset-specific** and **preliminary** language in places, but still embed **hard numbers** that can be mistaken for Paper 3 empirical contributions if read outside `docs/claim_boundary_statement.md`.
- **Implicit assumptions:** P3-C25 relies on a **stylised committee process** as illustration; P3-C29 assumes a **validation tier taxonomy** whose institutional meaning depends on the broader Ethical Alpha Audit programme framing.
- **Cross-paper dependency (not verified inside P3):** P3-C29–P3-C31 depend on companion papers / programme artefacts (**P4** and related sensitivity work) for independent numeric confirmation.

## P3 — Internal consistency notes (terminology + structure)

- **Tier counts:** The manuscript consistently centres **six** TJS documentation layers for **Primary Safety** and **three** for **Secondary Operational**, matching P3-C06 and the abstract fragments present in the DOCX body.
- **Non-compensatory framing:** The term **“non-compensatory”** appears in the Discussion validation / companion-evidence thread (P3-C29–P3-C30), consistent with the portfolio’s non-compensatory gate vocabulary.
- **Deterministic outputs:** The manuscript explicitly uses **deterministic outputs** language in the reproducibility/engine disclosure thread (P3-C33), consistent with RC-5 / P3-C20’s deterministic reproduction posture for **this repo’s hash-locked notebook outputs**, while noting P3-C33’s engine lineage is **not** the same evidence object as notebook output hashes.
- **EAA phrase check (`structured override`):** A case-insensitive substring search over `word/document.xml` in `inputs/manuscript.docx` found **no** occurrences of **“structured override”** (or **“override”** as a standalone governance term in that XML text). This is a **terminology alignment flag** only: it does **not** assert absence from other portfolio documents, only from this manuscript file’s extracted text.
- **No internal contradiction detected** between (a) “normative / not empirically validated” framing (P3-C14–P3-C15; Discussion) and (b) companion empirical narration (P3-C29–P3-C31), provided readers preserve the manuscript’s **preliminary / non-generalised** qualifiers and the XC boundary statement.

## P3 Stage 3 — Sensitivity Extension Claims (P3-C36–P3-C56) — added at WS-2.6 Phase 0

**Source:** Fresh extraction from `inputs/manuscript.docx` (Paper3 Manuscript v5 FINAL, sha `7d3531e9...`) at WS-2.6 Phase 0; UNION ALL combination with the existing 35-claim register; arbitrated per Walter's Phase 0.4c response and Phase 0.5 Quick-path arbitration (2026-05-03).

**Total claim count after extension:** 56 (P3-C01–P3-C56).

**Status convention for new claims:** All entries P3-C36–P3-C56 begin at status `MISSING`. The WS-2.6 Phase 11 quality gate (notebook execution + output validation) updates each to `Traced` (or `VERIFIED` where Walter confirms evidence is sufficient) based on the new sensitivity notebooks (05–08) that cover the simulation work. The "Notebook / code" and "Output / evidence" columns are placeholders until Phase 8 notebook authoring assigns specific paths.

### Sensitivity-extension claim register

| Claim ID | Atomic claim (paraphrase from manuscript v5 FINAL) | Manuscript anchor | Notebook / code | Output / evidence | Status |
|---|---|---|---|---|---|
| P3-C36 | The framework's tier-stratified documentation depth depends on tier-classification reliability for the proportionality argument to hold. | Methods §"Computational sensitivity analysis: design" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C37 | Two simulated raters classify each threshold as one of {Primary, Secondary, Uncertain}. | Methods §"Computational sensitivity analysis: design" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C38 | The simulation is sensitivity analysis, not empirical estimation. | Methods §"Computational sensitivity analysis: design" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C39 | Under stated modelling assumptions, the four governance outcomes vary monotonically with target κ. | Results §"Sensitivity analysis: κ regimes for the Negative Harm Test" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C40 | Three κ regimes follow from the sensitivity outputs under stated modelling assumptions. | Results §"Sensitivity analysis: κ regimes for the Negative Harm Test" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C41 | κ < 0.40 is the falsification regime (insufficient inter-rater reliability for unsupervised tier-classification use). | Results §"Sensitivity analysis: κ regimes for the Negative Harm Test" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C42 | 0.40 ≤ κ < 0.60 is the caution regime (acceptable with operational safeguards). | Results §"Sensitivity analysis: κ regimes for the Negative Harm Test" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C43 | κ ≥ 0.60 is the operational regime (acceptable under default-to-Primary adjudication). | Results §"Sensitivity analysis: κ regimes for the Negative Harm Test" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C44 | The κ regime is normative-from-analysis, not empirical (replaceable by empirical pilot data when available). | Results §"Sensitivity analysis: κ regimes for the Negative Harm Test" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C45 | The proposed pilot inter-rater reliability exercise produces κ < 0.40 on Primary/Secondary tier classification (falsification condition). | Discussion §"Theory of change and falsification conditions" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C46 | The first falsification condition is interpretable as a regime with quantified analytical consequences (cross-references κ regimes results). | Discussion §"Theory of change and falsification conditions" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C47 | The computational sensitivity analysis answers an analytical question about the tier-classification rule under stated modelling assumptions: given an assumed κ value and the default-to-Primary adjudication, what governance outcomes follow. | Discussion §"Sensitivity analysis: scope and limits" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C48 | The TJS depends on consistent classification of thresholds as Primary Safety or Secondary Operational. | Discussion §"Tier classification reliability" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C49 | Threshold coupling (Layer 4) remains the structural concern most inadequately addressed by current governance standards. | Discussion §"Threshold coupling: the least mature layer" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C50 | The supplementary pilot protocol formalises an empirical feasibility assessment within an existing hospital AI oversight committee. | Discussion §"Proposed pilot design with prespecified feasibility endpoints" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C51 | The κ-sensitivity simulation is conditional on stated modelling assumptions (probabilistic rater-error model parameterised to target κ; binary-plus-Uncertain output alphabet; default-to-Primary adjudication; base-rate prior on π_Primary). | Discussion §"Simulation-specific limits" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C52 | L4 (sensitivity analysis / threshold coupling) is the least methodologically mature layer. | Discussion §"Specific layer limits" | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C53 | A documentation architecture proposing tier-stratified documentation depth depends on tier-classification reliability for the proportionality argument to hold: if tier classification is unreliable, neither the burden reduction at the Secondary tier nor the proportionality of the documentation requirement is defensible. | Introduction (bridging methodological claim; Walter Phase 0.4c ADD) | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C54 | The classification rule is the Negative Harm Test: a threshold may be classified Secondary Operational only if its failure cannot lead to clinical intervention or omission (operational definition). | Methods §"Threshold classification" (Walter Phase 0.4c ADD) | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C55 | TJS integration requires three procedural changes to existing governance infrastructure: (a) a threshold justification record is produced for each numeric threshold at the point of deployment or substantive modification; (b) layers populated per the tier classification; (c) record routed to the appropriate committee. | Discussion §"Integrating TJS Into Existing Hospital Audit Infrastructure" (Walter Phase 0.4c ADD) | TBD (Phase 8) | TBD (Phase 11) | MISSING |
| P3-C56 | Documentation artefacts can be produced as compliance theatre — records completed for each threshold but without substantive engagement with the harm-control link or the sensitivity analysis (anti-gaming limitation acknowledgement). | Discussion §"Ritualistic compliance" (Walter Phase 0.4c ADD) | TBD (Phase 8) | TBD (Phase 11) | MISSING |

### Aliases (alternate phrasings of existing claims; recorded for cross-reference, no new IDs)

These fresh-extraction wordings are alternate phrasings of existing claim IDs. Walter arbitrated each at Phase 0.4c (Section E + Section G) and Phase 0.5 Quick-path (F27/F34/F54 demoted from initial ADD recommendation to ALIAS to avoid duplicating P3-C24/C27/C28).

| Fresh ID | Aliases to | Note |
|---|---|---|
| F36 | P3-C11 | Tier-gaming counter-position aliased to existing gaming-resistance claim. |
| F50 | P3-C03 | Production-model single-author limitation aliased to existing single-author method statement. |
| F51 | P3-C35 | "No primary data" statement aliased to existing data availability statement. |
| F04 | P3-C06 | Abstract restatement of TJS development aliased to TJS specification claim. |
| F09 | P3-C06 | Introduction restatement of TJS development aliased to TJS specification claim. |
| F11 | P3-C04 | Contribution restatement aliased to existing contribution claim. |
| F37 | P3-C04 | Discussion contribution restatement aliased to existing contribution claim. |
| F55 | P3-C15 | Conclusions restatement aliased to TJS-as-normative-proposal claim. |
| F27 | P3-C24 | Table 3 framework-comparison restatement aliased to existing Table 3 comparison claim (Phase 0.5 Quick-path). |
| F34 | P3-C27 | Tiered-structure-as-proportionality-response aliased to existing documentation-burden defence claim (Phase 0.5 Quick-path). |
| F54 | P3-C28 | Patient-level-consequence restatement aliased to existing patient-level consequence claim (Phase 0.5 Quick-path). |

### Retired fresh-extraction entries (no claims added)

These fresh-extraction entries did not become claims:

- **F01** — title text; structural metadata, no semantic claim (Walter Phase 0.4c RETIRE).
- **18 false positives** — caption labels (Table N., Figure N., L3., L4.), single-word section markers (Methods./Results./Conclusions.), Supplementary Appendix labels, reference numbers, single-word counter-position responses (TJS response./Steelman./Residual risk.). Caught by the Phase 0.1 claim-marker regex but not actually claims.
- **2 structural metadata** — F02 ("What this study adds" header content), F03 ("How this study might affect…" header content). Journal-format framing rather than substantively-claimed propositions.

### Cross-references (Phase 8 author guidance)

- **P3-C36 and P3-C53** both relate to tier-classification reliability as foundation for the proportionality argument, with different argumentative framings (P3-C36 is Methods-side scope-statement; P3-C53 is Introduction-side bridging claim). Phase 8 notebooks may want to cross-reference both when discussing the proportionality dependency.
- **P3-C39** references "four governance outcomes" — Phase 8 notebooks should enumerate the four outcomes explicitly in markdown narrative when referencing this claim, since the register entry is concise. The four outcomes per the simulation: misclassification rates pre-adjudication; net-Primary classification rate; unsafe-Secondary rate; over-escalation burden.

