"""Style analyzers for different aspects of writing."""

from .vocabulary import VocabularyAnalyzer
from .syntax import SyntaxAnalyzer
from .rhythm import RhythmAnalyzer
from .dialogue import DialogueAnalyzer
from .narrative import NarrativeAnalyzer
from .thematic import ThematicAnalyzer

# Optional LLM analyzer (requires anthropic package)
try:
    from .llm_analyzer import LLMAnalyzer, LLMAnalysisResult
    HAS_LLM = True
except ImportError:
    HAS_LLM = False
    LLMAnalyzer = None
    LLMAnalysisResult = None

__all__ = [
    "VocabularyAnalyzer",
    "SyntaxAnalyzer",
    "RhythmAnalyzer",
    "DialogueAnalyzer",
    "NarrativeAnalyzer",
    "ThematicAnalyzer",
    "LLMAnalyzer",
    "LLMAnalysisResult",
    "HAS_LLM",
]
