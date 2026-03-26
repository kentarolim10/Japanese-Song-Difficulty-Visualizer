from typing import Dict, List
from collections import Counter
import re

import fugashi

from app.data.loader import JLPTVocabulary, KanjiGrades


class JapaneseSongAnalyzer:
    def __init__(self):
        self.tagger = fugashi.Tagger()
        self.jlpt_vocab = JLPTVocabulary()
        self.kanji_grades = KanjiGrades()

    def analyze(self, lyrics: str) -> Dict:
        """Perform full analysis on song lyrics."""
        # Clean lyrics (remove metadata like [Verse 1], etc.)
        cleaned_lyrics = self._clean_lyrics(lyrics)

        # Tokenize
        tokens = list(self.tagger(cleaned_lyrics))

        # Run all analyses
        jlpt_counts = self._analyze_jlpt_vocabulary(tokens)
        kanji_stats = self._analyze_kanji(cleaned_lyrics)
        bunsetsu_stats = self._analyze_bunsetsu(cleaned_lyrics)
        lexical_stats = self._analyze_lexical_density(tokens)
        word_freq = self._compute_word_frequencies(tokens)

        return {
            **jlpt_counts,
            **kanji_stats,
            **bunsetsu_stats,
            **lexical_stats,
            "word_frequencies": word_freq,
        }

    def _clean_lyrics(self, lyrics: str) -> str:
        """Remove non-lyric content like [Verse 1], [Chorus], etc."""
        if not lyrics:
            return ""
        # Remove bracketed sections
        cleaned = re.sub(r'\[.*?\]', '', lyrics)
        # Remove multiple newlines
        cleaned = re.sub(r'\n+', '\n', cleaned)
        return cleaned.strip()

    def _get_lemma(self, token) -> str:
        """Get the lemma (dictionary form) of a token."""
        # fugashi with unidic provides lemma via feature
        if hasattr(token, 'feature') and hasattr(token.feature, 'lemma'):
            lemma = token.feature.lemma
            if lemma:
                return lemma
        return token.surface

    def _get_pos(self, token) -> str:
        """Get the part of speech of a token."""
        if hasattr(token, 'feature') and hasattr(token.feature, 'pos1'):
            return token.feature.pos1 or ''
        return ''

    def _is_content_word(self, token) -> bool:
        """Check if token is a content word (not punctuation/whitespace)."""
        pos = self._get_pos(token)
        return pos not in ('記号', '空白', '補助記号', '')

    def _is_bunsetsu_boundary(self, token) -> bool:
        """Check if token marks the end of a bunsetsu."""
        pos = self._get_pos(token)
        # Particles (助詞) and auxiliary verbs (助動詞) typically end bunsetsu
        return pos in ('助詞', '助動詞', '記号', '補助記号')

    def _analyze_jlpt_vocabulary(self, tokens: List) -> Dict[str, int]:
        """Count words by JLPT level using lemma (dictionary form)."""
        counts = {
            "jlpt_n5_count": 0,
            "jlpt_n4_count": 0,
            "jlpt_n3_count": 0,
            "jlpt_n2_count": 0,
            "jlpt_n1_count": 0,
            "jlpt_unknown_count": 0,
        }

        for token in tokens:
            # Skip punctuation and whitespace
            if not self._is_content_word(token):
                continue

            # Get lemma (dictionary form) for lookup
            lemma = self._get_lemma(token)
            level = self.jlpt_vocab.get_level(lemma)

            if level:
                counts[f"jlpt_n{level}_count"] += 1
            else:
                counts["jlpt_unknown_count"] += 1

        return counts

    def _analyze_kanji(self, text: str) -> Dict[str, int]:
        """Analyze kanji usage and complexity."""
        kanji_pattern = re.compile(r'[\u4e00-\u9fff]')
        all_kanji = kanji_pattern.findall(text)
        unique_kanji = set(all_kanji)

        grade_counts = {f"kanji_grade_{i}_count": 0 for i in range(1, 7)}
        grade_counts["kanji_secondary_count"] = 0
        grade_counts["kanji_uncommon_count"] = 0

        for kanji in unique_kanji:
            grade = self.kanji_grades.get_grade(kanji)
            if grade is not None and 1 <= grade <= 6:
                grade_counts[f"kanji_grade_{grade}_count"] += 1
            elif grade == 8:  # Secondary school jouyou
                grade_counts["kanji_secondary_count"] += 1
            else:
                grade_counts["kanji_uncommon_count"] += 1

        return {
            "total_kanji_count": len(all_kanji),
            "unique_kanji_count": len(unique_kanji),
            **grade_counts,
        }

    def _analyze_bunsetsu(self, text: str) -> Dict[str, any]:
        """Analyze bunsetsu (phrase) statistics.

        Bunsetsu boundaries occur after particles and auxiliary verbs.
        This is a simplified heuristic approach.
        """
        lines = text.split('\n')
        bunsetsu_lengths = []

        for line in lines:
            if not line.strip():
                continue

            tokens = list(self.tagger(line))
            current_bunsetsu_len = 0

            for token in tokens:
                current_bunsetsu_len += len(token.surface)

                # Check if this token ends a bunsetsu
                if self._is_bunsetsu_boundary(token):
                    if current_bunsetsu_len > 0:
                        bunsetsu_lengths.append(current_bunsetsu_len)
                        current_bunsetsu_len = 0

            # Don't forget the last bunsetsu in the line
            if current_bunsetsu_len > 0:
                bunsetsu_lengths.append(current_bunsetsu_len)

        if not bunsetsu_lengths:
            return {
                "total_bunsetsu_count": 0,
                "avg_bunsetsu_length": 0.0,
                "max_bunsetsu_length": 0,
                "min_bunsetsu_length": 0,
            }

        return {
            "total_bunsetsu_count": len(bunsetsu_lengths),
            "avg_bunsetsu_length": sum(bunsetsu_lengths) / len(bunsetsu_lengths),
            "max_bunsetsu_length": max(bunsetsu_lengths),
            "min_bunsetsu_length": min(bunsetsu_lengths),
        }

    def _analyze_lexical_density(self, tokens: List) -> Dict[str, any]:
        """Calculate lexical density (unique words / total words)."""
        content_words = [
            self._get_lemma(token)
            for token in tokens
            if self._is_content_word(token)
        ]

        total = len(content_words)
        unique = len(set(content_words))

        return {
            "total_words": total,
            "unique_words": unique,
            "lexical_density": unique / total if total > 0 else 0.0,
        }

    def _compute_word_frequencies(self, tokens: List, top_n: int = 50) -> Dict[str, int]:
        """Get word frequency distribution for top N words."""
        word_counts = Counter()

        for token in tokens:
            if self._is_content_word(token):
                lemma = self._get_lemma(token)
                word_counts[lemma] += 1

        return dict(word_counts.most_common(top_n))
