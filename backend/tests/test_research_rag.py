from src.research.rag import ResearchIndex, chunk_text
from src.research.search import Paper


class TestRAG:
    def test_index_and_search(self):
        index = ResearchIndex()
        paper = Paper(title="Test Paper", abstract="Attention mechanisms are important for neural networks.", source="test")
        index.index_paper(paper)
        results = index.search("attention mechanisms", top_k=3)
        assert len(results) >= 1
        assert results[0]["paper_title"] == "Test Paper"
        index.close()

    def test_empty_abstract_skipped(self):
        index = ResearchIndex()
        paper = Paper(title="No Abstract", abstract="", source="test")
        index.index_paper(paper)
        results = index.search("anything")
        assert len(results) == 0
        index.close()

    def test_chunking_overlap(self):
        text = "First sentence. Second sentence. Third sentence. Fourth sentence. Fifth sentence."
        chunks = chunk_text(text, chunk_size=40, overlap=20)
        assert len(chunks) >= 1
