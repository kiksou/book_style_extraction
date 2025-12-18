"""
Book Style Extractor - Extract writing style and narrative patterns from book sagas.

This tool analyzes books to create a comprehensive "writing bible" that captures:
- Vocabulary patterns and word choices
- Sentence structure and rhythm
- Narrative techniques and POV handling
- Character voice differentiation
- Thematic patterns
- Dialogue style
"""

__version__ = "0.1.0"

from .core import StyleExtractor, WritingBible
from .models import Book, Chapter, AnalysisResult

__all__ = ["StyleExtractor", "WritingBible", "Book", "Chapter", "AnalysisResult"]
