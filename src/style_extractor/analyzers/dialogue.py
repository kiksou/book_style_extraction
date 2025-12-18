"""Dialogue style analysis module."""

import re
from collections import Counter

from ..models import DialogueProfile


class DialogueAnalyzer:
    """Analyzes dialogue patterns and speech representation."""

    # Dialogue markers for different quote styles
    DIALOGUE_PATTERNS = [
        # English double quotes
        r'"([^"]+)"',
        # English single quotes
        r"'([^']+)'",
        # French guillemets
        r'«\s*([^»]+)\s*»',
        r'"\s*([^"]+)\s*"',
        # German quotes
        r'„([^"]+)"',
        # Dash dialogue (French/Spanish style)
        r'—\s*([^—\n]+?)(?=\s*—|\s*$|\n)',
        r'–\s*([^–\n]+?)(?=\s*–|\s*$|\n)',
    ]

    # Common dialogue tags
    DIALOGUE_TAGS_EN = {
        "said", "asked", "replied", "answered", "whispered", "shouted",
        "yelled", "muttered", "murmured", "called", "cried", "exclaimed",
        "demanded", "inquired", "responded", "added", "continued",
        "admitted", "agreed", "announced", "argued", "began", "begged",
        "commented", "complained", "confessed", "explained", "growled",
        "grumbled", "hissed", "insisted", "interrupted", "laughed",
        "mentioned", "moaned", "noted", "observed", "offered", "ordered",
        "pleaded", "promised", "protested", "questioned", "recalled",
        "remarked", "repeated", "screamed", "sighed", "snapped", "sobbed",
        "spoke", "stammered", "stated", "suggested", "told", "urged",
        "warned", "wondered", "yawned",
    }

    DIALOGUE_TAGS_FR = {
        "dit", "demanda", "répondit", "murmura", "chuchota", "cria",
        "s'exclama", "ajouta", "continua", "avoua", "expliqua", "soupira",
        "grogna", "hurla", "insista", "interrompit", "observa", "ordonna",
        "promit", "protesta", "questionna", "répéta", "suggéra", "supplia",
        "affirma", "annonça", "articula", "balbutia", "bégaya", "confia",
        "confirma", "corrigea", "déclara", "fit", "glissa", "grommela",
        "interrogea", "intervint", "lança", "marmonna", "objecta", "précisa",
        "proposa", "raconta", "renchérit", "reprit", "rétorqua", "révéla",
        "ricana", "souffla", "tempêta", "trancha",
    }

    def __init__(self):
        self.all_tags = self.DIALOGUE_TAGS_EN | self.DIALOGUE_TAGS_FR

    def analyze(self, text: str) -> DialogueProfile:
        """Perform complete dialogue analysis."""
        profile = DialogueProfile()

        # Extract all dialogue
        dialogues = self._extract_dialogues(text)
        total_words = len(text.split())

        if not dialogues:
            return profile

        # Dialogue ratio
        dialogue_words = sum(len(d.split()) for d in dialogues)
        profile.dialogue_ratio = dialogue_words / total_words if total_words > 0 else 0

        # Average dialogue length
        profile.avg_dialogue_length = dialogue_words / len(dialogues) if dialogues else 0

        # Analyze dialogue tags
        tag_analysis = self._analyze_tags(text)
        profile.said_frequency = tag_analysis["said_frequency"]
        profile.variety_of_tags = tag_analysis["tag_counts"]
        profile.action_tags_ratio = tag_analysis["action_tags_ratio"]

        # Dialogue interruptions
        profile.dialogue_interruption_frequency = self._count_interruptions(text, len(dialogues))

        # Internal monologue
        profile.internal_monologue_ratio = self._estimate_internal_monologue(text, total_words)

        return profile

    def _extract_dialogues(self, text: str) -> list[str]:
        """Extract all dialogue from text."""
        dialogues = []

        for pattern in self.DIALOGUE_PATTERNS:
            matches = re.findall(pattern, text, re.MULTILINE)
            dialogues.extend(matches)

        return dialogues

    def _analyze_tags(self, text: str) -> dict:
        """Analyze dialogue tag usage."""
        text_lower = text.lower()

        # Count each tag
        tag_counts = Counter()
        for tag in self.all_tags:
            pattern = rf'\b{tag}\b'
            count = len(re.findall(pattern, text_lower))
            if count > 0:
                tag_counts[tag] = count

        total_tags = sum(tag_counts.values()) or 1

        # Calculate "said" frequency
        said_count = tag_counts.get("said", 0) + tag_counts.get("dit", 0)
        said_frequency = said_count / total_tags

        # Action tags (when dialogue is followed by action instead of tag)
        action_pattern = r'[""»]\s*[A-Z][^.!?]*(?:smiled|nodded|shrugged|looked|turned|sourit|hocha|haussa|regarda)'
        action_tags = len(re.findall(action_pattern, text))
        action_tags_ratio = action_tags / total_tags if total_tags > 0 else 0

        return {
            "tag_counts": tag_counts.most_common(20),
            "said_frequency": said_frequency,
            "action_tags_ratio": action_tags_ratio,
        }

    def _count_interruptions(self, text: str, dialogue_count: int) -> float:
        """Count dialogue interruptions (mid-sentence breaks)."""
        # Patterns for interrupted dialogue
        interruption_patterns = [
            r'"[^"]*—[^"]*"',  # Em-dash in dialogue
            r'"[^"]*\.\.\.[^"]*"',  # Ellipsis in dialogue
            r'«[^»]*—[^»]*»',
            r'«[^»]*\.\.\.[^»]*»',
        ]

        interruptions = 0
        for pattern in interruption_patterns:
            interruptions += len(re.findall(pattern, text))

        return interruptions / dialogue_count if dialogue_count > 0 else 0

    def _estimate_internal_monologue(self, text: str, total_words: int) -> float:
        """Estimate ratio of internal monologue/thoughts."""
        # Patterns suggesting internal thought
        thought_patterns = [
            r'\bthought\b',
            r'\bwondered\b',
            r'\brealized\b',
            r'\bknew that\b',
            r'\bfelt that\b',
            r'\bpensa\b',
            r'\bsongea\b',
            r'\bse demanda\b',
            r'\bréalisa\b',
            r'\bcomprit\b',
            r'\bsavait que\b',
            r'\bsentait que\b',
        ]

        # Italicized text (often used for thoughts)
        italic_pattern = r'\*([^*]+)\*|_([^_]+)_'

        thought_count = 0
        for pattern in thought_patterns:
            thought_count += len(re.findall(pattern, text, re.IGNORECASE))

        italic_matches = re.findall(italic_pattern, text)
        thought_count += len(italic_matches)

        # Rough estimate: each thought marker represents ~20 words
        estimated_thought_words = thought_count * 20
        return estimated_thought_words / total_words if total_words > 0 else 0

    def get_dialogue_samples(self, text: str, count: int = 10) -> dict:
        """Extract sample dialogues for analysis."""
        dialogues = self._extract_dialogues(text)

        # Sort by length for variety
        short = [d for d in dialogues if len(d.split()) < 10]
        medium = [d for d in dialogues if 10 <= len(d.split()) <= 30]
        long = [d for d in dialogues if len(d.split()) > 30]

        return {
            "short_dialogues": short[:count],
            "medium_dialogues": medium[:count],
            "long_dialogues": long[:count],
        }
