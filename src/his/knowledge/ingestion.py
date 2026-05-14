from __future__ import annotations

from pathlib import Path


def extract_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")
    if suffix == ".pdf":
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Install pypdf to read PDF manuals.") from exc

        reader = PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    return ""


def iter_manual_texts(manuals_dir: Path) -> list[tuple[str, str]]:
    if not manuals_dir.exists():
        return []
    results: list[tuple[str, str]] = []
    for path in sorted(manuals_dir.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".txt", ".md", ".pdf"}:
            text = extract_text(path).strip()
            if text:
                results.append((path.name, text))
    return results
