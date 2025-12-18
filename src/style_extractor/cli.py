"""Command-line interface for the style extractor."""

import os
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel

from .core import WritingBible
from .analyzers import HAS_LLM


console = Console()


def load_env_file():
    """Load .env file if it exists."""
    env_path = Path.cwd() / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


@click.group()
@click.version_option(version="0.1.0")
def main():
    """Book Style Extractor - Extract writing style from book sagas.

    Analyze books to create a comprehensive "writing bible" that captures
    an author's style, voice, and narrative patterns.
    """
    pass


@main.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path for the writing bible (markdown)"
)
@click.option(
    "-n", "--name",
    default="Ma Saga",
    help="Name of the saga being analyzed"
)
@click.option(
    "-a", "--author",
    default="Unknown",
    help="Author name"
)
@click.option(
    "-q", "--quiet",
    is_flag=True,
    help="Suppress progress output"
)
@click.option(
    "--llm/--no-llm",
    default=False,
    help="Use Claude API to enhance local analysis"
)
@click.option(
    "--llm-only",
    is_flag=True,
    help="Use ONLY Claude API for analysis (no local analysis, better results)"
)
@click.option(
    "--api-key",
    envvar="ANTHROPIC_API_KEY",
    help="Anthropic API key (or set ANTHROPIC_API_KEY env var)"
)
@click.option(
    "--model",
    envvar="ANTHROPIC_MODEL",
    default="claude-sonnet-4-5-20250929",
    help="Claude model to use (or set ANTHROPIC_MODEL env var)"
)
def analyze(files, output, name, author, quiet, llm, llm_only, api_key, model):
    """Analyze book files and generate a writing bible.

    FILES can be one or more text files (.txt, .md, .epub) containing book content.

    Example:
        style-extractor analyze book1.epub book2.epub -o bible.md -n "My Saga"

    With LLM (recommended - best results):
        style-extractor analyze book.epub --llm-only -o bible.md

    With LLM enhancement (local + AI):
        style-extractor analyze book.epub --llm -o bible.md
    """
    load_env_file()

    if not files:
        console.print("[red]Error:[/red] No files provided. Use --help for usage.")
        sys.exit(1)

    use_ai = llm or llm_only

    if use_ai and not HAS_LLM:
        console.print("[red]Error:[/red] LLM support requires: pip install anthropic")
        sys.exit(1)

    if use_ai and not api_key:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            console.print("[red]Error:[/red] --llm/--llm-only requires API key. Use --api-key or set ANTHROPIC_API_KEY")
            sys.exit(1)

    if llm_only:
        mode = "[bold cyan]AI-only[/bold cyan]"
    elif llm:
        mode = "[cyan]AI-enhanced[/cyan]"
    else:
        mode = "[dim]local[/dim]"
    console.print(Panel.fit(
        f"[bold]Book Style Extractor[/bold]\n"
        f"Analyzing {len(files)} file(s) ({mode})",
        border_style="blue"
    ))

    try:
        bible = WritingBible(verbose=not quiet, use_llm=llm, llm_only=llm_only, api_key=api_key, model=model)
        result = bible.from_files(
            file_paths=list(files),
            saga_name=name,
            author=author,
            output_path=output,
        )

        if not output:
            # Print to stdout
            console.print("\n")
            console.print(result)

        console.print("\n[green]Analysis complete![/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path for the writing bible (markdown)"
)
@click.option(
    "-n", "--name",
    default="Ma Saga",
    help="Name of the saga being analyzed"
)
@click.option(
    "-a", "--author",
    default="Unknown",
    help="Author name"
)
@click.option(
    "-q", "--quiet",
    is_flag=True,
    help="Suppress progress output"
)
def analyze_dir(directory, output, name, author, quiet):
    """Analyze all books in a directory.

    Finds all .txt and .md files in DIRECTORY and analyzes them together.

    Example:
        style-extractor analyze-dir ./my_books -o bible.md -n "My Saga"
    """
    console.print(Panel.fit(
        f"[bold]Book Style Extractor[/bold]\n"
        f"Analyzing directory: {directory}",
        border_style="blue"
    ))

    try:
        bible = WritingBible(verbose=not quiet)
        result = bible.from_directory(
            directory=directory,
            saga_name=name,
            author=author,
            output_path=output,
        )

        if not output:
            console.print("\n")
            console.print(result)

        console.print("\n[green]Analysis complete![/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "-o", "--output",
    type=click.Path(),
    help="Output file path"
)
@click.option(
    "-n", "--name",
    default="Text",
    help="Name for the analysis"
)
def analyze_stdin(output, name):
    """Analyze text from standard input.

    Reads text from stdin and generates a writing bible.

    Example:
        cat mybook.txt | style-extractor analyze-stdin -o bible.md
    """
    console.print("[blue]Reading from stdin...[/blue]")

    text = sys.stdin.read()

    if not text.strip():
        console.print("[red]Error:[/red] No input received")
        sys.exit(1)

    try:
        bible = WritingBible(verbose=True)
        result = bible.from_text(text, saga_name=name)

        if output:
            Path(output).write_text(result, encoding="utf-8")
            console.print(f"[green]Bible saved to:[/green] {output}")
        else:
            console.print("\n")
            console.print(result)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@main.command()
def demo():
    """Run a demo analysis with sample text.

    Demonstrates the tool's capabilities using a built-in sample.
    """
    sample_text = '''
    Chapter 1: The Beginning

    The old man sat by the window, watching the rain trace silver paths down the glass.
    He had seen many storms in his long life, but none quite like this one. The wind
    howled through the streets of the ancient city, carrying whispers of change.

    "It's time," he murmured to himself, his weathered hands gripping the armrests
    of his chair. "After all these years, it's finally time."

    Sarah burst through the door, her dark hair plastered to her face, her eyes wild
    with a mixture of fear and excitement. She was young, barely twenty, but she
    carried herself with the weight of someone who had seen too much.

    "Grand-père!" she called out, breathless. "They're coming. The Council... they
    know about the artifact."

    The old man smiled, a slow, knowing smile that crinkled the corners of his eyes.
    "Let them come," he said softly. "We've been preparing for this moment for
    three generations."

    * * *

    Chapter 2: Revelations

    Dawn broke over the mountains, painting the sky in shades of gold and crimson.
    Sarah hadn't slept. How could she, knowing what awaited them? She stood on the
    balcony of the old house, her grandfather's house, and tried to make sense of
    everything she had learned.

    The artifact. The prophecy. The war that had shaped her family's destiny for
    a hundred years.

    "You look troubled," came a voice from behind her.

    She didn't turn around. She knew that voice—deep, melodious, touched with an
    accent she couldn't quite place. Marcus. Her grandfather's mysterious associate.

    "Wouldn't you be?" she replied. "Yesterday I was a normal graduate student.
    Today I'm supposedly the key to preventing the end of the world."

    Marcus laughed softly. "Normal. What a curious word. Tell me, Sarah, did you
    ever truly feel normal?"

    The question struck her harder than she expected. No. The answer was no. She had
    always known she was different. The dreams. The visions. The way she could
    sometimes sense things before they happened.

    "The power has always been in you," Marcus continued, stepping closer. "Your
    grandfather merely protected you from those who would exploit it."
    '''

    console.print(Panel.fit(
        "[bold]Book Style Extractor - Demo[/bold]\n"
        "Analyzing sample text...",
        border_style="blue"
    ))

    try:
        bible = WritingBible(verbose=True)
        result = bible.from_text(sample_text, saga_name="Demo Saga", author="Sample Author")

        console.print("\n")
        console.print(result)
        console.print("\n[green]Demo complete![/green]")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
