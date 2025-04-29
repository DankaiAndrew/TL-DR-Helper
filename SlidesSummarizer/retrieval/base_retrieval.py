from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple

class BaseRetrieval(ABC):
    """检索系统基类"""
    
    def __init__(self, config):
        """初始化检索系统"""
        self.config = config
    
    @abstractmethod
    def retrieve(self, query: str, documents: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        根据查询检索最相关的文档
        
        参数:
            query: 查询文本
            documents: 待检索的文档列表
            top_k: 返回的最相关文档数量
            
        返回:
            检索到的文档列表，按相关性排序
        """
        pass
    
    def prepare_documents(self, documents: List[Dict[str, Any]]) -> Any:
        """
        预处理文档，创建索引或向量表示
        
        参数:
            documents: 文档列表
            
        返回:
            处理后的索引或向量表示
        """
        return documents  # 默认实现不做任何处理
    
    def process_query(self, query: str) -> Any:
        """
        处理查询文本
        
        参数:
            query: 查询文本
            
        返回:
            处理后的查询表示
        """
        return query  # 默认实现不做任何处理 