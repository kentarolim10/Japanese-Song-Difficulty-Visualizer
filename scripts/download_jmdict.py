"""
Download and process JMdict (Japanese-English Dictionary) for vocab lookups.
Extracts word, reading (hiragana), and English definition.
"""
import gzip
import json
import urllib.request
import re
from pathlib import Path

JMDICT_URL = "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"
OUTPUT_DIR = Path(__file__).parent.parent / "app" / "data" / "jmdict"


def download_jmdict():
    """Download JMdict XML file."""
    print("Downloading JMdict (this may take a minute)...")
    gz_path = OUTPUT_DIR / "JMdict_e.gz"
    urllib.request.urlretrieve(JMDICT_URL, gz_path)
    print(f"Downloaded to {gz_path}")
    return gz_path


def parse_jmdict(gz_path: Path) -> dict:
    """Parse JMdict XML using regex (simpler than XML parsing for this format)."""
    print("Parsing JMdict...")
    words = {}

    with gzip.open(gz_path, 'rt', encoding='utf-8') as f:
        content = f.read()

    # Find all entries using regex
    entry_pattern = re.compile(r'<entry>(.*?)</entry>', re.DOTALL)
    keb_pattern = re.compile(r'<keb>([^<]+)</keb>')
    reb_pattern = re.compile(r'<reb>([^<]+)</reb>')
    gloss_pattern = re.compile(r'<gloss>([^<]+)</gloss>')

    entries = entry_pattern.findall(content)
    print(f"Found {len(entries)} entries")

    for i, entry in enumerate(entries):
        # Get kanji forms
        kanji_forms = keb_pattern.findall(entry)

        # Get reading forms
        readings = reb_pattern.findall(entry)

        if not readings:
            continue

        primary_reading = readings[0]

        # Get English definitions
        definitions = gloss_pattern.findall(entry)

        if not definitions:
            continue

        # Combine first few definitions
        definition = "; ".join(definitions[:3])

        # Add entry for each kanji form
        for kanji in kanji_forms:
            if kanji not in words:
                words[kanji] = {
                    "reading": primary_reading,
                    "definition": definition
                }

        # Also add entry for reading (for words without kanji, like hiragana-only words)
        for reading in readings:
            if reading not in words:
                words[reading] = {
                    "reading": reading,
                    "definition": definition
                }

        if (i + 1) % 50000 == 0:
            print(f"  Processed {i + 1} entries...")

    print(f"Extracted {len(words)} unique word entries")
    return words


def save_words(words: dict):
    """Save words to JSON file."""
    output_path = OUTPUT_DIR / "words.json"

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False)

    print(f"Saved to {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gz_path = OUTPUT_DIR / "JMdict_e.gz"
    if not gz_path.exists():
        gz_path = download_jmdict()

    words = parse_jmdict(gz_path)
    save_words(words)

    # Clean up gz file
    gz_path.unlink()
    print("Done!")


if __name__ == "__main__":
    main()
