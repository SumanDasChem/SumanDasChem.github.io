import json
import os
import requests
from collections import OrderedDict

# ==========================
# Configuration
# ==========================

ORCID = "0000-0002-4861-6942"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "GitHub-Publication-Updater"
}

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_FILE = os.path.join(DATA_DIR, "publications.json")

# ==========================
# Download ORCID Works
# ==========================

works_url = f"https://pub.orcid.org/v3.0/{ORCID}/works"

response = requests.get(works_url, headers=HEADERS)
response.raise_for_status()

works = response.json().get("group", [])

publications = []

print(f"Found {len(works)} ORCID records")

# ==========================
# Download each publication
# ==========================

for work in works:

    summary = work["work-summary"][0]
    put_code = summary["put-code"]

    detail_url = f"https://pub.orcid.org/v3.0/{ORCID}/work/{put_code}"

    detail = requests.get(detail_url, headers=HEADERS)
    detail.raise_for_status()

    detail = detail.json()

    # ----------------------
    # Title
    # ----------------------

    title = ""

    if detail.get("title"):
        title = detail["title"]["title"]["value"].strip()

    if title == "":
        continue

    # ----------------------
    # Journal
    # ----------------------

    journal = ""

    if detail.get("journal-title"):
        journal = detail["journal-title"]["value"].strip()

    # ----------------------
    # Year
    # ----------------------

    year = 0

    if detail.get("publication-date"):

        pub_date = detail["publication-date"]

        if pub_date.get("year"):

            try:
                year = int(pub_date["year"]["value"])
            except:
                year = 0

    # ----------------------
    # DOI
    # ----------------------

    doi = ""

    ids = detail.get("external-ids", {}).get("external-id", [])

    for item in ids:

        if item["external-id-type"].lower() == "doi":

            doi = "https://doi.org/" + item["external-id-value"]

            break

    publications.append({

        "year": year,
        "journal": journal,
        "title": title,
        "doi": doi

    })

# ==========================
# Remove duplicate titles
# ==========================

unique = OrderedDict()

for pub in publications:

    unique[pub["title"]] = pub

publications = list(unique.values())

# ==========================
# Sort
# ==========================

publications.sort(

    key=lambda x: (

        x["year"],
        x["journal"],
        x["title"]

    ),

    reverse=True

)

# ==========================
# Save JSON
# ==========================

os.makedirs(DATA_DIR, exist_ok=True)

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:

    json.dump(

        publications,
        f,
        indent=4,
        ensure_ascii=False

    )

print("----------------------------------")
print(f"Saved {len(publications)} publications")
print(f"Output : {OUTPUT_FILE}")
print("----------------------------------")
