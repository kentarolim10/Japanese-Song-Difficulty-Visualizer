import json
from pathlib import Path
from typing import Optional, Dict

DATA_DIR = Path(__file__).parent


class JLPTVocabulary:
    """Singleton loader for JLPT vocabulary data."""
    _instance = None
    _vocab: Dict[str, int] = {}  # word -> level (5, 4, 3, 2, 1)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Load JLPT vocabulary file."""
        file_path = DATA_DIR / "jlpt" / "jlpt_words.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Format is {"word": "N1/N2/N3/N4/N5", ...}
                for word, level_str in data.items():
                    # Extract level number from "N1", "N2", etc.
                    level = int(level_str[1])
                    self._vocab[word] = level

    def get_level(self, word: str) -> Optional[int]:
        """Get JLPT level for a word (5=easiest, 1=hardest)."""
        return self._vocab.get(word)


class KanjiGrades:
    """Singleton loader for kanji grade data."""
    _instance = None
    _grades: Dict[str, int] = {}  # kanji -> grade (1-6 kyouiku, 8 = secondary jouyou)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Load kanji grade data."""
        file_path = DATA_DIR / "kanji" / "kanji_jouyou.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Format is {"kanji": {"grade": N, ...}, ...}
                for kanji, info in data.items():
                    grade = info.get("grade")
                    if grade is not None:
                        self._grades[kanji] = grade

    def get_grade(self, kanji: str) -> Optional[int]:
        """Get grade level for a kanji (1-6 = elementary, 8 = secondary)."""
        return self._grades.get(kanji)


class JMnedict:
    """Singleton loader for JMnedict (Japanese proper nouns)."""
    _instance = None
    _names: set = set()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_data()
        return cls._instance

    def _load_data(self):
        """Load JMnedict names data."""
        file_path = DATA_DIR / "jmnedict" / "names.json"
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._names = set(data)

    def is_name(self, word: str) -> bool:
        """Check if a word is in JMnedict."""
        return word in self._names
