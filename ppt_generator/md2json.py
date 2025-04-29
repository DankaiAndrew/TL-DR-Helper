"""
This module parses a Markdown text into a JSON dict following strict five-section mapping.
"""

SECTION_MAPPING_REVERSE = {
    "content summary": "content_summary",
    "contribution": "contribution",
    "method": "method",
    "comparison": "comparison",
    "limitations and future work": "limitations_and_future_work"
}

def md2json(md_text):
    """
    Converts Markdown text into a JSON dict.

    Args:
        md_text (str): Markdown text.

    Returns:
        json_obj (dict): JSON structured dict matching strict five-section API requirement.
    """
    lines = [line.strip() for line in md_text.splitlines() if line.strip()]
    json_obj = {"title": "", "themes": {}}

    current_theme = None
    current_paper = None

    for line in lines:
        if line.startswith("# "):
            json_obj["title"] = line[2:].strip()
        elif line.startswith("## "):
            current_theme = line[3:].strip()
            json_obj["themes"][current_theme] = []
        elif line.startswith("### "):
            paper_name = line[4:].strip()
            current_paper = {"paper_name": paper_name, "summary": {}}
            if current_theme:
                json_obj["themes"][current_theme].append(current_paper)
        else:
            for human_title, json_key in SECTION_MAPPING_REVERSE.items():
                if line.lower().startswith(human_title + ":"):
                    content = line[len(human_title) + 1:].strip()
                    if current_paper:
                        current_paper["summary"][json_key] = content
                    break  # match found, no need to check other keys

    return json_obj
