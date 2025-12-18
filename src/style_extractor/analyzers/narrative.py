"""Narrative structure and techniques analysis module."""

import re
import statistics
from collections import Counter

from ..models import NarrativeProfile, POVType, TenseType


class NarrativeAnalyzer:
    """Analyzes narrative structure, POV, tense, and storytelling techniques."""

    # POV indicators
    FIRST_PERSON_MARKERS = {
        "i", "me", "my", "mine", "myself", "we", "us", "our", "ours",
        "je", "me", "moi", "mon", "ma", "mes", "nous", "notre", "nos",
    }

    SECOND_PERSON_MARKERS = {
        "you", "your", "yours", "yourself",
        "tu", "te", "toi", "ton", "ta", "tes", "vous", "votre", "vos",
    }

    THIRD_PERSON_MARKERS = {
        "he", "she", "him", "her", "his", "hers", "they", "them", "their",
        "il", "elle", "lui", "ils", "elles", "leur", "leurs", "son", "sa", "ses",
    }

    # Tense indicators
    PAST_INDICATORS = [
        r'\bwas\b', r'\bwere\b', r'\bhad\b', r'\b\w+ed\b',
        r'\bétait\b', r'\bétaient\b', r'\bavait\b', r'\bavaient\b',
        r'\b\w+ait\b', r'\b\w+aient\b', r'\bfut\b', r'\beurent\b',
    ]

    PRESENT_INDICATORS = [
        r'\bis\b', r'\bare\b', r'\bhas\b', r'\bhave\b',
        r'\best\b', r'\bsont\b', r'\ba\b', r'\bont\b',
    ]

    def __init__(self):
        pass

    def analyze(self, text: str, chapters: list[str] = None) -> NarrativeProfile:
        """Perform complete narrative analysis."""
        profile = NarrativeProfile()

        # Detect POV
        profile.primary_pov = self._detect_pov(text)

        # Detect tense
        profile.primary_tense = self._detect_tense(text)

        # Chapter analysis
        if chapters:
            chapter_lengths = [len(c.split()) for c in chapters]
            if chapter_lengths:
                profile.avg_chapter_length = statistics.mean(chapter_lengths)
                if len(chapter_lengths) > 1:
                    profile.chapter_length_variance = statistics.variance(chapter_lengths)

            # Extract chapter patterns
            profile.chapter_opening_patterns = self._extract_opening_patterns(chapters)
            profile.chapter_ending_patterns = self._extract_ending_patterns(chapters)
            profile.cliffhanger_frequency = self._detect_cliffhangers(chapters)

        # Scene analysis
        scenes = self._split_scenes(text)
        if scenes:
            scene_lengths = [len(s.split()) for s in scenes]
            profile.avg_scene_length = statistics.mean(scene_lengths) if scene_lengths else 0
            profile.scene_break_frequency = len(scenes) / (len(text.split()) / 1000)  # Per 1k words

        # Transition analysis
        profile.transition_words = self._analyze_transitions(text)
        profile.time_skip_patterns = self._find_time_skip_patterns(text)

        return profile

    def _detect_pov(self, text: str) -> POVType:
        """Detect the primary point of view."""
        words = text.lower().split()
        word_set = set(words)

        # Count markers
        first_count = sum(1 for w in words if w in self.FIRST_PERSON_MARKERS)
        second_count = sum(1 for w in words if w in self.SECOND_PERSON_MARKERS)
        third_count = sum(1 for w in words if w in self.THIRD_PERSON_MARKERS)

        total = first_count + second_count + third_count
        if total == 0:
            return POVType.THIRD_LIMITED

        first_ratio = first_count / total
        second_ratio = second_count / total
        third_ratio = third_count / total

        if first_ratio > 0.4:
            return POVType.FIRST_PERSON
        elif second_ratio > 0.3:
            return POVType.SECOND_PERSON
        elif third_ratio > 0.4:
            # Distinguish limited vs omniscient
            if self._is_omniscient(text):
                return POVType.THIRD_OMNISCIENT
            return POVType.THIRD_LIMITED
        else:
            return POVType.MIXED

    def _is_omniscient(self, text: str) -> bool:
        """Detect if third person is omniscient (multiple character thoughts)."""
        # Look for thought access to multiple characters
        thought_patterns = [
            r'(\w+)\s+thought',
            r'(\w+)\s+knew',
            r'(\w+)\s+felt',
            r'(\w+)\s+wondered',
            r'(\w+)\s+pensa',
            r'(\w+)\s+savait',
            r'(\w+)\s+sentait',
        ]

        characters_with_thoughts = set()
        for pattern in thought_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            characters_with_thoughts.update(m.lower() for m in matches)

        # Remove common words that aren't names
        non_names = {"he", "she", "it", "they", "il", "elle", "on"}
        characters_with_thoughts -= non_names

        return len(characters_with_thoughts) > 2

    def _detect_tense(self, text: str) -> TenseType:
        """Detect the primary narrative tense."""
        past_count = 0
        present_count = 0

        for pattern in self.PAST_INDICATORS:
            past_count += len(re.findall(pattern, text, re.IGNORECASE))

        for pattern in self.PRESENT_INDICATORS:
            present_count += len(re.findall(pattern, text, re.IGNORECASE))

        total = past_count + present_count
        if total == 0:
            return TenseType.PAST

        past_ratio = past_count / total

        if past_ratio > 0.7:
            return TenseType.PAST
        elif past_ratio < 0.3:
            return TenseType.PRESENT
        else:
            return TenseType.MIXED

    def _split_scenes(self, text: str) -> list[str]:
        """Split text into scenes."""
        # Common scene break patterns
        scene_breaks = [
            r'\n\s*\*\s*\*\s*\*\s*\n',  # * * *
            r'\n\s*#\s*#\s*#\s*\n',  # # # #
            r'\n\s*-\s*-\s*-\s*\n',  # - - -
            r'\n\s*~\s*~\s*~\s*\n',  # ~ ~ ~
            r'\n{3,}',  # Multiple blank lines
        ]

        combined_pattern = '|'.join(scene_breaks)
        scenes = re.split(combined_pattern, text)
        return [s.strip() for s in scenes if s.strip()]

    def _extract_opening_patterns(self, chapters: list[str]) -> list[str]:
        """Extract common chapter opening patterns."""
        patterns = []

        for chapter in chapters[:20]:  # Sample first 20 chapters
            # Get first sentence
            first_sentence = chapter.strip().split('.')[0] if chapter.strip() else ""
            if len(first_sentence) < 200:  # Reasonable length
                patterns.append(first_sentence[:100])

        # Categorize patterns
        categories = {
            "action": 0,
            "dialogue": 0,
            "description": 0,
            "character": 0,
            "time/place": 0,
        }

        dialogue_pattern = r'^[""«]|^—'
        time_pattern = r'^(the next|that night|when|le lendemain|cette nuit|quand)'
        action_verbs = ["walked", "ran", "grabbed", "looked", "marcha", "courut", "regarda"]

        for opening in patterns:
            opening_lower = opening.lower()
            if re.match(dialogue_pattern, opening):
                categories["dialogue"] += 1
            elif any(v in opening_lower for v in action_verbs):
                categories["action"] += 1
            elif re.match(time_pattern, opening_lower):
                categories["time/place"] += 1
            else:
                categories["description"] += 1

        # Return most common pattern type and examples
        sorted_cats = sorted(categories.items(), key=lambda x: x[1], reverse=True)
        return [f"{cat}: {count}" for cat, count in sorted_cats[:3]]

    def _extract_ending_patterns(self, chapters: list[str]) -> list[str]:
        """Extract common chapter ending patterns."""
        patterns = []

        for chapter in chapters[:20]:
            # Get last sentence
            sentences = re.split(r'[.!?]+', chapter.strip())
            sentences = [s.strip() for s in sentences if s.strip()]
            if sentences:
                last = sentences[-1]
                if len(last) < 200:
                    patterns.append(last[:100])

        return patterns[:10]

    def _detect_cliffhangers(self, chapters: list[str]) -> float:
        """Detect cliffhanger frequency at chapter ends."""
        cliffhanger_patterns = [
            r'[.!?]\s*$',  # Ends with punctuation
            r'\.{3}\s*$',  # Ends with ellipsis
            r'—\s*$',  # Ends with em-dash
        ]

        tension_words = [
            "suddenly", "then", "but", "when", "before",
            "soudain", "alors", "mais", "quand", "avant",
        ]

        cliffhangers = 0
        for chapter in chapters:
            last_sentence = chapter.strip()[-200:].lower()

            # Check for tension words near end
            if any(w in last_sentence for w in tension_words):
                cliffhangers += 1
                continue

            # Check for question ending
            if chapter.strip().endswith("?"):
                cliffhangers += 1

        return cliffhangers / len(chapters) if chapters else 0

    def _analyze_transitions(self, text: str) -> list[tuple[str, int]]:
        """Analyze transition words and phrases."""
        transitions = {
            # English
            "however": 0, "meanwhile": 0, "later": 0, "then": 0,
            "suddenly": 0, "finally": 0, "afterwards": 0, "therefore": 0,
            "moreover": 0, "furthermore": 0, "consequently": 0,
            # French
            "cependant": 0, "pendant ce temps": 0, "plus tard": 0, "puis": 0,
            "soudain": 0, "enfin": 0, "ensuite": 0, "donc": 0,
            "de plus": 0, "par conséquent": 0, "ainsi": 0,
        }

        text_lower = text.lower()
        for trans in transitions:
            transitions[trans] = len(re.findall(rf'\b{trans}\b', text_lower))

        sorted_trans = sorted(transitions.items(), key=lambda x: x[1], reverse=True)
        return [(t, c) for t, c in sorted_trans if c > 0][:15]

    def _find_time_skip_patterns(self, text: str) -> list[str]:
        """Find patterns used for time skips."""
        patterns = [
            r'(days? later)',
            r'(weeks? later)',
            r'(months? later)',
            r'(years? later)',
            r'(the next (morning|day|week|month|year))',
            r'(that (night|evening|afternoon))',
            r'(quelques jours plus tard)',
            r'(le lendemain)',
            r'(une semaine plus tard)',
            r'(des mois plus tard)',
        ]

        found_patterns = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if isinstance(matches[0], tuple):
                    found_patterns.extend([m[0] for m in matches])
                else:
                    found_patterns.extend(matches)

        # Count and return unique
        counted = Counter(found_patterns)
        return [p for p, _ in counted.most_common(10)]
