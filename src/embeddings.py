"""
embeddings.py
HuggingFace embedding modeli yönetimi
"""

from langchain.embeddings import HuggingFaceEmbeddings
from typing import List
import numpy as np


class EmbeddingManager:
    """Embedding işlemlerini yöneten sınıf"""
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Args:
            model_name: HuggingFace model adı
        """
        self.model_name = model_name
        
        print(f"🧠 Embedding modeli yükleniyor: {model_name}")
        
        # HuggingFace embeddings oluştur
        self.embedding_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        print(f"✅ Embedding modeli hazır!")
        
        # Test embedding ile boyutu öğren
        test_embedding = self.embed_query("test")
        self.embedding_dimension = len(test_embedding)
        print(f"📊 Embedding boyutu: {self.embedding_dimension}")
    
    def embed_query(self, text: str) -> List[float]:
        """Tek bir metin için embedding oluşturur"""
        return self.embedding_model.embed_query(text)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Birden fazla metin için embedding oluşturur"""
        return self.embedding_model.embed_documents(texts)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """İki embedding arasındaki cosine similarity hesaplar"""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        return float(similarity)
    
    def get_model_info(self) -> dict:
        """Model bilgilerini döndürür"""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "device": "cpu",
            "normalization": True
        }