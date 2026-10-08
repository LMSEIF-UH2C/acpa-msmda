# ACPA/MSMDA — Heuristic EPS Technology Recommendation Engine

**Public source version v0.1.1 (heuristic development implementation; citation and documentation update).**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23244629.svg)](https://doi.org/10.5281/zenodo.23244629)

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
python -m compileall -q src run_engine.py
```

The automated integration and packaging tests are maintained in the private
development repository and are not included in this 11-file source release.

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

## Release history and reproducibility

- **v0.1.0 (8 October 2026):** initial public release of the working heuristic engine with synthetic examples.
- **v0.1.1 (8 October 2026):** updated machine-readable software citation metadata and release documentation for scholarly archiving. The ranking algorithm, context rules, synthetic catalogue and runtime behavior are unchanged from v0.1.0.

Both versions are development artifacts. A version number or archival DOI does not imply empirical validation, educational efficacy or production readiness.

## License and citation

**Archived release:** [v0.1.1 on Zenodo](https://doi.org/10.5281/zenodo.23244629) (version-specific DOI: `10.5281/zenodo.23244629`).

Suggested software citation: Moudettir, Y., Lotfi, S., & Ouhrir, S. (2026). *ACPA/MSMDA: Heuristic EPS Technology Recommendation Engine* (Version v0.1.1) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23244629


The selected release files are offered under the accompanying MIT License.
See `NOTICE` for scope and the distinction from any industrial-property
rights associated with the wider project. See `CITATION.cff` for software
citation metadata. For reproducibility, cite the archived v0.1.1 release DOI above. Later versions should be cited using their own version-specific identifiers.
