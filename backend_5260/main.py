from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse

import os
from datetime import datetime
import shutil
from typing import Optional
import subprocess
import json
import sys
import ast
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent   
sys.path.insert(0, str(BASE_DIR))
from datetime import datetime
from ppt_generator.all_generators import (
    ppt_to_md,
    md_to_ppt,
    json_to_ppt,
    ppt_to_json,
    json_to_md,
    md_to_json
)

app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

import os
import shutil
import subprocess
import json
from pathlib import Path

def process_paper(paper_pdf_path: str) -> dict:
    """
    1. 将 PDF 复制到 SlidesSummarizer/data/<paper_name>/<paper_name>.pdf
    2. 在 SlidesSummarizer/ 目录下依次运行：
         python scripts/extract_paper.py --paper_name <paper_name>
         python scripts/retrieve_content.py --paper_name <paper_name>
         python scripts/predict.py paper_name=<paper_name>
    3. 从 predict.py 的 stdout 解析 JSON, 返回: 
       {
            "content_summary": "This paper discusses deep learning techniques...",
            "contribution": "Main contributions include...",
            "method": "The proposed method...",
            "comparison": "Compared to existing methods...",
            "limitations_and_future_work": "Current limitations..."
        }
    """

    # 1. 定位各个目录
    base_dir = Path(__file__).parent.resolve()                  # project/backend_5260
    slides_dir = base_dir.parent / "SlidesSummarizer"           # project/SlidesSummarizer
    scripts_dir = slides_dir / "scripts"                        # project/SlidesSummarizer/scripts
    data_root   = slides_dir / "data"                           # project/SlidesSummarizer/data

    # 2. 准备目标子目录
    base_name = Path(paper_pdf_path).stem                       
    paper_name = "_".join(base_name.split("_")[2:])
    dest_dir   = data_root / paper_name
    dest_dir.mkdir(parents=True, exist_ok=True)

    # 3. 复制 PDF 到 data/<paper_name>/
    dest_pdf = dest_dir / f"{paper_name}.pdf"
    shutil.copy(paper_pdf_path, dest_pdf)

    # 4. 依次运行三个脚本
    #    注意： cwd 设置为 slides_dir，以便脚本能正确引用 data/ 目录
    
    subprocess.run(
        ["python", str(scripts_dir / "extract_paper.py"), "--paper_name", paper_name],
        cwd=str(slides_dir),
        check=True
    )

    subprocess.run(
        ["python", str(scripts_dir / "retrieve_content.py"), "--paper_name", paper_name],
        cwd=str(slides_dir),
        check=True
    )
    
    subprocess.run(
        ["python", str(scripts_dir / "predict.py"), f"paper_name={paper_name}"],
        cwd=str(slides_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    

    # 5. 解析 predict.py 的输出（最终 dict 以 JSON 打印到 stdout）
    try:
        with open(dest_dir / "summary.json", 'r') as f:
            # First parse the outer string, then parse the inner JSON string
            summary_dict = json.loads(json.loads(f.read()))
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"Failed to parse JSON from predict.py\n"
        )

    return {
        "paper_name": paper_name,
        "summary": summary_dict
    }

def mock_pdf_processing():
    """
    模拟PDF处理结果
    实际处理逻辑待实现
    """
    return {
        "paper_name": "Sample Paper",
        "summary": {
            "content_summary": "This paper presents a novel approach to deep learning, focusing on improving model efficiency and accuracy. The authors propose a new architecture that significantly reduces computational requirements while maintaining high performance.",
            "contribution": "The main contributions of this work include: 1) A new lightweight neural network architecture, 2) An innovative training method that reduces memory usage, 3) Comprehensive experiments showing superior performance compared to existing methods.",
            "method": "The proposed method combines several techniques: 1) Knowledge distillation for model compression, 2) Dynamic pruning during training, 3) Adaptive learning rate scheduling. The implementation details and mathematical formulations are provided in Section 3.",
            "comparison": "Compared to existing methods, our approach achieves: 1) 30% reduction in model size, 2) 40% faster inference time, 3) 2% higher accuracy on benchmark datasets. Detailed comparison tables are provided in Section 4.",
            "limitations_and_future_work": "Current limitations include: 1) High computational cost during training, 2) Limited scalability to very large models. Future work will focus on: 1) Reducing training time, 2) Extending the method to other domains, 3) Investigating theoretical guarantees."
        }
    }

def mock_ppt_processing():
    """
    模拟PPT处理结果
    实际处理逻辑待实现
    """
    return {
        "title": "Sample PPT",
        "themes": {
            "Deep Learning": [
                {
                    "paper_name": "Paper 1",
                    "summary": {
                        "content_summary": "This paper discusses deep learning techniques...",
                        "contribution": "Main contributions include...",
                        "method": "The proposed method...",
                        "comparison": "Compared to existing methods...",
                        "limitations_and_future_work": "Current limitations..."
                    }
                }
            ],
            "Computer Vision": [
                {
                    "paper_name": "Paper 2",
                    "summary": {
                        "content_summary": "This paper focuses on computer vision...",
                        "contribution": "Main contributions include...",
                        "method": "The proposed method...",
                        "comparison": "Compared to existing methods...",
                        "limitations_and_future_work": "Current limitations..."
                    }
                }
            ]
        }
    }

@app.post("/pdf/summarize")
async def summarize_pdf(pdf: UploadFile = File(...)):
    try:
        # 验证文件类型
        if not pdf.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{pdf.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(pdf.file, buffer)
        
        # 获取模拟的处理结果
        #processing_result = mock_pdf_processing()
        processing_result = process_paper(file_path)
        
        """
        try:
            processing_result = await run_in_threadpool(process_paper, file_path)
        except Exception as e:
            # process_paper 内部抛出的任何异常，都转成 500 返回
            raise HTTPException(status_code=500, detail=str(e))
        """
        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "PDF file processed successfully",
                "filename": filename,
                "file_path": file_path,
                "paper_name": processing_result["paper_name"],
                "summary": processing_result["summary"]
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-ppt")
async def generate_ppt(ppt_data: dict):
    """
    生成 PPT 的逻辑：
    1. 基于 ppt_data 数据生成 PPT
    2. 返回生成的 PPT 文件给前端
    ppt_data 的格式示例：
    {
    "title":  "titlename", 
    "themes": {
        "theme1": [
        {
            "paper_name": "paper1",
            "summary":{
            "content_summary": "blablabla",
            "contribution": "blablabla",
            "method": "blablabla",
            "comparison":"blablabla",
            "limitations_and_future_work":"blablabla" }
            }
        },
        …  
        ],
        "theme2": [ … ],
        …
    }
    }
    """
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 调用 json_to_ppt 来生成 PPT 文件
    ppt_output_path = os.path.join(UPLOAD_DIR, f"{timestamp}_generated.pptx")
    try:
        json_to_ppt(
            json_obj=ppt_data,
            theme_path="ppt_mode/1",  # 可以根据需要设置不同的主题模板
            save_path=ppt_output_path,
            img_dic={}, 
            inter_md_path=None  
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PPT generation failed: {e}")

    # 以流的形式返回 PPT 文件
    def iter_ppt():
        with open(ppt_output_path, "rb") as f:
            yield from f
    
    filename = f"{ppt_data['title']}.pptx"
    return StreamingResponse(
        iter_ppt(),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.post("/ppt/process")
async def process_ppt(ppt: UploadFile = File(...)):
    try:
        # 验证文件类型
        if not ppt.filename.endswith('.pptx'):
            raise HTTPException(status_code=400, detail="Only PPTX files are allowed")
        
        # 生成唯一的文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{ppt.filename}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(ppt.file, buffer)
        
        # 获取模拟的处理结果
        #processing_result = mock_ppt_processing()
        data = ppt_to_json(
            ppt_path=file_path,
            theme_path="ppt_mode/1",
            output_img_dir=None,           # 禁止图片提取
            inter_md_path=None             # 不保存中间md
        )
        processing_result = json.loads(data)

        return JSONResponse(
            status_code=200,
            content={
                "status": "success",
                "message": "PPT file processed successfully",
                "filename": filename,
                "file_path": file_path,
                "title": processing_result["title"],
                "themes": processing_result["themes"]
            }
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    uvicorn.run(app, host=args.host, port=args.port)
