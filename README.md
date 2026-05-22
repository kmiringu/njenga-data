# NjengaData

Helping ordinary Kenyans understand the real cost of building their own home.

NjengaData pulls together four public data sources into a single pipeline that answers
the questions an incremental builder like James — earning KSh 40,000 a month — actually asks:
what will it cost, where is it cheaper, are materials getting more expensive, and can I afford it?

---

## Data sources

| Source | Description | Years |
|---|---|---|
| KNBS CIPI | Construction Input Price Index — quarterly material prices | 2019–2023 |
| CAHF | Centre for Affordable Housing Finance Africa — county housing costs | 2022 |
| KCHS | Kenya Continuous Household Survey — county median household income | 2022 |
| Integrum | Regional construction cost per m2 | 2021–2024 |

All sources are publicly available. Raw files are in `data/raw/`.

---
## Running the pipeline

Run the three notebooks in order:

| Notebook | Owner | What it does |
|---|---|---|
| `01_data_cleaning.ipynb` Loads, cleans and writes all four sources to `njenga.db` |
| `02_analysis.ipynb` Runs SQL queries against `njenga.db`, produces four findings |
| `03_dashboard.ipynb` Reads findings and generates four charts to `data/processed/charts/` |

Open each notebook and run **Kernel > Restart and Run All**.
Start with 01 — it builds the database that 02 and 03 depend on.

---

## The four findings

- **F1** — A 2BR low-rise in Nairobi costs KSh 2.2M–2.5M. Labour is the largest cost at 38–42%.
- **F2** — Steel prices rose 19.6% between 2019 and 2023. Cement rose 11.2%.
- **F3** — Coastal counties build 18–22% cheaper than Nairobi.
- **F4** — A household on median Nairobi income needs 25.4 years of savings to afford a 2BR build.

---
njenga-data/
├── data/
│   ├── raw/          # original source files, untouched
│   ├── processed/    # cleaned outputs and charts
│   └── njenga.db     # SQLite database built by notebook 01
├── notebooks/
│   ├── 01_data_cleaning.ipynb
│   ├── 02_analysis.ipynb
│   └── 03_dashboard.ipynb
├── assets/           # images used in notebooks
├── requirements.txt
└── README.md

---

*NjengaData — built for the 2026 Kenya Housing Data Hackathon.*