"""
download_data.py
-----------------
Downloads the real "Give Me Some Credit" dataset (Kaggle, 2011 credit
scoring competition) — ~150,000 real, anonymized consumer credit
records with a genuine default label (SeriousDlqin2yrs).

The raw file isn't committed to this repo (7+ MB, and best practice
for Kaggle-sourced data), so this script fetches it from a public
GitHub mirror on first run and caches it in data/raw/.

Original source / competition page:
    https://www.kaggle.com/c/GiveMeSomeCredit/data
Mirror used here (raw file committed to a public GitHub repo):
    https://github.com/JLZml/Credit-Scoring-Data-Sets

Run:
    python data/download_data.py
"""

import urllib.request
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parent / "raw"
RAW_DIR.mkdir(exist_ok=True)
OUT_PATH = RAW_DIR / "cs-training.csv"

MIRROR_URL = (
    "https://raw.githubusercontent.com/JLZml/Credit-Scoring-Data-Sets/"
    "master/3.%20Kaggle/Give%20Me%20Some%20Credit/cs-training.csv"
)

def main():
    if OUT_PATH.exists():
        print(f"Already downloaded: {OUT_PATH}")
        return
    print(f"Downloading from {MIRROR_URL} ...")
    urllib.request.urlretrieve(MIRROR_URL, OUT_PATH)
    print(f"Saved to {OUT_PATH} ({OUT_PATH.stat().st_size / 1e6:.1f} MB)")

if __name__ == "__main__":
    main()
