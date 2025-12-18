"""Core module tying together all analysis components."""

import re
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .models import (
    Book, Chapter, AnalysisResult, StyleFingerprint,
    VocabularyProfile, SyntaxProfile, RhythmProfile,
    DialogueProfile, NarrativeProfile, ThematicProfile,
)
from .analyzers import (
    VocabularyAnalyzer, SyntaxAnalyzer, RhythmAnalyzer,
    DialogueAnalyzer, NarrativeAnalyzer, ThematicAnalyzer,
)
from .extractors import TextLoader, ChapterSplitter
from .generators import BibleGenerator, MarkdownRenderer


console = Console()


class StyleExtractor:
    """Main class for extracting writing style from books."""

    def __init__(self, verbose: bool = True):
        self.verbose = verbose

        # Initialize analyzers
        self.vocab_analyzer = VocabularyAnalyzer()
        self.syntax_analyzer = SyntaxAnalyzer()
        self.rhythm_analyzer = RhythmAnalyzer()
        self.dialogue_analyzer = DialogueAnalyzer()
        self.narrative_analyzer = NarrativeAnalyzer()
        self.thematic_analyzer = ThematicAnalyzer()

        # Initialize extractors
        self.text_loader = TextLoader()
        self.chapter_splitter = ChapterSplitter()

    def load_books(self, paths: list[str | Path]) -> list[Book]:
        """Load books from file paths."""
        books = []

        for i, path in enumerate(paths):
            path = Path(path)

            if self.verbose:
                console.print(f"[blue]Loading[/blue] {path.name}...")

            try:
                content = self.text_loader.load_file(path)
                content = self.text_loader.clean_text(content)

                # Split into chapters
                chapter_infos = self.chapter_splitter.split_chapters(content)
                chapters = [
                    Chapter(
                        number=ci.number,
                        title=ci.title,
                        content=ci.content,
                    )
                    for ci in chapter_infos
                ]

                # Extract metadata from EPUB if available
                title = path.stem.replace("_", " ").replace("-", " ").title()
                author = "Unknown"

                if path.suffix.lower() == ".epub":
                    metadata = self.text_loader.get_epub_metadata(path)
                    if metadata.get("title"):
                        title = metadata["title"]
                    if metadata.get("author"):
                        author = metadata["author"]
                    if self.verbose and metadata.get("author"):
                        console.print(f"  [dim]Author: {author}[/dim]")

                book = Book(
                    title=title,
                    author=author,
                    content=content,
                    chapters=chapters,
                    file_path=path,
                    order_in_saga=i + 1,
                )

                books.append(book)

                if self.verbose:
                    console.print(
                        f"  [green]OK[/green] - {book.word_count:,} mots, "
                        f"{len(chapters)} chapitres"
                    )

            except Exception as e:
                console.print(f"  [red]Erreur[/red]: {e}")

        return books

    def analyze(
        self,
        books: list[Book],
        saga_name: str = "Saga",
        author: str = "Unknown",
    ) -> AnalysisResult:
        """Perform complete style analysis on a list of books."""
        if not books:
            raise ValueError("No books to analyze")

        # Combine all text
        all_text = "\n\n".join(book.content for book in books)
        all_chapters = []
        for book in books:
            all_chapters.extend([c.content for c in book.chapters])

        total_words = sum(book.word_count for book in books)

        if self.verbose:
            console.print(f"\n[bold]Analysing {len(books)} livre(s)...[/bold]")
            console.print(f"Total: {total_words:,} mots\n")

        # Run all analyses
        fingerprint = StyleFingerprint()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            disable=not self.verbose,
        ) as progress:
            # Vocabulary analysis
            task = progress.add_task("Analyse du vocabulaire...", total=None)
            fingerprint.vocabulary = self.vocab_analyzer.analyze(all_text)
            progress.update(task, completed=True)

            # Syntax analysis
            task = progress.add_task("Analyse syntaxique...", total=None)
            fingerprint.syntax = self.syntax_analyzer.analyze(all_text)
            progress.update(task, completed=True)

            # Rhythm analysis
            task = progress.add_task("Analyse du rythme...", total=None)
            fingerprint.rhythm = self.rhythm_analyzer.analyze(all_text)
            progress.update(task, completed=True)

            # Dialogue analysis
            task = progress.add_task("Analyse des dialogues...", total=None)
            fingerprint.dialogue = self.dialogue_analyzer.analyze(all_text)
            progress.update(task, completed=True)

            # Narrative analysis
            task = progress.add_task("Analyse narrative...", total=None)
            fingerprint.narrative = self.narrative_analyzer.analyze(all_text, all_chapters)
            progress.update(task, completed=True)

            # Thematic analysis
            task = progress.add_task("Analyse thématique...", total=None)
            fingerprint.thematic = self.thematic_analyzer.analyze(all_text, all_chapters)
            progress.update(task, completed=True)

        # Extract example passages
        examples = self._extract_examples(books, fingerprint)

        # Create result
        result = AnalysisResult(
            saga_name=saga_name,
            author=author,
            books_analyzed=[book.title for book in books],
            total_words=total_words,
            fingerprint=fingerprint,
            example_passages=examples,
        )

        return result

    def _extract_examples(
        self,
        books: list[Book],
        fingerprint: StyleFingerprint,
    ) -> dict[str, list[str]]:
        """Extract representative example passages."""
        examples = {
            "dialogue": [],
            "description": [],
            "action": [],
            "opening": [],
            "transition": [],
        }

        all_text = "\n\n".join(book.content for book in books)

        # Dialogue examples
        dialogue_samples = self.dialogue_analyzer.get_dialogue_samples(all_text, 5)
        examples["dialogue"] = dialogue_samples.get("medium_dialogues", [])[:5]

        # Description examples (passages with many adjectives)
        paragraphs = re.split(r'\n\s*\n', all_text)
        for para in paragraphs[:100]:
            if len(para) > 100 and len(para) < 500:
                adj_count = sum(1 for word in para.lower().split()
                              if word.endswith(('eux', 'euse', 'ful', 'ous', 'ive')))
                if adj_count > 3:
                    examples["description"].append(para)
                    if len(examples["description"]) >= 3:
                        break

        # Action examples (short, verb-heavy sentences)
        sentences = re.split(r'[.!?]+', all_text)
        for sent in sentences[:200]:
            sent = sent.strip()
            if 20 < len(sent) < 150:
                words = sent.lower().split()
                verb_endings = ('ed', 'ing', 'ait', 'rent', 'ut', 'it')
                verb_count = sum(1 for w in words if w.endswith(verb_endings))
                if verb_count >= 2 and len(words) < 15:
                    examples["action"].append(sent)
                    if len(examples["action"]) >= 5:
                        break

        # Chapter openings
        for book in books[:3]:
            for chapter in book.chapters[:3]:
                first_para = chapter.content.split('\n\n')[0][:300]
                if first_para:
                    examples["opening"].append(first_para)

        # Transition examples
        transition_patterns = [
            r'([^.]*(?:Plus tard|Le lendemain|Days later|Meanwhile)[^.]*\.)',
            r'([^.]*(?:soudain|suddenly|alors)[^.]*\.)',
        ]
        for pattern in transition_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            examples["transition"].extend(matches[:3])

        return examples


