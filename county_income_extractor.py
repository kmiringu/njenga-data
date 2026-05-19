"""
Kenya Poverty Report 2022 (KCHS) — County Expenditure Extractor
NjengaData | dev-real-data branch

Source: The Kenya Poverty Report 2022, KNBS
        Based on Kenya Continuous Household Survey (KCHS) 2022
        Tables 3.3a (rural) and 3.3b (urban)

Extracts mean and median monthly expenditure per adult equivalent
in KES for all available counties, split by rural and urban.

We use URBAN figures for James — he is building in a city.
Median is more appropriate than mean for affordability ratio
(mean is skewed by top quintile earners).

Output: data/processed/county_income.csv

Schema:
    county          | str   | e.g. Nairobi, Mombasa
    residence       | str   | Rural / Urban
    mean_monthly_kes| float | Mean monthly expenditure per adult equivalent
    median_monthly_kes| float | Median monthly expenditure per adult equivalent
    year            | int   | 2022
    source          | str   | KCHS 2022
"""

import pdfplumber
import pandas as pd
from pathlib import Path
import re

PDF_PATH   = Path("data/raw/finaccess/Kenya_Poverty_Report_2022.pdf")
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "county_income.csv"

def clean_float(val):
    if val is None:
        return None
    val = str(val).strip().replace(",", "").replace(" ", "")
    try:
        return float(val)
    except ValueError:
        return None

def is_county_name(val):
    """Check if value looks like a county name — not a number or header."""
    if not val:
        return False
    val = str(val).strip()
    if not val or val.isdigit():
        return False
    if val in ["Rural", "Urban", "National", "Mean", "Median", "County"]:
        return False
    if re.match(r'^[\d\.<>,-]+$', val):
        return False
    return len(val) > 2

def extract_county_tables(pdf_path):
    """
    Extract Tables 3.3a (rural, page 39) and 3.3b (urban, page 41).
    Each table has rows: County | Mean | Median | Q1% | Q2% | Q3% | Q4% | Q5%
    We only need County, Mean, Median.
    """
    records = []

    with pdfplumber.open(pdf_path) as pdf:
        # Page 39 = rural, Page 41 = urban (0-indexed: 38, 40)
        page_configs = [
            (38, "Rural"),
            (40, "Urban"),
        ]

        for page_idx, residence in page_configs:
            page = pdf.pages[page_idx]
            tables = page.extract_tables()

            print(f"\n  {residence} (page {page_idx+1}): {len(tables)} tables found")

            for table in tables:
                if not table:
                    continue

                # Each county is its own 1-row table in this PDF
                # Header row: [county_name, mean, median, Q1%, Q2%, Q3%, Q4%, Q5%]
                header = table[0]
                if not header or len(header) < 3:
                    continue

                # Check if header looks like a county data row
                county_name = str(header[0]).strip() if header[0] else ""
                mean_val    = clean_float(header[1]) if len(header) > 1 else None
                median_val  = clean_float(header[2]) if len(header) > 2 else None

                if is_county_name(county_name) and mean_val and median_val:
                    if 1000 <= mean_val <= 50000:  # sanity check
                        records.append({
                            "county":             county_name,
                            "residence":          residence,
                            "mean_monthly_kes":   mean_val,
                            "median_monthly_kes": median_val,
                            "year":               2022,
                            "source":             "KCHS 2022"
                        })
                        print(f"    {county_name}: mean={mean_val}, median={median_val}")

                # Also check data rows within each table
                for row in table[1:]:
                    if not row or len(row) < 3:
                        continue
                    county_name = str(row[0]).strip() if row[0] else ""
                    mean_val    = clean_float(row[1])
                    median_val  = clean_float(row[2])

                    if is_county_name(county_name) and mean_val and median_val:
                        if 1000 <= mean_val <= 50000:
                            records.append({
                                "county":             county_name,
                                "residence":          residence,
                                "mean_monthly_kes":   mean_val,
                                "median_monthly_kes": median_val,
                                "year":               2022,
                                "source":             "KCHS 2022"
                            })
                            print(f"    {county_name}: mean={mean_val}, median={median_val}")

    return records

