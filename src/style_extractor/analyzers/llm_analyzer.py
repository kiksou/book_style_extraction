"""LLM-powered analysis module using Claude API."""

import os
import json
from typing import Optional, Callable
from dataclasses import dataclass, field

from rich.console import Console

console = Console()


# Pricing per 1M tokens (USD) - December 2025
MODEL_PRICING = {
    # Claude 4.5 models (December 2025)
    "claude-sonnet-4-5-20250929": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 1.00, "output": 5.00},
    "claude-opus-4-5-20251101": {"input": 5.00, "output": 25.00},
    # Claude 4 models
    "claude-sonnet-4-20250514": {"input": 3.00, "output": 15.00},
    "claude-opus-4-20250514": {"input": 15.00, "output": 75.00},
    # Claude 3.5 / 3 models (legacy)
    "claude-3-5-sonnet-20241022": {"input": 3.00, "output": 15.00},
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
}


@dataclass
class APICallStats:
    """Stats for a single API call."""
    operation: str
    input_tokens: int
    output_tokens: int
    input_cost: float
    output_cost: float
    total_cost: float


@dataclass
class CostTracker:
    """Tracks API usage and costs."""
    model: str = "claude-sonnet-4-5-20250929"
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    calls: list[APICallStats] = field(default_factory=list)
    verbose: bool = True
    on_cost_update: Optional[Callable[[APICallStats], None]] = None

    def get_pricing(self) -> dict:
        """Get pricing for current model."""
        # Default to Sonnet 4.5 pricing if model not found
        return MODEL_PRICING.get(self.model, MODEL_PRICING["claude-sonnet-4-5-20250929"])

    def add_call(self, operation: str, input_tokens: int, output_tokens: int):
        """Record an API call and calculate costs."""
        pricing = self.get_pricing()

        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        call_stats = APICallStats(
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=input_cost,
            output_cost=output_cost,
            total_cost=total_cost,
        )

        self.calls.append(call_stats)
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.total_cost += total_cost

        if self.verbose:
            self._display_cost(call_stats)

        if self.on_cost_update:
            self.on_cost_update(call_stats)

    def _display_cost(self, call: APICallStats):
        """Display cost for a single call."""
        console.print(
            f"  [dim]API[/dim] {call.operation}: "
            f"[cyan]{call.input_tokens:,}[/cyan] in / "
            f"[cyan]{call.output_tokens:,}[/cyan] out = "
            f"[yellow]${call.total_cost:.4f}[/yellow] "
            f"[dim](total: ${self.total_cost:.4f})[/dim]"
        )

    def get_summary(self) -> dict:
        """Get cost summary."""
        return {
            "model": self.model,
            "total_calls": len(self.calls),
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens,
            "total_cost_usd": self.total_cost,
            "calls": [
                {
                    "operation": c.operation,
                    "input_tokens": c.input_tokens,
                    "output_tokens": c.output_tokens,
                    "cost": c.total_cost,
                }
                for c in self.calls
            ],
        }

    def display_final_summary(self):
        """Display final cost summary."""
        pricing = self.get_pricing()
        console.print("\n[bold]Coût API Claude[/bold]")
        console.print(f"  Modèle: [cyan]{self.model}[/cyan]")
        console.print(f"  Appels API: [cyan]{len(self.calls)}[/cyan]")
        console.print(
            f"  Tokens entrée: [cyan]{self.total_input_tokens:,}[/cyan] "
            f"(${pricing['input']:.2f}/1M)"
        )
        console.print(
            f"  Tokens sortie: [cyan]{self.total_output_tokens:,}[/cyan] "
            f"(${pricing['output']:.2f}/1M)"
        )
        console.print(f"  [bold yellow]Coût total: ${self.total_cost:.4f}[/bold yellow]")


