"""
KNBS Construction Input Price Index — PDF Extractor
NjengaData | dev-real-data branch

Extracts Table 1 (Building Cost Index) only — the most relevant
table for residential construction (James builds a house, not a road).

Table 1 is on page 2 in all PDF versions.
It contains 22 materials + 4 equipment + 2 transport + 6 labour = 34 items.

Strategy:
  - Extract text from page 2 only
  - Find lines that start with a row number
  - Parse product name, weight, and LAST numeric value (current quarter)
  - Sanity check: index values must be between 50 and 350

Output: data/processed/knbs_material_index.csv
Schema: year, quarter, category, product, weight, index_value
"""

import pdfplumber
import pandas as pd
import re
from pathlib import Path

INPUT_DIR   = Path("data/raw/knbs")
OUTPUT_DIR  = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "knbs_material_index.csv"

def parse_key(filename):
    stem = Path(filename).stem        # KNBS_CIPI_2024_Q3
    parts = stem.split("_")
    return int(parts[2]), parts[3]    # year, quarter

def infer_category(product):
    p = product.lower()
    if any(k in p for k in ["transport", "fuel", "lubricant"]):
        return "Transport and Fuel"
    if any(k in p for k in ["casual", "watchman", "plumber", "electrician",
                              "machine", "carpenter", "painter", "mason",
                              "foreman", "site agent", "laboratory", "driver",
                              "surveyor", "operator", "welder", "mechanic"]):
        return "Labour"
    if any(k in p for k in ["mixer", "poker", "vibrator", "excavator",
                              "compressor", "roller", "grader", "pedestrian"]):
        return "Equipment"
    return "Materials"

def normalise_spaced_numbers(line):
    """
    KNBS PDFs have two spacing artefacts:
      '1 07.02' -> '107.02'  index values >= 100 split as '1 xx.xx'
      '8 .37'   -> '8.37'    weights with space before decimal
      '0 .58'   -> '0.58'
    """
    line = re.sub(r'\b(1)\s+(\d{2}\.\d+)', r'\1\2', line)
    line = re.sub(r'\b(\d)\s+\.(\d+)', r'\1.\2', line)
    return line

def parse_data_line(line):
    """
    Parse a single data line from Table 1.
    Format: "6 Steel and reinforced bars 10.69 100 107.02 108.46 ... 120.78"
    Returns (product_name, weight, last_value) or None.
    """
    line = line.strip()
    if not line:
        return None

    # Must start with a row number (1-34)
    m = re.match(r'^(\d{1,2})\s+(.+)', line)
    if not m:
        return None

    row_num = int(m.group(1))
    if row_num < 1 or row_num > 40:
        return None

    rest = m.group(2)
    rest_norm = normalise_spaced_numbers(rest)

    # Extract all decimal numbers from the normalised line
    decimals = re.findall(r'\d+\.\d+', rest_norm)
    if len(decimals) < 2:
        return None

    # First decimal = weight (typically < 25)
    weight = float(decimals[0])
    if weight > 25:
        return None

    # Last decimal = current quarter value (must be in realistic range)
    last_val = float(decimals[-1])
    if not (50 <= last_val <= 350):
        return None

    # Product name = everything before the first decimal number
    name_match = re.match(r'^(.*?)\s+\d+\.\d+', rest_norm)
    if not name_match:
        return None

    product = name_match.group(1).strip()
    product = re.sub(r'\s+', ' ', product)

    # Skip known non-product lines
    skip = ["materials", "labour", "equipment", "transport and fuel",
            "transport and fuels", "overall building cost index",
            "overall construction cost index", "overall civil engineering"]
    if product.lower() in skip:
        return None

    return product, weight, last_val

def extract_table1_from_text(text, year, quarter):
    """
    Extract all Table 1 rows from page text.
    Table 1 starts after 'Building' header and ends at 'Overall Building Cost Index'.
    """
    records = []
    lines = text.split("\n")

    in_table = False
    for line in lines:
        stripped = line.strip()

        # Detect Table 1 start — look for the column header line
        if not in_table:
            if re.search(r'(Building.{0,30}(Index|Indices))', stripped, re.I):
                in_table = True
            continue

        # Stop at end of Table 1
        if re.search(r'overall building cost index', stripped, re.I):
            # Parse this summary line too if it has data
            break

        # Stop if we hit Table 2 or Table 3
        if re.search(r'civil engineering|overall construction', stripped, re.I):
            break

        result = parse_data_line(stripped)
        if result:
            product, weight, value = result
            records.append({
                "year":        year,
                "quarter":     quarter,
                "category":    infer_category(product),
                "product":     product,
                "weight":      weight,
                "index_value": value,
            })

    return records

def try_all_pages(pdf_path, year, quarter):
    """
    Try page 2 first (standard location for Table 1).
    Fall back to scanning all pages if page 2 yields nothing.
    """
    with pdfplumber.open(pdf_path) as pdf:
        # Try page 2 first
        if len(pdf.pages) >= 2:
            text = pdf.pages[1].extract_text()
            if text:
                records = extract_table1_from_text(text, year, quarter)
                if records:
                    return records, "page2"

        # Fall back — scan all pages
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            if re.search(r'Building.{0,30}(Index|Indices)', text, re.I):
                records = extract_table1_from_text(text, year, quarter)
                if records:
                    return records, f"page{i+1}"

    return [], "none"

def extract_all():
    pdfs = sorted(INPUT_DIR.glob("KNBS_CIPI_*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {INPUT_DIR.resolve()}")
        return

    all_records = []
    print(f"Processing {len(pdfs)} PDFs...\n")

    for pdf_path in pdfs:
        year, quarter = parse_key(pdf_path.name)
        print(f"  {year} {quarter} ...", end=" ", flush=True)

        try:
            records, source = try_all_pages(pdf_path, year, quarter)
            if records:
                all_records.extend(records)
                print(f"OK [{source}] — {len(records)} rows")
            else:
                print(f"WARN — 0 rows")
        except Exception as e:
            print(f"ERROR — {e}")

    if not all_records:
        print("\nNo records extracted.")
        return

    df = pd.DataFrame(all_records)
    df = df.dropna(subset=["index_value"])
    df = df.sort_values(["year", "quarter", "category", "product"])
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"\n--- Summary ---")
    print(f"Total rows:   {len(df)}")
    print(f"Years:        {sorted(df['year'].unique())}")
    print(f"Quarters:     {sorted(df['quarter'].unique())}")
    print(f"Products:     {df['product'].nunique()}")
    print(f"Output:       {OUTPUT_FILE.resolve()}")

    print(f"\nCement trend (base=100):")
    cement = df[df['product'].str.contains("Cement", case=False)][
        ["year","quarter","index_value"]].sort_values(["year","quarter"])
    print(cement.to_string(index=False))

    print(f"\nSteel trend (base=100):")
    steel = df[df['product'].str.contains("Steel", case=False)][
        ["year","quarter","index_value"]].sort_values(["year","quarter"])
    print(steel.to_string(index=False))

    print(f"\nOverall index range: {df['index_value'].min():.2f} — {df['index_value'].max():.2f}")

if __name__ == "__main__":
    print("NjengaData — KNBS CIPI Extractor")
    print("Extracting: Table 1 (Building Cost Index), base Dec 2019 = 100\n")
    extract_all()