class WritingBible:
    """High-level interface for generating writing bibles."""

    def __init__(
        self,
        verbose: bool = True,
        use_llm: bool = False,
        api_key: Optional[str] = None,
    ):
        self.extractor = StyleExtractor(verbose=verbose)
        self.generator = BibleGenerator()
        self.renderer = MarkdownRenderer()
        self.verbose = verbose
        self.use_llm = use_llm
        self.api_key = api_key
        self.llm_analyzer = None

        if use_llm:
            from .analyzers import LLMAnalyzer
            self.llm_analyzer = LLMAnalyzer(api_key=api_key)

    def from_files(
        self,
        file_paths: list[str | Path],
        saga_name: str = "Ma Saga",
        author: str = "Auteur",
        output_path: Optional[str | Path] = None,
    ) -> str:
        """Generate writing bible from book files."""
        # Load books
        books = self.extractor.load_books(file_paths)

        if not books:
            raise ValueError("No books could be loaded")

        # Analyze
        result = self.extractor.analyze(books, saga_name, author)

        # Generate bible
        bible = self.generator.generate(result)

        # Add LLM analysis if enabled
        if self.use_llm and self.llm_analyzer:
            if self.verbose:
                console.print("\n[cyan]Running LLM analysis...[/cyan]")

            all_text = "\n\n".join(book.content for book in books)
            llm_result = self.llm_analyzer.analyze_style(all_text)

            # Add LLM insights to bible
            bible["llm_analysis"] = {
                "summary": llm_result.writing_style_summary,
                "narrative_techniques": llm_result.narrative_techniques,
                "voice_characteristics": llm_result.voice_characteristics,
                "dialogue_style": llm_result.dialogue_style,
                "pacing": llm_result.pacing_description,
                "themes": llm_result.themes,
                "strengths": llm_result.strengths,
                "distinctive_features": llm_result.distinctive_features,
                "writing_rules": llm_result.writing_rules,
                "style_prompt": self.llm_analyzer.generate_style_prompt(llm_result),
            }

        # Render to markdown
        markdown = self.renderer.render(bible)

        # Save if path provided
        if output_path:
            output_path = Path(output_path)
            output_path.write_text(markdown, encoding="utf-8")

            if self.verbose:
                console.print(f"\n[green]Bible sauvegardée[/green] : {output_path}")

        return markdown

    def from_directory(
        self,
        directory: str | Path,
        saga_name: str = "Ma Saga",
        author: str = "Auteur",
        output_path: Optional[str | Path] = None,
    ) -> str:
        """Generate writing bible from all books in a directory."""
        directory = Path(directory)

        # Find all supported files
        files = (
            list(directory.glob("*.txt")) +
            list(directory.glob("*.md")) +
            list(directory.glob("*.epub"))
        )
        files = sorted(files)

        if not files:
            raise ValueError(f"No text files found in {directory}")

        return self.from_files(files, saga_name, author, output_path)

    def from_text(
        self,
        text: str,
        saga_name: str = "Texte",
        author: str = "Auteur",
    ) -> str:
        """Generate writing bible from raw text."""
        # Create a temporary book
        book = Book(
            title=saga_name,
            author=author,
            content=text,
        )

        # Analyze
        result = self.extractor.analyze([book], saga_name, author)

        # Generate bible
        bible = self.generator.generate(result)

        # Add LLM analysis if enabled
        if self.use_llm and self.llm_analyzer:
            llm_result = self.llm_analyzer.analyze_style(text)
            bible["llm_analysis"] = {
                "summary": llm_result.writing_style_summary,
                "narrative_techniques": llm_result.narrative_techniques,
                "voice_characteristics": llm_result.voice_characteristics,
                "dialogue_style": llm_result.dialogue_style,
                "pacing": llm_result.pacing_description,
                "themes": llm_result.themes,
                "strengths": llm_result.strengths,
                "distinctive_features": llm_result.distinctive_features,
                "writing_rules": llm_result.writing_rules,
                "style_prompt": self.llm_analyzer.generate_style_prompt(llm_result),
            }

        # Render to markdown
        return self.renderer.render(bible)
