"""Text loading and format conversion module."""

import re
import zipfile
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class EPUBChapter:
    """Represents a chapter extracted from EPUB."""
    title: str
    content: str
    order: int


class HTMLToTextConverter(HTMLParser):
    """Converts HTML to clean text while preserving structure."""

    # Tags that should add paragraph breaks
    BLOCK_TAGS = {
        "p", "div", "h1", "h2", "h3", "h4", "h5", "h6",
        "blockquote", "section", "article", "header", "footer",
        "li", "tr", "br", "hr"
    }

    # Tags to skip entirely
    SKIP_TAGS = {"script", "style", "head", "nav", "aside", "footer"}

    def __init__(self):
        super().__init__()
        self.text_parts = []
        self.current_text = []
        self.skip_depth = 0
        self.in_title = False
        self.title = ""

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()

        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return

        if tag == "title":
            self.in_title = True

        if tag in self.BLOCK_TAGS and self.current_text:
            self.text_parts.append("".join(self.current_text).strip())
            self.current_text = []

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in self.SKIP_TAGS:
            self.skip_depth = max(0, self.skip_depth - 1)
            return

        if tag == "title":
            self.in_title = False

        if tag in self.BLOCK_TAGS and self.current_text:
            self.text_parts.append("".join(self.current_text).strip())
            self.current_text = []

    def handle_data(self, data):
        if self.skip_depth > 0:
            return

        if self.in_title:
            self.title = data.strip()
            return

        # Clean up whitespace but preserve single spaces
        cleaned = re.sub(r'\s+', ' ', data)
        if cleaned.strip():
            self.current_text.append(cleaned)

    def get_text(self) -> str:
        """Get the extracted text."""
        if self.current_text:
            self.text_parts.append("".join(self.current_text).strip())

        # Join paragraphs with double newlines
        paragraphs = [p for p in self.text_parts if p]
        return "\n\n".join(paragraphs)


