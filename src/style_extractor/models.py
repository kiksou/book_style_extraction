"""Data models for the style extractor."""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any


class POVType(str, Enum):
    """Point of view types."""
    FIRST_PERSON = "first_person"
    THIRD_LIMITED = "third_limited"
    THIRD_OMNISCIENT = "third_omniscient"
    SECOND_PERSON = "second_person"
    MIXED = "mixed"


class TenseType(str, Enum):
    """Narrative tense types."""
    PAST = "past"
    PRESENT = "present"
    MIXED = "mixed"


@dataclass
class Chapter:
    """Represents a chapter or section of a book."""
    number: int
    title: str
    content: str
    word_count: int = 0

    def __post_init__(self):
        if not self.word_count:
            self.word_count = len(self.content.split())


@dataclass
class Book:
    """Represents a book in the saga."""
    title: str
    author: str
    content: str
    chapters: list[Chapter] = field(default_factory=list)
    file_path: Path | None = None
    order_in_saga: int = 1

    @property
    def word_count(self) -> int:
        return len(self.content.split())

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)


@dataclass
class VocabularyProfile:
    """Vocabulary analysis results."""
    total_words: int = 0
    unique_words: int = 0
    vocabulary_richness: float = 0.0  # Type-Token Ratio
    avg_word_length: float = 0.0

    # Frequency distributions
    most_common_words: list[tuple[str, int]] = field(default_factory=list)
    most_common_adjectives: list[tuple[str, int]] = field(default_factory=list)
    most_common_verbs: list[tuple[str, int]] = field(default_factory=list)
    most_common_adverbs: list[tuple[str, int]] = field(default_factory=list)

    # Signature words (distinctive to this author)
    signature_words: list[tuple[str, float]] = field(default_factory=list)

    # Rare/literary words usage
    rare_words_ratio: float = 0.0
    literary_words: list[str] = field(default_factory=list)


@dataclass
class SyntaxProfile:
    """Sentence structure analysis."""
    avg_sentence_length: float = 0.0
    median_sentence_length: float = 0.0
    sentence_length_variance: float = 0.0

    # Sentence types distribution
    short_sentences_ratio: float = 0.0  # < 10 words
    medium_sentences_ratio: float = 0.0  # 10-25 words
    long_sentences_ratio: float = 0.0  # > 25 words

    # Structure patterns
    avg_clauses_per_sentence: float = 0.0
    subordinate_clause_ratio: float = 0.0

    # Punctuation habits
    semicolon_frequency: float = 0.0
    dash_frequency: float = 0.0
    ellipsis_frequency: float = 0.0
    exclamation_frequency: float = 0.0
    question_frequency: float = 0.0

    # Paragraph structure
    avg_paragraph_length: float = 0.0
    avg_sentences_per_paragraph: float = 0.0


@dataclass
class RhythmProfile:
    """Prose rhythm and flow analysis."""
    avg_syllables_per_word: float = 0.0

    # Readability scores
    flesch_reading_ease: float = 0.0
    flesch_kincaid_grade: float = 0.0
    gunning_fog_index: float = 0.0

    # Rhythm patterns
    sentence_length_pattern: list[int] = field(default_factory=list)  # Rolling pattern
    rhythm_variety_score: float = 0.0  # How much sentence length varies

    # Pacing indicators
    action_density: float = 0.0  # Verbs per sentence
    description_density: float = 0.0  # Adjectives per sentence


@dataclass
class DialogueProfile:
    """Dialogue style analysis."""
    dialogue_ratio: float = 0.0  # % of text that is dialogue
    avg_dialogue_length: float = 0.0  # Words per dialogue block

    # Dialogue tags
    said_frequency: float = 0.0
    variety_of_tags: list[tuple[str, int]] = field(default_factory=list)
    action_tags_ratio: float = 0.0  # "He smiled." vs "he said"

    # Dialogue patterns
    dialogue_interruption_frequency: float = 0.0
    internal_monologue_ratio: float = 0.0


@dataclass
class NarrativeProfile:
    """Narrative structure and techniques."""
    primary_pov: POVType = POVType.THIRD_LIMITED
    primary_tense: TenseType = TenseType.PAST

    # Chapter structure
    avg_chapter_length: float = 0.0
    chapter_length_variance: float = 0.0

    # Scene structure
    avg_scene_length: float = 0.0
    scene_break_frequency: float = 0.0

    # Opening patterns
    chapter_opening_patterns: list[str] = field(default_factory=list)

    # Ending patterns
    chapter_ending_patterns: list[str] = field(default_factory=list)
    cliffhanger_frequency: float = 0.0

    # Transitions
    transition_words: list[tuple[str, int]] = field(default_factory=list)
    time_skip_patterns: list[str] = field(default_factory=list)


@dataclass
class ThematicProfile:
    """Thematic and motif analysis."""
    recurring_themes: list[tuple[str, float]] = field(default_factory=list)
    recurring_motifs: list[tuple[str, int]] = field(default_factory=list)
    symbolic_elements: list[tuple[str, str]] = field(default_factory=list)  # (symbol, meaning)

    # Emotional patterns
    emotional_arc_pattern: list[str] = field(default_factory=list)
    tension_building_techniques: list[str] = field(default_factory=list)


@dataclass
class StyleFingerprint:
    """Complete style fingerprint combining all analyses."""
    vocabulary: VocabularyProfile = field(default_factory=VocabularyProfile)
    syntax: SyntaxProfile = field(default_factory=SyntaxProfile)
    rhythm: RhythmProfile = field(default_factory=RhythmProfile)
    dialogue: DialogueProfile = field(default_factory=DialogueProfile)
    narrative: NarrativeProfile = field(default_factory=NarrativeProfile)
    thematic: ThematicProfile = field(default_factory=ThematicProfile)


@dataclass
class AnalysisResult:
    """Complete analysis result for a saga."""
    saga_name: str
    author: str
    books_analyzed: list[str]
    total_words: int
    fingerprint: StyleFingerprint

    # Writing guidelines derived from analysis
    writing_guidelines: dict[str, Any] = field(default_factory=dict)

    # Example passages for each style element
    example_passages: dict[str, list[str]] = field(default_factory=dict)
