"""Markdown rendering for writing bible output."""

from typing import Any
from datetime import datetime


class MarkdownRenderer:
    """Renders the writing bible as markdown."""

    def __init__(self):
        pass

    def render(self, bible: dict[str, Any]) -> str:
        """Render complete bible to markdown."""
        sections = [
            self._render_header(bible["metadata"]),
            self._render_quick_reference(bible["quick_reference"]),
            self._render_style_guide(bible["style_guide"]),
            self._render_voice_guide(bible["voice_guide"]),
            self._render_structure_guide(bible["structure_guide"]),
            self._render_dialogue_guide(bible["dialogue_guide"]),
            self._render_thematic_guide(bible["thematic_guide"]),
            self._render_writing_rules(bible["writing_rules"]),
            self._render_examples(bible.get("examples", {})),
        ]

        # Add LLM analysis if present
        if "llm_analysis" in bible:
            sections.append(self._render_llm_analysis(bible["llm_analysis"]))

        return "\n\n---\n\n".join(filter(None, sections))

    def _render_llm_analysis(self, llm: dict) -> str:
        """Render LLM-enhanced analysis section."""
        techniques = "\n".join(f"- {t}" for t in llm.get("narrative_techniques", []))
        voice = "\n".join(f"- {v}" for v in llm.get("voice_characteristics", []))
        themes = ", ".join(llm.get("themes", []))
        strengths = "\n".join(f"- {s}" for s in llm.get("strengths", []))
        features = "\n".join(f"- {f}" for f in llm.get("distinctive_features", []))
        rules = "\n".join(f"{i+1}. {r}" for i, r in enumerate(llm.get("writing_rules", [])))

        return f"""## Analyse LLM (Claude)

### Résumé du Style

{llm.get('summary', 'N/A')}

### Techniques Narratives

{techniques or 'N/A'}

### Caractéristiques de la Voix

{voice or 'N/A'}

### Style de Dialogue

{llm.get('dialogue_style', 'N/A')}

### Rythme et Pacing

{llm.get('pacing', 'N/A')}

### Thèmes Identifiés

{themes or 'N/A'}

### Points Forts

{strengths or 'N/A'}

### Traits Distinctifs

{features or 'N/A'}

### Règles d'Écriture (par LLM)

{rules or 'N/A'}

---

## Prompt pour Écrire dans ce Style

Utilisez ce prompt avec un LLM pour générer du texte dans le même style :

```
{llm.get('style_prompt', 'N/A')}
```"""

    def _render_header(self, metadata: dict) -> str:
        """Render document header."""
        date = metadata.get("analysis_date") or datetime.now().strftime("%Y-%m-%d")

        return f"""# Bible d'Ecriture : {metadata['saga_name']}

**Auteur analysé** : {metadata['author']}
**Livres analysés** : {', '.join(metadata['books_analyzed'])}
**Mots analysés** : {metadata['total_words_analyzed']:,}
**Date d'analyse** : {date}

> Ce document capture le style d'écriture et les patterns narratifs extraits de la saga analysée.
> Utilisez-le comme guide pour écrire dans un style similaire."""

    def _render_quick_reference(self, qr: dict) -> str:
        """Render quick reference card."""
        return f"""## Carte de Référence Rapide

| Élément | Cible |
|---------|-------|
| Longueur de phrase | {qr['sentence_length_target']} |
| Longueur de paragraphe | {qr['paragraph_length_target']} |
| Longueur de chapitre | {qr['chapter_length_target']} |
| Ratio de dialogue | {qr['dialogue_ratio_target']} |
| Point de vue | {qr['pov']} |
| Temps narratif | {qr['tense']} |

**Mots signature à utiliser** : {', '.join(qr['top_5_signature_words'])}"""

    def _render_style_guide(self, style: dict) -> str:
        """Render style guide section."""
        vocab = style["vocabulary"]
        sentences = style["sentences"]
        punct = style["punctuation"]
        para = style["paragraphs"]
        read = style["readability"]

        signature_words = ", ".join(vocab["signature_words"][:15])
        adj_list = ", ".join(vocab["preferred_adjectives"][:10])
        verb_list = ", ".join(vocab["preferred_verbs"][:10])

        return f"""## Guide de Style

### Vocabulaire

**Niveau** : {vocab['level'].upper()}
{vocab['description']}

- **Richesse lexicale** : {vocab['richness_score']} (ratio types/tokens)
- **Longueur moyenne des mots** : {vocab['avg_word_length']} caractères

**Mots signatures** (caractéristiques de ce style) :
> {signature_words}

**Adjectifs préférés** :
> {adj_list}

**Verbes préférés** :
> {verb_list}

### Structure des Phrases

**Style** : {sentences['style'].upper()}
{sentences['description']}

- **Longueur moyenne** : {sentences['avg_length']} mots
- **Distribution** :
  - Phrases courtes (<10 mots) : {sentences['length_distribution']['short']}
  - Phrases moyennes (10-25 mots) : {sentences['length_distribution']['medium']}
  - Phrases longues (>25 mots) : {sentences['length_distribution']['long']}

### Ponctuation

- Point-virgule : {'Utilisation fréquente' if punct['uses_semicolons'] else 'Utilisation rare'}
- Tirets : {'Utilisation fréquente' if punct['uses_dashes'] else 'Utilisation rare'}
- Points de suspension : {'Utilisation fréquente' if punct['uses_ellipsis'] else 'Utilisation rare'}
- Points d'exclamation : {punct['exclamation_frequency']}

### Paragraphes

- **Longueur moyenne** : {para['avg_length_words']:.0f} mots
- **Phrases par paragraphe** : {para['avg_sentences']}

### Lisibilité

- **Score Flesch** : {read['flesch_ease']} ({read['interpretation']})
- **Niveau scolaire** : {read['grade_level']}"""

    def _render_voice_guide(self, voice: dict) -> str:
        """Render voice guide section."""
        pov = voice["point_of_view"]
        tense = voice["tense"]
        rhythm = voice["rhythm"]
        trans = voice["transitions"]

        transition_words = ", ".join(trans["common_words"][:8])
        time_patterns = ", ".join(trans["time_skip_patterns"][:5]) if trans["time_skip_patterns"] else "N/A"

        return f"""## Guide de la Voix Narrative

### Point de Vue

**Principal** : {pov['primary'].upper()}
{pov['description']}

### Temps Narratif

**Principal** : {tense['primary'].upper()}
{tense['description']}

### Rythme

- **Variété** : {rhythm['variety_score']} (0 = monotone, 1 = très varié)
- **Style de rythme** : {rhythm['pacing']}
- **Densité d'action** : {rhythm['action_density']} verbes/phrase
- **Densité descriptive** : {rhythm['description_density']} adj/phrase

### Transitions

**Mots de transition courants** :
> {transition_words}

**Patterns de saut temporel** :
> {time_patterns}"""

    def _render_structure_guide(self, structure: dict) -> str:
        """Render structure guide section."""
        chapters = structure["chapters"]
        scenes = structure["scenes"]
        recs = structure["recommendations"]

        openings = ", ".join(chapters["opening_styles"][:3]) if chapters["opening_styles"] else "N/A"
        endings = f"Cliffhangers : {chapters['cliffhanger_frequency']}"

        rec_list = "\n".join(f"- {r}" for r in recs)

        return f"""## Guide de Structure

### Chapitres

- **Longueur moyenne** : {chapters['avg_length']:.0f} mots
- **Variation** : ±{chapters['variance']:.0f} mots
- **Styles d'ouverture** : {openings}
- **Style de fin** : {endings}

### Scènes

- **Longueur moyenne** : {scenes['avg_length']:.0f} mots
- **Fréquence des changements** : {scenes['frequency_per_1k_words']} par 1000 mots

### Recommandations

{rec_list}"""

    def _render_dialogue_guide(self, dialogue: dict) -> str:
        """Render dialogue guide section."""
        freq = dialogue["frequency"]
        style = dialogue["style"]
        mono = dialogue["internal_monologue"]
        recs = dialogue["recommendations"]

        tags = ", ".join(style["tag_variety"][:10])
        rec_list = "\n".join(f"- {r}" for r in recs)

        return f"""## Guide des Dialogues

### Fréquence

- **Ratio** : {freq['ratio']}
- **Interprétation** : {freq['interpretation']}

### Style

- **Longueur moyenne** : {style['avg_length']:.0f} mots par réplique
- **Usage de 'dit'** : {style['said_usage']} des incises
- **Actions comme incises** : {'Oui' if style['uses_action_tags'] else 'Non'}

**Verbes d'incise variés** :
> {tags}

### Monologue Intérieur

- **Fréquence** : {mono['frequency']}

### Recommandations

{rec_list}"""

    def _render_thematic_guide(self, thematic: dict) -> str:
        """Render thematic guide section."""
        themes = "\n".join(
            f"- **{t['theme'].title()}** : {t['prominence']:.1f}/10k mots"
            for t in thematic["major_themes"]
        )

        motifs = "\n".join(
            f"- {m['motif'].replace('_', ' ').title()} ({m['occurrences']} occurrences)"
            for m in thematic["recurring_motifs"]
        )

        symbols = "\n".join(
            f"- **{s['symbol'].title()}** : {s['meaning']}"
            for s in thematic["symbolism"]
        )

        arc = " → ".join(thematic["emotional_arc"]) if thematic["emotional_arc"] else "N/A"
        techniques = ", ".join(thematic["tension_techniques"]) if thematic["tension_techniques"] else "Aucune détectée"

        return f"""## Guide Thématique

### Thèmes Majeurs

{themes or 'Aucun thème dominant détecté'}

### Motifs Récurrents

{motifs or 'Aucun motif récurrent détecté'}

### Symbolisme

{symbols or 'Aucun symbole récurrent détecté'}

### Arc Émotionnel

> {arc}

### Techniques de Tension

> {techniques}"""

    def _render_writing_rules(self, rules: list[str]) -> str:
        """Render writing rules section."""
        if not rules:
            return ""

        rule_list = "\n".join(f"{i+1}. {rule}" for i, rule in enumerate(rules))

        return f"""## Règles d'Écriture

Ces règles sont dérivées de l'analyse du style :

{rule_list}"""

    def _render_examples(self, examples: dict[str, list[str]]) -> str:
        """Render example passages section."""
        if not examples:
            return ""

        sections = []
        for category, passages in examples.items():
            if passages:
                passage_md = "\n\n".join(f"> {p[:300]}..." if len(p) > 300 else f"> {p}" for p in passages[:3])
                sections.append(f"### {category.replace('_', ' ').title()}\n\n{passage_md}")

        if not sections:
            return ""

        return f"""## Exemples de Passages

{chr(10).join(sections)}"""
