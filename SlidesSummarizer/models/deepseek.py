from models.base_model import BaseModel
from openai import OpenAI
import base64

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

class DeepSeekAPI(BaseModel):
    def __init__(self, config):
        super().__init__(config)
        self.model = config.model
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.api_url
        )
        self.create_ask_message = lambda question: {
            "role": "user",
            "content": [
                {"type": "text", "text": question},
            ],
        }
        self.create_ans_message = lambda ans: {
            "role": "assistant",
            "content": [
                {"type": "text", "text": ans},
            ],
        }
    
    def create_text_message(self, texts, question):
        content = []
        for text in texts:
            content.append({"type": "text", "text": text})
        content.append({"type": "text", "text": question})
        message = {
            "role": "user",
            "content": content
        }
        return message
        

    def predict(self, question, texts = None, images = None, history = None):
        self.clean_up()
        messages = self.process_message(question, texts, images, history)
        
        # 将复杂的OpenAI格式消息转换为DeepSeek支持的简单格式
        simple_messages = []
        for msg in messages:
            if isinstance(msg.get("content"), list):
                # 收集文本内容
                text_content = ""
                for content_item in msg["content"]:
                    if content_item.get("type") == "text":
                        text_content += content_item.get("text", "") + "\n"
                
                simple_messages.append({
                    "role": msg["role"],
                    "content": text_content.strip()
                })
            else:
                # 如果已经是简单格式，直接使用
                simple_messages.append(msg)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=simple_messages,
                temperature=self.config.temperature if hasattr(self.config, "temperature") else 0.7
             #  max_tokens=self.config.max_new_tokens,
            )
            result = response.choices[0].message.content
            messages.append(self.create_ans_message(result))
            return result, messages
            
        except Exception as e:
            print(f"Error calling DeepSeek API: {str(e)}")
            return "", messages
    
    def is_valid_history(self, history):
        if not isinstance(history, list):
            return False
        for item in history:
            if not isinstance(item, dict):
                return False
            if "role" not in item or "content" not in item:
                return False
        return True 