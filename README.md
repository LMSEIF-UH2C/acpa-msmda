# ACPA/MSMDA

Proof of Concept (PoC) of the ACPA/MSMDA recommendation system for adapted physical education.

Developed at ENS Casablanca, Université Hassan II.

Patent context: OMPIC application No. 74877 (2026).

## Status

This repository currently contains a minimal research PoC.

The purpose of this version is to demonstrate the technical pipeline:

Profile → adaptation rules → exercise filtering → recommendation → explanation

The sample rules and exercise catalogue included in this PoC are demonstration data. They must not be considered the definitive implementation of the patented ACPA/MSMDA decision logic until alignment with the original source code and research documentation has been completed.

## Architecture

```text
User profile
     ↓
Rule engine
     ↓
Adaptation policy
     ↓
Exercise catalogue
     ↓
Filtering + scoring
     ↓
Recommendations
     ↓
Explanation / traceability
```

## Repository structure

```text
acpa-msmda/
├── README.md
├── LICENSE
├── requirements.txt
├── app.py
├── engine.py
├── data/
│   ├── exercises.json
│   └── rules.json
└── tests/
    └── test_cases.py
```

## Installation

Python 3.10+ recommended.

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```bash
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the PoC

```bash
streamlit run app.py
```

## Run tests

```bash
python -m unittest discover -s tests -v
```

## Current PoC inputs

- mobility level
- balance support requirement
- cardio tolerance
- available equipment
- teaching environment
- pedagogical objective

## Recommendation output

For each recommendation the engine returns:

- activity
- description
- intensity level
- compatibility score
- applied adaptation criteria
- triggered rule identifiers
- explanation

## Research and intellectual-property notice

This repository is under active research development.

The current demonstration rules are intentionally separated from the definitive ACPA/MSMDA knowledge base.

No assumption should be made that the sample rule set reproduces the complete patented method described in OMPIC application No. 74877.

The MIT License in this repository applies to the software code in this repository. It does not grant rights under any patent, thesis, article, dataset, or other research output unless explicitly stated.

## Disclaimer

This research prototype supports educational decision-making in adapted physical education.

It is not a medical device and does not provide medical diagnosis or medical treatment recommendations.

## Author

Youness Moudettir  
ENS Casablanca  
Université Hassan II

## License

Software code in this repository is released under the MIT License. See [LICENSE](LICENSE).
