"""LLM-enhanced analysis module using Claude API."""

import os
import json
from typing import Optional
from dataclasses import dataclass


@dataclass
class LLMAnalysisResult:
    """Results from LLM analysis."""
    writing_style_summary: str
    narrative_techniques: list[str]
    voice_characteristics: list[str]
    dialogue_style: str
    pacing_description: str
    themes: list[str]
    strengths: list[str]
    distinctive_features: list[str]
    writing_rules: list[str]
    example_prompts: list[str]


class LLMAnalyzer:
    """Uses Claude API for deep style analysis."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-20250514"):
        """
        Initialize LLM analyzer.

        Args:
            api_key: Anthropic API key. If not provided, looks for ANTHROPIC_API_KEY env var.
            model: Model to use (default: claude-sonnet-4-20250514)
        """
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.model = model
        self._client = None

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

    def analyze_style(self, text_sample: str, max_tokens: int = 4096) -> LLMAnalysisResult:
        """
        Analyze writing style using Claude.

        Args:
            text_sample: Text sample to analyze (will be truncated if too long)
            max_tokens: Max tokens for response

        Returns:
            LLMAnalysisResult with detailed analysis
        """
        # Truncate sample if needed (keep ~50k chars for context)
        if len(text_sample) > 50000:
            # Take beginning, middle, and end
            chunk_size = 15000
            sample = (
                text_sample[:chunk_size] +
                "\n\n[...]\n\n" +
                text_sample[len(text_sample)//2 - chunk_size//2:len(text_sample)//2 + chunk_size//2] +
                "\n\n[...]\n\n" +
                text_sample[-chunk_size:]
            )
        else:
            sample = text_sample

        prompt = f"""Analyse le style d'écriture de ce texte en détail. Je veux créer une "bible d'écriture" pour pouvoir écrire dans le même style.

TEXTE À ANALYSER:
---
{sample}
---

Réponds en JSON avec cette structure exacte:
{{
    "writing_style_summary": "Description générale du style en 2-3 phrases",
    "narrative_techniques": ["technique1", "technique2", ...],
    "voice_characteristics": ["caractéristique1", "caractéristique2", ...],
    "dialogue_style": "Description du style de dialogue",
    "pacing_description": "Description du rythme narratif",
    "themes": ["thème1", "thème2", ...],
    "strengths": ["point fort 1", "point fort 2", ...],
    "distinctive_features": ["trait distinctif 1", "trait distinctif 2", ...],
    "writing_rules": [
        "Règle 1: ...",
        "Règle 2: ...",
        ...
    ],
    "example_prompts": [
        "Prompt pour générer du texte dans ce style 1",
        "Prompt pour générer du texte dans ce style 2"
    ]
}}

Sois précis et actionnable dans les règles d'écriture. L'objectif est de pouvoir reproduire ce style."""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse JSON response
        response_text = response.content[0].text

        # Extract JSON from response (handle markdown code blocks)
        if "```json" in response_text:
            json_str = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            json_str = response_text.split("```")[1].split("```")[0]
        else:
            json_str = response_text

        try:
            data = json.loads(json_str.strip())
        except json.JSONDecodeError:
            # Fallback: try to extract what we can
            data = {
                "writing_style_summary": response_text[:500],
                "narrative_techniques": [],
                "voice_characteristics": [],
                "dialogue_style": "",
                "pacing_description": "",
                "themes": [],
                "strengths": [],
                "distinctive_features": [],
                "writing_rules": [],
                "example_prompts": [],
            }

        return LLMAnalysisResult(
            writing_style_summary=data.get("writing_style_summary", ""),
            narrative_techniques=data.get("narrative_techniques", []),
            voice_characteristics=data.get("voice_characteristics", []),
            dialogue_style=data.get("dialogue_style", ""),
            pacing_description=data.get("pacing_description", ""),
            themes=data.get("themes", []),
            strengths=data.get("strengths", []),
            distinctive_features=data.get("distinctive_features", []),
            writing_rules=data.get("writing_rules", []),
            example_prompts=data.get("example_prompts", []),
        )

    def analyze_chapter_style(self, chapter_text: str) -> dict:
        """Analyze a single chapter for style elements."""
        prompt = f"""Analyse ce chapitre et extrais les éléments de style:

{chapter_text[:10000]}

Réponds en JSON:
{{
    "opening_technique": "comment le chapitre commence",
    "closing_technique": "comment il se termine",
    "dominant_mood": "ambiance dominante",
    "pov_consistency": "cohérence du point de vue",
    "tension_level": "niveau de tension (1-10)",
    "dialogue_narrative_ratio": "estimation du ratio dialogue/narration",
    "notable_techniques": ["technique1", ...]
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text

        try:
            if "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
            else:
                json_str = response_text
            return json.loads(json_str.strip())
        except (json.JSONDecodeError, IndexError):
            return {}

    def generate_style_prompt(self, analysis_result: LLMAnalysisResult) -> str:
        """Generate a prompt that can be used to write in this style."""
        rules = "\n".join(f"- {rule}" for rule in analysis_result.writing_rules)
        features = ", ".join(analysis_result.distinctive_features)
        techniques = ", ".join(analysis_result.narrative_techniques)

        return f"""Tu es un écrivain qui maîtrise ce style d'écriture:

STYLE: {analysis_result.writing_style_summary}

CARACTÉRISTIQUES DE LA VOIX:
{chr(10).join(f'- {v}' for v in analysis_result.voice_characteristics)}

TECHNIQUES NARRATIVES: {techniques}

STYLE DE DIALOGUE: {analysis_result.dialogue_style}

RYTHME: {analysis_result.pacing_description}

TRAITS DISTINCTIFS: {features}

RÈGLES D'ÉCRITURE À SUIVRE:
{rules}

Écris dans ce style exact. Maintiens la cohérence de la voix, du rythme et des techniques tout au long du texte."""
