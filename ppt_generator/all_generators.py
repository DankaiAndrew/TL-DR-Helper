"""
All-in-one generators: ppt2md, md2ppt, json2ppt, ppt2json, json2md, md2json
"""

import os
import json
from ppt_generator.ppt2md import PptToMarkdownConverter
from ppt_generator.md2ppt import PptGenerator
from ppt_generator.utils import read_md_file, save_md
from ppt_generator.json2md import json2md
from ppt_generator.md2json import md2json


def ppt_to_md(ppt_path, theme_path, output_img_dir=None, output_md_path=None):
    """
    Convert PPTX to Markdown.

    Returns:
        str: Markdown text.
    """
    print(f"[INFO] Converting PPT to Markdown...")

    is_save = False if not output_md_path else True
    converter = PptToMarkdownConverter(
        ppt_path=ppt_path,
        output_md_path=output_md_path,
        output_img_dir=output_img_dir,
        theme_path=theme_path
    )
    md_text = converter.convert(isSave=is_save)

    if is_save:
        print(f"[INFO] Markdown file saved to: {output_md_path}")
    print(f"[INFO] PPT to Markdown conversion completed.")

    return md_text


def md_to_ppt(md_path, theme_path, save_path, img_dic=None):
    """
    Convert Markdown to PPTX and save.
    """
    print(f"[INFO] Converting Markdown to PPT...")

    if img_dic is None:
        img_dic = {}
    md_content = read_md_file(md_path)
    ppt_gen = PptGenerator(
        client=None,
        img_dic=img_dic,
        md_str=md_content,
        theme_path=theme_path,
        save_path=save_path
    )
    print(f"[INFO] PPT file saved to: {save_path}")
    print(f"[INFO] Markdown to PPT conversion completed.")


def json_to_ppt(json_obj, theme_path, save_path, img_dic=None, inter_md_path=None):
    """
    Convert JSON to Markdown and then to PPTX.
    """
    print(f"[INFO] Converting JSON to PPT...")

    is_save_md = False if not inter_md_path else True
    if img_dic is None:
        img_dic = {}

    md_content = json2md(json_obj)
    if is_save_md:
        save_md(md_content, inter_md_path)
        print(f"[INFO] Intermediate Markdown file saved to: {inter_md_path}")

    ppt_gen = PptGenerator(
        client=None,
        img_dic=img_dic,
        md_str=md_content,
        theme_path=theme_path,
        save_path=save_path
    )

    print(f"[INFO] PPT file saved to: {save_path}")
    print(f"[INFO] JSON to PPT conversion completed.")


def ppt_to_json(ppt_path, theme_path, output_img_dir=None, inter_md_path=None):
    """
    Convert PPTX directly to JSON string.
    """
    print(f"[INFO] Converting PPT to JSON...")

    is_save_md = False if not inter_md_path else True
    converter = PptToMarkdownConverter(
        ppt_path=ppt_path,
        output_md_path=inter_md_path,
        output_img_dir=output_img_dir,
        theme_path=theme_path,
    )
    md_text = converter.convert(isSave=is_save_md)

    json_obj = md2json(md_text)
    print(f"[INFO] PPT to JSON conversion completed.")

    return json.dumps(json_obj, indent=2, ensure_ascii=False)


def json_to_md(json_obj, output_md_path=None):
    """
    Convert JSON to Markdown.

    Returns:
        str: Markdown text.
    """
    print(f"[INFO] Converting JSON to Markdown...")

    md_text = json2md(json_obj)
    is_save = False if not output_md_path else True
    if is_save:
        save_md(md_text, output_md_path)
        print(f"[INFO] Markdown file saved to: {output_md_path}")

    print(f"[INFO] JSON to Markdown conversion completed.")
    return md_text


def md_to_json(md_path):
    """
    Convert Markdown file to JSON.

    Returns:
        str: JSON formatted string.
    """
    print(f"[INFO] Converting Markdown to JSON...")

    md_text = read_md_file(md_path)
    json_obj = md2json(md_text)

    print(f"[INFO] Markdown to JSON conversion completed.")
    return json.dumps(json_obj, indent=2, ensure_ascii=False)