def add_national_and_missing(records):
    """
    Add national figures and any key counties missed by extractor.
    Values read directly from report text.
    """
    # National figures from Table 3.3a/3.3b header rows (confirmed from PDF)
    manual = [
        # National
        {"county": "National", "residence": "Rural",  "mean_monthly_kes": 5712,  "median_monthly_kes": 4881,  "year": 2022, "source": "KCHS 2022"},
        {"county": "National", "residence": "Urban",  "mean_monthly_kes": 12978, "median_monthly_kes": 9433,  "year": 2022, "source": "KCHS 2022"},
        # Nairobi urban — from page 40 text: "KSh 12,831 and Tharaka-Nithi (12,776)"
        {"county": "Nairobi",  "residence": "Urban",  "mean_monthly_kes": 12831, "median_monthly_kes": 9433,  "year": 2022, "source": "KCHS 2022"},
        # Mombasa urban — Table 3.3b: Mean 12,072, Median 11,597
        {"county": "Mombasa",  "residence": "Urban",  "mean_monthly_kes": 12072, "median_monthly_kes": 11597, "year": 2022, "source": "KCHS 2022"},
    ]

    # Check which counties are already in records to avoid duplicates
    existing = {(r["county"], r["residence"]) for r in records}
    for m in manual:
        if (m["county"], m["residence"]) not in existing:
            records.append(m)
            print(f"    [manual] {m['county']} ({m['residence']}): mean={m['mean_monthly_kes']}, median={m['median_monthly_kes']}")

    return records

def extract_all():
    if not PDF_PATH.exists():
        print(f"ERROR: {PDF_PATH} not found.")
        print("Download: https://www.knbs.or.ke/wp-content/uploads/2024/10/The-Kenya-Poverty-Report-2022.pdf")
        return

    print("NjengaData — County Income Extractor")
    print("Source: Kenya Poverty Report 2022 (KCHS)\n")
    print("Extracting county expenditure tables...")

    records = extract_county_tables(PDF_PATH)
    records = add_national_and_missing(records)

    if not records:
        print("\nNo records extracted.")
        return

    df = pd.DataFrame(records)
    df = df.drop_duplicates(subset=["county", "residence"])
    df = df.sort_values(["residence", "mean_monthly_kes"], ascending=[True, False])
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n--- Summary ---")
    print(f"Total rows:  {len(df)}")
    print(f"Counties:    {df['county'].nunique()}")
    print(f"Output:      {OUTPUT_FILE.resolve()}")

    print(f"\nUrban counties by mean monthly expenditure:")
    urban = df[df['residence'] == 'Urban'][
        ["county", "mean_monthly_kes", "median_monthly_kes"]
    ].sort_values("mean_monthly_kes", ascending=False)
    print(urban.to_string(index=False))

    print(f"\nAffordability ratio check (CAHF 2BR low-rise = KES 3,015,486):")
    cahf_cost = 3_015_486
    avg_hh_size = 3.9

    data = {
        "Nairobi":  9433,
        "Mombasa":  11597,
        "Nakuru":   11194,
        "Kiambu":   11682,
    }

    print("Corrected affordability ratios")
    print("CAHF 2BR low-rise = KES 3,015,486")
    print("Household size: 3.9 persons (KNBS average)\n")
    print(f"{'County':15} {'Per adult/mo':>15} {'HH monthly':>15} {'HH   annual':>15} {'Years':>8}")
    print("-" * 70)
    for county, per_adult in data.items():
        hh_monthly = per_adult * avg_hh_size
        hh_annual  = hh_monthly * 12
        years      = cahf_cost / hh_annual
        print(f"{county:15} {per_adult:>15,.0f} {hh_monthly:>15,.0f} {hh_annual:>15,.0f} {years:>8.1f}")

if __name__ == "__main__":
    extract_all()
