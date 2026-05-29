import anthropic 
import instructor

from schemas.asset_profile import AssetProfile

# If extraction failed after retries. Return None and 
# let the piplined decide what to do.


client = instructor.from_anthropic(anthropic.Anthropic())


SYSTEM_PROMPT = """
You are a senior real estate analyst specializing in German commercial property markets,
with deep knowledge of Baden-Württemberg's investment landscape.

Your job is to read raw property documents — listings, insolvency notices, zoning filings,
corporate registry entries — and extract structured acquisition intelligence.

SAX-Gruppe's investment criteria you must apply:
- Target transaction volume: above €20 million
- Focus regions: Baden-Württemberg, growth markets across Germany
- Asset classes: retail, office, hotel, logistics, residential, mixed-use, Denkmal
- High interest in conversion plays: micro-apartments, boutique hotels, assisted living
- Actively seeks distressed assets and off-market opportunities

Be precise. If a value is not clearly stated or reasonably inferable, return null.
Do not hallucinate figures. A null field is always better than a guess.
"""

def extract_profile(filename: str, raw_text: str) -> AssetProfile | None:
    """
    Send a raw document through the LLM and return a validated AssetProfile.
    Returns None if extraction fails after Instructor's internal retries.
    """

    try:
        profile = client.chat.completions.create(
            model="claude-opus-4-5",
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": f"Extract acquisition intelligence from the following document:\n\n{raw_text}"
                }
            ],
            system= SYSTEM_PROMPT,
            response_model=AssetProfile,
        )

        # These two fields aren't extracted by the LLM — we set them here.
        profile.source_file = filename
        profile.raw_source_text = raw_text

        return profile

    except Exception as e:
        print(f"[extractor] Failed on {filename}: {e}")
        return None