"""Chapter and scene splitting module."""

import re
from dataclasses import dataclass


@dataclass
class ChapterInfo:
    """Information about a detected chapter."""
    number: int
    title: str
    content: str
    start_pos: int
    end_pos: int


class ChapterSplitter:
    """Splits books into chapters and scenes."""

    # Common chapter heading patterns
    CHAPTER_PATTERNS = [
        # English patterns
        r'^(?:CHAPTER|Chapter|CHAPITRE|Chapitre)\s+(\d+|[IVXLCDM]+)(?:\s*[:\-—]\s*(.+))?$',
        r'^(?:CHAPTER|Chapter|CHAPITRE|Chapitre)\s+([A-Za-z]+)(?:\s*[:\-—]\s*(.+))?$',
        r'^(\d+|[IVXLCDM]+)\s*[:\-—.]\s*(.+)$',
        r'^(\d+)\s*$',  # Just a number on its own line
        # French patterns
        r'^(?:Chapitre|CHAPITRE)\s+(\d+|premier|deuxième|troisième|[IVXLCDM]+)(?:\s*[:\-—]\s*(.+))?$',
        # Part/Book patterns
        r'^(?:PART|Part|PARTIE|Partie|BOOK|Book|LIVRE|Livre)\s+(\d+|[IVXLCDM]+)(?:\s*[:\-—]\s*(.+))?$',
    ]

    # Scene break patterns
    SCENE_BREAK_PATTERNS = [
        r'\n\s*\*\s*\*\s*\*\s*\n',
        r'\n\s*#\s*#\s*#\s*\n',
        r'\n\s*~\s*~\s*~\s*\n',
        r'\n\s*-\s*-\s*-\s*\n',
        r'\n\s*\* \* \*\s*\n',
        r'\n{4,}',  # Multiple blank lines
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p, re.MULTILINE | re.IGNORECASE) for p in self.CHAPTER_PATTERNS]

    def split_chapters(self, text: str) -> list[ChapterInfo]:
        """Split text into chapters."""
        chapters = []

        # Find all chapter headings
        headings = self._find_headings(text)

        if not headings:
            # No chapters found, treat entire text as one chapter
            return [ChapterInfo(
                number=1,
                title="",
                content=text,
                start_pos=0,
                end_pos=len(text),
            )]

        # Extract chapter content between headings
        for i, heading in enumerate(headings):
            start_pos = heading["pos"]
            end_pos = headings[i + 1]["pos"] if i + 1 < len(headings) else len(text)

            content = text[start_pos:end_pos]
            # Remove the heading from content
            content = re.sub(r'^[^\n]+\n', '', content, count=1).strip()

            chapters.append(ChapterInfo(
                number=heading["number"],
                title=heading["title"],
                content=content,
                start_pos=start_pos,
                end_pos=end_pos,
            ))

        return chapters

    def _find_headings(self, text: str) -> list[dict]:
        """Find all chapter headings in text."""
        headings = []

        lines = text.split('\n')
        pos = 0

        for line in lines:
            stripped = line.strip()
            if stripped:
                for pattern in self.compiled_patterns:
                    match = pattern.match(stripped)
                    if match:
                        groups = match.groups()
                        number = self._parse_number(groups[0]) if groups else len(headings) + 1
                        title = groups[1].strip() if len(groups) > 1 and groups[1] else ""

                        headings.append({
                            "pos": pos,
                            "number": number,
                            "title": title,
                            "raw": stripped,
                        })
                        break

            pos += len(line) + 1  # +1 for newline

        return headings

    def _parse_number(self, num_str: str) -> int:
        """Parse chapter number from string."""
        if not num_str:
            return 0

        # Try as integer
        try:
            return int(num_str)
        except ValueError:
            pass

        # Try as Roman numeral
        roman_values = {
            'I': 1, 'V': 5, 'X': 10, 'L': 50,
            'C': 100, 'D': 500, 'M': 1000
        }
        num_str_upper = num_str.upper()

        if all(c in roman_values for c in num_str_upper):
            total = 0
            prev = 0
            for char in reversed(num_str_upper):
                curr = roman_values[char]
                if curr < prev:
                    total -= curr
                else:
                    total += curr
                prev = curr
            return total

        # Word numbers (French)
        word_numbers = {
            "premier": 1, "première": 1, "un": 1, "une": 1,
            "deuxième": 2, "second": 2, "seconde": 2, "deux": 2,
            "troisième": 3, "trois": 3,
            "quatrième": 4, "quatre": 4,
            "cinquième": 5, "cinq": 5,
            "sixième": 6, "six": 6,
            "septième": 7, "sept": 7,
            "huitième": 8, "huit": 8,
            "neuvième": 9, "neuf": 9,
            "dixième": 10, "dix": 10,
        }

        lower = num_str.lower()
        if lower in word_numbers:
            return word_numbers[lower]

        return 0

    def split_scenes(self, text: str) -> list[str]:
        """Split text into scenes."""
        combined_pattern = '|'.join(self.SCENE_BREAK_PATTERNS)
        scenes = re.split(combined_pattern, text)
        return [s.strip() for s in scenes if s.strip()]

    def get_chapter_stats(self, chapters: list[ChapterInfo]) -> dict:
        """Get statistics about chapters."""
        if not chapters:
            return {}

        lengths = [len(c.content.split()) for c in chapters]

        return {
            "total_chapters": len(chapters),
            "total_words": sum(lengths),
            "avg_chapter_length": sum(lengths) / len(chapters),
            "min_chapter_length": min(lengths),
            "max_chapter_length": max(lengths),
            "chapters_with_titles": sum(1 for c in chapters if c.title),
        }

    def detect_structure_type(self, text: str) -> str:
        """Detect the type of chapter structure used."""
        headings = self._find_headings(text)

        if not headings:
            return "no_chapters"

        # Check what types of headings were found
        has_numbers = any(h["number"] > 0 for h in headings)
        has_titles = any(h["title"] for h in headings)

        if has_numbers and has_titles:
            return "numbered_with_titles"
        elif has_numbers:
            return "numbered_only"
        elif has_titles:
            return "titled_only"
        else:
            return "unknown"
