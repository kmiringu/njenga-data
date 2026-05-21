# 03_dashboard.ipynb — Update README
**Visualization Specialist: Stacey Koigu | Moringa Hackathon 22 May 2026**

---

## What I Did 

The original spec was 4 charts. I delivered 5 charts plus an Executive Summary and judge Q&A cells. Everything is backed by data already in `njenga.db` or the processed CSVs.

| What | Where | Why |
|---|---|---|
| Chart 3 — dynamic % labels | Section 5 | Labels compute from actual data, not hardcoded |
| Per-material loop | Section 5 | Can show 1, 2, or all 3 materials by changing one list |
| Chart 5 — Benchmark vs Real | Section 8 (new) | Uses both CAHF and Kemika to validate the numbers |
| Executive Summary | Section 3 (new) | Judges see findings first before any chart |
| df_q5 data load | Section 2 | One SQL query added to existing data loading cell |
| Verification cell | Section 9 | Updated to check all 5 charts |

---

## Judge Questions — What to Say

### "Where did this data come from and can you trust it?"
Point at Chart 5. Say:
> *"CAHF is a pan-African research body. Kemika are real anonymised project BOQs from 2023 and 2024. The two sources track each other closely — which validates both. Where they diverge, like land and materials rising in 2024, that is real inflation showing up in real projects."*

### "Why only four counties?"
> *"These are the only four with complete data across all three sources — CAHF, Kemika, and KNBS. Including others would mean mixing complete and incomplete cost structures, which makes county comparison misleading. With more data we would expand to ten-plus counties starting with Kisumu, Eldoret, and Machakos."*

### "What would a homeowner actually do with this?"
Run the homeowner cost checker cell. Say:
> *"A homeowner changes their county and instantly sees what their house should cost per category. If a contractor quotes KES 1.5M for materials when the benchmark is KES 1.2M, they know to ask why. That is the transparency this project delivers."*

### "What is your recommendation?"
> *"Every recommendation points back to a finding. Compliance fees are the most addressable cost at 12.7%. Nakuru is the most underutilised opportunity — 27% cheaper than Nairobi for the same house. Steel has softened since 2022 making now a better time to build. And the core recommendation is transparency — homeowners need a benchmark to negotiate with."*

### "What caused the 2022 steel spike?"
> *"Post-COVID global supply chain crisis. Steel prices spiked worldwide due to shipping disruptions, energy costs, and surging construction demand as lockdowns lifted. Cement never corrected — it has risen every year since 2019."*

### "What would you do with more time?"
> *"Five things: expand to more counties, track material prices by county not just nationally, collect real contractor quotes to show the markup gap, break cost down to KES per square metre, and build a web app where any homeowner can check if they are being overcharged."*

---
