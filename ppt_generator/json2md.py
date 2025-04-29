"""
This module converts a JSON object into a Markdown text following strict five-section mapping.
"""

SECTION_ORDER = [
    "content_summary",
    "contribution",
    "method",
    "comparison",
    "limitations_and_future_work"
]

SECTION_NAME_MAPPING = {
    "content_summary": "content summary",
    "contribution": "contribution",
    "method": "method",
    "comparison": "comparison",
    "limitations_and_future_work": "limitations and future work"
}

def json2md(json_obj):
    """
    Converts JSON dict into a Markdown text.

    Args:
        json_obj (dict): JSON object with 'title' and 'themes'.

    Returns:
        md_text (str): Markdown formatted text.
    """
    md_lines = []

    title = json_obj.get("title", "Untitled Presentation")
    md_lines.append(f"# {title}\n")

    themes = json_obj.get("themes", {})

    for theme_name, papers in themes.items():
        md_lines.append(f"## {theme_name}\n")
        for paper in papers:
            paper_name = paper.get("paper_name", "Unnamed Paper")
            summary = paper.get("summary", {})

            md_lines.append(f"### {paper_name}\n")

            for key in SECTION_ORDER:
                if key in summary:
                    section_title = SECTION_NAME_MAPPING[key]
                    md_lines.append(f"{section_title}: {summary[key].strip()}")
            md_lines.append("")  # Blank line after each paper

    return "\n".join(md_lines)
