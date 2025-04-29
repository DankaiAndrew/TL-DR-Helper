#!/usr/bin/env python3
import os
import sys
import json
import time
import fitz  # PyMuPDF
import shutil
import argparse
from PIL import Image
from pathlib import Path
from typing import Dict, Any, List


def extract_paper(
    paper_name: str, 
    data_folder: str = "data",
    output_dir: str = "data",
    resolution: int = 300, 
    max_pages: int = 30, 
    max_chars_per_page: int = 4000
) -> Dict[str, Any]:
    """
    Extract text and images from a PDF paper
    
    Args:
        paper_name: Name of the paper (filename without extension)
        data_folder: Path to the data folder containing papers
        output_dir: Output directory for extracted content
        resolution: Image resolution in DPI
        max_pages: Maximum pages to process
        max_chars_per_page: Maximum characters per page
        
    Returns:
        Dictionary containing extraction results
    """
    start_time = time.time()
    
    # Build the PDF path from paper name and data folder
    pdf_path = os.path.join(data_folder,f"{paper_name}", f"{paper_name}.pdf")
    
    # Ensure the PDF exists
    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found at {pdf_path}")
        return {
            "extraction_dir": None,
            "num_pages": 0,
            "extraction_time": time.time() - start_time,
            "error": f"PDF not found at {pdf_path}"
        }
    
    # 确保输出目录存在
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取PDF文件名（不含扩展名）
    extraction_dir = os.path.join(output_dir, paper_name)

    if not os.path.exists(extraction_dir):
        os.makedirs(extraction_dir)

    images_dir = os.path.join(extraction_dir, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    # 存储结果的数据结构
    result = {
        "title": paper_name,
        "pages": []
    }
    
    # 打开PDF文件
    try:
        pdf_document = fitz.open(pdf_path)
        page_count = min(len(pdf_document), max_pages)
        
        # 遍历页面
        for page_idx in range(page_count):
            page = pdf_document[page_idx]
            page_num = page_idx + 1
            
            # 提取文本
            text = page.get_text()
            #if len(text) > max_chars_per_page:
            #    text = text[:max_chars_per_page]
            
            # 存储页面信息
            page_info = {
                "page_num": page_num,
                "text": text
            }
            result["pages"].append(page_info)
            
            # 提取图像 - 保存整页为图像
            pixmap = page.get_pixmap(matrix=fitz.Matrix(resolution/72, resolution/72))
            image_path = os.path.join(images_dir, f"{page_num:02d}_page.png")
            pixmap.save(image_path)
            
            """
            # 提取页面上的内嵌图像
            image_list = page.get_images(full=True)
            
            # 遍历图像
            for img_idx, img_info in enumerate(image_list):
                img_idx += 1
                xref = img_info[0]  # 图像引用
                
                try:
                    base_img = pdf_document.extract_image(xref)
                    image_bytes = base_img["image"]
                    image_ext = base_img["ext"]
                    
                    # 保存图像
                    image_filename = f"{page_num:02d}_{img_idx:02d}.{image_ext}"
                    image_path = os.path.join(images_dir, image_filename)
                    
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    
                    # 检查图像是否太小（可能是图标等）
                    with Image.open(image_path) as img:
                        width, height = img.size
                        if width < 100 or height < 100:
                            # 太小的图像可能不是重要图表
                            os.remove(image_path)
                            continue
                except Exception as e:
                    print(f"Error extracting image {img_idx} from page {page_num}: {e}")
            """
        
        # 保存提取的内容到JSON文件
        content_path = os.path.join(extraction_dir, "content.json")
        with open(content_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # 关闭PDF文档
        pdf_document.close()
        
        extraction_time = time.time() - start_time
        
        # 返回提取信息
        return {
            "extraction_dir": extraction_dir,
            "num_pages": page_count,
            "extraction_time": extraction_time,
        }
        
    except Exception as e:
        print(f"Error extracting PDF {pdf_path}: {e}")
        return {
            "extraction_dir": extraction_dir,
            "num_pages": 0,
            "extraction_time": time.time() - start_time,
            "error": str(e)
        }

def main():
    """Command line entry point for paper extraction"""
    parser = argparse.ArgumentParser(description="Extract text and images from PDF papers")
    parser.add_argument("--paper_name", help="Name of the paper (without extension)")
    parser.add_argument("-d", "--data-folder", default="data", help="Path to the data folder containing papers")
    parser.add_argument("-o", "--output", default="data", help="Output directory")
    parser.add_argument("-r", "--resolution", type=int, default=300, help="Image resolution in DPI")
    parser.add_argument("-m", "--max-pages", type=int, default=30, help="Maximum pages to process")
    parser.add_argument("-c", "--max-chars", type=int, default=4000, help="Maximum characters per page")
    
    args = parser.parse_args()
    
    result = extract_paper(
        paper_name=args.paper_name,
        data_folder=args.data_folder,
        output_dir=args.output,
        resolution=args.resolution,
        max_pages=args.max_pages,
        max_chars_per_page=args.max_chars
    )
    
    print(f"Extraction completed:")
    print(f"- Paper: {args.paper_name}")
    print(f"- Directory: {result['extraction_dir']}")
    print(f"- Pages processed: {result['num_pages']}")
    print(f"- Time taken: {result['extraction_time']:.2f} seconds")

if __name__ == "__main__":
    main() 