from typing import Dict, List
from collections import Counter
import re

import fugashi

from app.data.loader import JLPTVocabulary, KanjiGrades, JMnedict


class JapaneseSongAnalyzer:
    def __init__(self):
        self.tagger = fugashi.Tagger()
        self.jlpt_vocab = JLPTVocabulary()
        self.kanji_grades = KanjiGrades()
        self.jmnedict = JMnedict()

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

        # Detect special word categories
        onomatopoeia = self._detect_onomatopoeia(tokens)
        proper_nouns = self._detect_proper_nouns(tokens)
        archaic_words = self._detect_archaic_words(tokens)

        return {
            **jlpt_counts,
            **kanji_stats,
            **bunsetsu_stats,
            **lexical_stats,
            "word_frequencies": word_freq,
            "onomatopoeia": onomatopoeia,
            "proper_nouns": proper_nouns,
            "archaic_words": archaic_words,
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

    def _is_abab_pattern(self, text: str) -> bool:
        """Check if text follows ABAB repetition pattern (e.g., ドキドキ, キラキラ)."""
        if len(text) < 4 or len(text) % 2 != 0:
            return False
        half = len(text) // 2
        return text[:half] == text[half:]

    def _is_abcb_pattern(self, text: str) -> bool:
        """Check if text follows ABCB pattern (e.g., ドタバタ, ガサゴソ)."""
        if len(text) != 4:
            return False
        # 2nd and 4th characters match (positions 1 and 3)
        return text[1] == text[3]

    def _is_onomatopoeia_pattern(self, text: str) -> bool:
        """Check if text matches common onomatopoeia patterns."""
        if len(text) < 2:
            return False
        # ABAB: ドキドキ, キラキラ
        if self._is_abab_pattern(text):
            return True
        # ABCB: ドタバタ, ガチャガチャ... wait that's ABAB
        # ABCB for 4 chars: ドタバタ (do-ta-ba-ta)
        if self._is_abcb_pattern(text):
            return True
        # っ or ん endings for short words (minimum 3 chars to avoid false positives like やっ)
        if 3 <= len(text) <= 4 and (text.endswith('っ') or text.endswith('ん')):
            return True
        # ーり endings (ゆっくり, のんびり pattern)
        if text.endswith('り') and len(text) >= 3:
            return True
        return False

    def _detect_onomatopoeia(self, tokens: List) -> List[str]:
        """Detect onomatopoeia (擬音語/擬態語) in text."""
        found = set()

        # Common onomatopoeia that may not match patterns
        common_onomatopoeia = {
            # Sound effects (擬音語)
            'ドキドキ', 'バタバタ', 'ガタガタ', 'カタカタ', 'ゴロゴロ',
            'ザーザー', 'シトシト', 'パラパラ', 'ポツポツ', 'ドシドシ',
            'バンバン', 'ドンドン', 'カンカン', 'チリンチリン', 'リンリン',
            'ワンワン', 'ニャーニャー', 'ブーブー', 'モーモー', 'ケロケロ',
            'ガチャガチャ', 'ジャラジャラ', 'カチャカチャ', 'ガシャガシャ',
            # State/manner (擬態語)
            'キラキラ', 'ピカピカ', 'ツヤツヤ', 'テカテカ', 'ギラギラ',
            'フワフワ', 'モフモフ', 'サラサラ', 'ツルツル', 'ベタベタ',
            'ドロドロ', 'ネバネバ', 'トロトロ', 'グチャグチャ', 'ボロボロ',
            'イライラ', 'ムカムカ', 'ワクワク', 'ソワソワ', 'ドキドキ',
            'ニコニコ', 'ニヤニヤ', 'ヘラヘラ', 'シクシク', 'メソメソ',
            # ABCB patterns
            'ドタバタ', 'ガサゴソ', 'ゴチャゴチャ', 'バタバタ', 'ガタピシ',
            # Other common ones
            'ゆっくり', 'のんびり', 'びっくり', 'すっきり', 'がっかり',
            'ぐっすり', 'こっそり', 'ばっちり', 'しっかり', 'ぴったり',
            'じっと', 'そっと', 'ふと', 'きっと', 'ずっと', 'もっと',
            'ぼんやり', 'うっかり', 'はっきり', 'ぼんやり', 'ちゃんと',
        }

        for token in tokens:
            surface = token.surface
            pos = self._get_pos(token)

            # Skip verbs - they can have っ endings from conjugation (e.g., わかっ from わかる)
            if pos == '動詞':
                continue

            # Check against common onomatopoeia list
            if surface in common_onomatopoeia:
                found.add(surface)
                continue

            # Check POS tags commonly associated with onomatopoeia
            # Only apply pattern matching for these specific POS tags
            if pos in ('副詞', '感動詞'):
                if self._is_onomatopoeia_pattern(surface):
                    found.add(surface)
                continue

            # For katakana words with ABAB/ABCB patterns (not っ/ん endings which could be loanword verbs)
            if self._is_katakana(surface) and (self._is_abab_pattern(surface) or self._is_abcb_pattern(surface)):
                found.add(surface)

        return sorted(list(found))

    def _is_katakana(self, text: str) -> bool:
        """Check if text is primarily katakana."""
        if not text:
            return False
        katakana_count = sum(1 for c in text if '\u30a0' <= c <= '\u30ff')
        return katakana_count >= len(text) * 0.8

    def _is_hiragana(self, text: str) -> bool:
        """Check if text is primarily hiragana."""
        if not text:
            return False
        hiragana_count = sum(1 for c in text if '\u3040' <= c <= '\u309f')
        return hiragana_count >= len(text) * 0.8

    def _detect_proper_nouns(self, tokens: List) -> List[str]:
        """Detect proper nouns (names, places, organizations)."""
        found = set()

        for token in tokens:
            surface = token.surface

            # For katakana words: check JMnedict (foreign names are usually katakana)
            # This avoids false positives from kanji/hiragana words that are also names
            if self._is_katakana(surface) and len(surface) >= 3:
                if self.jmnedict.is_name(surface):
                    found.add(surface)
                    continue

            # For non-katakana words: rely on MeCab's contextual POS tagging only
            # (JMnedict would give false positives like 納屋, まなこ)
            if hasattr(token, 'feature'):
                feature = token.feature
                pos1 = getattr(feature, 'pos1', '') or ''
                pos2 = getattr(feature, 'pos2', '') or ''

                if pos1 == '名詞' and pos2 == '固有名詞':
                    found.add(surface)
                # Also check for proper noun subcategories
                pos3 = getattr(feature, 'pos3', '') or ''
                if pos3 in ('人名', '地名', '組織'):
                    found.add(surface)

        return sorted(list(found))

    def _detect_archaic_words(self, tokens: List) -> List[str]:
        """Detect archaic/literary Japanese words and expressions."""
        found = set()

        # Common archaic/literary words and particles
        archaic_patterns = {
            'ぞ', 'かな', 'けり', 'なり', 'たり', 'ぬ', 'む', 'らむ',
            'べし', 'まじ', 'じ', 'めり', 'なむ', 'てむ', 'き', 'けむ',
            '汝', 'われ', '我', '己', 'おのれ', '御身', 'なんぢ',
            'されど', 'しかれども', 'しかして', 'さりながら',
            'いにしへ', 'いにしえ', 'むかし', 'ゆゑ', 'ゆえ',
            'あはれ', 'をかし', 'いとど', 'いと', 'げに',
        }

        for token in tokens:
            surface = token.surface
            lemma = self._get_lemma(token)

            # Check if surface or lemma matches archaic patterns
            if surface in archaic_patterns or lemma in archaic_patterns:
                found.add(surface)

            # Check for classical conjugation types in feature
            if hasattr(token, 'feature'):
                feature = token.feature
                # Some morphological analyzers mark classical forms
                ctype = getattr(feature, 'cType', '') or ''
                cform = getattr(feature, 'cForm', '') or ''

                # Classical conjugation indicators
                if '文語' in ctype or '古典' in ctype:
                    found.add(surface)
                if '文語' in cform or '已然形' in cform or '連体形-古典' in cform:
                    found.add(surface)

        return sorted(list(found))
