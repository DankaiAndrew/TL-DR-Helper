import torch
from torch.utils.data import DataLoader
from PIL import Image
from tqdm import tqdm
import os
import pickle
from colpali_engine.models.paligemma_colbert_architecture import ColPali
from colpali_engine.trainer.retrieval_evaluator import CustomEvaluator
from colpali_engine.utils.colpali_processing_utils import process_images, process_queries
from transformers import AutoProcessor

import json
from pathlib import Path
import argparse

# Import models directory
os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

class ImageRetrieval:
    """基于视觉语言模型的论文图像检索系统"""
    
    def __init__(self):
        """初始化图像检索系统"""
        # 初始化视觉语言模型
        model_name = "vidore/colpali"
        print(f"Loading model: {model_name}")
        
        self.model = ColPali.from_pretrained("vidore/colpaligemma-3b-mix-448-base", torch_dtype=torch.float32, device_map="auto").eval()
        self.model.load_adapter(model_name)
        self.processor = AutoProcessor.from_pretrained(model_name)
        
        # 预定义特殊查询
        self.special_queries = {
            "model_structure": "Find model architecture diagrams, structure charts, neural network designs, or framework illustrations",
            "experiment_results": "Find experimental results, data tables, performance charts, evaluation metrics, or comparison graphs"
        }
        
        print("Model initialized successfully")
    
    def load_images(self, image_dir):
        """加载目录中的所有图像"""
        print(f"Loading images from {image_dir}")
        images = []
        image_paths = []
        valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        
        # 按文件名中的数字排序
        files = sorted(os.listdir(image_dir), 
                      key=lambda x: int(''.join(filter(str.isdigit, x))) if any(c.isdigit() for c in x) else float('inf'))
        
        for filename in files:
            filepath = os.path.join(image_dir, filename)
            if os.path.isfile(filepath) and any(filename.lower().endswith(ext) for ext in valid_extensions):
                try:
                    img = Image.open(filepath).convert('RGB')
                    images.append(img)
                    image_paths.append(filepath)
                except Exception as e:
                    print(f"Error loading image {filepath}: {e}")
        
        print(f"Loaded {len(images)} images")
        return images, image_paths
    
    def embed_images(self, images):
        """生成图像嵌入"""
        print("Generating image embeddings...")
        image_embeddings = []
        
        # 处理每个图像
        for img in tqdm(images):
            processed_img = process_images(self.processor, [img]).to(self.model.device)
            with torch.no_grad():
                embedding = self.model(**processed_img)
                image_embeddings.append(embedding[0])  # 取第一个嵌入（批次大小为1）
        
        return torch.stack(image_embeddings, dim=0)
    
    def query_images(self, query_text, image_embeddings, top_k=3):
        """根据查询文本检索图像"""
        print(f"Querying with: '{query_text}'")
        
        # 处理查询
        query = [query_text]
        batch_queries = process_queries(
            self.processor, 
            query, 
            Image.new("RGB", (448, 448), (255, 255, 255))
        ).to(self.model.device)
        
        # 生成查询嵌入
        with torch.no_grad():
            query_embedding = self.model(**batch_queries)
        
        # 计算相似度并排序
        evaluator = CustomEvaluator(is_multi_vector=True)
        scores = evaluator.evaluate(query_embedding, image_embeddings)
        
        # 获取top-k结果
        scores_tensor = torch.tensor(scores)
        top_results = torch.topk(scores_tensor, min(top_k, scores_tensor.shape[1]), dim=-1)
        
        top_indices = top_results.indices.tolist()[0]
        top_scores = top_results.values.tolist()[0]
        
        return top_indices, top_scores
    
    def find_model_structure_pages(self, image_dir, output_dir=None, top_k=3):
        """检索包含模型结构的页面"""
        # 加载图像
        images, image_paths = self.load_images(image_dir)
        if not images:
            print("No images found")
            return []
        
        # 生成嵌入
        image_embeddings = self.embed_images(images)
        
        # 用于找模型结构的查询
        query = self.special_queries["model_structure"]
        top_indices, top_scores = self.query_images(query, image_embeddings, top_k)
        
        # 获取结果路径
        result_paths = [image_paths[i] for i in top_indices]
        
        # 保存结果
        results = {
            "query": query,
            "model_structure_pages": [Path(p).name for p in result_paths],
            "scores": top_scores,
            "full_paths": result_paths
        }
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "model_structure_pages.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Model structure pages saved to {output_path}")
        
        # 打印结果
        print("\nModel Structure Pages:")
        for i, (idx, score) in enumerate(zip(top_indices, top_scores)):
            print(f"{i+1}. {Path(image_paths[idx]).name} (Score: {score:.4f})")
        
        return results
    
    def find_experiment_results_pages(self, image_dir, output_dir=None, top_k=3):
        """检索包含实验结果的页面"""
        # 加载图像
        images, image_paths = self.load_images(image_dir)
        if not images:
            print("No images found")
            return []
        
        # 生成嵌入
        image_embeddings = self.embed_images(images)
        
        # 用于找实验结果的查询
        query = self.special_queries["experiment_results"]
        top_indices, top_scores = self.query_images(query, image_embeddings, top_k)
        
        # 获取结果路径
        result_paths = [image_paths[i] for i in top_indices]
        
        # 保存结果
        results = {
            "query": query,
            "experiment_results_pages": [Path(p).name for p in result_paths],
            "scores": top_scores,
            "full_paths": result_paths
        }
        
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, "experiment_results_pages.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"Experiment results pages saved to {output_path}")
        
        # 打印结果
        print("\nExperiment Results Pages:")
        for i, (idx, score) in enumerate(zip(top_indices, top_scores)):
            print(f"{i+1}. {Path(image_paths[idx]).name} (Score: {score:.4f})")
        
        return results
    
    def find_specialized_pages(self, image_dir, output_dir=None, top_k=3):
        """检索模型结构和实验结果页面"""
        # 创建输出目录
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        
        # 检索模型结构页面
        print("\n=== Finding Model Structure Pages ===")
        model_results = self.find_model_structure_pages(image_dir, output_dir, top_k)
        
        # 检索实验结果页面
        print("\n=== Finding Experiment Results Pages ===")
        experiment_results = self.find_experiment_results_pages(image_dir, output_dir, top_k)
        
        # 合并结果
        combined_results = {
            "model_structure": model_results,
            "experiment_results": experiment_results
        }
        
        # 保存合并结果
        if output_dir:
            output_path = os.path.join(output_dir, "specialized_pages.json")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(combined_results, f, ensure_ascii=False, indent=2)
            print(f"\nCombined results saved to {output_path}")
        
        return combined_results

