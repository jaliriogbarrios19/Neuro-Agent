"""Deep Research — search papers across multiple academic engines."""

import asyncio
import re
from dataclasses import dataclass, field


@dataclass
class Paper:
    title: str
    authors: list[str] = field(default_factory=list)
    year: str = ""
    abstract: str = ""
    doi: str = ""
    url: str = ""
    source: str = ""
    citations: int = 0


async def _fetch_json(client, url: str, params: dict | None = None) -> dict:
    resp = await client.get(url, params=params or {}, timeout=15)
    resp.raise_for_status()
    return resp.json()


async def _fetch_xml(client, url: str, params: dict | None = None) -> str:
    resp = await client.get(url, params=params or {}, timeout=15)
    resp.raise_for_status()
    return resp.text


async def search_semantic_scholar(query: str, max_results: int = 10) -> list[Paper]:
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            data = await _fetch_json(
                client,
                "https://api.semanticscholar.org/graph/v1/paper/search",
                {"query": query, "limit": max_results, "fields": "title,authors,year,abstract,externalIds,citationCount,url"},
            )
    except Exception:
        return []

    papers = []
    for item in data.get("data", []):
        papers.append(Paper(
            title=item.get("title", ""),
            authors=[a.get("name", "") for a in item.get("authors", [])],
            year=str(item.get("year", "")),
            abstract=item.get("abstract", ""),
            doi=item.get("externalIds", {}).get("DOI", ""),
            url=item.get("url", ""),
            source="semantic_scholar",
            citations=item.get("citationCount", 0),
        ))
    return papers


async def search_arxiv(query: str, max_results: int = 10) -> list[Paper]:
    try:
        import arxiv

        client = arxiv.Client()
        search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
        results = [r async for r in client.results(search)]
    except Exception:
        return []

    papers = []
    for r in results:
        papers.append(Paper(
            title=r.title,
            authors=[a.name for a in r.authors],
            year=str(r.published.year),
            abstract=r.summary,
            url=r.entry_id,
            source="arxiv",
        ))
    return papers


async def search_crossref(query: str, max_results: int = 10) -> list[Paper]:
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            data = await _fetch_json(
                client,
                "https://api.crossref.org/works",
                {"query": query, "rows": max_results, "select": "title,author,created,abstract,DOI,URL"},
            )
    except Exception:
        return []

    papers = []
    for item in data.get("message", {}).get("items", []):
        title_list = item.get("title", [])
        papers.append(Paper(
            title=title_list[0] if title_list else "",
            authors=[f"{a.get('given','')} {a.get('family','')}".strip() for a in item.get("author", [])],
            year=str(item.get("created", {}).get("date-parts", [[0]])[0][0]),
            abstract=item.get("abstract", ""),
            doi=item.get("DOI", ""),
            url=item.get("URL", ""),
            source="crossref",
        ))
    return papers


async def search_pubmed(query: str, max_results: int = 10) -> list[Paper]:
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            search_data = await _fetch_json(
                client,
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi",
                {"db": "pubmed", "term": query, "retmax": max_results, "retmode": "json"},
            )
            ids = search_data.get("esearchresult", {}).get("idlist", [])
            if not ids:
                return []

            fetch_data = await _fetch_json(
                client,
                "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi",
                {"db": "pubmed", "id": ",".join(ids), "retmode": "json"},
            )
    except Exception:
        return []

    papers = []
    for pid in ids:
        info = fetch_data.get("result", {}).get(pid, {})
        papers.append(Paper(
            title=info.get("title", ""),
            authors=[a.get("name", "") for a in info.get("authors", [])],
            year=str(info.get("pubdate", ""))[:4],
            abstract="",
            doi=f"10.0000/pubmed.{pid}",
            url=f"https://pubmed.ncbi.nlm.nih.gov/{pid}/",
            source="pubmed",
        ))
    return papers


async def search_openalex(query: str, max_results: int = 10) -> list[Paper]:
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            data = await _fetch_json(
                client,
                "https://api.openalex.org/works",
                {"search": query, "per_page": max_results},
            )
    except Exception:
        return []

    papers = []
    for item in data.get("results", []):
        papers.append(Paper(
            title=item.get("title", ""),
            authors=[a.get("author", {}).get("display_name", "") for a in item.get("authorships", [])],
            year=str(item.get("publication_year", "")),
            abstract="",
            doi=item.get("doi", ""),
            url="",
            source="openalex",
            citations=item.get("cited_by_count", 0),
        ))
    return papers


def _clean_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]", "", t.lower())


def _deduplicate(papers: list[Paper]) -> list[Paper]:
    seen_doi: set[str] = set()
    seen_title: set[str] = set()
    result = []
    for p in papers:
        if p.doi and p.doi in seen_doi:
            continue
        ct = _clean_title(p.title)
        if ct in seen_title:
            continue
        if p.doi:
            seen_doi.add(p.doi)
        seen_title.add(ct)
        result.append(p)
    return result


async def search_papers(query: str, max_results: int = 20) -> list[Paper]:
    tasks = [
        search_semantic_scholar(query, max_results),
        search_arxiv(query, max_results),
        search_crossref(query, max_results),
        search_pubmed(query, max_results),
        search_openalex(query, max_results),
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    all_papers = []
    for r in results:
        if isinstance(r, list):
            all_papers.extend(r)
    return _deduplicate(all_papers)[:max_results]
