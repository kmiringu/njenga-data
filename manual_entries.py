"""
Manual data entry for image-based KNBS CIPI PDFs
NjengaData | dev-real-data branch

Sources read directly from uploaded PDFs:
- 2021 Q4: page 2 of KNBS_CIPI_2021_Q4.pdf (Table 1)
- 2022 Q2: page 3 of KNBS_CIPI_2022_Q4.pdf (Q2-2022 column)
- 2022 Q3: page 3 of KNBS_CIPI_2022_Q3.pdf (Q3-2022 column)
- 2022 Q4: page 3 of KNBS_CIPI_2022_Q4.pdf (Q4-2022 column)
- 2025 Q3: partial from narrative text

All values: Table 1 Building Cost Index, base Dec 2019 = 100
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR  = Path("data/processed")
OUTPUT_FILE = OUTPUT_DIR / "knbs_material_index.csv"

# ── 2021 Q4 ── page 2 of KNBS_CIPI_2021_Q4.pdf, Q4-2021 column
Q4_2021 = [
    ("Materials",        "Cement /Lime",                            14.18,  96.32),
    ("Materials",        "Hard core",                                8.37, 103.64),
    ("Materials",        "Quarry products(waste,dust and murram)",   1.27, 103.90),
    ("Materials",        "Sand",                                     3.14,  93.93),
    ("Materials",        "Ballast",                                  4.50,  97.96),
    ("Materials",        "Steel and reinforced bars",               10.69, 131.81),
    ("Materials",        "Stones",                                   2.42,  95.35),
    ("Materials",        "Damp Proofing and Anti-termite",           0.58,  91.84),
    ("Materials",        "Timber and Wood",                          2.20,  99.57),
    ("Materials",        "Paving blocks",                            2.06, 120.61),
    ("Materials",        "Roofing materials",                        0.70, 101.61),
    ("Materials",        "Doors",                                    0.24, 100.68),
    ("Materials",        "Metal doors and windows",                  0.26, 103.42),
    ("Materials",        "Glass and glass putty",                    0.16, 114.18),
    ("Materials",        "Locks and iron mongery",                   0.78, 105.31),
    ("Materials",        "Tiles",                                    0.84, 104.53),
    ("Materials",        "Chip boards and MDF",                      1.01,  98.66),
    ("Materials",        "Paints",                                   1.06, 102.13),
    ("Materials",        "Sanitary fittings",                        0.16, 103.18),
    ("Materials",        "Water fittings",                           0.11, 101.50),
    ("Materials",        "Water wastes",                             0.12, 102.91),
    ("Materials",        "Electrical fittings",                      0.51, 102.79),
    ("Equipment",        "Equipment-Concrete Mixer",                 5.16,  97.99),
    ("Equipment",        "Equipment-Concrete poker / Vibrator",      2.36, 103.71),
    ("Equipment",        "Equipment-Excavator and Pedestrian Roller",2.64, 100.01),
    ("Equipment",        "Compressors",                              3.04,  99.45),
    ("Transport and Fuel","Transport",                               5.99, 108.90),
    ("Transport and Fuel","Fuel",                                    3.99, 102.30),
    ("Labour",           "Casual",                                   6.67, 106.99),
    ("Labour",           "Watchman",                                 2.01, 106.49),
    ("Labour",           "Plumber/Electrician",                      0.52, 102.38),
    ("Labour",           "Machine /plant operators",                 0.91, 100.61),
    ("Labour",           "Carpenter/Painter/Welder/Mechanic",        3.53, 104.56),
    ("Labour",           "Mason/foreman",                            7.80, 104.43),
]

# ── 2022 Q2 ── page 3 of KNBS_CIPI_2022_Q4.pdf, Q2-2022 column
Q2_2022 = [
    ("Materials",        "Cement /Lime",                            14.18, 105.84),
    ("Materials",        "Hard core",                                8.37, 108.61),
    ("Materials",        "Quarry products(waste,dust and murram)",   1.27, 105.81),
    ("Materials",        "Sand",                                     3.14,  94.43),
    ("Materials",        "Ballast",                                  4.50,  98.54),
    ("Materials",        "Steel and reinforced bars",               10.69, 189.19),
    ("Materials",        "Stones",                                   2.42,  99.15),
    ("Materials",        "Damp Proofing and Anti-termite",           0.58,  89.76),
    ("Materials",        "Timber and Wood",                          2.20,  98.41),
    ("Materials",        "Paving blocks",                            2.06, 126.98),
    ("Materials",        "Roofing materials",                        0.70, 108.20),
    ("Materials",        "Doors",                                    0.24, 104.41),
    ("Materials",        "Metal doors and windows",                  0.26, 108.05),
    ("Materials",        "Glass and glass putty",                    0.16, 136.13),
    ("Materials",        "Locks and iron mongery",                   0.78, 110.52),
    ("Materials",        "Tiles",                                    0.84, 109.71),
    ("Materials",        "Chip boards and MDF",                      1.01,  97.53),
    ("Materials",        "Paints",                                   1.06, 105.11),
    ("Materials",        "Sanitary fittings",                        0.16, 111.57),
    ("Materials",        "Water fittings",                           0.11, 111.96),
    ("Materials",        "Water wastes",                             0.12, 105.05),
    ("Materials",        "Electrical fittings",                      0.51, 112.50),
    ("Equipment",        "Equipment-Concrete Mixer",                 5.16, 106.49),
    ("Equipment",        "Equipment-Concrete poker / Vibrator",      2.36, 110.93),
    ("Equipment",        "Equipment-Excavator and Pedestrian Roller",2.64, 104.56),
    ("Equipment",        "Compressors",                              3.04, 101.70),
    ("Transport and Fuel","Transport",                               5.99, 113.09),
    ("Transport and Fuel","Fuel",                                    3.99, 106.61),
    ("Labour",           "Casual",                                   6.67, 109.74),
    ("Labour",           "Watchman",                                 2.01, 108.89),
    ("Labour",           "Plumber/Electrician",                      0.52, 103.18),
    ("Labour",           "Machine /plant operators",                 0.91, 102.40),
    ("Labour",           "Carpenter/Painter/Welder/Mechanic",        3.53, 105.75),
    ("Labour",           "Mason/foreman",                            7.80, 106.74),
]

# ── 2022 Q3 ── page 3 of KNBS_CIPI_2022_Q3.pdf (confirmed from uploaded PDF)
Q3_2022 = [
    ("Materials",        "Cement /Lime",                            14.18, 102.79),
    ("Materials",        "Hard core",                                8.37, 108.13),
    ("Materials",        "Quarry products(waste,dust and murram)",   1.27, 101.93),
    ("Materials",        "Sand",                                     3.14,  94.94),
    ("Materials",        "Ballast",                                  4.50,  96.59),
    ("Materials",        "Steel and reinforced bars",               10.69, 171.44),
    ("Materials",        "Stones",                                   2.42,  99.81),
    ("Materials",        "Damp Proofing and Anti-termite",           0.58,  82.40),
    ("Materials",        "Timber and Wood",                          2.20,  98.54),
    ("Materials",        "Paving blocks",                            2.06, 115.12),
    ("Materials",        "Roofing materials",                        0.70, 110.69),
    ("Materials",        "Doors",                                    0.24, 107.83),
    ("Materials",        "Metal doors and windows",                  0.26, 108.27),
    ("Materials",        "Glass and glass putty",                    0.16, 133.66),
    ("Materials",        "Locks and iron mongery",                   0.78, 105.57),
    ("Materials",        "Tiles",                                    0.84, 111.21),
    ("Materials",        "Chip boards and MDF",                      1.01,  97.79),
    ("Materials",        "Paints",                                   1.06, 104.59),
    ("Materials",        "Sanitary fittings",                        0.16, 109.92),
    ("Materials",        "Water fittings",                           0.11, 112.06),
    ("Materials",        "Water wastes",                             0.12, 104.32),
    ("Materials",        "Electrical fittings",                      0.51, 104.17),
    ("Equipment",        "Equipment-Concrete Mixer",                 5.16, 106.11),
    ("Equipment",        "Equipment-Concrete poker / Vibrator",      2.36, 104.90),
    ("Equipment",        "Equipment-Excavator and Pedestrian Roller",2.64, 101.76),
    ("Equipment",        "Compressors",                              3.04, 104.67),
    ("Transport and Fuel","Transport",                               5.99, 115.35),
    ("Transport and Fuel","Fuel",                                    3.99, 111.95),
    ("Labour",           "Casual",                                   6.67, 109.65),
    ("Labour",           "Watchman",                                 2.01, 110.28),
    ("Labour",           "Plumber/Electrician",                      0.52, 100.61),
    ("Labour",           "Machine /plant operators",                 0.91, 104.65),
    ("Labour",           "Carpenter/Painter/Welder/Mechanic",        3.53, 106.62),
    ("Labour",           "Mason/foreman",                            7.80, 109.21),
]

# ── 2022 Q4 ── page 3 of KNBS_CIPI_2022_Q4.pdf, Q4-2022 column
Q4_2022 = [
    ("Materials",        "Cement /Lime",                            14.18, 103.51),
    ("Materials",        "Hard core",                                8.37, 108.76),
    ("Materials",        "Quarry products(waste,dust and murram)",   1.27, 101.97),
    ("Materials",        "Sand",                                     3.14,  96.20),
    ("Materials",        "Ballast",                                  4.50, 100.47),
    ("Materials",        "Steel and reinforced bars",               10.69, 168.58),
    ("Materials",        "Stones",                                   2.42, 100.31),
    ("Materials",        "Damp Proofing and Anti-termite",           0.58,  81.60),
    ("Materials",        "Timber and Wood",                          2.20,  97.52),
    ("Materials",        "Paving blocks",                            2.06, 114.22),
    ("Materials",        "Roofing materials",                        0.70, 110.42),
    ("Materials",        "Doors",                                    0.24, 109.27),
    ("Materials",        "Metal doors and windows",                  0.26, 101.27),
    ("Materials",        "Glass and glass putty",                    0.16, 135.59),
    ("Materials",        "Locks and iron mongery",                   0.78, 109.01),
    ("Materials",        "Tiles",                                    0.84, 112.10),
    ("Materials",        "Chip boards and MDF",                      1.01,  96.55),
    ("Materials",        "Paints",                                   1.06, 106.08),
    ("Materials",        "Sanitary fittings",                        0.16, 114.23),
    ("Materials",        "Water fittings",                           0.11, 112.72),
    ("Materials",        "Water wastes",                             0.12, 107.67),
    ("Materials",        "Electrical fittings",                      0.51, 104.35),
    ("Equipment",        "Equipment-Concrete Mixer",                 5.16, 105.39),
    ("Equipment",        "Equipment-Concrete poker / Vibrator",      2.36, 102.14),
    ("Equipment",        "Equipment-Excavator and Pedestrian Roller",2.64, 100.66),
    ("Equipment",        "Compressors",                              3.04, 104.27),
    ("Transport and Fuel","Transport",                               5.99, 117.72),
    ("Transport and Fuel","Fuel",                                    3.99, 116.38),
    ("Labour",           "Casual",                                   6.67, 109.65),
    ("Labour",           "Watchman",                                 2.01, 110.28),
    ("Labour",           "Plumber/Electrician",                      0.52, 101.41),
    ("Labour",           "Machine /plant operators",                 0.91, 105.10),
    ("Labour",           "Carpenter/Painter/Welder/Mechanic",        3.53, 107.39),
    ("Labour",           "Mason/foreman",                            7.80, 109.21),
]

# ── 2025 Q3 ── partial from narrative text (2025 Q3 PDF is image-based)
# Values derived from percentage changes stated in text applied to Q2 2025 values
Q3_2025_PARTIAL = [
    ("Materials",        "Steel and reinforced bars",               10.69, 184.99),
    ("Materials",        "Sand",                                     3.14, 108.34),
    ("Materials",        "Cement /Lime",                            14.18, 118.76),
    ("Materials",        "Roofing materials",                        0.70, 124.97),
    ("Transport and Fuel","Transport",                               5.99, 139.15),
    ("Transport and Fuel","Fuel",                                    3.99, 136.12),
]

def build_records(data, year, quarter):
    return [{
        "year": year, "quarter": quarter,
        "category": r[0], "product": r[1],
        "weight": r[2], "index_value": r[3],
    } for r in data]

def append_to_csv():
    if not OUTPUT_FILE.exists():
        print(f"ERROR: {OUTPUT_FILE} not found. Run knbs_extractor.py first.")
        return

    existing = pd.read_csv(OUTPUT_FILE)
    print(f"Existing rows: {len(existing)}")

    additions = [
        (Q4_2021, 2021, "Q4"),
        (Q2_2022, 2022, "Q2"),
        (Q3_2022, 2022, "Q3"),
        (Q4_2022, 2022, "Q4"),
        (Q3_2025_PARTIAL, 2025, "Q3"),
    ]

    new_records = []
    for data, year, quarter in additions:
        new_records.extend(build_records(data, year, quarter))

    new_df = pd.DataFrame(new_records)

    # Remove any existing entries for these quarters to avoid duplicates
    remove = [(2021,"Q4"),(2022,"Q2"),(2022,"Q3"),(2022,"Q4"),(2025,"Q3")]
    mask = ~existing.apply(
        lambda r: any(r["year"]==y and r["quarter"]==q for y,q in remove), axis=1
    )
    existing_clean = existing[mask]

    combined = pd.concat([existing_clean, new_df], ignore_index=True)
    combined = combined.sort_values(["year","quarter","category","product"])
    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"Added rows:    {len(new_df)}")
    print(f"Total rows:    {len(combined)}")

    print(f"\nQuarters now covered:")
    summary = combined.groupby(["year","quarter"])["product"].count().reset_index()
    summary.columns = ["year","quarter","products"]
    print(summary.to_string(index=False))

    print(f"\nCement trend (base=100):")
    cement = combined[combined['product'].str.contains("Cement", case=False)][
        ["year","quarter","index_value"]].sort_values(["year","quarter"])
    print(cement.to_string(index=False))

    print(f"\nSteel trend (base=100):")
    steel = combined[combined['product'].str.contains("Steel", case=False)][
        ["year","quarter","index_value"]].sort_values(["year","quarter"])
    print(steel.to_string(index=False))

if __name__ == "__main__":
    print("NjengaData — Manual KNBS Data Entry")
    print("Adding: 2021 Q4, 2022 Q2/Q3/Q4, 2025 Q3 partial\n")
    append_to_csv()
