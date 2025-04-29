import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from PIL import Image
import os
from models.base_model import BaseModel

class Qwen2VL(BaseModel):
    """Qwen VL模型实现"""
    
    def __init__(self, config):
        """初始化Qwen VL模型"""
        super().__init__(config)
        
        print(f"Loading local Qwen VL model from: {self.config.model_id}")
        
        # 加载模型和tokenizer
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_id, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                self.config.model_id,
                device_map="auto",
                trust_remote_code=True,
                torch_dtype=torch.float16  # 使用半精度以节省内存
            ).eval()
            print("Model loaded successfully!")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, question, texts=None, images=None, history=None):
        """预测回答"""
        if history is None:
            history = []
        
        # 处理图像
        image_list = []
        if images:
            for img_path in images:
                try:
                    if os.path.exists(img_path):
                        image = Image.open(img_path).convert('RGB')
                        image_list.append(image)
                except Exception as e:
                    print(f"Error loading image {img_path}: {e}")
        
        # 处理文本
        if texts:
            # 将文本添加到问题中
            text_context = "\n\n".join(texts)
            if len(text_context) > 10000:  # 限制文本长度
                text_context = text_context[:10000] + "..."
            question = f"Paper content:\n{text_context}\n\nQuestion: {question}"
        
        try:
            # 构建信息
            if image_list:
                query = [{"image": image_list, "text": question}]
            else:
                query = question
            
            # 生成回答
            response, history = self.model.chat(self.tokenizer, query=query, history=history)
            
            return response, history
        except Exception as e:
            error_msg = f"Error during prediction: {str(e)}"
            print(error_msg)
            return error_msg, history
    
    def clean_up(self):
        """清理资源"""
        super().clean_up()
        # 如果需要额外的清理，在这里添加 