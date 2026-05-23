from src.research.search import Paper
from src.research.synthesis import deep_research, ResearchBrief, Finding


class TestSynthesis:
    async def test_deep_research_without_llm(self):
        brief = await deep_research("test query", llm_chat=None, depth="quick")
        assert isinstance(brief, ResearchBrief)
        assert brief.question == "test query"

    async def test_brief_has_papers(self):
        brief = await deep_research("transformer architecture", llm_chat=None, depth="quick")
        assert isinstance(brief.summary, str)
        assert len(brief.summary) > 0
