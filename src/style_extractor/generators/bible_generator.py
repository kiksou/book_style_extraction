"""Writing bible generator from analysis results."""

from typing import Any

from ..models import AnalysisResult, StyleFingerprint


class BibleGenerator:
    """Generates a comprehensive writing bible from analysis results."""

    def __init__(self):
        pass

    def generate(self, result: AnalysisResult) -> dict[str, Any]:
        """Generate complete writing bible."""
        bible = {
            "metadata": self._generate_metadata(result),
            "style_guide": self._generate_style_guide(result.fingerprint),
            "voice_guide": self._generate_voice_guide(result.fingerprint),
            "structure_guide": self._generate_structure_guide(result.fingerprint),
            "dialogue_guide": self._generate_dialogue_guide(result.fingerprint),
            "thematic_guide": self._generate_thematic_guide(result.fingerprint),
            "quick_reference": self._generate_quick_reference(result.fingerprint),
            "writing_rules": self._generate_writing_rules(result.fingerprint),
            "examples": result.example_passages,
        }

        return bible

    def _generate_metadata(self, result: AnalysisResult) -> dict:
        """Generate metadata section."""
        return {
            "saga_name": result.saga_name,
            "author": result.author,
            "books_analyzed": result.books_analyzed,
            "total_words_analyzed": result.total_words,
            "analysis_date": None,  # To be filled
        }

    def _generate_style_guide(self, fp: StyleFingerprint) -> dict:
        """Generate prose style guide."""
        vocab = fp.vocabulary
        syntax = fp.syntax
        rhythm = fp.rhythm

        # Determine vocabulary level
        if vocab.vocabulary_richness > 0.15:
            vocab_level = "rich"
            vocab_desc = "Vocabulaire riche et varié. Utiliser des synonymes et éviter les répétitions."
        elif vocab.vocabulary_richness > 0.10:
            vocab_level = "moderate"
            vocab_desc = "Vocabulaire équilibré. Alterner mots courants et expressions plus recherchées."
        else:
            vocab_level = "accessible"
            vocab_desc = "Vocabulaire accessible. Privilégier la clarté et les mots courants."

        # Determine sentence style
        if syntax.avg_sentence_length > 25:
            sentence_style = "complex"
            sentence_desc = "Phrases longues et complexes avec plusieurs propositions."
        elif syntax.avg_sentence_length > 15:
            sentence_style = "balanced"
            sentence_desc = "Phrases de longueur moyenne, équilibrées."
        else:
            sentence_style = "concise"
            sentence_desc = "Phrases courtes et percutantes."

        return {
            "vocabulary": {
                "level": vocab_level,
                "description": vocab_desc,
                "richness_score": round(vocab.vocabulary_richness, 3),
                "avg_word_length": round(vocab.avg_word_length, 1),
                "signature_words": [w for w, _ in vocab.signature_words[:20]],
                "preferred_adjectives": [w for w, _ in vocab.most_common_adjectives[:15]],
                "preferred_verbs": [w for w, _ in vocab.most_common_verbs[:15]],
                "preferred_adverbs": [w for w, _ in vocab.most_common_adverbs[:10]],
            },
            "sentences": {
                "style": sentence_style,
                "description": sentence_desc,
                "avg_length": round(syntax.avg_sentence_length, 1),
                "length_distribution": {
                    "short": f"{syntax.short_sentences_ratio:.0%}",
                    "medium": f"{syntax.medium_sentences_ratio:.0%}",
                    "long": f"{syntax.long_sentences_ratio:.0%}",
                },
            },
            "punctuation": {
                "uses_semicolons": syntax.semicolon_frequency > 0.5,
                "uses_dashes": syntax.dash_frequency > 0.5,
                "uses_ellipsis": syntax.ellipsis_frequency > 0.3,
                "exclamation_frequency": "frequent" if syntax.exclamation_frequency > 1 else "rare",
            },
            "paragraphs": {
                "avg_length_words": round(syntax.avg_paragraph_length, 0),
                "avg_sentences": round(syntax.avg_sentences_per_paragraph, 1),
            },
            "readability": {
                "flesch_ease": round(rhythm.flesch_reading_ease, 1),
                "grade_level": round(rhythm.flesch_kincaid_grade, 1),
                "interpretation": self._interpret_readability(rhythm.flesch_reading_ease),
            },
        }

    def _generate_voice_guide(self, fp: StyleFingerprint) -> dict:
        """Generate narrative voice guide."""
        narrative = fp.narrative
        rhythm = fp.rhythm

        return {
            "point_of_view": {
                "primary": narrative.primary_pov.value,
                "description": self._describe_pov(narrative.primary_pov.value),
            },
            "tense": {
                "primary": narrative.primary_tense.value,
                "description": self._describe_tense(narrative.primary_tense.value),
            },
            "rhythm": {
                "variety_score": round(rhythm.rhythm_variety_score, 2),
                "pacing": self._describe_pacing(rhythm),
                "action_density": round(rhythm.action_density, 2),
                "description_density": round(rhythm.description_density, 2),
            },
            "transitions": {
                "common_words": [w for w, _ in narrative.transition_words[:10]],
                "time_skip_patterns": narrative.time_skip_patterns,
            },
        }

    def _generate_structure_guide(self, fp: StyleFingerprint) -> dict:
        """Generate structural guide."""
        narrative = fp.narrative

        return {
            "chapters": {
                "avg_length": round(narrative.avg_chapter_length, 0),
                "variance": round(narrative.chapter_length_variance, 0) if narrative.chapter_length_variance else 0,
                "opening_styles": narrative.chapter_opening_patterns,
                "ending_styles": narrative.chapter_ending_patterns,
                "cliffhanger_frequency": f"{narrative.cliffhanger_frequency:.0%}",
            },
            "scenes": {
                "avg_length": round(narrative.avg_scene_length, 0),
                "frequency_per_1k_words": round(narrative.scene_break_frequency, 2),
            },
            "recommendations": self._structure_recommendations(narrative),
        }

    def _generate_dialogue_guide(self, fp: StyleFingerprint) -> dict:
        """Generate dialogue style guide."""
        dialogue = fp.dialogue

        return {
            "frequency": {
                "ratio": f"{dialogue.dialogue_ratio:.0%}",
                "interpretation": self._interpret_dialogue_ratio(dialogue.dialogue_ratio),
            },
            "style": {
                "avg_length": round(dialogue.avg_dialogue_length, 1),
                "said_usage": f"{dialogue.said_frequency:.0%}",
                "tag_variety": [tag for tag, _ in dialogue.variety_of_tags[:15]],
                "uses_action_tags": dialogue.action_tags_ratio > 0.1,
            },
            "internal_monologue": {
                "frequency": f"{dialogue.internal_monologue_ratio:.1%}",
            },
            "recommendations": self._dialogue_recommendations(dialogue),
        }

    def _generate_thematic_guide(self, fp: StyleFingerprint) -> dict:
        """Generate thematic guide."""
        thematic = fp.thematic

        return {
            "major_themes": [
                {"theme": theme, "prominence": score}
                for theme, score in thematic.recurring_themes[:5]
            ],
            "recurring_motifs": [
                {"motif": motif, "occurrences": count}
                for motif, count in thematic.recurring_motifs[:8]
            ],
            "symbolism": [
                {"symbol": symbol, "meaning": meaning}
                for symbol, meaning in thematic.symbolic_elements[:10]
            ],
            "emotional_arc": thematic.emotional_arc_pattern,
            "tension_techniques": thematic.tension_building_techniques,
        }

    def _generate_quick_reference(self, fp: StyleFingerprint) -> dict:
        """Generate quick reference card."""
        return {
            "sentence_length_target": f"{fp.syntax.avg_sentence_length:.0f} mots",
            "paragraph_length_target": f"{fp.syntax.avg_paragraph_length:.0f} mots",
            "chapter_length_target": f"{fp.narrative.avg_chapter_length:.0f} mots",
            "dialogue_ratio_target": f"{fp.dialogue.dialogue_ratio:.0%}",
            "pov": fp.narrative.primary_pov.value,
            "tense": fp.narrative.primary_tense.value,
            "top_5_signature_words": [w for w, _ in fp.vocabulary.signature_words[:5]],
        }

    def _generate_writing_rules(self, fp: StyleFingerprint) -> list[str]:
        """Generate actionable writing rules."""
        rules = []

        # Vocabulary rules
        if fp.vocabulary.vocabulary_richness > 0.12:
            rules.append("Varier le vocabulaire : éviter de répéter le même mot dans un paragraphe")
        else:
            rules.append("Garder un vocabulaire accessible : préférer les mots courants")

        # Sentence rules
        if fp.syntax.short_sentences_ratio > 0.3:
            rules.append(f"Utiliser des phrases courtes pour le rythme : {fp.syntax.short_sentences_ratio:.0%} des phrases < 10 mots")

        if fp.syntax.long_sentences_ratio > 0.2:
            rules.append("Construire des phrases complexes avec plusieurs propositions")

        # Punctuation rules
        if fp.syntax.dash_frequency > 0.5:
            rules.append("Utiliser les tirets cadratins pour les incises et interruptions")

        if fp.syntax.semicolon_frequency > 0.5:
            rules.append("Utiliser le point-virgule pour lier des propositions indépendantes")

        # Dialogue rules
        if fp.dialogue.said_frequency > 0.5:
            rules.append("Préférer 'dit' comme verbe de dialogue principal")
        else:
            rules.append("Varier les verbes de dialogue : utiliser des alternatives expressives")

        if fp.dialogue.action_tags_ratio > 0.1:
            rules.append("Remplacer parfois les incises par des actions (sourire, hocher la tête)")

        # Narrative rules
        if fp.narrative.cliffhanger_frequency > 0.3:
            rules.append("Terminer les chapitres sur des moments de tension ou des questions")

        # Thematic rules
        if fp.thematic.tension_building_techniques:
            techniques = ", ".join(fp.thematic.tension_building_techniques)
            rules.append(f"Techniques de tension à utiliser : {techniques}")

        return rules

    def _interpret_readability(self, flesch_score: float) -> str:
        """Interpret Flesch reading ease score."""
        if flesch_score >= 80:
            return "Très facile à lire - style conversationnel"
        elif flesch_score >= 60:
            return "Facile à lire - accessible au grand public"
        elif flesch_score >= 40:
            return "Moyennement difficile - style littéraire standard"
        elif flesch_score >= 20:
            return "Difficile - style littéraire soutenu"
        else:
            return "Très difficile - style académique ou technique"

    def _describe_pov(self, pov: str) -> str:
        """Describe POV style."""
        descriptions = {
            "first_person": "Narration à la première personne (je/nous). Le lecteur vit l'histoire à travers le narrateur.",
            "third_limited": "Narration à la troisième personne limitée. On suit un personnage sans accès aux pensées des autres.",
            "third_omniscient": "Narration à la troisième personne omnisciente. Le narrateur connaît les pensées de tous.",
            "second_person": "Narration à la deuxième personne (tu/vous). Style immersif et inhabituel.",
            "mixed": "Point de vue mixte. Alternance entre plusieurs perspectives ou modes.",
        }
        return descriptions.get(pov, "Non déterminé")

    def _describe_tense(self, tense: str) -> str:
        """Describe narrative tense."""
        descriptions = {
            "past": "Temps du passé (passé simple/imparfait). Style narratif classique.",
            "present": "Présent de narration. Crée une immersion immédiate.",
            "mixed": "Temps mixtes. Utilisé pour distinguer temporalités ou niveaux narratifs.",
        }
        return descriptions.get(tense, "Non déterminé")

    def _describe_pacing(self, rhythm) -> str:
        """Describe pacing style."""
        if rhythm.action_density > rhythm.description_density * 1.5:
            return "Rythme rapide - orienté action"
        elif rhythm.description_density > rhythm.action_density * 1.5:
            return "Rythme lent - orienté description"
        else:
            return "Rythme équilibré - action et description"

    def _structure_recommendations(self, narrative) -> list[str]:
        """Generate structure recommendations."""
        recs = []

        if narrative.avg_chapter_length > 5000:
            recs.append("Chapitres longs : prévoir 4000-6000 mots par chapitre")
        elif narrative.avg_chapter_length > 2500:
            recs.append("Chapitres moyens : viser 2500-4000 mots par chapitre")
        else:
            recs.append("Chapitres courts : viser 1500-2500 mots par chapitre")

        if narrative.scene_break_frequency > 2:
            recs.append("Utiliser des sauts de scène fréquents (2-3 par chapitre)")

        if narrative.cliffhanger_frequency > 0.4:
            recs.append("Privilégier les fins de chapitre en suspens")

        return recs

    def _dialogue_recommendations(self, dialogue) -> list[str]:
        """Generate dialogue recommendations."""
        recs = []

        if dialogue.dialogue_ratio > 0.3:
            recs.append("Style dialogue-heavy : viser 30-40% de dialogue")
        elif dialogue.dialogue_ratio > 0.15:
            recs.append("Équilibre narration/dialogue : viser 15-25% de dialogue")
        else:
            recs.append("Style narratif : le dialogue accompagne, 10-15%")

        if dialogue.avg_dialogue_length < 15:
            recs.append("Dialogues courts et percutants : éviter les longues tirades")
        elif dialogue.avg_dialogue_length > 30:
            recs.append("Dialogues développés : permettre des échanges étoffés")

        return recs

    def _interpret_dialogue_ratio(self, ratio: float) -> str:
        """Interpret dialogue ratio."""
        if ratio > 0.35:
            return "Très dialogué - style théâtral ou cinématographique"
        elif ratio > 0.20:
            return "Bien dialogué - équilibre narration/dialogue"
        elif ratio > 0.10:
            return "Modérément dialogué - focus sur la narration"
        else:
            return "Peu dialogué - style introspectif ou descriptif"
