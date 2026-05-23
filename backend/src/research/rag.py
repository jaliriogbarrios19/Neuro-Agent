"""Research RAG pipeline — text chunking, FTS5 indexing, and retrieval."""

import re
import sqlite3
from pathlib import Path

from src.research.search import Paper


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks = []
    current = ""
    for sentence in sentences:
        if len(current) + len(sentence) > chunk_size and current:
            chunks.append(current.strip())
            words = current.split()
            current = " ".join(words[-max(1, overlap // 10):]) + " " if words else ""
        current += sentence + " "
    if current.strip():
        chunks.append(current.strip())
    return chunks


class ResearchIndex:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("CREATE TABLE IF NOT EXISTS chunks (id INTEGER PRIMARY KEY, paper_title TEXT, text TEXT, source TEXT)")
        self.conn.execute("CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(text, content=chunks, content_rowid=id)")
        self.conn.commit()

    def index_paper(self, paper: Paper, full_text: str = "") -> None:
        text = full_text or paper.abstract
        if not text:
            return
        for chunk in chunk_text(text):
            self.conn.execute("INSERT INTO chunks (paper_title, text, source) VALUES (?, ?, ?)", (paper.title, chunk, paper.source))
        self.conn.commit()
        self.conn.execute("INSERT INTO chunks_fts(chunks_fts) VALUES('rebuild')")
        self.conn.commit()

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        safe_query = " ".join(f'"{t}"' for t in query.split() if len(t) > 1)
        if not safe_query:
            safe_query = query.replace("'", "''")
        rows = self.conn.execute(
            "SELECT c.paper_title, c.text, c.source FROM chunks_fts f JOIN chunks c ON f.rowid = c.id WHERE chunks_fts MATCH ? LIMIT ?",
            (safe_query, top_k),
        ).fetchall()
        return [{"paper_title": r[0], "text": r[1], "source": r[2]} for r in rows]

    def close(self):
        self.conn.close()
