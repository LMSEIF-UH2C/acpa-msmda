# ACPA/MSMDA — Heuristic EPS Technology Recommendation Engine

**Public source release v0.1.0 (heuristic development implementation).**

This is a **working source-code release of the current ACPA/MSMDA heuristic
engine**, not merely a viewer of fictional data. The code performs the
following computational operations:

1. Normalize and tokenize pedagogical text in French, Arabic or English.
2. Identify a limited, deterministic set of context expressions.
3. Adjust and normalize weights across **18 EPS technology criteria**.
4. Compute weighted composite scores, apply an illustrative safety penalty,
   and rank tools by their scores.
5. Report context flags, all 18 weights, criterion names, relative scores
   and a machine-readable demonstration-only status.

## Reproduce locally

Requires **Python 3.11 or 3.12**. The engine has **no third-party runtime
dependencies** and uses a **five-item synthetic catalogue**.

```bash
python run_engine.py --language fr --query "basketball sans connexion budget limité"
python run_engine.py --language en --query "large class with low budget"
python run_engine.py --language ar --query "كرة السلة بدون انترنت"
python -m unittest discover -s tests -v
```

## What this version does not establish

- The NLP is **rule-based**, not a trained, benchmarked language model.
- Contextual boosts and scores are **illustrative** and not calibrated against
  an expert-labeled or representative evaluation dataset.
- Catalogue tools and their 18 values are **fictional**; rankings are **not
  empirical recommendations** or product comparisons.
- Relative scores depend on catalogue membership; 100 does **not** mean
  perfect suitability.
- There is no demonstrated educational efficacy, generalization, fairness,
  or readiness for operational decisions about pupils.
- This release does not include the separate private sync, persistence,
  monitoring or web application modules.

## Privacy and security

The command-line program runs locally, makes no network requests and does
not persist input. Use fictional contexts only; do not enter student or other
personal data. This code is an illustrative research-development artifact,
not an authorized production system.

## Associated industrial-property application

The broader ACPA/MSMDA project is associated with OMPIC patent application No. 74877, filed on 23 April 2026. Filing does not imply a granted patent. This repository's MIT software copyright license does not include an express patent grant. See `NOTICE`.

## License and citation

The selected release files are offered under the accompanying MIT License.
See `NOTICE` for scope and the distinction from any industrial-property
rights associated with the wider project. See `CITATION.cff` for software
citation metadata. For reproducibility, cite the exact public commit SHA or a tagged release when available.
