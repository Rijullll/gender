import streamlit as st
import pandas as pd
import numpy as np
import base64
import requests
import io
import os
import sys
import time
from PIL import Image, ImageEnhance, ImageOps

# --- AUTO INSTALL LIBRARIES ON DEMAND ---
try:
    import pypdf
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    import pypdf

# Set Streamlit Page Configuration
st.set_page_config(
    page_title="DocMind AI - Streamlit Document Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PREMIUM GLASSMORPHISM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');

    /* Global Fonts */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Outfit', sans-serif;
    }

    /* Gradient Title */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #3b82f6, #8b5cf6, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }

    .tagline {
        font-size: 1.1rem;
        color: #94a3b8;
        margin-bottom: 2rem;
    }

    /* Glassmorphism Cards */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    }
    
    .light-glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(0, 0, 0, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.05);
    }

    /* Login Screen Container */
    .login-container {
        max-width: 420px;
        margin: 80px auto;
        text-align: center;
    }

    .login-logo {
        background: #3b82f6;
        color: white;
        width: 64px;
        height: 64px;
        border-radius: 16px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 20px auto;
        font-size: 32px;
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
    }

    /* Badge styles */
    .ocr-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }

    /* Preset prompt chips */
    .preset-chip-btn {
        margin: 4px;
        border-radius: 20px;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: #475569;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #64748b;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATES INITIALIZATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if 'docs' not in st.session_state:
    st.session_state.docs = {}  # fileId -> doc dict

if 'active_doc_id' not in st.session_state:
    st.session_state.active_doc_id = None

if 'chat_histories' not in st.session_state:
    st.session_state.chat_histories = {
        'global': [
            {"role": "assistant", "content": "Hello! I am your DocMind AI Assistant. Upload documents to get started. I will perform OCR and auto-analyze their content, then answer any questions you have!"}
        ]
    }

# --- AUTHENTICATION LAYER ---
def render_login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<div class="login-logo">🧠</div>', unsafe_allow_html=True)
    st.markdown('<h2>DocMind AI</h2>', unsafe_allow_html=True)
    st.markdown('<p style="color: #94a3b8; margin-bottom: 24px;">AI Document Analyzer Agent Portal</p>', unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", value="admin", placeholder="Enter username")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        submit = st.form_submit_button("Sign In")
        
        if submit:
            if username == "admin" and password == "password":
                st.session_state.logged_in = True
                st.success("Access Granted! Loading portal...")
                time.sleep(0.5)
                st.rerun()
            else:
                st.error("Invalid credentials. Try admin / password.")
                
    st.markdown('</div>', unsafe_allow_html=True)

# --- API HELPER FUNCTIONS ---
def call_gemini(api_key, model, prompt, mime_type=None, b64_data=None, system_prompt=None):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    parts = []
    if mime_type and b64_data:
        parts.append({
            "inline_data": {
                "mime_type": mime_type,
                "data": b64_data
            }
        })
    parts.append({"text": prompt})
    
    payload = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": {"temperature": 0.15}
    }
    
    if system_prompt:
        payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        if response.status_code != 200:
            return f"Error ({response.status_code}): {response.text}"
        data = response.json()
        if "candidates" in data and data["candidates"][0]["content"]["parts"][0]["text"]:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return "Empty or malformed API response."
    except Exception as e:
        return f"API Exception: {str(e)}"

def call_openai(api_key, model, prompt, mime_type=None, b64_data=None, system_prompt=None):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
        
    content_list = [{"type": "text", "text": prompt}]
    if mime_type and b64_data and mime_type.startswith("image/"):
        content_list.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type};base64,{b64_data}"}
        })
        
    messages.append({"role": "user", "content": content_list})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.15
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            return f"Error ({response.status_code}): {response.text}"
        data = response.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API Exception: {str(e)}"

