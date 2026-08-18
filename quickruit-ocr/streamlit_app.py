import os
import sys
import json
import cv2
import numpy as np
import streamlit as st
import pytesseract

# Ensure the app module path is resolved correctly for local imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.preprocessing import validate_image, preprocess_pipeline
from app.ocr import rotate_by_osd, execute_ocr
from app.parser import clean_text, extract_name, extract_id_number, extract_date_of_birth, extract_gender

# Page configuration
st.set_page_config(
    page_title="QuickRuit OCR Data Extractor",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for premium look
st.markdown(
    """
    <style>
        .stButton>button {
            background-color: #6366f1;
            color: white;
            border-radius: 8px;
            font-weight: 600;
            border: none;
            padding: 0.5rem 1rem;
            transition: all 0.2s;
        }
        .stButton>button:hover {
            background-color: #4f46e5;
            border: none;
            color: white;
            transform: translateY(-1px);
        }
        .header-glow {
            background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .metric-card {
            background-color: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.08);
            padding: 1.25rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        .metric-label {
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #9ca3af;
            margin-bottom: 0.25rem;
        }
        .metric-value {
            font-size: 1.2rem;
            font-weight: 600;
            color: #f3f4f6;
        }
        .metric-value-null {
            font-size: 1.2rem;
            font-weight: 500;
            color: rgba(156, 163, 175, 0.4);
            font-style: italic;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Title & Description
st.write(
    f"""
    <h1>⚡ <span class="header-glow">QuickRuit Standalone OCR</span></h1>
    <p style="font-size: 1.1rem; color: #9ca3af; margin-bottom: 2rem;">
        Extract structured fields from Aadhaar or PAN card images instantly using custom local image preprocessing and Tesseract OCR.
    </p>
    """,
    unsafe_allow_html=True
)

# Sidebar configurations
st.sidebar.markdown("### ⚙️ Engine Configurations")

# Allow manual override of Tesseract path directly in UI
default_tesseract_path = os.getenv("TESSERACT_CMD", "tesseract")
tesseract_path = st.sidebar.text_input(
    "Tesseract Binary Path",
    value=default_tesseract_path,
    help="Path to the tesseract executable. Default runs 'tesseract' globally."
)

# Preprocessing configs
threshold_method = st.sidebar.selectbox(
    "Binarization Method",
    options=["adaptive", "otsu"],
    index=0,
    help="Adaptive thresholding handles uneven lighting and shadows. Otsu is better for uniform scans."
)

st.sidebar.markdown("---")
st.sidebar.markdown(
    """
    ### 🛠️ Preprocessing Pipeline
    1. **Scale/Upscale**: Low resolution images are intelligently scaled up.
    2. **Grayscale**: Converted to single channel.
    3. **Bilateral Noise Reduction**: Removes camera grains while preserving card boundaries and text lines.
    4. **OSD Orientation Check**: Auto-rotates image (90/180/270 degrees) if text is misaligned.
    5. **Deskewing**: Detects horizontal text tilt and aligns the image.
    6. **Binarization**: Converts to pure black-and-white.
    """
)

# Main UI
uploaded_file = st.file_uploader(
    "Upload ID Image...",
    type=["png", "jpg", "jpeg", "webp", "bmp", "tiff"],
    help="Select a clean photo or scan of a PAN or Aadhaar card"
)

if uploaded_file is not None:
    # Set the custom path before processing
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Read bytes
    file_bytes = uploaded_file.read()
    
    # Run processing with loader
    with st.spinner("Processing image through pipeline (decoding, deskewing, binarizing)..."):
        try:
            # 1. Decode & Validate image
            raw_img = validate_image(file_bytes)
            
            # 2. Correct Orientation (OSD)
            oriented_img = rotate_by_osd(raw_img)
            
            # 3. Preprocess pipeline
            deskewed_gray, binary_img = preprocess_pipeline(oriented_img, threshold_method=threshold_method)
            
            # 4. Execute OCR with fallback
            raw_text = execute_ocr(binary_img, gray_img=deskewed_gray)
            cleaned_raw_text = clean_text(raw_text)
            
            # 5. Extract structured fields
            name = extract_name(cleaned_raw_text)
            id_number = extract_id_number(cleaned_raw_text)
            date_of_birth = extract_date_of_birth(cleaned_raw_text)
            gender = extract_gender(cleaned_raw_text)
            
            # Prepare result dictionary
            extracted_json = {
                "success": True,
                "data": {
                    "name": name,
                    "id_number": id_number,
                    "date_of_birth": date_of_birth,
                    "gender": gender
                },
                "raw_text": cleaned_raw_text
            }
            
            st.success("OCR Extraction Successful!")
            
            # Tabs for viewing results
            tab_dashboard, tab_json, tab_raw = st.tabs(["📊 Extraction Dashboard", "code JSON Output", "📝 Raw OCR Text"])
            
            with tab_dashboard:
                col_images, col_fields = st.columns([1.2, 1])
                
                with col_images:
                    st.markdown("#### 🖼️ Image Preprocessing")
                    img_view_option = st.radio(
                        "Display Mode",
                        options=["Original", "Binarized (OCR Input)", "Compare Side-by-Side"],
                        horizontal=True
                    )
                    
                    # Convert BGR (cv2 default) to RGB for Streamlit displaying
                    rgb_oriented = cv2.cvtColor(oriented_img, cv2.COLOR_BGR2RGB)
                    
                    if img_view_option == "Original":
                        st.image(rgb_oriented, use_column_width=True, caption="Uploaded & Oriented Image")
                    elif img_view_option == "Binarized (OCR Input)":
                        st.image(binary_img, use_column_width=True, caption="Preprocessed Binary Image")
                    else:
                        c1, c2 = st.columns(2)
                        with c1:
                            st.image(rgb_oriented, use_column_width=True, caption="Oriented Original")
                        with c2:
                            st.image(binary_img, use_column_width=True, caption="Binarized Input")
                            
                with col_fields:
                    st.markdown("#### 🔑 Extracted Fields")
                    
                    fields = [
                        ("Name", name),
                        ("ID / Document Number", id_number),
                        ("Date of Birth", date_of_birth),
                        ("Gender", gender)
                    ]
                    
                    for label, val in fields:
                        val_str = val if val else "Not detected"
                        val_class = "metric-value" if val else "metric-value-null"
                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <div class="metric-label">{label}</div>
                                <div class="{val_class}">{val_str}</div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        
                    # Download button for JSON
                    st.download_button(
                        label="📥 Download JSON Result",
                        data=json.dumps(extracted_json, indent=2),
                        file_name="ocr_extracted_data.json",
                        mime="application/json"
                    )
                    
            with tab_json:
                st.markdown("#### 🖥️ Raw API JSON Response")
                st.json(extracted_json)
                
            with tab_raw:
                st.markdown("#### 📄 Extracted Clean Text String")
                st.text_area("OCR Raw Text", value=cleaned_raw_text, height=350)
                
        except Exception as e:
            st.error(f"Processing failed: {str(e)}")
            st.info(
                """
                **Tip for Windows users:**
                If you encounter a "Tesseract OCR execution failed" error, Tesseract is likely not installed or not in your system PATH. 
                Please download it from [UB Mannheim's Tesseract Page](https://github.com/UB-Mannheim/tesseract/wiki) and enter the absolute path to your `tesseract.exe` (e.g. `C:\\Program Files\\Tesseract-OCR\\tesseract.exe`) in the **Tesseract Binary Path** input box in the sidebar.
                """
            )
else:
    # Demo empty state
    st.info("👋 Upload an ID document image to extract text and structured details.")
