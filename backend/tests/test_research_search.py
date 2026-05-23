import pytest
from src.research.search import (
    Paper, _clean_title, _deduplicate,
    search_semantic_scholar, search_arxiv,
)


class TestDedup:
    def test_clean_title_normalizes(self):
        assert _clean_title("Hello World! 2023") == "helloworld2023"

    def test_deduplicate_by_doi(self):
        p1 = Paper(title="Foo", doi="10.1234/foo", source="semantic_scholar")
        p2 = Paper(title="Foo", doi="10.1234/foo", source="crossref")
        result = _deduplicate([p1, p2])
        assert len(result) == 1

    def test_deduplicate_by_title(self):
        p1 = Paper(title="Deep Learning for NLP", source="arxiv")
        p2 = Paper(title="Deep Learning for NLP", source="pubmed")
        result = _deduplicate([p1, p2])
        assert len(result) == 1


class TestChunking:
    def test_chunk_short_text(self):
        from src.research.rag import chunk_text

        chunks = chunk_text("Short text.")
        assert len(chunks) == 1

    def test_chunk_long_text(self):
        from src.research.rag import chunk_text

        text = "Sentence one. " * 200
        chunks = chunk_text(text)
        assert len(chunks) > 1


class TestSearchEngines:
    @pytest.mark.asyncio
    async def test_semantic_scholar_returns_papers(self):
        papers = await search_semantic_scholar("transformer", max_results=3)
        assert isinstance(papers, list)
        if papers:
            assert papers[0].source == "semantic_scholar"

    @pytest.mark.asyncio
    async def test_arxiv_returns_papers(self):
        papers = await search_arxiv("neural network", max_results=3)
        assert isinstance(papers, list)
