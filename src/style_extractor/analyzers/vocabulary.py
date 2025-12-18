"""Vocabulary analysis module."""

import re
from collections import Counter
from typing import Optional

from ..models import VocabularyProfile


class VocabularyAnalyzer:
    """Analyzes vocabulary patterns and word choices."""

    # Common words to exclude from signature analysis (French + English stopwords)
    STOPWORDS = {
        # English
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
        "be", "have", "has", "had", "do", "does", "did", "will", "would",
        "could", "should", "may", "might", "must", "shall", "can", "need",
        "it", "its", "this", "that", "these", "those", "i", "you", "he",
        "she", "we", "they", "me", "him", "her", "us", "them", "my", "your",
        "his", "our", "their", "what", "which", "who", "whom", "when",
        "where", "why", "how", "all", "each", "every", "both", "few", "more",
        "most", "other", "some", "such", "no", "not", "only", "same", "so",
        "than", "too", "very", "just", "also", "now", "here", "there", "then",
        # French
        "le", "la", "les", "un", "une", "des", "du", "de", "et", "ou", "mais",
        "donc", "car", "ni", "que", "qui", "quoi", "dont", "où", "ce", "cet",
        "cette", "ces", "mon", "ton", "son", "ma", "ta", "sa", "mes", "tes",
        "ses", "notre", "votre", "leur", "nos", "vos", "leurs", "je", "tu",
        "il", "elle", "on", "nous", "vous", "ils", "elles", "me", "te", "se",
        "lui", "y", "en", "dans", "sur", "sous", "avec", "sans", "pour",
        "par", "entre", "vers", "chez", "être", "avoir", "faire", "dire",
        "aller", "voir", "savoir", "pouvoir", "falloir", "vouloir", "venir",
        "est", "sont", "était", "été", "ai", "as", "avait", "ont", "fait",
        "dit", "va", "vais", "peut", "veut", "faut", "pas", "plus", "moins",
        "très", "bien", "tout", "tous", "toute", "toutes", "même", "autre",
        "autres", "si", "ne", "ni", "peu", "comme", "alors", "aussi", "quand",
    }

    # POS patterns for French/English (simplified)
    ADJECTIVE_SUFFIXES = [
        "eux", "euse", "euses", "if", "ive", "ives", "al", "ale", "aux",
        "el", "elle", "elles", "ique", "iques", "able", "ables", "ible",
        "ibles", "ant", "ante", "ants", "antes", "ent", "ente", "ents",
        "ly", "ful", "less", "ous", "ive", "able", "ible", "al", "ial",
    ]

    ADVERB_SUFFIXES = ["ment", "ly", "ement", "amment", "emment"]

    VERB_SUFFIXES = [
        "er", "ir", "re", "ait", "aient", "ions", "iez", "ons", "ez",
        "ed", "ing", "tion", "sion",
    ]

    def __init__(self, language: str = "auto"):
        self.language = language

    def analyze(self, text: str) -> VocabularyProfile:
        """Perform complete vocabulary analysis."""
        words = self._tokenize(text)
        words_lower = [w.lower() for w in words]

        profile = VocabularyProfile()

        # Basic counts
        profile.total_words = len(words)
        unique_words = set(words_lower)
        profile.unique_words = len(unique_words)

        # Vocabulary richness (Type-Token Ratio)
        if profile.total_words > 0:
            profile.vocabulary_richness = profile.unique_words / profile.total_words

        # Average word length
        if words:
            profile.avg_word_length = sum(len(w) for w in words) / len(words)

        # Word frequency analysis
        word_freq = Counter(words_lower)

        # Filter out stopwords for meaningful analysis
        meaningful_words = {
            w: c for w, c in word_freq.items()
            if w not in self.STOPWORDS and len(w) > 2
        }

        profile.most_common_words = Counter(meaningful_words).most_common(50)

        # POS-based analysis (heuristic without full NLP)
        profile.most_common_adjectives = self._extract_by_suffix(
            meaningful_words, self.ADJECTIVE_SUFFIXES, 30
        )
        profile.most_common_adverbs = self._extract_by_suffix(
            meaningful_words, self.ADVERB_SUFFIXES, 20
        )
        profile.most_common_verbs = self._extract_by_suffix(
            meaningful_words, self.VERB_SUFFIXES, 30
        )

        # Signature words (words with distinctive frequency)
        profile.signature_words = self._find_signature_words(meaningful_words, profile.total_words)

        # Rare words analysis
        rare_words = [w for w, c in word_freq.items() if c == 1 and len(w) > 6]
        profile.rare_words_ratio = len(rare_words) / max(profile.unique_words, 1)
        profile.literary_words = self._find_literary_words(rare_words)[:30]

        return profile

    def _tokenize(self, text: str) -> list[str]:
        """Simple word tokenization."""
        # Remove punctuation except apostrophes within words
        text = re.sub(r"[^\w\s\'-]", " ", text)
        words = text.split()
        # Clean up
        words = [w.strip("'-") for w in words if w.strip("'-")]
        return words

    def _extract_by_suffix(
        self, word_freq: dict[str, int], suffixes: list[str], limit: int
    ) -> list[tuple[str, int]]:
        """Extract words by suffix patterns."""
        matching = {}
        for word, count in word_freq.items():
            for suffix in suffixes:
                if word.endswith(suffix) and len(word) > len(suffix) + 2:
                    matching[word] = count
                    break
        return Counter(matching).most_common(limit)

    def _find_signature_words(
        self, word_freq: dict[str, int], total_words: int
    ) -> list[tuple[str, float]]:
        """Find words that appear with distinctive frequency."""
        if total_words == 0:
            return []

        # Calculate relative frequency
        freq_scores = []
        for word, count in word_freq.items():
            if count >= 3 and len(word) >= 4:  # Meaningful threshold
                rel_freq = count / total_words * 10000  # Per 10k words
                # Favor medium-frequency words (not too common, not too rare)
                if 5 <= rel_freq <= 100:
                    freq_scores.append((word, rel_freq))

        # Sort by frequency and return top distinctive words
        freq_scores.sort(key=lambda x: x[1], reverse=True)
        return freq_scores[:40]

    def _find_literary_words(self, rare_words: list[str]) -> list[str]:
        """Identify potentially literary or sophisticated words."""
        literary = []
        for word in rare_words:
            # Heuristics for literary words
            if len(word) >= 8:  # Longer words tend to be more literary
                literary.append(word)
        return sorted(literary, key=len, reverse=True)
