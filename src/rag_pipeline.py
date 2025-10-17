"""
rag_pipeline.py
Ana RAG (Retrieval Augmented Generation) pipeline
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict

from src.data_processor import PDFProcessor
from src.embeddings import EmbeddingManager
from src.vector_store import VectorStore


class RAGPipeline:
    """RAG sisteminin ana sınıfı"""
    
    def __init__(self, pdf_path: str, use_gemini: bool = False):
        self.pdf_path = pdf_path
        self.use_gemini = use_gemini
        
        print("🚀 RAG Pipeline başlatılıyor...\n")
        
        self.pdf_processor = PDFProcessor(chunk_size=1000, chunk_overlap=200)
        self.embedder = EmbeddingManager()
        self.vector_store = VectorStore(collection_name="istanbul_bolge_plani")
        
        if use_gemini:
            load_dotenv()
            api_key = os.getenv("GEMINI_API_KEY")
            if api_key:
                genai.configure(api_key=api_key)
                self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                print("✅ Gemini API hazır!")
            else:
                print("⚠️ GEMINI_API_KEY bulunamadı")
                self.use_gemini = False
        
        self.chunks = []
        print("\n✅ RAG Pipeline hazır!\n")
    
    def index_document(self):
        """PDF'i işler ve vector database'e ekler"""
        print("="*80)
        print("📚 BELGE İNDEKSLEME BAŞLIYOR")
        print("="*80 + "\n")
        
        self.chunks = self.pdf_processor.process_pdf(self.pdf_path)
        
        if not self.chunks:
            raise ValueError("❌ PDF işlenemedi!")
        
        print("\n🧠 Embedding'ler oluşturuluyor...")
        embeddings = self.embedder.embed_documents(self.chunks)
        
        print("\n💾 Vector database'e ekleniyor...")
        self.vector_store.add_documents(
            documents=self.chunks,
            embeddings=embeddings,
            batch_size=10
        )
        
        print("\n✅ İNDEKSLEME TAMAMLANDI!\n")
    
    def retrieve(self, query: str, n_results: int = 5) -> Dict:
        """Sorguya en uygun belgeleri getirir"""
        query_embedding = self.embedder.embed_query(query)
        documents, ids, distances = self.vector_store.query(query_embedding, n_results)
        
        return {
            "documents": documents,
            "ids": ids,
            "distances": distances
        }
    
    def generate_with_gemini(self, query: str, context: str) -> str:
        """Gemini API ile cevap üretir"""
        prompt = f"""Sen İstanbul Bölge Planı uzmanı bir asistansın. 
Aşağıdaki belgeden alınan bilgilere dayanarak soruyu cevapla.

BELGE İÇERİĞİ:
{context}

SORU: {query}

CEVAP:"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"⚠️ Gemini API hatası: {e}")
            return self.generate_local(query, context)
    
    def generate_local(self, query: str, context: str) -> str:
        """Local cevap üretir"""
        return f"""📄 İstanbul Bölge Planı belgesinde bulunan ilgili bilgiler:

{context[:1000]}...

📌 Not: Bu cevap belge içeriğinden otomatik olarak çıkarılmıştır."""
    
    def query(self, question: str, n_results: int = 5) -> Dict:
        """Tam RAG pipeline"""
        print(f"\n❓ SORU: {question}\n")
        print("🔍 İlgili belgeler aranıyor...")
        
        retrieval_results = self.retrieve(question, n_results)
        documents = retrieval_results["documents"]
        ids = retrieval_results["ids"]
        
        print(f"✅ {len(documents)} ilgili belge bulundu\n")
        
        context = "\n\n".join(documents)
        
        print("🤖 Cevap oluşturuluyor...\n")
        
        if self.use_gemini:
            answer = self.generate_with_gemini(question, context)
        else:
            answer = self.generate_local(question, context)
        
        print(f"💬 CEVAP:\n{answer}\n")
        
        return {
            "question": question,
            "answer": answer,
            "sources": ids,
            "source_documents": documents
        }
    
    def get_stats(self) -> Dict:
        """Pipeline istatistikleri"""
        return {
            "pdf_path": self.pdf_path,
            "total_chunks": len(self.chunks),
            "vector_db_size": self.vector_store.get_stats()["total_documents"],
            "embedding_model": self.embedder.model_name,
            "embedding_dimension": self.embedder.embedding_dimension,
            "gemini_enabled": self.use_gemini
        }