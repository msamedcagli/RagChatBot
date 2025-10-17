"""
streamlit_app.py
İstanbul Boğazı temalı Streamlit web arayüzü - Import Fix
"""

import streamlit as st
import sys
import os

# Path ayarları - Mutlaka en üstte olmalı!
if __name__ == "__main__":
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    project_root = os.path.dirname(current_dir)
    
    # sys.path'e ekle
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Debug
    print(f"📂 Current file: {current_file}")
    print(f"📂 Project root: {project_root}")
    print(f"✅ sys.path updated")

# Şimdi import dene
try:
    from src.rag_pipeline import RAGPipeline
    from src.data_processor import PDFProcessor
    from src.embeddings import EmbeddingManager
    from src.vector_store import VectorStore
    IMPORTS_OK = True
except ImportError as e:
    IMPORTS_OK = False
    IMPORT_ERROR = str(e)


# Sayfa konfigürasyonu
st.set_page_config(
    page_title="İstanbul Bölge Planı RAG Chatbot",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import kontrolü
if not IMPORTS_OK:
    st.error(f"""
    ❌ **Import Hatası**
    
    Hata: `{IMPORT_ERROR}`
    
    **Çözüm:**
    1. Terminal'i kapatın
    2. Proje klasörüne gidin: `cd "D:\\Masaüstü\\Akbank -RagChatboot"`
    3. Çalıştırın: `streamlit run app/streamlit_app.py`
    
    **Not:** Streamlit'i app/ klasöründen DEĞİL, proje root klasöründen çalıştırın!
    """)
    st.code("""
# DOĞRU KULLANIM:
cd "D:\\Masaüstü\\Akbank -RagChatboot"
streamlit run app/streamlit_app.py
    """, language="bash")
    st.stop()

# Custom CSS - İstanbul Boğazı arka plan
st.markdown("""
<style>
    /* Ana container için Boğaz arka planı */
    .stApp {
        background: linear-gradient(rgba(0, 31, 63, 0.85), rgba(0, 31, 63, 0.85)),
                    url('https://images.unsplash.com/photo-1524231757912-21f4fe3a7200?q=80&w=2071');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Chat mesajları için stil */
    .chat-message {
        padding: 1.5rem;
        border-radius: 15px;
        margin-bottom: 1rem;
        display: flex;
        backdrop-filter: blur(10px);
        animation: fadeIn 0.5s;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .chat-message.user {
        background: linear-gradient(135deg, rgba(33, 147, 176, 0.9), rgba(109, 213, 237, 0.9));
        border-left: 5px solid #1e88e5;
    }
    
    .chat-message.assistant {
        background: linear-gradient(135deg, rgba(67, 97, 238, 0.9), rgba(114, 9, 183, 0.9));
        border-left: 5px solid #7b1fa2;
    }
    
    .chat-message .message {
        width: 100%;
        color: white;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    /* Başlık stilleri */
    h1, h2, h3 {
        color: white !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
    }
    
    /* Input alanları */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        color: #000000 !important;
        font-size: 1.1rem;
        padding: 0.75rem;
        border: 2px solid rgba(255, 255, 255, 0.3);
    }
    
    .stTextInput > div > div > input:focus {
        border: 2px solid #667eea;
        box-shadow: 0 0 15px rgba(102, 126, 234, 0.5);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #666666 !important;
    }
    
    /* Butonlar */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: transform 0.2s;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
    }
    
    /* Kartlar */
    .info-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: white;
        margin-bottom: 1rem;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.3);
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)


# Session state başlatma
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'indexed' not in st.session_state:
    st.session_state.indexed = False


def initialize_pipeline(use_gemini):
    """RAG Pipeline'ı başlatır"""
    try:
        with st.spinner("🚀 RAG Pipeline başlatılıyor..."):
            pdf_path = "Data/2024-2028-İstanbul-bölge-planı-taslak.pdf"
            
            # PDF varlık kontrolü
            if not os.path.exists(pdf_path):
                st.error(f"❌ PDF bulunamadı: {pdf_path}")
                st.info("Lütfen PDF'i Data/ klasörüne ekleyin.")
                return False
            
            pipeline = RAGPipeline(pdf_path=pdf_path, use_gemini=use_gemini)
            
            if not st.session_state.indexed:
                with st.spinner("📚 Belge indeksleniyor... (Bu işlem birkaç dakika sürebilir)"):
                    pipeline.index_document()
                    st.session_state.indexed = True
            
            st.session_state.pipeline = pipeline
            return True
    except Exception as e:
        st.error(f"❌ Pipeline başlatma hatası: {e}")
        import traceback
        st.code(traceback.format_exc())
        return False


def display_message(message, is_user=False):
    """Chat mesajını gösterir"""
    message_type = "user" if is_user else "assistant"
    icon = "🙋" if is_user else "🤖"
    
    st.markdown(f"""
    <div class="chat-message {message_type}">
        <div class="message">
            <strong>{icon} {"Siz" if is_user else "Asistan"}:</strong><br>
            {message}
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    """Ana uygulama"""
    
    # Başlık
    st.markdown("""
    <h1 style='text-align: center; font-size: 3rem; margin-bottom: 2rem;'>
        🏛️ İstanbul Bölge Planı RAG Chatbot
    </h1>
    <p style='text-align: center; color: white; font-size: 1.2rem; margin-bottom: 3rem;'>
        2024-2028 İstanbul Bölge Planı Taslak Belgesi Üzerinde Akıllı Asistan
    </p>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("### ⚙️ Ayarlar")
        
        # API seçimi
        use_gemini = st.checkbox("🤖 Gemini API Kullan", value=False, 
                                  help="Daha kaliteli cevaplar için Gemini API'yi aktif edin")
        
        st.markdown("---")
        
        # Pipeline başlat butonu
        if st.button("🚀 Sistemi Başlat", use_container_width=True):
            if initialize_pipeline(use_gemini):
                st.success("✅ Sistem hazır!")
        
        st.markdown("---")
        
        # İstatistikler
        if st.session_state.pipeline:
            st.markdown("### 📊 İstatistikler")
            stats = st.session_state.pipeline.get_stats()
            
            st.markdown(f"""
            <div class="info-card">
                <strong>Toplam Chunk:</strong> {stats['total_chunks']}<br>
                <strong>Vector DB:</strong> {stats['vector_db_size']}<br>
                <strong>Model:</strong> {stats['embedding_model'].split('/')[-1]}<br>
                <strong>Embedding Boyutu:</strong> {stats['embedding_dimension']}<br>
                <strong>Gemini:</strong> {"✅ Aktif" if stats['gemini_enabled'] else "❌ Pasif"}
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Örnek sorular
        st.markdown("### 💡 Örnek Sorular")
        example_questions = [
            "Ana hedefler nelerdir?",
            "Ulaşım planları nedir?",
            "Çevre politikaları neler?",
            "Kentsel dönüşüm nedir?"
        ]
        
        for q in example_questions:
            if st.button(q, key=f"example_{q}", use_container_width=True):
                st.session_state.current_question = q
        
        st.markdown("---")
        
        # Sohbeti temizle
        if st.button("🗑️ Sohbeti Temizle", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Ana alan
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat alanı
        chat_container = st.container()
        
        with chat_container:
            # Chat geçmişini göster
            for message in st.session_state.chat_history:
                display_message(message["question"], is_user=True)
                display_message(message["answer"], is_user=False)
        
        # Soru input alanı
        st.markdown("<br>", unsafe_allow_html=True)
        
        question = st.text_input(
            "Sorunuzu yazın:",
            placeholder="Örn: İstanbul bölge planının ana hedefleri nelerdir?",
            key="question_input",
            label_visibility="collapsed"
        )
        
        # Örnek sorudan gelen
        if 'current_question' in st.session_state and st.session_state.current_question:
            question = st.session_state.current_question
            st.session_state.current_question = None
        
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 4])
        
        with col_btn1:
            ask_button = st.button("📤 Gönder", use_container_width=True)
        
        with col_btn2:
            if st.button("🔄 Yenile", use_container_width=True):
                st.rerun()
        
        # Soru işleme
        if ask_button and question:
            if not st.session_state.pipeline:
                st.warning("⚠️ Lütfen önce 'Sistemi Başlat' butonuna tıklayın!")
            else:
                with st.spinner("🤔 Düşünüyorum..."):
                    try:
                        result = st.session_state.pipeline.query(question, n_results=3)
                        
                        # Chat geçmişine ekle
                        st.session_state.chat_history.append({
                            "question": question,
                            "answer": result["answer"]
                        })
                        
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")
                        import traceback
                        with st.expander("🔍 Detaylı Hata"):
                            st.code(traceback.format_exc())
    
    with col2:
        st.markdown("### 📚 Hakkında")
        st.markdown("""
        <div class="info-card">
            Bu chatbot, <strong>2024-2028 İstanbul Bölge Planı Taslak Belgesi</strong> 
            üzerinde RAG (Retrieval Augmented Generation) teknolojisi ile çalışır.
            <br><br>
            <strong>Özellikler:</strong><br>
            ✅ HuggingFace Embeddings<br>
            ✅ ChromaDB Vector Store<br>
            ✅ Gemini API Entegrasyonu<br>
            ✅ İnteraktif Sohbet<br>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🎓 Teknolojiler")
        st.markdown("""
        <div class="info-card">
            <strong>Embedding:</strong> sentence-transformers<br>
            <strong>Vector DB:</strong> ChromaDB<br>
            <strong>LLM:</strong> Gemini 1.5 Flash<br>
            <strong>Framework:</strong> LangChain<br>
            <strong>UI:</strong> Streamlit<br>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()