# --- AUTO PROCESS FUNCTION ---
def run_ocr_and_analysis(file_id, file_name, file_type, file_bytes, api_key, provider, model_name, system_prompt):
    # Perform OCR
    b64_content = base64.b64encode(file_bytes).decode("utf-8")
    ocr_prompt = "Perform OCR on this document. Extract all readable text. Maintain paragraphs, lists, tables, structural headers, numbers, and dates. Output only the extracted document text without any introductory comments or pleasantries."
    
    extracted = ""
    if not api_key:
        extracted = "API key missing during upload. Please set your API key in the sidebar and click '⚡ Run OCR & AI Analysis' to extract text."
        st.session_state.docs[file_id]["extracted_text"] = extracted
        st.session_state.docs[file_id]["status"] = "key_missing"
        return

    try:
        if provider == "Google Gemini":
            extracted = call_gemini(api_key, model_name, ocr_prompt, 
                                    mime_type=file_type, 
                                    b64_data=b64_content, 
                                    system_prompt="You are a professional document OCR digitizer. Output only raw document text.")
        else:
            if file_type == "application/pdf":
                pdf_reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page_idx, page in enumerate(pdf_reader.pages):
                    extracted += f"--- PAGE {page_idx+1} ---\n"
                    extracted += page.extract_text() + "\n\n"
            else:
                extracted = call_openai(api_key, model_name, ocr_prompt, 
                                        mime_type=file_type, 
                                        b64_data=b64_content)
        
        st.session_state.docs[file_id]["extracted_text"] = extracted
        st.session_state.docs[file_id]["status"] = "done"
    except Exception as e:
        st.session_state.docs[file_id]["extracted_text"] = f"OCR Error: {str(e)}"
        st.session_state.docs[file_id]["status"] = "error"
        return

    # Auto generate summary
    if extracted and not extracted.startswith("OCR Error"):
        sum_prompt = f"Analyze this document. Perform the following tasks:\n1. Identify the Document Type.\n2. Write a 3-5 sentence concise summary.\n3. List 3 key topics.\n4. Extract key dates/metadata.\n\nDocument Extracted Text:\n{extracted[:20000]}"
        
        try:
            summary_res = ""
            if provider == "Google Gemini":
                summary_res = call_gemini(api_key, model_name, sum_prompt, system_prompt=system_prompt)
            else:
                summary_res = call_openai(api_key, model_name, sum_prompt, system_prompt=system_prompt)
                
            st.session_state.docs[file_id]["summary"] = summary_res
            st.session_state.chat_histories[file_id] = [
                {"role": "assistant", "content": f"### Document Analyzed: **{file_name}**\n\n{summary_res}"}
            ]
        except Exception as e:
            st.session_state.docs[file_id]["summary"] = f"Summary generation error: {str(e)}"