@dataclass
class LLMAnalysisResult:
    """Complete results from LLM analysis."""
    # Style summary
    writing_style_summary: str = ""

    # Vocabulary
    vocabulary_level: str = ""  # rich, moderate, accessible
    vocabulary_description: str = ""
    signature_words: list[str] = field(default_factory=list)
    preferred_adjectives: list[str] = field(default_factory=list)
    preferred_verbs: list[str] = field(default_factory=list)

    # Syntax
    sentence_style: str = ""  # complex, balanced, concise
    sentence_description: str = ""
    punctuation_habits: list[str] = field(default_factory=list)

    # Rhythm
    pacing_description: str = ""
    rhythm_patterns: list[str] = field(default_factory=list)

    # Dialogue
    dialogue_style: str = ""
    dialogue_tags_preference: str = ""
    dialogue_characteristics: list[str] = field(default_factory=list)

    # Narrative
    pov_analysis: str = ""
    tense_analysis: str = ""
    narrative_techniques: list[str] = field(default_factory=list)
    chapter_structure: str = ""
    opening_patterns: list[str] = field(default_factory=list)
    ending_patterns: list[str] = field(default_factory=list)
    transition_techniques: list[str] = field(default_factory=list)

    # Thematic
    themes: list[str] = field(default_factory=list)
    motifs: list[str] = field(default_factory=list)
    symbolism: list[str] = field(default_factory=list)
    emotional_patterns: list[str] = field(default_factory=list)
    tension_techniques: list[str] = field(default_factory=list)

    # Voice
    voice_characteristics: list[str] = field(default_factory=list)
    tone_description: str = ""

    # Strengths and distinctive features
    strengths: list[str] = field(default_factory=list)
    distinctive_features: list[str] = field(default_factory=list)

    # Actionable rules
    writing_rules: list[str] = field(default_factory=list)

    # Ready-to-use prompts
    style_prompt: str = ""
    example_prompts: list[str] = field(default_factory=list)


class LLMAnalyzer:
    """Uses Claude API for comprehensive style analysis."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        verbose: bool = True,
    ):
        """
        Initialize LLM analyzer.

        Args:
            api_key: Anthropic API key. If not provided, looks for ANTHROPIC_API_KEY env var.
            model: Model to use (default: claude-sonnet-4-5-20250929)
            verbose: Display cost information in real-time
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self.verbose = verbose
        self._client = None
        self.cost_tracker = CostTracker(model=model, verbose=verbose)

    @property
    def client(self):
        """Lazy-load the Anthropic client."""
        if self._client is None:
            if not self.api_key:
                raise ValueError(
                    "API key required. Set ANTHROPIC_API_KEY environment variable "
                    "or pass api_key to LLMAnalyzer()"
                )
            try:
                from anthropic import Anthropic
                self._client = Anthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError(
                    "anthropic package required. Install with: pip install anthropic"
                )
        return self._client

    def _call_api(self, operation: str, prompt: str, max_tokens: int = 4000) -> str:
        """Make API call and track costs."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        # Track costs
        usage = response.usage
        self.cost_tracker.add_call(
            operation=operation,
            input_tokens=usage.input_tokens,
            output_tokens=usage.output_tokens,
        )

        return response.content[0].text

    def analyze_complete(self, text_sample: str, saga_name: str = "", author: str = "") -> LLMAnalysisResult:
        """
        Perform complete style analysis using Claude.

        Args:
            text_sample: Text sample to analyze
            saga_name: Name of the saga for context
            author: Author name for context

        Returns:
            LLMAnalysisResult with comprehensive analysis
        """
        # Prepare sample (truncate intelligently if needed)
        sample = self._prepare_sample(text_sample)

        context = ""
        if saga_name or author:
            context = f"\nContexte: Saga '{saga_name}' par {author}\n" if saga_name and author else ""

        prompt = f"""Tu es un expert en analyse littéraire et en style d'écriture. Analyse ce texte en profondeur pour créer une "bible d'écriture" complète qui permettra de reproduire exactement ce style.
{context}
TEXTE À ANALYSER:
---
{sample}
---

Analyse TOUS les aspects suivants et réponds en JSON structuré:

