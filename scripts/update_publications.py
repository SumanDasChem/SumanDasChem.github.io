import json
import requests
import os

ORCID = "0000-0002-4861-6942"

headers = {
    "Accept": "application/json"
}

works_url = f"https://pub.orcid.org/v3.0/{ORCID}/works"

response = requests.get(works_url, headers=headers)
response.raise_for_status()

works = response.json()["group"]

publications = []

for work in works:

    summary = work["work-summary"][0]

    put_code = summary["put-code"]

    detail_url = f"https://pub.orcid.org/v3.0/{ORCID}/work/{put_code}"

    detail = requests.get(detail_url, headers=headers).json()

    title = ""

    if detail.get("title"):
        title = detail["title"]["title"]["value"]

    journal = ""

    if detail.get("journal-title"):
        journal = detail["journal-title"]["value"]

    year = ""

    if detail.get("publication-date"):
        if detail["publication-date"].get("year"):
            year = detail["publication-date"]["year"]["value"]

    doi = ""

    for ext in detail.get("external-ids", {}).get("external-id", []):

        if ext["external-id-type"].lower() == "doi":

            doi = "https://doi.org/" + ext["external-id-value"]

            break

    publications.append({

        "year": int(year) if year else 0,

        "journal": journal,

        "title": title,

        "doi": doi

    })

publications.sort(

    key=lambda x: (x["year"], x["journal"]),

    reverse=True

)

os.makedirs("../data", exist_ok=True)

with open("../data/publications.json", "w", encoding="utf-8") as f:

    json.dump(publications, f, indent=4, ensure_ascii=False)

print(f"{len(publications)} publications written.")