# --- MAIN APP LOGIC ---
def render_app():
    # SIDEBAR SETUP
    with st.sidebar:
        st.markdown('<div class="brand"><h3>🧠 DocMind AI Portal</h3></div>', unsafe_allow_html=True)
        st.write("")
        
        # Logout button
        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
        st.divider()
        
        # API Settings
        st.subheader("⚙️ API Configuration")
        provider = st.radio("AI Provider", ["Google Gemini", "OpenAI"], index=0)
        
        api_key = ""
        model_name = ""
        
        if provider == "Google Gemini":
            api_key = st.text_input("Gemini API Key", type="password", 
                                    value=os.getenv("GEMINI_API_KEY", ""),
                                    placeholder="Paste APIzaSy...")
            model_name = st.selectbox("Model", ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-1.5-flash", "gemini-1.5-pro"])
        else:
            api_key = st.text_input("OpenAI API Key", type="password", 
                                    value=os.getenv("OPENAI_API_KEY", ""),
                                    placeholder="Paste sk-...")
            model_name = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"])
            
        system_prompt = st.text_area("System Prompt", 
                                     value="You are an advanced AI Document Analyzer. Answer questions using ONLY the facts extracted from the uploaded document(s). If the information is not contained in the text, politely state that you cannot find it. Quote relevant passages, maintain precision, and avoid hallucinating.",
                                     height=150)
        
        st.divider()
        
        # Document Uploader in Sidebar (available always)
        st.subheader("📤 Upload More Files")
        uploaded_files = st.file_uploader("Upload PDF or Image", 
                                         type=["pdf", "png", "jpg", "jpeg", "webp"], 
                                         accept_multiple_files=True,
                                         key="sidebar_uploader")
        
        if uploaded_files:
            for file in uploaded_files:
                file_id = f"doc_{file.name}_{file.size}"
                if file_id not in st.session_state.docs:
                    file_bytes = file.read()
                    
                    st.session_state.docs[file_id] = {
                        "id": file_id,
                        "name": file.name,
                        "type": file.type,
                        "raw_bytes": file_bytes,
                        "processed_bytes": file_bytes,
                        "extracted_text": "",
                        "summary": "",
                        "status": "pending"
                    }
                    st.session_state.active_doc_id = file_id
                    
                    # Run auto-processing immediately
                    with st.status(f"Processing {file.name}..."):
                        run_ocr_and_analysis(file_id, file.name, file.type, file_bytes, api_key, provider, model_name, system_prompt)
                    st.rerun()
            
        # Document List Switcher
        if st.session_state.docs:
            st.subheader("📄 Document List")
            doc_options = {doc["name"]: doc_id for doc_id, doc in st.session_state.docs.items()}
            
            # Find index of current active doc name
            active_doc_name = None
            for name, doc_id in doc_options.items():
                if doc_id == st.session_state.active_doc_id:
                    active_doc_name = name
                    break
            
            selected_name = st.selectbox("Select Active Document", 
                                         options=list(doc_options.keys()),
                                         index=list(doc_options.keys()).index(active_doc_name) if active_doc_name else 0)
            
            st.session_state.active_doc_id = doc_options[selected_name]
            
            if st.button("🗑️ Delete Current Document", use_container_width=True):
                del_id = st.session_state.active_doc_id
                del st.session_state.docs[del_id]
                if del_id in st.session_state.chat_histories:
                    del st.session_state.chat_histories[del_id]
                
                st.session_state.active_doc_id = list(st.session_state.docs.keys())[0] if st.session_state.docs else None
                st.toast("Document deleted!")
                st.rerun()

    # MAIN SCREEN
    st.markdown('<h1 class="main-title">DocMind AI</h1>', unsafe_allow_html=True)
    st.markdown('<p class="tagline">Explore, edit, OCR, and converse with your documents side-by-side.</p>', unsafe_allow_html=True)

    # Empty State Uploader (highly visible in main panel when no documents exist)
    if not st.session_state.docs:
        st.markdown('<div class="glass-card" style="text-align: center; padding: 40px; margin-top: 20px;">', unsafe_allow_html=True)
        st.markdown('<h3>📤 Upload your first document</h3>', unsafe_allow_html=True)
        st.markdown('<p style="color: #94a3b8; margin-bottom: 24px;">Drag and drop a PDF or image here. OCR and AI summarization will run automatically on upload.</p>', unsafe_allow_html=True)
        
        main_uploaded_files = st.file_uploader("Choose files", 
                                               type=["pdf", "png", "jpg", "jpeg", "webp"], 
                                               accept_multiple_files=True,
                                               key="main_uploader")
        
        if main_uploaded_files:
            for file in main_uploaded_files:
                file_id = f"doc_{file.name}_{file.size}"
                if file_id not in st.session_state.docs:
                    file_bytes = file.read()
                    st.session_state.docs[file_id] = {
                        "id": file_id,
                        "name": file.name,
                        "type": file.type,
                        "raw_bytes": file_bytes,
                        "processed_bytes": file_bytes,
                        "extracted_text": "",
                        "summary": "",
                        "status": "pending"
                    }
                    st.session_state.active_doc_id = file_id
                    
                    with st.status(f"Processing {file.name}..."):
                        run_ocr_and_analysis(file_id, file.name, file.type, file_bytes, api_key, provider, model_name, system_prompt)
            st.rerun()
            
        st.markdown('</div>', unsafe_allow_html=True)
        return

    active_doc = st.session_state.docs[st.session_state.active_doc_id]
    
    # 2-Column Responsive Workspace: Left for Viewer/Scanner, Right for Chat
    col_viewer, col_chat = st.columns([1.1, 0.9])
    
    with col_viewer:
        st.subheader("📄 Document Control Panel")
        tab_preview, tab_scanner, tab_ocr = st.tabs(["👁️ Preview", "⚙️ Scanner / Editor", "📝 Extracted Text"])
        
        # -- TAB: PREVIEW --
        with tab_preview:
            if active_doc["type"] == "application/pdf":
                st.info("PDF document uploaded successfully. Preview text in the Extracted Text tab.")
                try:
                    pdf_reader = pypdf.PdfReader(io.BytesIO(active_doc["processed_bytes"]))
                    st.write(f"**Total Pages**: {len(pdf_reader.pages)}")
                except Exception as e:
                    st.error("Error reading PDF metadata.")
            else:
                # Image render
                image = Image.open(io.BytesIO(active_doc["processed_bytes"]))
                st.image(image, caption=active_doc["name"], use_container_width=True)
                
        # -- TAB: SCANNER / EDITOR --
        with tab_scanner:
            if active_doc["type"] == "application/pdf":
                st.warning("Image adjustments (rotation, contrast, brightness) are only supported for image uploads (PNG, JPG, WEBP).")
            else:
                st.markdown("#### Crop & Image Enhancements")
                
                # Image adjustments interface
                col_s1, col_s2 = st.columns(2)
                with col_s1:
                    rotate_deg = st.selectbox("Rotate Image", [0, 90, 180, 270], index=0)
                    brightness = st.slider("Brightness Boost", -100, 100, 0, step=5)
                with col_s2:
                    contrast = st.slider("Contrast Boost", -100, 100, 0, step=5)
                    filter_opt = st.selectbox("Color Filter", ["None", "Grayscale", "Black & White (High Contrast)"])
                
                apply_clicked = st.button("Apply Enhancements", use_container_width=True)
                
                if apply_clicked:
                    with st.spinner("Applying filters..."):
                        # Open original raw image
                        img = Image.open(io.BytesIO(active_doc["raw_bytes"]))
                        
                        # Rotate
                        if rotate_deg != 0:
                            img = img.rotate(-rotate_deg, expand=True)
                        
                        # Brightness
                        if brightness != 0:
                            enhancer = ImageEnhance.Brightness(img)
                            img = enhancer.enhance(1.0 + (brightness / 100.0))
                            
                        # Contrast
                        if contrast != 0:
                            enhancer = ImageEnhance.Contrast(img)
                            img = enhancer.enhance(1.0 + (contrast / 100.0))
                            
                        # Filter
                        if filter_opt == "Grayscale":
                            img = ImageOps.grayscale(img)
                        elif filter_opt == "Black & White (High Contrast)":
                            img = ImageOps.grayscale(img)
                            img = img.point(lambda x: 0 if x < 128 else 255, '1')
                        
                        # Save back
                        out_buffer = io.BytesIO()
                        img_format = "PNG" if active_doc["type"] == "image/png" else "JPEG"
                        img.save(out_buffer, format=img_format)
                        active_doc["processed_bytes"] = out_buffer.getvalue()
                        
                        # Re-run OCR automatically after adjustments
                        if api_key:
                            run_ocr_and_analysis(active_doc["id"], active_doc["name"], active_doc["type"], 
                                                 active_doc["processed_bytes"], api_key, provider, model_name, system_prompt)
                        st.toast("Filters applied and text re-analyzed!")
                        st.rerun()

        # -- TAB: EXTRACTED TEXT (OCR) --
        with tab_ocr:
            st.markdown("#### OCR Engine Status")
            
            trigger_ocr = False
            
            if active_doc["extracted_text"] == "" or active_doc["status"] == "key_missing":
                st.warning("OCR has not been run or is pending an API Key.")
                trigger_ocr = st.button("⚡ Run OCR & AI Analysis", use_container_width=True)
            else:
                st.markdown('<span class="ocr-badge">Extracted Text Ready</span>', unsafe_allow_html=True)
                st.write("")
                
                # Raw text text-area for editing or copying
                edited_text = st.text_area("Raw Extracted Text (Editable)", 
                                           value=active_doc["extracted_text"], 
                                           height=320)
                
                # Update text in memory if user edits it
                if edited_text != active_doc["extracted_text"]:
                    active_doc["extracted_text"] = edited_text
                    
                # Download button
                st.download_button("📥 Download Extracted Text", 
                                   data=active_doc["extracted_text"], 
                                   file_name=f"{active_doc['name']}_ocr.txt", 
                                   mime="text/plain", 
                                   use_container_width=True)
                
                # Re-run button
                trigger_ocr = st.button("🔄 Re-run OCR & AI Analysis", use_container_width=True)
                
            if trigger_ocr:
                if not api_key:
                    st.error("Please configure your API key in the sidebar settings first!")
                else:
                    with st.status("Executing Multimodal OCR and Text Extraction..."):
                        run_ocr_and_analysis(active_doc["id"], active_doc["name"], active_doc["type"], 
                                             active_doc["processed_bytes"], api_key, provider, model_name, system_prompt)
                    st.toast("OCR and AI analysis complete!")
                    st.rerun()

    # --- RIGHT COLUMN: CHAT INTERFACE ---
    with col_chat:
        st.subheader("💬 AI Chat Assistant")
        
        # Chat scope selection
        scope = st.selectbox("Conversation Scope", ["Active Document Only", "All Documents Combined"])
        
        active_scope_id = active_doc["id"] if (scope == "Active Document Only" and active_doc) else "global"
        
        if active_scope_id not in st.session_state.chat_histories:
            st.session_state.chat_histories[active_scope_id] = [
                {"role": "assistant", "content": "I am ready. Ask me any questions about the document."}
            ]
            
        chat_history = st.session_state.chat_histories[active_scope_id]
        
        # Render historical chat logs
        chat_container = st.container(height=380)
        with chat_container:
            for message in chat_history:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    
        # Presets prompt chips
        st.write("")
        st.markdown("**Quick Prompts:**")
        col_p1, col_p2, col_p3 = st.columns(3)
        
        preset_val = None
        with col_p1:
            if st.button("📋 Summarize", key="chip_sum", use_container_width=True):
                preset_val = "Summarize this document."
        with col_p2:
            if st.button("📅 Find Deadlines", key="chip_dates", use_container_width=True):
                preset_val = "Find all dates, deadlines, and timeline points."
        with col_p3:
            if st.button("📌 Action Items", key="chip_actions", use_container_width=True):
                preset_val = "List all important action items and tasks."
                
        # Chat input field
        user_query = st.chat_input("Ask a question about document context...")
        
        if preset_val:
            user_query = preset_val
            
        if user_query:
            if not api_key:
                st.error("Please configure your API key in the sidebar settings first!")
            elif scope == "Active Document Only" and (active_doc["extracted_text"] == "" or active_doc["status"] == "key_missing"):
                st.error("Please run OCR on the active document first to build text context!")
            else:
                # Add user query to log
                chat_history.append({"role": "user", "content": user_query})
                with chat_container:
                    with st.chat_message("user"):
                        st.write(user_query)
                
                # Build context prompt
                context_str = ""
                if scope == "Active Document Only":
                    context_str = f"Active Document Name: {active_doc['name']}\nExtracted text:\n{active_doc['extracted_text']}"
                else:
                    # All docs
                    for idx, (doc_id, doc) in enumerate(st.session_state.docs.items()):
                        if doc["extracted_text"] != "" and doc["status"] == "done":
                            context_str += f"Document [{idx+1}] Name: {doc['name']}\nText:\n{doc['extracted_text']}\n---\n"
                
                prompt = f"""Use the document context below to answer the user's question. Answer using ONLY these facts. If not found, say so. Quote relevant sections.

--- CONTEXT ---
{context_str[:25000]}

--- USER QUESTION ---
{user_query}"""

                with st.spinner("AI thinking..."):
                    response = ""
                    if provider == "Google Gemini":
                        response = call_gemini(api_key, model_name, prompt, system_prompt=system_prompt)
                    else:
                        response = call_openai(api_key, model_name, prompt, system_prompt=system_prompt)
                        
                    chat_history.append({"role": "assistant", "content": response})
                    st.rerun()

# --- MAIN EXECUTION ROUTER ---
if not st.session_state.logged_in:
    render_login()
else:
    render_app()
