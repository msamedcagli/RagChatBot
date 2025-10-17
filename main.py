"""
main.py
RAG Chatbot'un komut satırından çalıştırılması
"""

import os
import sys
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.rag_pipeline import RAGPipeline


def main():
    """Ana fonksiyon"""
    
    print("="*80)
    print("🏛️  AKBANK RAG CHATBOT - İSTANBUL BÖLGE PLANI")
    print("="*80 + "\n")
    
    # PDF yolu
    pdf_path = "Data/2024-2028-İstanbul-bölge-planı-taslak.pdf"
    
    # PDF varlık kontrolü
    if not os.path.exists(pdf_path):
        print(f"❌ PDF bulunamadı: {pdf_path}")
        print("Lütfen PDF dosyasını Data/ klasörüne ekleyin.")
        return
    
    # Gemini API kullanımı
    print("🤖 Cevap üretimi için seçenek:")
    print("  1. Gemini API (daha kaliteli cevaplar)")
    print("  2. Local Mode (API gerekmez)")
    
    choice = input("\nSeçiminiz (1/2): ").strip()
    use_gemini = choice == "1"
    
    print("\n" + "="*80 + "\n")
    
    # RAG Pipeline oluştur
    pipeline = RAGPipeline(pdf_path=pdf_path, use_gemini=use_gemini)
    
    # Belgeyi indeksle
    pipeline.index_document()
    
    # İstatistikleri göster
    print("\n📊 SİSTEM İSTATİSTİKLERİ:")
    stats = pipeline.get_stats()
    for key, value in stats.items():
        print(f"  • {key}: {value}")
    
    # İnteraktif mod
    print("\n" + "="*80)
    print("💬 İNTERAKTİF SORU-CEVAP MODU")
    print("="*80)
    print("Çıkmak için 'quit' yazın")
    print("Modu değiştirmek için 'mode' yazın\n")
    
    while True:
        try:
            question = input("🙋 Sorunuz: ").strip()
            
            if not question:
                continue
            
            if question.lower() in ['quit', 'exit', 'çık', 'q']:
                print("\n👋 Görüşmek üzere!")
                break
            
            if question.lower() == 'mode':
                pipeline.use_gemini = not pipeline.use_gemini
                mode_text = "Gemini API" if pipeline.use_gemini else "Local Mode"
                print(f"🔄 Mod değiştirildi: {mode_text}\n")
                continue
            
            # Soruyu işle
            result = pipeline.query(question, n_results=3)
            
        except KeyboardInterrupt:
            print("\n\n👋 Program sonlandırıldı!")
            break
        except Exception as e:
            print(f"\n❌ Hata: {e}\n")


if __name__ == "__main__":
    main()