{{
    "writing_style_summary": "Résumé du style en 3-4 phrases, captant l'essence",

    "vocabulary": {{
        "level": "rich|moderate|accessible",
        "description": "Description détaillée du vocabulaire utilisé",
        "signature_words": ["mot1", "mot2", ...],
        "preferred_adjectives": ["adj1", "adj2", ...],
        "preferred_verbs": ["verbe1", "verbe2", ...]
    }},

    "syntax": {{
        "style": "complex|balanced|concise",
        "description": "Description de la structure des phrases",
        "punctuation_habits": ["habitude1", "habitude2", ...]
    }},

    "rhythm": {{
        "pacing": "Description du rythme narratif",
        "patterns": ["pattern1", "pattern2", ...]
    }},

    "dialogue": {{
        "style": "Description du style de dialogue",
        "tags_preference": "Préférence pour les incises (dit, action, varié...)",
        "characteristics": ["caractéristique1", ...]
    }},

    "narrative": {{
        "pov": "Analyse du point de vue",
        "tense": "Analyse du temps narratif",
        "techniques": ["technique1", "technique2", ...],
        "chapter_structure": "Description de la structure des chapitres",
        "opening_patterns": ["pattern d'ouverture 1", ...],
        "ending_patterns": ["pattern de fin 1", ...],
        "transitions": ["technique de transition 1", ...]
    }},

    "thematic": {{
        "themes": ["thème1", "thème2", ...],
        "motifs": ["motif récurrent 1", ...],
        "symbolism": ["élément symbolique 1", ...],
        "emotional_patterns": ["pattern émotionnel 1", ...],
        "tension_techniques": ["technique de tension 1", ...]
    }},

    "voice": {{
        "characteristics": ["caractéristique de voix 1", ...],
        "tone": "Description du ton général"
    }},

    "strengths": ["point fort 1", "point fort 2", ...],
    "distinctive_features": ["trait distinctif 1", ...],

    "writing_rules": [
        "Règle précise et actionnable 1",
        "Règle précise et actionnable 2",
        ...
    ],

    "style_prompt": "Prompt complet pour écrire dans ce style (utilisable directement avec un LLM)",

    "example_prompts": [
        "Prompt exemple pour une scène d'action",
        "Prompt exemple pour un dialogue",
        "Prompt exemple pour une description"
    ]
}}

IMPORTANT:
- Sois TRÈS précis et spécifique dans chaque analyse
- Les règles d'écriture doivent être directement applicables
- Le style_prompt doit être complet et utilisable tel quel
- Donne des exemples concrets tirés du texte quand pertinent"""

        response_text = self._call_api("Analyse complète", prompt, max_tokens=8000)
        return self._parse_response(response_text)

    def analyze_vocabulary(self, text: str) -> dict:
        """Analyze vocabulary patterns."""
        sample = self._prepare_sample(text, max_chars=30000)

        prompt = f"""Analyse le vocabulaire de ce texte:

{sample}

Réponds en JSON:
{{
    "level": "rich|moderate|accessible",
    "richness_description": "description de la richesse lexicale",
    "signature_words": ["les 20 mots les plus caractéristiques de ce style"],
    "adjectives": ["les 15 adjectifs les plus utilisés"],
    "verbs": ["les 15 verbes les plus caractéristiques"],
    "adverbs": ["les 10 adverbes fréquents"],
    "literary_words": ["mots recherchés ou littéraires utilisés"],
    "word_length_tendency": "courte|moyenne|longue",
    "register": "familier|courant|soutenu|littéraire"
}}"""

        response_text = self._call_api("Vocabulaire", prompt, max_tokens=2000)
        return self._extract_json(response_text)

    def analyze_syntax(self, text: str) -> dict:
        """Analyze sentence structure."""
        sample = self._prepare_sample(text, max_chars=30000)

        prompt = f"""Analyse la syntaxe et la structure des phrases:

{sample}

Réponds en JSON:
{{
    "sentence_style": "complex|balanced|concise",
    "average_length_impression": "courte|moyenne|longue",
    "structure_patterns": ["patterns de structure identifiés"],
    "punctuation": {{
        "semicolons": "fréquent|occasionnel|rare",
        "dashes": "fréquent|occasionnel|rare",
        "ellipsis": "fréquent|occasionnel|rare",
        "exclamations": "fréquent|occasionnel|rare"
    }},
    "paragraph_style": "description du style de paragraphe",
    "clause_complexity": "description de la complexité des propositions"
}}"""

        response_text = self._call_api("Syntaxe", prompt, max_tokens=1500)
        return self._extract_json(response_text)

    def analyze_dialogue(self, text: str) -> dict:
        """Analyze dialogue style."""
        sample = self._prepare_sample(text, max_chars=30000)

        prompt = f"""Analyse le style des dialogues:

{sample}

