# Methods Note

## Paper classification

Paper 2 is a **conceptual synthesis and normative governance proposal**. It is not a systematic review and does not report empirical findings. No primary data were generated.

## Search strategy

Targeted searches were conducted in PubMed, Web of Science, and Google Scholar using combinations of the terms "clinical AI threshold," "algorithmic audit," "governance metric," "safety boundary," "medical device threshold," and "performance cutoff." Regulatory document repositories searched included EUR-Lex, FDA.gov, MHRA.gov.uk, WHO institutional repository, and ISO online browsing platform. Search dates: January 2018–December 2025.

Citation tracking from key references (Leveson 2011, Obermeyer et al 2019, Thomas & Uminsky 2022, Lekadir et al 2025) supplemented the database searches.

## Inclusion criterion

A candidate failure mechanism must be structural — arising from how thresholds are designed or deployed — rather than from errors in any individual numeric value.

## Grouping and synthesis

Candidate mechanisms identified from the literature were grouped by structural similarity. The grouping was performed by the author; two initial candidates ("proxy bias" and "causal opacity") were consolidated into "proxy thresholding." The resulting six mechanisms were assessed against existing governance instruments.

## Reproducibility caveat

Because this is a conceptual synthesis rather than a systematic review, the literature identification process is not fully reproducible in the systematic review sense. Whether other analysts would derive the same six mechanisms is an empirical question that the proposed inter-rater reliability exercise is designed to address.

## Regulatory alignment

All regulatory alignment assessments are interpretive inferences by the author reflecting the governance intent of the cited provisions. They should not be read as statements of regulatory intent or legal requirement.

## Threshold classification

- **Primary Safety Thresholds:** failure can directly cause patient harm → all 6 TJS layers required
- **Secondary Operational Thresholds:** failure does not directly cause irreversible patient harm → 3 core layers required
- **Uncertain:** defaults to Primary Safety requirements

## Proposed pilot (not executed)

The manuscript proposes a pilot design with prespecified endpoints (median completion time, inter-rater kappa, Likert acceptability). This pilot has not been conducted; it defines the pathway for empirical validation.

## Repository data extraction

All JSON data files in `data/tables/` and `data/schemas/` were manually extracted from the manuscript text. The manuscript .docx files do not contain Word table objects; tables were reconstructed from inline paragraph text. Each JSON file includes a `_provenance` field citing the manuscript source.
