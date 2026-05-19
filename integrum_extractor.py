"""
Integrum Regional Construction Costs — Extractor
NjengaData | dev-real-data branch

Source: Integrum Construction annual cost reports
        integrum.co.ke/construction-costs-in-kenya-[year]/

Data confirmed from published annual reports 2021-2025.
Standard bungalow rate per m2 — the most relevant typology
for James (incremental home builder).

Three regions:
  Nairobi/Mt Kenya — covers Nairobi, Kiambu, Machakos, Nyeri,
                      Nanyuki, Meru, Murang'a, Kirinyaga, Embu
  Coast            — covers Mombasa, Kilifi, Kwale
  Western/Nyanza   — covers Kisumu, Kakamega, Kericho, Kitale,
                      Kisii, Eldoret

Output: data/processed/integrum_regional_costs.csv

Schema:
    year          | int   | 2021-2025
    region        | str   | Nairobi/Mt Kenya, Coast, Western/Nyanza
    typology      | str   | Standard Bungalow
    cost_per_m2   | int   | KES per square metre
    yoy_change_pct| float | Year-on-year percentage change
    source        | str   | Integrum Construction Cost Report [year]
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR  = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "integrum_regional_costs.csv"

# All values confirmed from Integrum annual reports
# Standard Bungalow rate per m2 in KES
# Sources:
#   2021: integrum.co.ke/construction-costs-in-kenya-2021/
#   2022: integrum.co.ke/construction-costs-in-kenya-2022-index-528/
#   2023: integrum.co.ke/construction-costs-in-kenya-2023/
#   2024: integrum.co.ke/construction-costs-in-kenya-2024/
#   2025: integrum.co.ke/2025-construction-costs-in-kenya-322/

RAW_DATA = [
    # year  region                cost_per_m2
    (2021,  "Nairobi/Mt Kenya",   33450),
    (2021,  "Coast",              35410),
    (2021,  "Western/Nyanza",     36300),
    (2022,  "Nairobi/Mt Kenya",   34650),
    (2022,  "Coast",              36250),
    (2022,  "Western/Nyanza",     36850),
    (2023,  "Nairobi/Mt Kenya",   41600),
    (2023,  "Coast",              43250),
    (2023,  "Western/Nyanza",     42000),
    (2024,  "Nairobi/Mt Kenya",   48750),
    (2024,  "Coast",              51800),
    (2024,  "Western/Nyanza",     48750),
    (2025,  "Nairobi/Mt Kenya",   54730),
    # Coast and Western 2025 not yet confirmed in search results
]

def build_dataset():
    records = []

    for year, region, cost in RAW_DATA:
        records.append({
            "year":       year,
            "region":     region,
            "typology":   "Standard Bungalow",
            "cost_per_m2": cost,
            "source":     f"Integrum Construction Cost Report {year}"
        })

    df = pd.DataFrame(records)

    # Calculate year-on-year change per region
    df = df.sort_values(["region", "year"])
    df["yoy_change_pct"] = df.groupby("region")["cost_per_m2"].pct_change() * 100
    df["yoy_change_pct"] = df["yoy_change_pct"].round(2)

    return df

def analyse(df):
    print(f"\n--- Regional cost trend (Standard Bungalow, KES/m2) ---\n")

    for region in df["region"].unique():
        rdf = df[df["region"] == region].sort_values("year")
        print(f"{region}:")
        for _, row in rdf.iterrows():
            yoy = f"+{row['yoy_change_pct']:.1f}%" if pd.notna(row['yoy_change_pct']) else "base"
            print(f"  {int(row['year'])}: KES {int(row['cost_per_m2']):,}/m2  ({yoy})")
        print()

    # Finding 3: Is it cheaper to build outside Nairobi?
    print("--- Finding 3: Regional cost comparison ---\n")
    pivot = df.pivot_table(
        index="year", columns="region", values="cost_per_m2"
    )
    print(pivot.to_string())

    print("\n--- Key insight ---")
    nbi_2021 = df[(df["region"]=="Nairobi/Mt Kenya") & (df["year"]==2021)]["cost_per_m2"].values[0]
    nbi_2024 = df[(df["region"]=="Nairobi/Mt Kenya") & (df["year"]==2024)]["cost_per_m2"].values[0]
    cst_2024 = df[(df["region"]=="Coast") & (df["year"]==2024)]["cost_per_m2"].values[0]
    wst_2024 = df[(df["region"]=="Western/Nyanza") & (df["year"]==2024)]["cost_per_m2"].values[0]

    print(f"Nairobi 2021 to 2024: KES {nbi_2021:,} -> KES {nbi_2024:,} "
          f"(+{((nbi_2024-nbi_2021)/nbi_2021*100):.1f}%)")
    print(f"Coast 2024:           KES {cst_2024:,}/m2 "
          f"({'MORE' if cst_2024 > nbi_2024 else 'LESS'} expensive than Nairobi)")
    print(f"Western/Nyanza 2024:  KES {wst_2024:,}/m2 "
          f"({'MORE' if wst_2024 > nbi_2024 else 'SAME/LESS'} than Nairobi)")

    # For a standard 2BR bungalow (55m2 per CAHF)
    size_m2 = 55
    print(f"\nFor a 55m2 standard bungalow in 2024:")
    for region in ["Nairobi/Mt Kenya", "Coast", "Western/Nyanza"]:
        row = df[(df["region"]==region) & (df["year"]==2024)]
        if not row.empty:
            total = int(row["cost_per_m2"].values[0]) * size_m2
            print(f"  {region}: KES {total:,}")

def main():
    print("NjengaData — Integrum Regional Cost Extractor")
    print("Source: Integrum Construction annual cost reports 2021-2025\n")

    df = build_dataset()
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Rows written: {len(df)}")
    print(f"Output:       {OUTPUT_FILE.resolve()}")

    analyse(df)

if __name__ == "__main__":
    main()
