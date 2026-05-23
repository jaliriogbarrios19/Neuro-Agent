"""Research synthesis — query decomposition, cross-verification, structured briefs."""

from dataclasses import dataclass, field

from src.research.rag import ResearchIndex
from src.research.search import Paper, search_papers


@dataclass
class Finding:
    claim: str
    confidence: str  # "high" | "medium" | "low"
    supporting_sources: list[str] = field(default_factory=list)
    contradicting_sources: list[str] = field(default_factory=list)


@dataclass
class ResearchBrief:
    question: str
    summary: str
    findings: list[Finding] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    papers: list[Paper] = field(default_factory=list)
    references: list[str] = field(default_factory=list)


async def deep_research(query: str, llm_chat=None, depth: str = "standard") -> ResearchBrief:
    max_results = {"quick": 5, "standard": 10, "deep": 20}.get(depth, 10)

    papers = await search_papers(query, max_results)

    index = ResearchIndex()
    for p in papers:
        index.index_paper(p)

    chunks = index.search(query, top_k=10)
    index.close()

    if llm_chat is None:
        return _build_brief(query, papers, chunks)

    context = "\n\n".join(
        f"[{i+1}] {c['paper_title']} — {c['text'][:300]}" for i, c in enumerate(chunks)
    )

    prompt = f"""You are a research scientist. Analyze the following papers about: "{query}"

{context}

Produce a JSON response with:
- "summary": 2-3 paragraph synthesis of findings
- "findings": list of {{"claim": "...", "confidence": "high|medium|low"}}
- "gaps": list of knowledge gaps or limitations
- "references": list of paper titles as citations

Return ONLY valid JSON."""

    messages = [{"role": "user", "content": prompt}]
    response_parts = []
    async for event in llm_chat(messages):
        if event["type"] == "token":
            response_parts.append(event["data"])

    import json

    try:
        raw = "".join(response_parts)
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0]
        data = json.loads(raw)
        findings = [Finding(
            claim=f.get("claim", ""),
            confidence=f.get("confidence", "medium"),
        ) for f in data.get("findings", [])]

        return ResearchBrief(
            question=query,
            summary=data.get("summary", ""),
            findings=findings,
            gaps=data.get("gaps", []),
            papers=papers,
            references=[p.title for p in papers],
        )
    except (json.JSONDecodeError, IndexError):
        return _build_brief(query, papers, chunks)


def _build_brief(query: str, papers: list[Paper], chunks: list[dict]) -> ResearchBrief:
    if papers:
        summary = f"Found {len(papers)} papers about '{query}'. Key sources: " + "; ".join(
            f"{p.title} ({p.year})" for p in papers[:5]
        )
    else:
        summary = f"No papers found for '{query}'."

    findings = [
        Finding(claim=f"{p.title} — {p.abstract[:200] if p.abstract else 'No abstract available'}", confidence="medium")
        for p in papers[:3]
    ]

    return ResearchBrief(
        question=query,
        summary=summary,
        findings=findings,
        gaps=[],
        papers=papers,
        references=[p.title for p in papers],
    )
