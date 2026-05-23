from src.research.search import Paper
from src.research.synthesis import ResearchBrief
from src.research.export import export_bibtex, export_apa, export_markdown


class TestExport:
    def test_export_bibtex(self):
        brief = ResearchBrief(
            question="test",
            summary="test",
            papers=[Paper(title="Test Paper & More", authors=["John Doe"], year="2023", doi="10.1234/test")],
        )
        bib = export_bibtex(brief)
        assert "@article{" in bib
        assert "Test Paper" in bib
        assert "10.1234/test" in bib

    def test_export_apa(self):
        brief = ResearchBrief(
            question="test",
            summary="test",
            papers=[Paper(title="Test Paper", authors=["Jane Smith"], year="2024", doi="10.1234/test2")],
        )
        apa = export_apa(brief)
        assert "Smith (2024)" in apa
        assert "Test Paper" in apa

    def test_export_markdown(self):
        brief = ResearchBrief(
            question="What is AI?",
            summary="AI is artificial intelligence.",
            findings=[],
            references=["Paper One", "Paper Two"],
        )
        md = export_markdown(brief)
        assert "# Research Brief" in md
        assert "Paper One" in md
        assert "Paper Two" in md
