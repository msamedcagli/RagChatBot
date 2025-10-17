"""
data_processor.py
PDF belgelerini okuma ve metin parçalama (chunking) işlemleri
"""

from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from tqdm import tqdm
from typing import List, Optional


class PDFProcessor:
    """PDF belgelerini işleyen sınıf"""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def extract_text_from_pdf(self, pdf_path: str) -> Optional[str]:
        """PDF dosyasından metin çıkarır"""
        try:
            reader = PdfReader(pdf_path)
            text = ""
            
            print(f"📖 PDF okunuyor: {pdf_path}")
            print(f"📄 Toplam sayfa sayısı: {len(reader.pages)}")
            
            for i, page in enumerate(tqdm(reader.pages, desc="Sayfalar işleniyor")):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            
            print(f"✅ PDF başarıyla okundu!")
            print(f"📊 Toplam karakter: {len(text):,}")
            
            return text
            
        except Exception as e:
            print(f"❌ PDF okuma hatası: {e}")
            return None
    
    def split_text(self, text: str) -> List[str]:
        """Metni chunk'lara böler"""
        if not text:
            return []
        
        chunks = self.text_splitter.split_text(text)
        
        print(f"✂️ Metin bölümlendi!")
        print(f"📊 Toplam chunk sayısı: {len(chunks)}")
        
        return chunks
    
    def process_pdf(self, pdf_path: str) -> List[str]:
        """PDF'i okur ve chunk'lara böler"""
        text = self.extract_text_from_pdf(pdf_path)
        
        if not text:
            return []
        
        chunks = self.split_text(text)
        return chunks