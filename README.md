# ACPA/MSMDA — EPS teaching assistant and research engine

**Release v0.2.0 (25 November 2026):** trilingual EPS technology evaluation and teaching assistant (French, Arabic, English). The release code passed 264 automated tests under Python 3.12 and 3.14, and the Laboratory statistics matched an independent R 4.5.2 computation on 29/29 metrics. Intended for research and teacher-facing evaluation; institutional production readiness has not been established.

[Public demonstration](https://acpa-msmda.streamlit.app/) · [Release notes](docs/release-v0.2.0.md) · [Scientific status](docs/statut-scientifique-v0.2.0.md) · [Changelog](CHANGELOG.md) · [Privacy and deployment](docs/privacy-deployment.md)

**Archived research engine:** v0.1.1, released separately with the DOI below. Its synthetic catalogue and citation must not be confused with the later application.

## Current application

This public implementation is distinct from the doctoral ACPA/MSMDA prototype evaluated in the associated research: the prototype's empirical results (context extraction, expert agreement, usability) do not apply to it. The application catalogue of 2,466 entries derives from a mapping of 45,676 store records (40,759 after deduplication). See [scientific status](docs/statut-scientifique-v0.2.0.md).

The scientific workflow is Evaluate → Explore → Scenario, supported by the EPS Space. The Streamlit interface provides a real-app catalogue with documented and unverified entries, contextual search, a teaching studio, workshop planning, field tools, formative assessment, performance analysis, annual cycle planning and a teaching journal with class projects. The Laboratory offers 32 field instruments, optional visual cues (AI-generated illustrations and OpenMoji pictograms) and a three-level restitution of analyses (Understand, Analyse, Investigate). Teacher data stays in the server session (temporary) and is saved as Excel workbooks that can be restored (formulas are rejected); JSON is kept for the Investigate level and technical uses. The application is not a persistent school database. A rule-based assistant provides source-linked suggestions, not generative AI or proof of teaching efficacy.

Start locally:

```bash
python -m pip install -r requirements.txt
streamlit run app.py
python -m unittest discover -s tests -v
```

See [the teacher guide](docs/teacher-guide.md) and [release checklist](docs/release-checklist.md). The separate [offline companion](offline/README.md) and [local video workspace](video/README.md) are experimental, not integrated public services.

## Archived engine v0.1.1

The following description refers to the archived engine and its reproducible synthetic examples.

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

The archived versions and current release preparation are research software artifacts. A version number or archival DOI does not imply empirical validation, educational efficacy or production readiness.

## License and citation

**Current release:** [v0.2.0 on Zenodo](https://doi.org/10.5281/zenodo.24544420) (version-specific DOI: `10.5281/zenodo.24544420`). All versions: `10.5281/zenodo.23244628` (resolves to the latest version).

Suggested software citation: Moudettir, Y., Ouhrir, S., & Lotfi, S. (2026). *ACPA/MSMDA: EPS Technology Evaluation and Teaching Assistant* (Version v0.2.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.24544420

**Earlier archived release:** [v0.1.1 on Zenodo](https://doi.org/10.5281/zenodo.23244629) (version-specific DOI: `10.5281/zenodo.23244629`).

Suggested software citation: Moudettir, Y., Lotfi, S., & Ouhrir, S. (2026). *ACPA/MSMDA: Heuristic EPS Technology Recommendation Engine* (Version v0.1.1) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23244629


The source code is offered under the accompanying MIT License. The Laboratory illustrations are under CC BY 4.0 to the extent of the rights held, and the OpenMoji pictograms under CC BY-SA 4.0 (see `assets/visual-bank/LICENCE-ILLUSTRATIONS.md`).
See `NOTICE` for scope and the distinction from any industrial-property
rights associated with the wider project. See `CITATION.cff` for software
citation metadata. For reproducibility, cite the version-specific DOI of the release you used: v0.2.0 or v0.1.1 above.


