"""Research export — BibTeX, APA 7, and Markdown formatting."""

from src.research.synthesis import ResearchBrief


def escape_latex(text: str) -> str:
    return text.replace("&", "\\&").replace("%", "\\%").replace("$", "\\$").replace("#", "\\#").replace("_", "\\_").replace("{", "\\{").replace("}", "\\}")


def export_bibtex(brief: ResearchBrief) -> str:
    entries = []
    for i, p in enumerate(brief.papers):
        key = f"ref{i+1}_{p.authors[0].split()[-1] if p.authors else 'unknown'}{p.year}"
        entry = f"@article{{{key},\n  title = {{{escape_latex(p.title)}}},\n  author = {{{' and '.join(escape_latex(a) for a in p.authors)}}},\n  year = {{{p.year}}},\n  doi = {{{p.doi}}},\n  url = {{{p.url}}},\n}}"
        entries.append(entry)
    return "\n\n".join(entries)


def export_apa(brief: ResearchBrief) -> str:
    lines = [f"# References — {brief.question}\n"]
    for i, p in enumerate(brief.papers):
        authors = ", ".join(a.split()[-1] for a in p.authors if a) if p.authors else "Unknown"
        line = f"{i+1}. {authors} ({p.year}). *{p.title}*."
        if p.doi:
            line += f" https://doi.org/{p.doi}"
        if p.url:
            line += f" {p.url}"
        lines.append(line)
    return "\n".join(lines)


def export_markdown(brief: ResearchBrief) -> str:
    lines = [f"# Research Brief: {brief.question}\n", f"## Summary\n{brief.summary}\n"]

    if brief.findings:
        lines.append("## Key Findings\n")
        for f in brief.findings:
            lines.append(f"- **[{f.confidence.upper()}]** {f.claim}")

    if brief.gaps:
        lines.append("\n## Knowledge Gaps\n")
        for g in brief.gaps:
            lines.append(f"- {g}")

    if brief.references:
        lines.append("\n## References\n")
        for i, r in enumerate(brief.references):
            lines.append(f"{i+1}. {r}")

    return "\n".join(lines)
