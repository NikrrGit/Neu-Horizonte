import sys
from pathlib import Path

# Make sure the project root is on the path so imports work
# when this script is run directly from the terminal.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pipeline.loader import load_documents
from pipeline.extractor import extract_profile
from pipeline.scorer import score_profile
from pipeline.storage import init_db, upsert_profile


def run():
    print("=" * 50)
    print("SAX Sourcing Engine — Pipeline Run")
    print("=" * 50)

    # Boot the database — creates the table if this is the first run
    init_db()

    # Load every document from the corpus folder
    documents = load_documents()
    if not documents:
        print("[pipeline] No documents found in corpus/. Add some .txt files and try again.")
        return

    succeeded = 0
    failed = 0

    for filename, raw_text in documents:
        print(f"[pipeline] Processing: {filename}")

        # Extract structured profile from raw text via LLM
        profile = extract_profile(filename, raw_text)
        if profile is None:
            print(f"[pipeline] Extraction failed — skipping {filename}\n")
            failed += 1
            continue

        # Score the profile against SAX's investment criteria
        profile = score_profile(profile)

        # Persist to DuckDB — safe to re-run, will overwrite existing record
        upsert_profile(profile)

        print(f"[pipeline] ✓ {filename} — fit score: {profile.sax_fit_score} | {profile.location_city} | {profile.asset_class.value}\n")
        succeeded += 1

    print("=" * 50)
    print(f"[pipeline] Done. {succeeded} extracted, {failed} failed.")
    print("=" * 50)


if __name__ == "__main__":
    run()