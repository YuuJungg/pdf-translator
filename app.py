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
    
    # Check for API key in secrets for auto-fill
    default_key = st.secrets.get("GOOGLE_API_KEY", "")
    api_key = st.text_input(
        "Enter your Gemini API Key", 
        value=default_key,
        type="password", 
        help="Get your key at https://aistudio.google.com/app/apikey"
    )
    
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
uploaded_file = st.file_uploader("Upload English PDF", type=["pdf"], label_visibility="collapsed")

if uploaded_file and api_key:
    st.markdown(f"<div class='status-badge'>File ready: {uploaded_file.name}</div>", unsafe_allow_html=True)
    
    if st.button("Generate Professional Insights"):
            try:
                main_progress = st.progress(0, text="Process starting...")
                status_text = st.empty()
                
                status_text.markdown("🔍 **Analyzing PDF structure...**")
                
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                processor = PDFProcessor(tmp_path)
                model_name = 'gemini-1.5-flash-002' if "Flash" in model_choice else 'gemini-1.5-pro-002'
                llm = LLMService(api_key=api_key, model_name=model_name)

                page_count = processor.get_page_count()
                status_text.markdown(f"📖 **Reading {page_count} pages...**")
                pages = processor.extract_text_by_pages()
                
                # CHUNKING LOGIC (10 pages per chunk)
                chunk_size = 10
                chunks = [pages[i:i + chunk_size] for i in range(0, len(pages), chunk_size)]
                total_chunks = len(chunks)
                
                translated_chunks = []
                summary_chunks = []
                
                res_col1, res_col2 = st.columns(2)
                with res_col1:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.markdown("### 🇰🇷 AI Translation")
                    trans_placeholder = st.empty()
                    st.markdown("</div>", unsafe_allow_html=True)
                
                with res_col2:
                    st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                    st.markdown("### 📝 Executive Summary")
                    sum_placeholder = st.empty()
                    st.markdown("</div>", unsafe_allow_html=True)

                for idx, chunk in enumerate(chunks):
                    chunk_text = "\n\n".join(chunk)
                    current_progress = (idx / total_chunks)
                    main_progress.progress(current_progress, text=f"Processing segments ({idx+1}/{total_chunks})...")
                    
                    # Parallel or Sequential processing
                    status_text.markdown(f"🧠 **AI working on segment {idx+1} of {total_chunks}...**")
                    
                    chunk_trans = llm.translate_text(chunk_text)
                    translated_chunks.append(chunk_trans)
                    trans_placeholder.info(f"Progress: {int((idx+1)/total_chunks*100)}% translated")
                    
                    chunk_sum = llm.summarize_text(chunk_text)
                    summary_chunks.append(chunk_sum)
                    sum_placeholder.info(f"Progress: {int((idx+1)/total_chunks*100)}% summarized")

                main_progress.progress(1.0, text="Processing complete!")
                
                # Combine results
                final_translation = "\n\n".join(translated_chunks)
                # For summary, we might want a final summary of summaries if it's too long
                if len(summary_chunks) > 1:
                    status_text.markdown("🎯 **Synthesizing final executive summary...**")
                    final_summary = llm.summarize_text("\n\n".join(summary_chunks))
                else:
                    final_summary = summary_chunks[0]

                trans_placeholder.success("Translation Complete")
                with res_col1:
                    st.download_button("Download Translation (.md)", final_translation, "translation.md", "text/markdown", key="dl_trans")
                
                sum_placeholder.success("Summary Complete")
                with res_col2:
                    st.download_button("Download Summary (.md)", final_summary, "summary.md", "text/markdown", key="dl_sum")
                
                status_text.markdown("✨ **Your professional insights are ready below.**")
                
                processor.close()
                os.unlink(tmp_path)

            except Exception as e:
                st.error(f"Error during processing: {e}")
                st.info("Tip: If you see a '404' error, try clicking 'Reboot app' in the Manage menu.")
                
elif not api_key and uploaded_file:
    st.warning("Please enter your API Key in the sidebar to proceed.")
else:
    st.markdown("<p style='text-align: center; color: #64748b;'>Drop your English research paper or document above to begin.</p>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center; color: #475569;'>© 2026 AI PDF Insight Premium. All rights reserved.</p>", unsafe_allow_html=True)
