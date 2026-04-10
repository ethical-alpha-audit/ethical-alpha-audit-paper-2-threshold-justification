# Reproducibility Statement

## How to reproduce

From the repository root, with dependencies installed per `requirements.txt`:

```bash
python reproduce_all.py
```

This executes 4 notebooks in sequence, computes SHA-256 hashes of all 8 output files, and validates them against `config/expected_outputs.json`. A passing result (`ALL STEPS PASSED`) confirms bitwise-identical reproduction.

## Determinism guarantees

- `PYTHONHASHSEED=0` enforced by harness
- No randomness in any notebook (no `random`, no `numpy.random`, no Monte Carlo)
- No external data fetching (all inputs are checked-in JSON files)
- No system-dependent operations (no timestamps, no PIDs in outputs)
- All CSV output uses `index=False, encoding='utf-8'`
- All JSON output uses `indent=2, sort_keys=True, ensure_ascii=False`
- `.gitattributes` prevents line-ending conversion for output files

## Validation without execution

```bash
python scripts/validate_outputs.py
```

Requires only Python stdlib. Verifies checked-in outputs match expected hashes.

## Nature of this repository

This is a **conceptual framework repository**. Notebooks render structured data extracted from the manuscript — they do not perform computational experiments, statistical analyses, or simulations. All outputs are deterministic transformations of static JSON inputs derived from the published text.
