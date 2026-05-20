"""
CAHF Housing Development Cost Benchmark Kenya 2022 — Extractor
NjengaData | dev-real-data branch

Source: Centre for Affordable Housing Finance in Africa
        Housing Development Cost Benchmarking in Kenya 2022
        Published by CAHF, funded by FSD Africa

Extracts Table 3 (page 11) — cost breakdown by category
for three typologies, all Nairobi, Q3 2022.

Output: data/processed/cahf_cost_breakdown.csv

Schema:
    county          | str   | Nairobi (only city benchmarked)
    unit_type       | str   | 55m2_house / 2BR_lowrise / 2BR_highrise
    unit_size_m2    | int   | 55 / 44 / 44
    cost_category   | str   | Land, Infrastructure, Compliance, etc.
    amount_kes      | int   | Cost per dwelling unit in KES
    pct_of_total    | float | Percentage of total development cost
    year            | int   | 2022
    source          | str   | CAHF HDCB Kenya 2022
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path

PDF_PATH   = Path("data/raw/cahf/CAHF-output_Layout-of-HDCB-Report_Final-0923.pdf")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "cahf_cost_breakdown.csv"

# Page 11 table structure (0-indexed page 10):
# Col 0: cost_category
# Col 1: 55m2 per unit KES
# Col 2: 55m2 per m2 KES
# Col 3: 55m2 % of total
# Col 4: low-rise per unit KES
# Col 5: low-rise per m2 KES
# Col 6: low-rise % of total
# Col 7: high-rise per unit KES
# Col 8: high-rise per m2 KES
# Col 9: high-rise % of total

TYPOLOGIES = [
    ("55m2_house",   55,  1, 3),   # (unit_type, size_m2, amount_col, pct_col)
    ("2BR_lowrise",  44,  4, 6),
    ("2BR_highrise", 44,  7, 9),
]

VALID_CATEGORIES = [
    "Land", "Infrastructure", "Compliances", "Construction",
    "Professional", "Other development", "Marketing", "Finance",
    "Developer overhead", "Total"
]

def clean_kes(val):
    """Convert '378 575' or '378,575' to 378575."""
    if val is None:
        return None
    val = str(val).strip().replace(" ", "").replace(",", "")
    try:
        return int(float(val))
    except ValueError:
        return None

def clean_pct(val):
    """Convert '9.57%' to 9.57."""
    if val is None:
        return None
    val = str(val).strip().replace("%", "").replace(" ", "")
    try:
        return float(val)
    except ValueError:
        return None

def is_category_row(val):
    """Check if the row is a cost category we want."""
    if not val:
        return False
    val = str(val).strip()
    return any(cat.lower() in val.lower() for cat in VALID_CATEGORIES)

def extract_cahf(pdf_path):
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        # Table 3 is on page 11 (0-indexed: page 10)
        page = pdf.pages[10]
        tables = page.extract_tables()

        if not tables:
            print("ERROR: No tables found on page 11")
            return records

        # Find the right table — should have 10 cols and cost category rows
        target_table = None
        for t in tables:
            if t and len(t[0]) >= 9:
                target_table = t
                break

        if not target_table:
            print("ERROR: Could not find cost breakdown table")
            return records

        print(f"Table found: {len(target_table)} rows x {len(target_table[0])} cols")
        print(f"Header: {target_table[0]}")

        for row in target_table:
            if not row or not row[0]:
                continue

            category = str(row[0]).strip()
            if not category or not is_category_row(category):
                continue

            # Clean category name
            if "Compliances" in category or "compliances" in category:
                category = "Compliance"
            elif "Professional" in category:
                category = "Professional fees"
            elif "Other development" in category:
                category = "Other development costs"
            elif "Developer overhead" in category:
                category = "Developer overhead"

            for unit_type, size_m2, amt_col, pct_col in TYPOLOGIES:
                amount = clean_kes(row[amt_col]) if amt_col < len(row) else None
                pct    = clean_pct(row[pct_col]) if pct_col < len(row) else None

                if amount and amount > 0:
                    records.append({
                        "county":       "Nairobi",
                        "unit_type":    unit_type,
                        "unit_size_m2": size_m2,
                        "cost_category": category,
                        "amount_kes":   amount,
                        "pct_of_total": pct,
                        "year":         2022,
                        "source":       "CAHF HDCB Kenya 2022"
                    })
                    print(f"  {unit_type:15} {category:30} KES {amount:>10,}  {pct}%")

    return records

def analyse(df):
    print(f"\n--- Finding 1: Where does James's money go? ---")
    print(f"(2BR low-rise apartment, Nairobi 2022)\n")

    lowrise = df[df["unit_type"] == "2BR_lowrise"].copy()
    lowrise = lowrise[lowrise["cost_category"] != "Total"]
    lowrise = lowrise.sort_values("pct_of_total", ascending=False)

    for _, row in lowrise.iterrows():
        bar = "█" * int(row["pct_of_total"] / 2)
        print(f"  {row['cost_category']:30} {bar:30} {row['pct_of_total']:5.1f}%  KES {row['amount_kes']:>10,}")

    # Pre-construction costs (land + infrastructure + compliance)
    pre_construction = lowrise[lowrise["cost_category"].isin(
        ["Land", "Infrastructure", "Compliance"]
    )]["pct_of_total"].sum()
    print(f"\n  Pre-construction total (Land + Infra + Compliance): {pre_construction:.1f}%")

    print(f"\n--- Typology comparison (total development cost) ---\n")
    totals = df[df["cost_category"] == "Total"][
        ["unit_type", "unit_size_m2", "amount_kes"]
    ].sort_values("amount_kes", ascending=False)
    for _, row in totals.iterrows():
        print(f"  {row['unit_type']:15} ({row['unit_size_m2']}m2): KES {row['amount_kes']:>12,}")

def main():
    if not PDF_PATH.exists():
        print(f"ERROR: {PDF_PATH} not found.")
        print("Place CAHF PDF at data/raw/cahf/CAHF-output_Layout-of-HDCB-Report_Final-0923.pdf")
        return

    print("NjengaData — CAHF Cost Breakdown Extractor")
    print("Source: CAHF Housing Development Cost Benchmark Kenya 2022\n")
    print("Extracting Table 3 (page 11)...\n")

    records = extract_cahf(PDF_PATH)

    if not records:
        print("No records extracted.")
        return

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n--- Summary ---")
    print(f"Rows:    {len(df)}")
    print(f"Output:  {OUTPUT_FILE.resolve()}")

    analyse(df)

if __name__ == "__main__":
    main()
