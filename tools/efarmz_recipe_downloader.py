import argparse
import os
import time
import sys
from pathlib import Path
from typing import Iterable
import string

import requests

BASE_URL = "https://cdn.efarmz.be/recipes/FR/{letter}{num:03}.pdf"
OUTPUT_DIR_TEMPLATE = "output/efarmz_recipes_{letter}"


DEFAULT_API_BASE_URL = "http://localhost:8000"


def iter_pdf_files(root: Path, recursive: bool) -> Iterable[Path]:
    """Yield all .pdf files under `root`."""
    if recursive:
        yield from root.rglob("*.pdf")
    else:
        yield from root.glob("*.pdf")


def import_pdf(api_base_url: str, pdf_path: Path, timeout: int = 60) -> dict:
    """Call the /pdf/import endpoint for a single PDF and return parsed JSON."""
    url = api_base_url.rstrip("/") + "/pdf/import"

    with pdf_path.open("rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        resp = requests.post(url, files=files, timeout=timeout)

    # Raise for HTTP errors, caller will handle
    resp.raise_for_status()
    return resp.json()

def download_efarmz_recipes(start=1, end=999):
    # letters = string.ascii_lowercase
    letters = ['p', 'l']
    for letter in letters:
        output_dir = OUTPUT_DIR_TEMPLATE.format(letter=letter)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Processing letter {letter}...")

        for num in range(start, end + 1):
            url = BASE_URL.format(letter=letter, num=num)
            print(f"Checking {url} ...")

            filename = os.path.join(output_dir, f"{letter}{num:03}.pdf")

            if os.path.exists(filename):
                print("File exists. Skipping.")
                continue

            try:
                # Don't follow redirects so we can see 302 status codes
                response = requests.get(url, allow_redirects=False)
            except requests.RequestException as e:
                print(f"Request failed for {url}: {e}")
                continue

            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"Saved {filename}")
            elif response.status_code == 302:
                print(f"Got 302 (Not Found) at {letter}{num:03}. Skipping.")
                continue
            else:
                print(f"Got unexpected status {response.status_code} at {letter}{num:03}. Stopping letter {letter}.")
                continue

            time.sleep(1)


if __name__ == "__main__":
    download_efarmz_recipes(start=1, end=999)

