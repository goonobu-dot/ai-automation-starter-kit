from __future__ import annotations

from dataclasses import dataclass
from html.parser import HTMLParser


@dataclass(frozen=True)
class HtmlContent:
    title: str
    text: str


class _VisibleTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self._in_title = False
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"script", "style"}:
            self._ignored_depth += 1
        if tag == "title":
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self._ignored_depth:
            self._ignored_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        cleaned = " ".join(data.split())
        if not cleaned or self._ignored_depth:
            return
        if self._in_title:
            self.title_parts.append(cleaned)
        else:
            self.text_parts.append(cleaned)


def extract_html_content(html: str) -> HtmlContent:
    parser = _VisibleTextParser()
    parser.feed(html)
    title = " ".join(parser.title_parts).strip()
    text = " ".join(parser.text_parts).strip()
    return HtmlContent(title=title, text=text)