Réponds en JSON:
{{
    "dialogue_frequency": "fréquent|modéré|rare",
    "style": "description du style de dialogue",
    "length": "répliques courtes|moyennes|longues",
    "tags": {{
        "preference": "dit dominant|varié|actions comme tags",
        "common_tags": ["les verbes d'incise utilisés"]
    }},
    "characteristics": ["caractéristiques notables"],
    "punctuation_in_dialogue": "description",
    "internal_monologue": "fréquent|occasionnel|rare"
}}"""

        response_text = self._call_api("Dialogues", prompt, max_tokens=1500)
        return self._extract_json(response_text)

    def analyze_narrative(self, text: str, chapters: list[str] = None) -> dict:
        """Analyze narrative structure."""
        sample = self._prepare_sample(text, max_chars=30000)

        # Add chapter openings/endings if available
        chapter_info = ""
        if chapters and len(chapters) > 1:
            openings = [c[:500] for c in chapters[:5]]
            endings = [c[-500:] for c in chapters[:5]]
            chapter_info = f"\n\nDébuts de chapitres:\n" + "\n---\n".join(openings)
            chapter_info += f"\n\nFins de chapitres:\n" + "\n---\n".join(endings)

        prompt = f"""Analyse la structure narrative:

{sample}
{chapter_info}

Réponds en JSON:
{{
    "pov": {{
        "type": "première personne|troisième limitée|troisième omnisciente|mixte",
        "description": "description détaillée du POV"
    }},
    "tense": {{
        "primary": "passé|présent|mixte",
        "usage": "description de l'usage des temps"
    }},
    "techniques": ["techniques narratives identifiées"],
    "chapter_structure": "description de la structure des chapitres",
    "scene_transitions": ["techniques de transition"],
    "opening_patterns": ["patterns d'ouverture de chapitre"],
    "ending_patterns": ["patterns de fin de chapitre"],
    "pacing_techniques": ["techniques de rythme"],
    "time_handling": "description de la gestion du temps"
}}"""

        response_text = self._call_api("Structure narrative", prompt, max_tokens=2000)
        return self._extract_json(response_text)

    def analyze_themes(self, text: str) -> dict:
        """Analyze themes and motifs."""
        sample = self._prepare_sample(text, max_chars=40000)

        prompt = f"""Analyse les thèmes, motifs et éléments symboliques:

{sample}

Réponds en JSON:
{{
    "major_themes": ["thème majeur 1", "thème majeur 2", ...],
    "minor_themes": ["thème secondaire 1", ...],
    "recurring_motifs": ["motif récurrent 1", ...],
    "symbolism": [
        {{"symbol": "élément", "meaning": "signification"}},
        ...
    ],
    "emotional_arc": "description de l'arc émotionnel",
    "tension_techniques": ["technique de tension 1", ...],
    "atmosphere": "description de l'atmosphère générale"
}}"""

        response_text = self._call_api("Thèmes", prompt, max_tokens=2000)
        return self._extract_json(response_text)

    def generate_writing_rules(self, analysis: LLMAnalysisResult) -> list[str]:
        """Generate specific writing rules from analysis."""
        analysis_summary = f"""
Style: {analysis.writing_style_summary}
Vocabulaire: {analysis.vocabulary_level} - {analysis.vocabulary_description}
Syntaxe: {analysis.sentence_style} - {analysis.sentence_description}
Dialogue: {analysis.dialogue_style}
Narration: {analysis.pov_analysis}, {analysis.tense_analysis}
Techniques: {', '.join(analysis.narrative_techniques[:5])}
Traits distinctifs: {', '.join(analysis.distinctive_features[:5])}
"""

        prompt = f"""À partir de cette analyse de style, génère 15-20 règles d'écriture PRÉCISES et ACTIONNABLES:

{analysis_summary}

Les règles doivent être:
- Spécifiques (pas de généralités)
- Directement applicables
- Mesurables quand possible
- Couvrir tous les aspects (vocabulaire, syntaxe, dialogue, narration, rythme)

Réponds en JSON:
{{
    "rules": [
        "Règle 1: ...",
        "Règle 2: ...",
        ...
    ]
}}"""

        response_text = self._call_api("Règles d'écriture", prompt, max_tokens=2000)
        data = self._extract_json(response_text)
        return data.get("rules", [])

    def generate_style_prompt(self, analysis: LLMAnalysisResult) -> str:
        """Generate a comprehensive prompt for writing in this style."""
        prompt = f"""Crée un prompt COMPLET et DÉTAILLÉ pour qu'un LLM puisse écrire exactement dans ce style:

ANALYSE DU STYLE:
- Résumé: {analysis.writing_style_summary}
- Vocabulaire: {analysis.vocabulary_level} - Mots signatures: {', '.join(analysis.signature_words[:10])}
- Syntaxe: {analysis.sentence_style} - {analysis.sentence_description}
- Rythme: {analysis.pacing_description}
- Dialogue: {analysis.dialogue_style}
- POV: {analysis.pov_analysis}
- Temps: {analysis.tense_analysis}
- Techniques: {', '.join(analysis.narrative_techniques[:5])}
- Voix: {', '.join(analysis.voice_characteristics[:5])}
- Traits distinctifs: {', '.join(analysis.distinctive_features[:5])}

