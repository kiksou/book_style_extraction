"""Text loading and format conversion module."""

import re
from pathlib import Path
from typing import Optional


class TextLoader:
    """Loads text from various file formats."""

    SUPPORTED_FORMATS = {".txt", ".md", ".markdown", ".text"}

    def __init__(self):
        pass

    def load_file(self, file_path: str | Path) -> str:
        """Load text from a file."""
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        suffix = path.suffix.lower()

        if suffix in self.SUPPORTED_FORMATS:
            return self._load_text_file(path)
        elif suffix == ".epub":
            return self._load_epub(path)
        elif suffix == ".pdf":
            return self._load_pdf(path)
        elif suffix in {".doc", ".docx"}:
            return self._load_docx(path)
        else:
            # Try as plain text
            return self._load_text_file(path)

    def load_directory(self, dir_path: str | Path, recursive: bool = True) -> list[tuple[Path, str]]:
        """Load all supported files from a directory."""
        path = Path(dir_path)

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")

        files = []
        pattern = "**/*" if recursive else "*"

        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in self.SUPPORTED_FORMATS:
                try:
                    content = self.load_file(file_path)
                    files.append((file_path, content))
                except Exception as e:
                    print(f"Warning: Could not load {file_path}: {e}")

        # Sort by filename for consistent ordering
        files.sort(key=lambda x: x[0].name)
        return files

    def _load_text_file(self, path: Path) -> str:
        """Load plain text or markdown file."""
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                with open(path, "r", encoding=encoding) as f:
                    return f.read()
            except UnicodeDecodeError:
                continue

        raise ValueError(f"Could not decode file: {path}")

    def _load_epub(self, path: Path) -> str:
        """Load text from EPUB file."""
        try:
            import zipfile
            from html.parser import HTMLParser

            class HTMLTextExtractor(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.text = []
                    self.in_body = False

                def handle_starttag(self, tag, attrs):
                    if tag == "body":
                        self.in_body = True
                    elif tag in ("p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "br"):
                        self.text.append("\n")

                def handle_endtag(self, tag):
                    if tag == "body":
                        self.in_body = False
                    elif tag == "p":
                        self.text.append("\n")

                def handle_data(self, data):
                    if self.in_body:
                        self.text.append(data)

            with zipfile.ZipFile(path, "r") as epub:
                text_parts = []

                # Find content files
                for name in epub.namelist():
                    if name.endswith((".xhtml", ".html", ".htm")):
                        with epub.open(name) as f:
                            content = f.read().decode("utf-8")
                            extractor = HTMLTextExtractor()
                            extractor.feed(content)
                            text_parts.append("".join(extractor.text))

                return "\n\n".join(text_parts)

        except ImportError:
            raise ImportError("EPUB support requires no additional packages, but file may be corrupted")

    def _load_pdf(self, path: Path) -> str:
        """Load text from PDF file."""
        try:
            import subprocess

            # Try pdftotext (poppler-utils)
            result = subprocess.run(
                ["pdftotext", "-layout", str(path), "-"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return result.stdout

        except FileNotFoundError:
            pass

        # Fallback message
        raise ImportError(
            "PDF support requires pdftotext (poppler-utils). "
            "Install with: apt-get install poppler-utils"
        )

    def _load_docx(self, path: Path) -> str:
        """Load text from DOCX file."""
        try:
            import zipfile
            import xml.etree.ElementTree as ET

            with zipfile.ZipFile(path, "r") as docx:
                with docx.open("word/document.xml") as f:
                    tree = ET.parse(f)
                    root = tree.getroot()

                    # Word XML namespace
                    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}

                    paragraphs = []
                    for para in root.iter("{%s}p" % ns["w"]):
                        texts = []
                        for text in para.iter("{%s}t" % ns["w"]):
                            if text.text:
                                texts.append(text.text)
                        if texts:
                            paragraphs.append("".join(texts))

                    return "\n\n".join(paragraphs)

        except Exception as e:
            raise ImportError(f"Could not load DOCX file: {e}")

    def clean_text(self, text: str) -> str:
        """Clean and normalize text."""
        # Normalize whitespace
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Remove common OCR artifacts
        text = re.sub(r"[^\S\n]+", " ", text)

        # Fix common encoding issues
        replacements = {
            "â€™": "'",
            "â€œ": '"',
            "â€": '"',
            "â€"": "—",
            "â€"": "–",
            "Ã©": "é",
            "Ã¨": "è",
            "Ã ": "à",
            "Ã´": "ô",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)

        return text.strip()
