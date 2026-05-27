import os
from pathlib import Path

# Supported file types in the corpus folder.
# We keep this small on purpose — txt for manually copied notices,
# md if someone drafts a mock doc, pdf support comes later via pdfplumber.
SUPPORTED_EXTENSIONS = {".txt", ".md"}

CORPUS_DIR = Path(__file__).resolve().parents[1] / "corpus"


def load_documents(corpus_dir: Path = CORPUS_DIR) -> list[tuple[str, str]]:
    """
    Walk the corpus directory recursively and return all readable documents
    as a list of (filename, raw_text) tuples.

    Skips files it can't read rather than crashing the whole pipeline.
    """
    documents = []

    for filepath in sorted(corpus_dir.rglob("*")):
        if filepath.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        try:
            text = filepath.read_text(encoding="utf-8").strip()
            if not text:
                print(f"[loader] Skipping empty file: {filepath.name}")
                continue

            documents.append((filepath.name, text))
            print(f"[loader] Loaded: {filepath.name}")

        except Exception as e:
            print(f"[loader] Could not read {filepath.name}: {e}")

    print(f"\n[loader] {len(documents)} documents ready for extraction\n")
    return documents