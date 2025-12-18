"""Syntax and sentence structure analysis module."""

import re
import statistics
from collections import Counter

from ..models import SyntaxProfile


class SyntaxAnalyzer:
    """Analyzes sentence structure and syntactic patterns."""

    # Sentence boundary patterns
    SENTENCE_END = re.compile(r'[.!?]+["»\'\)]*\s+|[.!?]+["»\'\)]*$')

    # Clause markers
    SUBORDINATE_MARKERS = {
        # English
        "although", "because", "since", "while", "whereas", "if", "unless",
        "when", "whenever", "where", "wherever", "after", "before", "until",
        "though", "even though", "as if", "as though", "so that", "in order that",
        "that", "which", "who", "whom", "whose",
        # French
        "bien que", "quoique", "parce que", "puisque", "comme", "tandis que",
        "alors que", "pendant que", "lorsque", "quand", "si", "à moins que",
        "pour que", "afin que", "de sorte que", "avant que", "après que",
        "jusqu'à ce que", "dès que", "aussitôt que",
    }

    def __init__(self):
        pass

    def analyze(self, text: str) -> SyntaxProfile:
        """Perform complete syntax analysis."""
        profile = SyntaxProfile()

        # Split into sentences
        sentences = self._split_sentences(text)
        if not sentences:
            return profile

        # Calculate sentence lengths
        sentence_lengths = [len(s.split()) for s in sentences]

        # Basic statistics
        profile.avg_sentence_length = statistics.mean(sentence_lengths)
        profile.median_sentence_length = statistics.median(sentence_lengths)
        if len(sentence_lengths) > 1:
            profile.sentence_length_variance = statistics.variance(sentence_lengths)

        # Sentence length distribution
        total = len(sentences)
        profile.short_sentences_ratio = sum(1 for l in sentence_lengths if l < 10) / total
        profile.medium_sentences_ratio = sum(1 for l in sentence_lengths if 10 <= l <= 25) / total
        profile.long_sentences_ratio = sum(1 for l in sentence_lengths if l > 25) / total

        # Clause analysis
        clause_counts = [self._count_clauses(s) for s in sentences]
        profile.avg_clauses_per_sentence = statistics.mean(clause_counts) if clause_counts else 0

        subordinate_counts = [self._count_subordinate_clauses(s) for s in sentences]
        if sum(clause_counts) > 0:
            profile.subordinate_clause_ratio = sum(subordinate_counts) / sum(clause_counts)

        # Punctuation analysis
        total_chars = len(text)
        if total_chars > 0:
            profile.semicolon_frequency = text.count(";") / total_chars * 1000
            profile.dash_frequency = (text.count("—") + text.count("–") + text.count(" - ")) / total_chars * 1000
            profile.ellipsis_frequency = (text.count("...") + text.count("…")) / total_chars * 1000
            profile.exclamation_frequency = text.count("!") / total_chars * 1000
            profile.question_frequency = text.count("?") / total_chars * 1000

        # Paragraph analysis
        paragraphs = self._split_paragraphs(text)
        if paragraphs:
            para_lengths = [len(p.split()) for p in paragraphs]
            profile.avg_paragraph_length = statistics.mean(para_lengths)

            para_sentences = [len(self._split_sentences(p)) for p in paragraphs]
            profile.avg_sentences_per_paragraph = statistics.mean(para_sentences)

        return profile

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle common abbreviations
        text = re.sub(r'\b(Mr|Mrs|Ms|Dr|Prof|etc|vs|fig|vol)\.\s', r'\1<DOT> ', text, flags=re.IGNORECASE)
        text = re.sub(r'\b(M|Mme|Mlle|MM)\.\s', r'\1<DOT> ', text)

        # Split on sentence boundaries
        sentences = self.SENTENCE_END.split(text)

        # Clean up
        sentences = [s.replace('<DOT>', '.').strip() for s in sentences if s.strip()]
        return sentences

    def _split_paragraphs(self, text: str) -> list[str]:
        """Split text into paragraphs."""
        paragraphs = re.split(r'\n\s*\n|\n{2,}', text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _count_clauses(self, sentence: str) -> int:
        """Estimate number of clauses in a sentence."""
        # Count clause separators
        separators = [",", ";", ":", "—", "–", " - "]
        count = 1  # Start with 1 for main clause
        for sep in separators:
            count += sentence.count(sep)

        # Also count subordinate markers
        for marker in self.SUBORDINATE_MARKERS:
            if f" {marker} " in sentence.lower() or sentence.lower().startswith(f"{marker} "):
                count += 1

        return count

    def _count_subordinate_clauses(self, sentence: str) -> int:
        """Count subordinate clauses in a sentence."""
        count = 0
        sentence_lower = sentence.lower()

        for marker in self.SUBORDINATE_MARKERS:
            # Check for marker as standalone word
            pattern = rf'\b{re.escape(marker)}\b'
            count += len(re.findall(pattern, sentence_lower))

        return count

    def get_sentence_patterns(self, text: str, sample_size: int = 20) -> dict:
        """Extract common sentence opening patterns."""
        sentences = self._split_sentences(text)

        # Get first few words of each sentence
        openings = []
        for s in sentences:
            words = s.split()[:3]
            if words:
                openings.append(" ".join(words).lower())

        # Find common patterns
        opening_freq = Counter(openings)

        # Categorize openings
        patterns = {
            "pronoun_starts": 0,
            "article_starts": 0,
            "action_starts": 0,
            "adverb_starts": 0,
            "conjunction_starts": 0,
        }

        pronouns = {"i", "he", "she", "it", "we", "they", "you", "je", "il", "elle", "on", "nous", "ils", "elles"}
        articles = {"the", "a", "an", "le", "la", "les", "un", "une", "des", "l'"}
        conjunctions = {"and", "but", "so", "yet", "or", "et", "mais", "donc", "or", "car"}

        for sentence in sentences:
            first_word = sentence.split()[0].lower() if sentence.split() else ""
            if first_word in pronouns:
                patterns["pronoun_starts"] += 1
            elif first_word in articles:
                patterns["article_starts"] += 1
            elif first_word in conjunctions:
                patterns["conjunction_starts"] += 1

        # Normalize
        total = len(sentences) or 1
        for key in patterns:
            patterns[key] = patterns[key] / total

        return {
            "opening_patterns": opening_freq.most_common(sample_size),
            "pattern_distribution": patterns,
        }
