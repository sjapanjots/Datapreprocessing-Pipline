# Data Preprocessing Pipeline

A modular Python pipeline that turns **messy, raw data** into **clean, structured,
analysis-ready datasets**. Built for real-world data problems where inputs arrive
with duplicates, missing values, inconsistent labels, and mixed types.

```
load  ──▶  clean  ──▶  validate  ──▶  export
(ingest)   (transform)   (check)        (persist)
```

---

## Features

- **Reads CSV and Excel** files (`.csv`, `.xlsx`, `.xls`) with full control over
  pandas read options (separators, encodings, dtypes).
- **Normalizes column labels** to consistent `snake_case` and strips stray
  whitespace from text cells.
- **Removes duplicate rows**, with optional subset (natural-key) comparison.
- **Resolves missing values** intelligently by dtype:
  - numeric → median / mean / zero / drop-rows
  - categorical → mode / constant / drop-rows
  - drops columns whose missing fraction exceeds a threshold (default 50%).
- **Validates the data** against required columns, dtype contracts, and quality
  rules (fully-missing and constant columns), with optional fail-fast.
- **Exports** to CSV and Parquet (snappy-compressed) for downstream analytics.
- **Fully configurable** via immutable dataclasses — no magic globals, no
  accidental mutation.
- **Never mutates input** — every stage works on copies, so raw data is preserved.
- **Clear structured logging** at every step.

---

## Installation

Requirements: **Python 3.10+**

```bash
# 1. Clone the repository
git clone https://github.com/sjapanjots/Datapreprocessing-Pipline.git
cd Datapreprocessing-Pipline

# 2. (Recommended) create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate      # macOS / Linux

# 3. Install the package with its runtime dependencies
pip install -e .

# 4. (Optional) install dev dependencies for tests and linting
pip install -e ".[dev]"
```

---

## Quick Start

Point the pipeline at a raw file. It reads it, cleans it, validates it, and
writes the result into the processed folder:

```bash
python -m data_pipeline data/raw/my_file.csv
```

The cleaned output lands at `data/processed/processed.csv`.

### Options

```
python -m data_pipeline <source> [--output-dir DIR] [--log-level LEVEL]

  source         Path to the raw input file (CSV or Excel)
  --output-dir   Where to write the processed output (default: data/processed)
  --log-level    DEBUG | INFO | WARNING | ERROR | CRITICAL  (default: INFO)
```

Example:

```bash
python -m data_pipeline data/raw/customers.csv \
    --output-dir data/processed \
    --log-level DEBUG
```

---

## Using it as a library

The whole pipeline is composed from small, reusable pieces. You can drive the
full flow with one object:

```python
from data_pipeline.pipeline import Pipeline

summary = Pipeline().run("data/raw/sales.csv", output_dir="data/processed")
print(summary)
# {
#   'input_rows': 10000,
#   'input_columns': 12,
#   'output_rows': 9987,
#   'output_columns': 10,
#   'validation_passed': True,
#   'validation_details': [],
#   'written': [WindowsPath('data/processed/processed.csv')],
# }
```

Or assemble individual stages for fine-grained control:

```python
from data_pipeline.config import PipelineConfig
from data_pipeline.cleaners import build_cleaning_pipeline
from data_pipeline.validators import CompositeValidator, SchemaValidator, QualityValidator
from data_pipeline.exporters import CompositeExporter, CsvExporter, ParquetExporter

config = PipelineConfig()
cleaner = build_cleaning_pipeline(config.cleaning)

validators = CompositeValidator(
    [
        SchemaValidator(required_columns=("user_id", "age"), expected_dtypes={"age": "numeric"}),
        QualityValidator(),
    ],
    fail_on_error=False,
)

exporters = CompositeExporter([CsvExporter(), ParquetExporter()])

raw = ...                 # any DataFrame you have
clean = cleaner.transform(raw)
report = validators.validate(clean)

if report.details:
    print("Issues found:", report.details)

exporters.export(clean, "data/processed/out")
```

Each stage can be used independently too — see the `cleaners`, `validators`,
`loaders`, and `exporters` subpackages.

---

## Configuration

Tune behaviour through the immutable config objects in `data_pipeline/config.py`:

