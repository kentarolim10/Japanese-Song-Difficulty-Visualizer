"""
Download and process JMnedict (Japanese Names Dictionary) into a simple JSON lookup.
"""
import gzip
import json
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

JMNEDICT_URL = "http://ftp.edrdg.org/pub/Nihongo/JMnedict.xml.gz"
OUTPUT_DIR = Path(__file__).parent.parent / "app" / "data" / "jmnedict"


def download_jmnedict():
    """Download JMnedict XML file."""
    print("Downloading JMnedict (this may take a minute)...")
    gz_path = OUTPUT_DIR / "JMnedict.xml.gz"
    urllib.request.urlretrieve(JMNEDICT_URL, gz_path)
    print(f"Downloaded to {gz_path}")
    return gz_path


def parse_jmnedict(gz_path: Path) -> set:
    """Parse JMnedict XML and extract all name entries."""
    print("Parsing JMnedict XML...")
    names = set()

    with gzip.open(gz_path, 'rt', encoding='utf-8') as f:
        # Parse incrementally to handle large file
        context = ET.iterparse(f, events=('end',))

        for event, elem in context:
            if elem.tag == 'entry':
                # Get all readings (keb = kanji, reb = reading)
                for keb in elem.findall('.//keb'):
                    if keb.text:
                        names.add(keb.text)
                for reb in elem.findall('.//reb'):
                    if reb.text:
                        names.add(reb.text)
                # Clear element to save memory
                elem.clear()

    print(f"Found {len(names)} unique name entries")
    return names


def save_names(names: set):
    """Save names to JSON file."""
    output_path = OUTPUT_DIR / "names.json"

    # Save as a list (will be loaded as a set)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(sorted(list(names)), f, ensure_ascii=False)

    print(f"Saved to {output_path}")
    print(f"File size: {output_path.stat().st_size / 1024 / 1024:.1f} MB")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    gz_path = download_jmnedict()
    names = parse_jmnedict(gz_path)
    save_names(names)

    # Clean up gz file
    gz_path.unlink()
    print("Done!")


if __name__ == "__main__":
    main()
