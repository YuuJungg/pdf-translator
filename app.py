import streamlit as st
import os
from pdf_processor import PDFProcessor
from llm_service import LLMService
import tempfile
import time

# Load custom CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

st.set_page_config(
    page_title="AI PDF Insight - Premium Edition", 
    page_icon="🔮", 
    layout="wide",
    initial_sidebar_state="expanded"
)

if os.path.exists("styles.css"):
    local_css("styles.css")

# --- UI Layout ---

# Sidebar
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>🔮 AI Settings</h2>", unsafe_allow_html=True)
    st.markdown("---")
    api_key = st.text_input("Enter your Gemini API Key", type="password", help="Get your key at https://aistudio.google.com/app/apikey")
    
    st.markdown("### Model Preference")
    model_choice = st.selectbox("Select AI Model", ["Gemini 1.5 Flash (Fast)", "Gemini 1.5 Pro (Precision)"])
    
    st.markdown("---")
    st.markdown("### Export Settings")
    include_pages = st.checkbox("Include Page Markers", value=True)
    
    if not api_key:
        st.info("🗝️ API key is required to activate the AI.")

# Main Header
st.markdown("<div class='main-title'>AI PDF Insight</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Professional Large-Scale PDF Translation & Summarization</div>", unsafe_allow_html=True)

# Landing Grid
if not st.session_state.get('processed', False):
    col_feat1, col_feat2, col_feat3 = st.columns(3)
    with col_feat1:
        st.markdown("""
        <div class='glass-card'>
            <h3>🚀 Ultra Fast</h3>
            <p>100+ pages processed in seconds using Gemini's world-class context window.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_feat2:
        st.markdown("""
        <div class='glass-card'>
            <h3>💎 Pro Quality</h3>
            <p>Naturally translated and intelligently summarized by the latest AI models.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_feat3:
        st.markdown("""
        <div class='glass-card'>
            <h3>📁 Dual Output</h3>
            <p>Get two distinct professional markdown files: Full Translation & Executive Summary.</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# Main Action Area
uploaded_file = st.file_uploader("", type=["pdf"])

if uploaded_file and api_key:
    st.markdown(f"<div class='status-badge'>File ready: {uploaded_file.name}</div>", unsafe_allow_html=True)
    
    if st.button("Generate Professional Insights"):
        with st.container():
            try:
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                status_text.markdown("🔍 **Analyzing PDF structure...**")
                progress_bar.progress(10)
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                processor = PDFProcessor(tmp_path)
                model_name = 'gemini-1.5-flash' if "Flash" in model_choice else 'gemini-1.5-pro'
                
                # 가독성과 안정성을 위해 LLM 서비스 초기화 방식 개선
                llm = LLMService(api_key=api_key)
                import google.generativeai as genai
                llm.model = genai.GenerativeModel(model_name)

                page_count = processor.get_page_count()
                status_text.markdown(f"📖 **Extracting text from {page_count} pages...**")
                full_text = processor.extract_text()
                progress_bar.progress(30)
                
                # Use columns for results
                res_col1, res_col2 = st.columns(2)
                
                with res_col1:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.markdown("### 🇰🇷 AI Translation")
                    trans_placeholder = st.empty()
                    trans_placeholder.info("Applying AI linguistic processing...")
                    translation = llm.translate_text(full_text)
                    trans_placeholder.success("Translation Complete")
                    st.download_button("Download Translation (.md)", translation, "translation.md", "text/markdown")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                progress_bar.progress(70)
                
                with res_col2:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.markdown("### 📝 Executive Summary")
                    sum_placeholder = st.empty()
                    sum_placeholder.info("Contextualizing core value...")
                    summary = llm.summarize_text(full_text)
                    sum_placeholder.success("Summary Complete")
                    st.download_button("Download Summary (.md)", summary, "summary.md", "text/markdown")
                    st.markdown("</div>", unsafe_allow_html=True)
                
                progress_bar.progress(100)
                status_text.markdown("✨ **All insights generated successfully!**")
                
                processor.close()
                os.unlink(tmp_path)

            except Exception as e:
                st.error(f"Error during processing: {e}")
                
elif not api_key and uploaded_file:
    st.warning("Please enter your API Key in the sidebar to proceed.")
else:
    st.markdown("<p style='text-align: center; color: #64748b;'>Drop your English research paper or document above to begin.</p>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #475569;'>© 2026 AI PDF Insight Premium. All rights reserved.</p>", unsafe_allow_html=True)