Génère un prompt système complet (500-800 mots) qui capture TOUS ces éléments de manière à ce qu'un LLM puisse reproduire fidèlement ce style. Le prompt doit être directement utilisable."""

        response_text = self._call_api("Génération prompt", prompt, max_tokens=2000)
        return response_text.strip()

    def _prepare_sample(self, text: str, max_chars: int = 50000) -> str:
        """Prepare text sample for analysis."""
        if len(text) <= max_chars:
            return text

        # Take beginning, middle, and end for representative sample
        chunk_size = max_chars // 3

        beginning = text[:chunk_size]
        middle_start = len(text) // 2 - chunk_size // 2
        middle = text[middle_start:middle_start + chunk_size]
        ending = text[-chunk_size:]

        return f"{beginning}\n\n[...]\n\n{middle}\n\n[...]\n\n{ending}"

    def _parse_response(self, response_text: str) -> LLMAnalysisResult:
        """Parse LLM response into structured result."""
        data = self._extract_json(response_text)

        result = LLMAnalysisResult()

        # Main summary
        result.writing_style_summary = data.get("writing_style_summary", "")

        # Vocabulary
        vocab = data.get("vocabulary", {})
        result.vocabulary_level = vocab.get("level", "")
        result.vocabulary_description = vocab.get("description", "")
        result.signature_words = vocab.get("signature_words", [])
        result.preferred_adjectives = vocab.get("preferred_adjectives", [])
        result.preferred_verbs = vocab.get("preferred_verbs", [])

        # Syntax
        syntax = data.get("syntax", {})
        result.sentence_style = syntax.get("style", "")
        result.sentence_description = syntax.get("description", "")
        result.punctuation_habits = syntax.get("punctuation_habits", [])

        # Rhythm
        rhythm = data.get("rhythm", {})
        result.pacing_description = rhythm.get("pacing", "")
        result.rhythm_patterns = rhythm.get("patterns", [])

        # Dialogue
        dialogue = data.get("dialogue", {})
        result.dialogue_style = dialogue.get("style", "")
        result.dialogue_tags_preference = dialogue.get("tags_preference", "")
        result.dialogue_characteristics = dialogue.get("characteristics", [])

        # Narrative
        narrative = data.get("narrative", {})
        result.pov_analysis = narrative.get("pov", "")
        result.tense_analysis = narrative.get("tense", "")
        result.narrative_techniques = narrative.get("techniques", [])
        result.chapter_structure = narrative.get("chapter_structure", "")
        result.opening_patterns = narrative.get("opening_patterns", [])
        result.ending_patterns = narrative.get("ending_patterns", [])
        result.transition_techniques = narrative.get("transitions", [])

        # Thematic
        thematic = data.get("thematic", {})
        result.themes = thematic.get("themes", [])
        result.motifs = thematic.get("motifs", [])
        result.symbolism = thematic.get("symbolism", [])
        result.emotional_patterns = thematic.get("emotional_patterns", [])
        result.tension_techniques = thematic.get("tension_techniques", [])

        # Voice
        voice = data.get("voice", {})
        result.voice_characteristics = voice.get("characteristics", [])
        result.tone_description = voice.get("tone", "")

        # Meta
        result.strengths = data.get("strengths", [])
        result.distinctive_features = data.get("distinctive_features", [])
        result.writing_rules = data.get("writing_rules", [])
        result.style_prompt = data.get("style_prompt", "")
        result.example_prompts = data.get("example_prompts", [])

        return result

    def _extract_json(self, text: str) -> dict:
        """Extract JSON from response text."""
        # Try to find JSON in code blocks
        if "```json" in text:
            json_str = text.split("```json")[1].split("```")[0]
        elif "```" in text:
            parts = text.split("```")
            for part in parts[1::2]:  # Odd indices are inside code blocks
                if part.strip().startswith("{"):
                    json_str = part
                    break
            else:
                json_str = text
        else:
            # Try to find JSON object directly
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                json_str = text[start:end]
            else:
                json_str = text

        try:
            return json.loads(json_str.strip())
        except json.JSONDecodeError:
            return {}
