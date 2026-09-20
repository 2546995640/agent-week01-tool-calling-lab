"""Transparent BM25-style retrieval, requiring no model or vector database."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Section:
    source: str
    heading: str
    text: str

    @property
    def citation(self) -> str:
        return f"{self.source}#{self.heading}"


@dataclass(frozen=True)
class Hit:
    section: Section
    score: float


def tokenize(text: str) -> list[str]:
    text = text.lower()
    english = re.findall(r"[a-z0-9]+", text)
    chinese = re.findall(r"[\u4e00-\u9fff]+", text)
    bigrams = [segment[index : index + 2] for segment in chinese for index in range(len(segment) - 1)]
    return english + bigrams


def load_sections(folder: Path) -> list[Section]:
    sections: list[Section] = []
    for path in sorted(folder.glob("*.md")):
        heading: str | None = None
        lines: list[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.startswith("## "):
                if heading and lines:
                    sections.append(Section(path.name, heading, "\n".join(lines).strip()))
                heading = line[3:].strip()
                lines = []
            elif heading:
                lines.append(line)
        if heading and lines:
            sections.append(Section(path.name, heading, "\n".join(lines).strip()))
    return sections


def search(question: str, sections: list[Section], *, limit: int = 3) -> list[Hit]:
    if not sections or limit < 1:
        return []
    query_terms = set(tokenize(question))
    if not query_terms:
        return []
    documents = [Counter(tokenize(section.heading + " " + section.text)) for section in sections]
    lengths = [sum(counts.values()) for counts in documents]
    avg_length = sum(lengths) / len(lengths)
    df = Counter(term for counts in documents for term in counts)
    hits: list[Hit] = []
    for section, counts, length in zip(sections, documents, lengths):
        score = 0.0
        for term in query_terms:
            frequency = counts[term]
            if not frequency:
                continue
            inverse_frequency = math.log(1 + (len(sections) - df[term] + 0.5) / (df[term] + 0.5))
            score += inverse_frequency * frequency * 2.2 / (
                frequency + 1.2 * (0.25 + 0.75 * length / avg_length)
            )
        if score > 0:
            hits.append(Hit(section, round(score, 4)))
    return sorted(hits, key=lambda hit: (-hit.score, hit.section.citation))[:limit]