class TextLoader:
    """Loads text from various file formats."""

    SUPPORTED_FORMATS = {".txt", ".md", ".markdown", ".text", ".epub"}

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

        all_formats = self.SUPPORTED_FORMATS | {".epub", ".pdf", ".docx"}

        for file_path in path.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in all_formats:
                try:
                    content = self.load_file(file_path)
                    files.append((file_path, content))
                except Exception as e:
                    print(f"Warning: Could not load {file_path}: {e}")

        # Sort by filename for consistent ordering
        files.sort(key=lambda x: x[0].name)
        return files

    def get_epub_metadata(self, path: Path) -> dict:
        """Extract metadata from an EPUB file."""
        metadata = {
            "title": "",
            "author": "",
            "language": "",
            "publisher": "",
            "date": "",
            "description": "",
        }

        try:
            with zipfile.ZipFile(path, "r") as epub:
                # Find OPF file
                opf_path = None
                container_path = "META-INF/container.xml"

                if container_path in epub.namelist():
                    container = ET.fromstring(epub.read(container_path))
                    rootfile = container.find(".//{*}rootfile")
                    if rootfile is not None:
                        opf_path = rootfile.get("full-path")

                if not opf_path:
                    opf_path = self._find_opf_file(epub)

                if opf_path:
                    opf_content = epub.read(opf_path)
                    opf_root = ET.fromstring(opf_content)

                    # DC namespace for Dublin Core metadata
                    dc_ns = "http://purl.org/dc/elements/1.1/"

                    # Extract metadata
                    for elem in opf_root.findall(f".//{{{dc_ns}}}title"):
                        if elem.text:
                            metadata["title"] = elem.text.strip()
                            break

                    for elem in opf_root.findall(f".//{{{dc_ns}}}creator"):
                        if elem.text:
                            metadata["author"] = elem.text.strip()
                            break

                    for elem in opf_root.findall(f".//{{{dc_ns}}}language"):
                        if elem.text:
                            metadata["language"] = elem.text.strip()
                            break

                    for elem in opf_root.findall(f".//{{{dc_ns}}}publisher"):
                        if elem.text:
                            metadata["publisher"] = elem.text.strip()
                            break

                    for elem in opf_root.findall(f".//{{{dc_ns}}}date"):
                        if elem.text:
                            metadata["date"] = elem.text.strip()
                            break

                    for elem in opf_root.findall(f".//{{{dc_ns}}}description"):
                        if elem.text:
                            metadata["description"] = elem.text.strip()
                            break

        except Exception:
            pass

        return metadata

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
        """Load text from EPUB file with proper reading order."""
        try:
            with zipfile.ZipFile(path, "r") as epub:
                # Step 1: Find the root file (content.opf) from container.xml
                container_path = "META-INF/container.xml"
                if container_path not in epub.namelist():
                    # Fallback: try to find content.opf directly
                    opf_path = self._find_opf_file(epub)
                else:
                    container = ET.fromstring(epub.read(container_path))
                    ns = {"c": "urn:oasis:names:tc:opendocument:xmlns:container"}
                    rootfile = container.find(".//c:rootfile", ns)
                    if rootfile is None:
                        # Try without namespace
                        rootfile = container.find(".//{*}rootfile")
                    opf_path = rootfile.get("full-path") if rootfile is not None else None

                if not opf_path:
                    opf_path = self._find_opf_file(epub)

                if not opf_path:
                    # Last resort: just grab all HTML files
                    return self._load_epub_fallback(epub)

                # Step 2: Parse the OPF file to get manifest and spine
                opf_content = epub.read(opf_path)
                opf_root = ET.fromstring(opf_content)

                # Get the base directory of the OPF file
                opf_dir = str(Path(opf_path).parent)
                if opf_dir == ".":
                    opf_dir = ""

                # Parse manifest (id -> href mapping)
                manifest = {}
                ns_opf = {"opf": "http://www.idpf.org/2007/opf"}

                for item in opf_root.findall(".//{*}item"):
                    item_id = item.get("id")
                    href = item.get("href")
                    media_type = item.get("media-type", "")

                    if item_id and href:
                        # Handle relative paths
                        if opf_dir:
                            full_href = f"{opf_dir}/{href}"
                        else:
                            full_href = href
                        manifest[item_id] = {
                            "href": full_href,
                            "media_type": media_type
                        }

                # Step 3: Parse spine to get reading order
                spine_items = []
                for itemref in opf_root.findall(".//{*}itemref"):
                    idref = itemref.get("idref")
                    if idref and idref in manifest:
                        spine_items.append(manifest[idref])

                # Step 4: Extract text from each spine item in order
                chapters = []
                for i, item in enumerate(spine_items):
                    href = item["href"]
                    media_type = item.get("media_type", "")

                    # Only process HTML/XHTML files
                    if not (media_type.startswith("application/xhtml") or
                            media_type.startswith("text/html") or
                            href.endswith((".xhtml", ".html", ".htm"))):
                        continue

                    # Try to find the file (handle URL encoding)
                    file_path = self._find_epub_file(epub, href)
                    if not file_path:
                        continue

                    try:
                        content = self._read_epub_file(epub, file_path)
                        chapter = self._extract_chapter_from_html(content, i)
                        if chapter and len(chapter.content.strip()) > 100:
                            chapters.append(chapter)
                    except Exception:
                        continue

                if not chapters:
                    return self._load_epub_fallback(epub)

                # Combine chapters with separators
                result_parts = []
                for chapter in chapters:
                    if chapter.title:
                        result_parts.append(f"\n\n## {chapter.title}\n\n")
                    result_parts.append(chapter.content)

                return "\n\n".join(result_parts)

        except zipfile.BadZipFile:
            raise ValueError(f"Invalid EPUB file (not a valid ZIP): {path}")
        except ET.ParseError as e:
            raise ValueError(f"Invalid EPUB structure (XML parse error): {e}")
        except Exception as e:
            raise ValueError(f"Could not read EPUB file: {e}")

    def _find_opf_file(self, epub: zipfile.ZipFile) -> Optional[str]:
        """Find the OPF file in the EPUB archive."""
        for name in epub.namelist():
            if name.endswith(".opf"):
                return name
        return None

    def _find_epub_file(self, epub: zipfile.ZipFile, href: str) -> Optional[str]:
        """Find a file in the EPUB, handling URL encoding and path variations."""
        from urllib.parse import unquote

        # Try exact path
        if href in epub.namelist():
            return href

        # Try URL decoded path
        decoded = unquote(href)
        if decoded in epub.namelist():
            return decoded

        # Try without leading slash
        if href.startswith("/"):
            href_no_slash = href[1:]
            if href_no_slash in epub.namelist():
                return href_no_slash

        # Try case-insensitive match
        href_lower = href.lower()
        for name in epub.namelist():
            if name.lower() == href_lower:
                return name

        return None

    def _read_epub_file(self, epub: zipfile.ZipFile, file_path: str) -> str:
        """Read and decode an EPUB file with encoding detection."""
        raw_content = epub.read(file_path)

        # Try different encodings
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252", "iso-8859-1"]

        for encoding in encodings:
            try:
                return raw_content.decode(encoding)
            except (UnicodeDecodeError, LookupError):
                continue

        # Last resort: decode with errors replaced
        return raw_content.decode("utf-8", errors="replace")

    def _extract_chapter_from_html(self, html_content: str, order: int) -> EPUBChapter:
        """Extract chapter content from HTML."""
        converter = HTMLToTextConverter()

        try:
            converter.feed(html_content)
        except Exception:
            # If HTML parsing fails, try basic regex extraction
            text = re.sub(r'<[^>]+>', ' ', html_content)
            text = re.sub(r'\s+', ' ', text).strip()
            return EPUBChapter(title="", content=text, order=order)

        return EPUBChapter(
            title=converter.title,
            content=converter.get_text(),
            order=order
        )

    def _load_epub_fallback(self, epub: zipfile.ZipFile) -> str:
        """Fallback method: load all HTML files in alphabetical order."""
        html_files = sorted([
            name for name in epub.namelist()
            if name.endswith((".xhtml", ".html", ".htm"))
            and "toc" not in name.lower()
            and "nav" not in name.lower()
            and "cover" not in name.lower()
        ])

        text_parts = []
        for file_path in html_files:
            try:
                content = self._read_epub_file(epub, file_path)
                chapter = self._extract_chapter_from_html(content, 0)
                if chapter.content.strip():
                    text_parts.append(chapter.content)
            except Exception:
                continue

        return "\n\n".join(text_parts)

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
