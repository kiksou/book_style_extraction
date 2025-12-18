"""Prose rhythm and readability analysis module."""

import re
import statistics

from ..models import RhythmProfile


class RhythmAnalyzer:
    """Analyzes prose rhythm, flow, and readability."""

    # Syllable counting patterns (English-focused, approximation for French)
    VOWELS = "aeiouyàâäéèêëïîôùûüœæ"
    SILENT_E = re.compile(r'[^l]e$|ed$|es$', re.IGNORECASE)

    def __init__(self):
        pass

    def analyze(self, text: str) -> RhythmProfile:
        """Perform complete rhythm analysis."""
        profile = RhythmProfile()

        words = self._get_words(text)
        sentences = self._split_sentences(text)

        if not words or not sentences:
            return profile

        # Syllable analysis
        syllable_counts = [self._count_syllables(w) for w in words]
        profile.avg_syllables_per_word = statistics.mean(syllable_counts) if syllable_counts else 0

        # Readability scores
        total_words = len(words)
        total_sentences = len(sentences)
        total_syllables = sum(syllable_counts)

        # Flesch Reading Ease (adapted)
        if total_sentences > 0 and total_words > 0:
            avg_sentence_length = total_words / total_sentences
            avg_syllables = total_syllables / total_words

            profile.flesch_reading_ease = (
                206.835
                - 1.015 * avg_sentence_length
                - 84.6 * avg_syllables
            )

            # Flesch-Kincaid Grade Level
            profile.flesch_kincaid_grade = (
                0.39 * avg_sentence_length
                + 11.8 * avg_syllables
                - 15.59
            )

            # Gunning Fog Index
            complex_words = sum(1 for c in syllable_counts if c >= 3)
            complex_ratio = complex_words / total_words if total_words > 0 else 0
            profile.gunning_fog_index = 0.4 * (avg_sentence_length + 100 * complex_ratio)

        # Sentence length pattern (for rhythm analysis)
        sentence_lengths = [len(s.split()) for s in sentences]
        profile.sentence_length_pattern = sentence_lengths[:50]  # First 50 for pattern

        # Rhythm variety score
        if len(sentence_lengths) > 1:
            mean_len = statistics.mean(sentence_lengths)
            variations = [abs(l - mean_len) for l in sentence_lengths]
            profile.rhythm_variety_score = statistics.mean(variations) / max(mean_len, 1)

        # Pacing indicators
        verbs = self._count_verbs_approx(text)
        adjectives = self._count_adjectives_approx(text)

        if total_sentences > 0:
            profile.action_density = verbs / total_sentences
            profile.description_density = adjectives / total_sentences

        return profile

    def _get_words(self, text: str) -> list[str]:
        """Extract words from text."""
        text = re.sub(r'[^\w\s\'-]', ' ', text)
        return [w.strip("'-") for w in text.split() if w.strip("'-")]

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        sentences = re.split(r'[.!?]+["»\'\)]*\s+|[.!?]+["»\'\)]*$', text)
        return [s.strip() for s in sentences if s.strip()]

    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower().strip()
        if len(word) <= 2:
            return 1

        # Count vowel groups
        count = 0
        prev_is_vowel = False

        for char in word:
            is_vowel = char in self.VOWELS
            if is_vowel and not prev_is_vowel:
                count += 1
            prev_is_vowel = is_vowel

        # Handle silent e
        if self.SILENT_E.search(word):
            count -= 1

        # Handle special endings
        if word.endswith('le') and len(word) > 2 and word[-3] not in self.VOWELS:
            count += 1

        return max(1, count)

    def _count_verbs_approx(self, text: str) -> int:
        """Approximate verb count using suffix patterns."""
        verb_patterns = [
            r'\b\w+ed\b',
            r'\b\w+ing\b',
            r'\b\w+ait\b',
            r'\b\w+aient\b',
            r'\b\w+ions\b',
            r'\b\w+era\b',
            r'\b\w+erait\b',
        ]
        count = 0
        for pattern in verb_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

    def _count_adjectives_approx(self, text: str) -> int:
        """Approximate adjective count using suffix patterns."""
        adj_patterns = [
            r'\b\w+ful\b',
            r'\b\w+less\b',
            r'\b\w+ous\b',
            r'\b\w+ive\b',
            r'\b\w+eux\b',
            r'\b\w+euse\b',
            r'\b\w+ique\b',
            r'\b\w+able\b',
        ]
        count = 0
        for pattern in adj_patterns:
            count += len(re.findall(pattern, text, re.IGNORECASE))
        return count

    def get_rhythm_visualization(self, text: str, window: int = 10) -> dict:
        """Generate rhythm visualization data."""
        sentences = self._split_sentences(text)
        lengths = [len(s.split()) for s in sentences]

        # Rolling average for smoothing
        rolling_avg = []
        for i in range(len(lengths)):
            start = max(0, i - window // 2)
            end = min(len(lengths), i + window // 2 + 1)
            rolling_avg.append(statistics.mean(lengths[start:end]))

        # Identify rhythm patterns
        patterns = self._identify_patterns(lengths)

        return {
            "sentence_lengths": lengths,
            "rolling_average": rolling_avg,
            "patterns": patterns,
        }

    def _identify_patterns(self, lengths: list[int]) -> list[str]:
        """Identify recurring rhythm patterns."""
        patterns = []

        # Check for long-short alternation
        alternations = 0
        for i in range(1, len(lengths)):
            if (lengths[i] > 15 and lengths[i-1] < 10) or (lengths[i] < 10 and lengths[i-1] > 15):
                alternations += 1

        if alternations > len(lengths) * 0.3:
            patterns.append("alternating_rhythm")

        # Check for buildup patterns (increasing length)
        buildups = 0
        for i in range(3, len(lengths)):
            if lengths[i-2] < lengths[i-1] < lengths[i]:
                buildups += 1

        if buildups > len(lengths) * 0.1:
            patterns.append("building_tension")

        # Check for staccato sequences (multiple short sentences)
        staccato = 0
        for i in range(2, len(lengths)):
            if lengths[i] < 8 and lengths[i-1] < 8 and lengths[i-2] < 8:
                staccato += 1

        if staccato > len(lengths) * 0.05:
            patterns.append("staccato_sequences")

        return patterns
