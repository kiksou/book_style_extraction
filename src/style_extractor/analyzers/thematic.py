"""Thematic and motif analysis module."""

import re
from collections import Counter

from ..models import ThematicProfile


class ThematicAnalyzer:
    """Analyzes themes, motifs, and symbolic elements in narrative."""

    # Common literary themes to detect
    THEME_KEYWORDS = {
        "love": {
            "en": ["love", "heart", "passion", "romance", "desire", "beloved", "affection"],
            "fr": ["amour", "coeur", "passion", "romance", "désir", "bien-aimé", "affection"],
        },
        "death": {
            "en": ["death", "die", "dead", "dying", "kill", "murder", "grave", "funeral"],
            "fr": ["mort", "mourir", "tuer", "meurtre", "tombe", "funérailles", "décès"],
        },
        "power": {
            "en": ["power", "control", "rule", "kingdom", "throne", "authority", "command"],
            "fr": ["pouvoir", "contrôle", "règne", "royaume", "trône", "autorité", "commande"],
        },
        "betrayal": {
            "en": ["betray", "traitor", "treachery", "deceive", "trust", "lie", "secret"],
            "fr": ["trahir", "traître", "trahison", "tromper", "confiance", "mensonge", "secret"],
        },
        "revenge": {
            "en": ["revenge", "vengeance", "avenge", "retribution", "payback"],
            "fr": ["vengeance", "revanche", "venger", "représailles"],
        },
        "redemption": {
            "en": ["redemption", "forgive", "save", "salvation", "atone", "repent"],
            "fr": ["rédemption", "pardonner", "sauver", "salut", "expier", "repentir"],
        },
        "identity": {
            "en": ["identity", "who am i", "self", "belong", "true nature", "discover"],
            "fr": ["identité", "qui suis-je", "soi", "appartenir", "vraie nature", "découvrir"],
        },
        "freedom": {
            "en": ["freedom", "free", "escape", "liberty", "prison", "chains", "liberation"],
            "fr": ["liberté", "libre", "évasion", "prison", "chaînes", "libération"],
        },
        "sacrifice": {
            "en": ["sacrifice", "give up", "surrender", "cost", "price", "duty"],
            "fr": ["sacrifice", "abandonner", "renoncer", "coût", "prix", "devoir"],
        },
        "family": {
            "en": ["family", "father", "mother", "brother", "sister", "son", "daughter", "blood"],
            "fr": ["famille", "père", "mère", "frère", "soeur", "fils", "fille", "sang"],
        },
        "war": {
            "en": ["war", "battle", "fight", "soldier", "army", "enemy", "victory", "defeat"],
            "fr": ["guerre", "bataille", "combat", "soldat", "armée", "ennemi", "victoire", "défaite"],
        },
        "nature": {
            "en": ["nature", "forest", "sea", "mountain", "river", "storm", "earth", "sky"],
            "fr": ["nature", "forêt", "mer", "montagne", "rivière", "tempête", "terre", "ciel"],
        },
    }

    # Motif patterns (recurring images/symbols)
    MOTIF_PATTERNS = {
        "light_darkness": [
            r'\b(light|dark|shadow|sun|moon|bright|dim|glow|shine)\b',
            r'\b(lumière|ombre|soleil|lune|brillant|sombre|lueur)\b',
        ],
        "water": [
            r'\b(water|sea|ocean|river|rain|storm|wave|drown|flow)\b',
            r'\b(eau|mer|océan|rivière|pluie|tempête|vague|noyer|couler)\b',
        ],
        "fire": [
            r'\b(fire|flame|burn|heat|ash|smoke|blaze)\b',
            r'\b(feu|flamme|brûler|chaleur|cendre|fumée|brasier)\b',
        ],
        "blood": [
            r'\b(blood|bleed|wound|scar|red|crimson)\b',
            r'\b(sang|saigner|blessure|cicatrice|rouge|cramoisi)\b',
        ],
        "dreams": [
            r'\b(dream|nightmare|sleep|vision|wake)\b',
            r'\b(rêve|cauchemar|sommeil|vision|réveil)\b',
        ],
        "journey": [
            r'\b(journey|road|path|way|travel|destination|quest)\b',
            r'\b(voyage|route|chemin|voie|voyager|destination|quête)\b',
        ],
        "time": [
            r'\b(time|hour|moment|past|future|memory|remember)\b',
            r'\b(temps|heure|moment|passé|futur|mémoire|souvenir)\b',
        ],
    }

    # Emotional arc patterns
    EMOTION_KEYWORDS = {
        "joy": ["happy", "joy", "laugh", "smile", "delight", "heureux", "joie", "rire", "sourire"],
        "sadness": ["sad", "cry", "tears", "grief", "mourn", "triste", "pleurer", "larmes", "deuil"],
        "anger": ["angry", "rage", "fury", "hate", "furious", "colère", "rage", "fureur", "haine"],
        "fear": ["fear", "afraid", "terror", "panic", "dread", "peur", "terreur", "panique", "effroi"],
        "hope": ["hope", "wish", "dream", "believe", "faith", "espoir", "souhaiter", "croire", "foi"],
        "despair": ["despair", "hopeless", "doom", "lost", "désespoir", "perdu", "condamné"],
    }

    def __init__(self):
        pass

    def analyze(self, text: str, chapters: list[str] = None) -> ThematicProfile:
        """Perform complete thematic analysis."""
        profile = ThematicProfile()

        text_lower = text.lower()

        # Theme detection
        profile.recurring_themes = self._detect_themes(text_lower)

        # Motif detection
        profile.recurring_motifs = self._detect_motifs(text_lower)

        # Symbolic elements (basic detection)
        profile.symbolic_elements = self._detect_symbols(text_lower)

        # Emotional arc
        if chapters:
            profile.emotional_arc_pattern = self._analyze_emotional_arc(chapters)

        # Tension building techniques
        profile.tension_building_techniques = self._detect_tension_techniques(text)

        return profile

    def _detect_themes(self, text: str) -> list[tuple[str, float]]:
        """Detect and score recurring themes."""
        theme_scores = {}
        total_words = len(text.split())

        for theme, keywords in self.THEME_KEYWORDS.items():
            count = 0
            all_keywords = keywords.get("en", []) + keywords.get("fr", [])

            for keyword in all_keywords:
                count += len(re.findall(rf'\b{keyword}\b', text, re.IGNORECASE))

            if count > 0:
                # Score based on frequency per 10k words
                score = (count / total_words) * 10000
                theme_scores[theme] = round(score, 2)

        # Sort by score
        sorted_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_themes[:10]

    def _detect_motifs(self, text: str) -> list[tuple[str, int]]:
        """Detect recurring motifs and images."""
        motif_counts = {}

        for motif, patterns in self.MOTIF_PATTERNS.items():
            count = 0
            for pattern in patterns:
                count += len(re.findall(pattern, text, re.IGNORECASE))
            if count > 0:
                motif_counts[motif] = count

        sorted_motifs = sorted(motif_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_motifs

    def _detect_symbols(self, text: str) -> list[tuple[str, str]]:
        """Detect potential symbolic elements."""
        symbols = []

        # Color symbolism
        color_counts = Counter()
        colors = {
            "red": "passion/danger/blood",
            "blue": "sadness/calm/royalty",
            "green": "nature/envy/growth",
            "black": "death/mystery/evil",
            "white": "purity/innocence/death",
            "gold": "wealth/divinity/corruption",
            "silver": "purity/moon/feminine",
        }

        for color, meaning in colors.items():
            count = len(re.findall(rf'\b{color}\b', text, re.IGNORECASE))
            if count > 5:
                symbols.append((color, meaning))

        # Weather symbolism
        weather = {
            "storm": "conflict/turmoil/change",
            "rain": "cleansing/sadness/renewal",
            "sun": "hope/life/truth",
            "darkness": "evil/ignorance/death",
        }

        for element, meaning in weather.items():
            count = len(re.findall(rf'\b{element}\b', text, re.IGNORECASE))
            if count > 3:
                symbols.append((element, meaning))

        return symbols[:15]

    def _analyze_emotional_arc(self, chapters: list[str]) -> list[str]:
        """Analyze emotional arc across chapters."""
        arc = []

        for i, chapter in enumerate(chapters):
            chapter_lower = chapter.lower()
            emotions = {}

            for emotion, keywords in self.EMOTION_KEYWORDS.items():
                count = sum(len(re.findall(rf'\b{kw}\b', chapter_lower)) for kw in keywords)
                emotions[emotion] = count

            # Find dominant emotion
            if emotions:
                dominant = max(emotions, key=emotions.get)
                arc.append(dominant)
            else:
                arc.append("neutral")

        # Simplify arc to key transitions
        simplified = self._simplify_arc(arc)
        return simplified

    def _simplify_arc(self, arc: list[str]) -> list[str]:
        """Simplify emotional arc to key transitions."""
        if len(arc) <= 5:
            return arc

        # Split into segments
        segment_size = len(arc) // 5
        simplified = []

        for i in range(5):
            start = i * segment_size
            end = start + segment_size if i < 4 else len(arc)
            segment = arc[start:end]

            # Find most common emotion in segment
            counter = Counter(segment)
            most_common = counter.most_common(1)[0][0] if counter else "neutral"
            simplified.append(most_common)

        return simplified

    def _detect_tension_techniques(self, text: str) -> list[str]:
        """Detect tension-building techniques used."""
        techniques = []

        # Foreshadowing
        foreshadow_patterns = [
            r'\b(little did|would later|was to come|didn\'t know)\b',
            r'\b(il ne savait pas|allait bientôt|ne se doutait pas)\b',
        ]
        if any(re.search(p, text, re.IGNORECASE) for p in foreshadow_patterns):
            techniques.append("foreshadowing")

        # Dramatic irony (reader knows more than character)
        irony_patterns = [
            r'\b(unaware|oblivious|didn\'t realize|had no idea)\b',
            r'\b(sans savoir|ignorant|ne réalisait pas)\b',
        ]
        if any(re.search(p, text, re.IGNORECASE) for p in irony_patterns):
            techniques.append("dramatic_irony")

        # Time pressure
        time_pressure = [
            r'\b(running out of time|too late|before it\'s|hurry)\b',
            r'\b(plus le temps|trop tard|avant qu\'il|dépêche)\b',
        ]
        if any(re.search(p, text, re.IGNORECASE) for p in time_pressure):
            techniques.append("time_pressure")

        # Mystery/questions
        if text.count("?") / len(text.split()) > 0.02:
            techniques.append("questioning")

        # Short sentences for tension
        sentences = re.split(r'[.!?]+', text)
        short = sum(1 for s in sentences if len(s.split()) < 5)
        if short / len(sentences) > 0.2:
            techniques.append("staccato_pacing")

        # Cliffhangers (chapters ending in tension)
        if re.search(r'(suddenly|but then|when—|soudain|mais alors|quand—)\s*$', text):
            techniques.append("cliffhangers")

        return techniques