| Setting | Default | Purpose |
|---|---|---|
| `cleaning.drop_duplicate_rows` | `True` | Remove exact duplicate rows |
| `cleaning.strip_whitespace` | `True` | Trim leading/trailing spaces in text |
| `cleaning.normalize_column_names` | `True` | Convert labels to `snake_case` |
| `cleaning.missing_column_threshold` | `0.5` | Drop columns with >50% missing |
| `cleaning.numeric_fill_strategy` | `median` | `median`/`mean`/`zero`/`drop` |
| `cleaning.categorical_fill_strategy` | `mode` | `mode`/`constant`/`drop` |
| `validation.required_columns` | `()` | Columns that must be present |
| `validation.fail_on_error` | `False` | Raise if validation fails |

---

## Project structure

```
Datapreprocessing-Pipline/
├── data/
│   ├── raw/                  # put unprocessed source files here
│   ├── processed/            # pipeline output is written here
│   └── external/             # reference / lookup data
├── src/data_pipeline/
│   ├── loaders/              # ingestion (FileLoader for CSV/Excel/base loader)
│   ├── cleaners/             # column normalization, dedup, missing-value handling
│   ├── validators/           # schema + quality checks, ValidationResult
│   ├── exporters/            # CSV/Parquet writers + composite exporter
│   ├── pipeline.py           # end-to-end orchestrator
│   ├── cli.py                # command-line entry point
│   ├── __main__.py           # enables `python -m data_pipeline`
│   └── config.py             # immutable pipeline configuration
└── tests/                    # pytest suite (65 tests)
```

---

## Running tests and lint

```bash
python -m pytest              # run the full test suite (65 tests)
python -m ruff check src tests   # lint the codebase
```

---

## How this helps solve real-world problems

Real datasets are almost never clean. This pipeline automates the boring,
error-prone "data munging" step that dominates real projects:

- **Customer or CRM exports** — deduplicates records, normalizes names, fills
  missing demographic fields, and drops junk columns before analytics or a
  postgres/warehouse load.
- **Sales & financial records** — fills missing numeric amounts with a defensible
  median, removes duplicated transaction rows, and catches constant (dead)
  columns before they poison aggregates.
- **Survey / form responses** — strips inconsistent whitespace, unifies column
  names from messy spreadsheets, and handles partial responses.
- **Marketing / ad logs** — converts ad-hoc CSV dumps into tidy, schema-checked
  data ready for BI dashboards.
- **Migrating to a structured database** — validates that required columns and
  types exist *before* load, so inserts never fail at runtime.

Because raw inputs are **never mutated** and every change is **logged and
validated**, the output is auditable — you always know exactly what was cleaned
and why.

---

## How much data can it process at once?

The pipeline is built on **pandas** and holds the dataset **in memory** while
processing, so capacity scales with the **available RAM** of the machine running
it — not with a fixed limit in the code.

Rough guideline for a typical desktop / laptop (16–32 GB RAM):

| Input size | Rows (approx, ~12 cols) | Memory footprint | Runtime |
|---|---|---|---|
| ~50 MB | ~600k rows | ~1.5 GB | seconds |
| ~250 MB | ~3M rows | ~6–8 GB | tens of seconds |
| ~1 GB | ~12M rows | ~15–25 GB | a few minutes |

A useful rule of thumb: a loaded DataFrame uses roughly **8–15x the raw file
size** in RAM (since pandas stores typed values plus overhead). Because the
pipeline works on **copies** during cleaning, peak memory is roughly
**2–3× the loaded frame**. Plan for that headroom.

For **very large data** (many GBs, tens of millions of rows) that cannot fit
memory comfortably, the recommended approach is to:

- ingest in **chunks** with `pd.read_csv(..., chunksize=...)` and pass each
  chunk through the cleaning steps, or
- use a **columnar engine** (e.g. DuckDB / Polars) for out-of-core processing
  then feed the result into this pipeline's exporters.

---

## License

MIT — see [LICENSE](LICENSE).

---

## About the author

**Japanjot Singh** is available for **freelance and contract work** — and open to
**hiring**. If you need clean, production-grade data pipelines, data engineering,
or Python development, feel free to reach out.

- Available for: freelance, contract, and full-time roles
- Focus: data pipelines, data preprocessing, data engineering, Python

