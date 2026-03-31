"""
Normalize JLPT levels so that when both kanji and hiragana forms exist,
they use the lower (easier) level.

"""
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).parent.parent / "app" / "data"


def load_jlpt():
    """Load current JLPT data."""
    path = DATA_DIR / "jlpt" / "jlpt_words.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_jmdict():
    """Load JMdict for reading lookups."""
    path = DATA_DIR / "jmdict" / "words.json"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_level_number(level_str: str) -> int:
    """Convert 'N1' to 1, 'N5' to 5, etc."""
    return int(level_str[1])


def normalize_levels(jlpt: dict, jmdict: dict) -> dict:
    """Normalize levels so words with same reading use the easier level."""

    # Group words by their reading
    reading_to_words = defaultdict(list)

    for word, level in jlpt.items():
        # Get reading from JMdict
        info = jmdict.get(word)
        if info and info.get("reading"):
            reading = info["reading"]
        else:
            # If no JMdict entry, use the word itself as reading
            reading = word

        reading_to_words[reading].append((word, level))

    # Find groups with multiple levels and normalize
    normalized = {}
    changes = []

    for reading, words in reading_to_words.items():
        if len(words) == 1:
            # Single word, no normalization needed
            word, level = words[0]
            normalized[word] = level
        else:
            # Multiple words with same reading - use lowest level (highest number)
            levels = [get_level_number(level) for _, level in words]
            easiest_level = max(levels)  # N5=5 is easier than N1=1
            easiest_level_str = f"N{easiest_level}"

            for word, original_level in words:
                if original_level != easiest_level_str:
                    changes.append((word, original_level, easiest_level_str, reading))
                normalized[word] = easiest_level_str

    return normalized, changes


def save_jlpt(data: dict):
    """Save normalized JLPT data."""
    path = DATA_DIR / "jlpt" / "jlpt_words.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Saved to {path}")


def main():
    print("Loading JLPT data...")
    jlpt = load_jlpt()
    print(f"Loaded {len(jlpt)} words")

    print("Loading JMdict...")
    jmdict = load_jmdict()
    print(f"Loaded {len(jmdict)} entries")

    print("Normalizing levels...")
    normalized, changes = normalize_levels(jlpt, jmdict)

    print(f"\nFound {len(changes)} words to normalize:")
    for word, old, new, reading in changes[:20]:
        print(f"  {word} ({reading}): {old} -> {new}")
    if len(changes) > 20:
        print(f"  ... and {len(changes) - 20} more")

    save_jlpt(normalized)
    print("Done!")


if __name__ == "__main__":
    main()