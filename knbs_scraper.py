"""
KNBS Construction Input Price Index — PDF Downloader
NjengaData | dev-real-data branch

Downloads all confirmed CIPI quarterly PDFs from knbs.or.ke.
URLs are hardcoded — KNBS naming is inconsistent across quarters,
so a pattern-based approach would miss files.

Output: data/raw/knbs/*.pdf
"""

import requests
import urllib3
import time
import os
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://www.knbs.or.ke/wp-content/uploads"

PDFS = {
    "2021_Q1": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-First-Quarter-2021.pdf",
    "2021_Q2": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-Second-Quarter-2021.pdf",
    "2021_Q3": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-Third-Quarter-2021.pdf",
    "2021_Q4": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-Fourth-Quarter-2021.pdf",
    "2022_Q1": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-First-Quarter-2022.pdf",
    "2022_Q2": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-Second-Quarter-2022.pdf",
    "2022_Q3": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-Third-Quarter-2022.pdf",
    "2022_Q4": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-Fourth-Quarter-2022.pdf",
    "2023_Q1": f"{BASE}/2023/08/Kenya-Construction-Input-Price-Index-First-Quarter-2023.pdf",
    "2023_Q2": f"{BASE}/2023/07/Construction-Input-Price-Indices-for-Second-Quarter-2023.pdf",
    "2023_Q3": f"{BASE}/2023/10/Construction-Input-Price-Indices-for-Third-Quarter-2023.pdf",
    "2023_Q4": f"{BASE}/2024/01/Construction-Input-Price-Indices-for-F-ourth-Quarter-2023.pdf",
    "2024_Q1": f"{BASE}/2024/03/Construction-Input-Price-Indices-First-Quarter-2024.pdf",
    "2024_Q2": f"{BASE}/2024/07/Construction-Input-Price-Indices-Second-Quarter-2024.pdf",
    "2024_Q3": f"{BASE}/2024/10/Construction-Input-Price-Indices-for-Third-Quarter-2024.pdf",
    "2024_Q4": f"{BASE}/2025/01/Construction-Input-Price-Indices-for-Fourth-Quarter-2024.pdf",
    "2025_Q1": f"{BASE}/2025/04/Construction-Input-Price-Indices-First-Quarter-2025.pdf",
    "2025_Q2": f"{BASE}/2025/07/Construction-Input-Price-Indices-Second-Quarter-2025.pdf",
    "2025_Q3": f"{BASE}/2025/10/Construction-Input-Price-Indices-for-Third-Quarter-2025.pdf",
    "2025_Q4": f"{BASE}/2026/02/Construction-Input-Price-Indices-Fourth-Quarter-2025.pdf",
}

OUTPUT_DIR = Path("data/raw/knbs")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; NjengaData/1.0; research use)"
}

def download_all():
    results = {"success": [], "failed": []}

    for key, url in PDFS.items():
        filename = OUTPUT_DIR / f"KNBS_CIPI_{key}.pdf"

        if filename.exists():
            print(f"  SKIP  {key} — already downloaded")
            results["success"].append(key)
            continue

        try:
            print(f"  GET   {key} ...", end=" ", flush=True)
            r = requests.get(url, headers=HEADERS, timeout=30, verify=False)

            if r.status_code == 200 and r.headers.get("content-type", "").startswith("application/pdf"):
                filename.write_bytes(r.content)
                size_kb = len(r.content) // 1024
                print(f"OK ({size_kb} KB)")
                results["success"].append(key)
            else:
                print(f"FAIL — HTTP {r.status_code}")
                results["failed"].append((key, r.status_code))

        except Exception as e:
            print(f"ERROR — {e}")
            results["failed"].append((key, str(e)))

        time.sleep(1)

    print(f"\n--- Summary ---")
    print(f"Downloaded: {len(results['success'])} / {len(PDFS)}")
    if results["failed"]:
        print(f"Failed:     {len(results['failed'])}")
        for key, reason in results["failed"]:
            print(f"  {key}: {reason}")

    return results

if __name__ == "__main__":
    print("NjengaData — KNBS CIPI Downloader")
    print(f"Target: {len(PDFS)} quarterly reports")
    print(f"Output: {OUTPUT_DIR.resolve()}\n")
    download_all()
