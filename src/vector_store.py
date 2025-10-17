"""
vector_store.py
ChromaDB vector database yönetimi
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Tuple
from tqdm import tqdm


class VectorStore:
    """ChromaDB vector database yönetimi"""
    
    def __init__(self, collection_name: str = "istanbul_bolge_plani"):
        self.collection_name = collection_name
        
        print(f"💾 ChromaDB başlatılıyor...")
        
        self.client = chromadb.Client(Settings(
            anonymized_telemetry=False,
            allow_reset=True
        ))
        
        try:
            self.collection = self.client.get_collection(name=collection_name)
            print(f"✅ Mevcut koleksiyon yüklendi: {collection_name}")
        except:
            self.collection = self.client.create_collection(
                name=collection_name,
                metadata={"description": "RAG Vector Database"}
            )
            print(f"✅ Yeni koleksiyon oluşturuldu: {collection_name}")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], 
                     batch_size: int = 10, metadata: List[Dict] = None):
        """Belgeleri veritabanına ekler"""
        print(f"\n⬆️ {len(documents)} belge ekleniyor...")
        
        if metadata is None:
            metadata = [{"source": f"chunk_{i}"} for i in range(len(documents))]
        
        for i in tqdm(range(0, len(documents), batch_size), desc="Batch'ler ekleniyor"):
            batch_docs = documents[i:i+batch_size]
            batch_embeddings = embeddings[i:i+batch_size]
            batch_metadata = metadata[i:i+batch_size]
            batch_ids = [f"chunk_{j}" for j in range(i, i+len(batch_docs))]
            
            self.collection.add(
                embeddings=batch_embeddings,
                documents=batch_docs,
                metadatas=batch_metadata,
                ids=batch_ids
            )
        
        print(f"✅ Toplam {len(documents)} belge eklendi!")
    
    def query(self, query_embedding: List[float], n_results: int = 5) -> Tuple[List[str], List[str], List[float]]:
        """Query embedding'e en yakın belgeleri getirir"""
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        documents = results['documents'][0]
        ids = results['ids'][0]
        distances = results['distances'][0] if 'distances' in results else []
        
        return documents, ids, distances
    
    def get_stats(self) -> Dict:
        """Veritabanı istatistiklerini döndürür"""
        return {
            "collection_name": self.collection_name,
            "total_documents": self.collection.count()
        }