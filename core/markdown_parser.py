from __future__ import annotations

from markdown_it import MarkdownIt


md = MarkdownIt("commonmark", {"html": False, "breaks": True})


def to_plaintext(markdown_text: str) -> str:
    return markdown_text


def to_html(markdown_text: str) -> str:
    return md.render(markdown_text)
