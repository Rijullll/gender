from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import HTMLResponse
import uvicorn

from app.schemas import OCRResponse, ExtractedData
from app.preprocessing import validate_image, preprocess_pipeline
from app.ocr import rotate_by_osd, execute_ocr
from app.parser import clean_text, extract_name, extract_id_number, extract_date_of_birth, extract_gender

app = FastAPI(
    title="QuickRuit OCR Data Extraction API",
    description="A lightweight standalone API to extract structured fields (Name, ID, DOB, Gender) from ID card images using OpenCV and Tesseract OCR.",
    version="1.0.0"
)

@app.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """
    Simple health check endpoint returning status ok.
    """
    return {"status": "ok"}

@app.post("/extract", response_model=OCRResponse)
async def extract_data(file: UploadFile = File(...)):
    """
    Accepts an ID card image file via multipart/form-data, preprocesses it,
    runs OCR, and extracts structural fields.
    """
    # 1. Validate file extension
    allowed_extensions = {"png", "jpg", "jpeg", "webp", "tiff", "bmp"}
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in allowed_extensions:
        return OCRResponse(
            success=False,
            error=f"Unsupported file format '{file_ext}'. Allowed formats: {', '.join(allowed_extensions)}"
        )

    try:
        # Read file bytes
        contents = await file.read()
        
        # 2. Decode and validate image
        try:
            raw_img = validate_image(contents)
        except ValueError as e:
            return OCRResponse(success=False, error=str(e))
            
        # 3. Orient image using OSD
        oriented_img = rotate_by_osd(raw_img)
        
        # 4. Preprocess (scaling, grayscale, denoising, deskewing, binarization)
        deskewed_gray, binary_img = preprocess_pipeline(oriented_img)
        
        # 5. Run OCR with fallback mechanisms
        raw_text = execute_ocr(binary_img, gray_img=deskewed_gray)
        cleaned_raw_text = clean_text(raw_text)
        
        # 6. Parse structured fields
        name = extract_name(cleaned_raw_text)
        id_number = extract_id_number(cleaned_raw_text)
        date_of_birth = extract_date_of_birth(cleaned_raw_text)
        gender = extract_gender(cleaned_raw_text)
        
        data = ExtractedData(
            name=name,
            id_number=id_number,
            date_of_birth=date_of_birth,
            gender=gender
        )
        
        return OCRResponse(
            success=True,
            data=data,
            raw_text=cleaned_raw_text
        )

    except Exception as e:
        return OCRResponse(
            success=False,
            error=f"An internal error occurred during processing: {str(e)}"
        )

@app.get("/", response_class=HTMLResponse)
def index_page():
    """
    Serves a beautiful, interactive, single-page web UI for testing the OCR API.
    """
    html_content = r"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>QuickRuit OCR Data Extractor</title>
        <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root {
                --primary: #6366f1;
                --primary-glow: rgba(99, 102, 241, 0.15);
                --primary-hover: #4f46e5;
                --background: #090d16;
                --panel: rgba(17, 24, 39, 0.7);
                --border: rgba(255, 255, 255, 0.08);
                --text-main: #f3f4f6;
                --text-muted: #9ca3af;
                --success: #10b981;
                --error: #ef4444;
            }

            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
            }

            body {
                font-family: 'Outfit', sans-serif;
                background-color: var(--background);
                color: var(--text-main);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                justify-content: space-between;
                overflow-x: hidden;
            }

            /* Ambient background glow */
            .bg-glow {
                position: absolute;
                width: 600px;
                height: 600px;
                background: radial-gradient(circle, rgba(99, 102, 241, 0.08) 0%, rgba(0,0,0,0) 70%);
                top: -10%;
                left: -10%;
                z-index: -1;
                pointer-events: none;
            }
            .bg-glow-right {
                position: absolute;
                width: 600px;
                height: 600px;
                background: radial-gradient(circle, rgba(139, 92, 246, 0.05) 0%, rgba(0,0,0,0) 70%);
                bottom: -10%;
                right: -10%;
                z-index: -1;
                pointer-events: none;
            }

            header {
                max-width: 1200px;
                width: 100%;
                margin: 0 auto;
                padding: 2rem 1.5rem;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }

            .logo {
                font-size: 1.5rem;
                font-weight: 700;
                background: linear-gradient(135deg, #818cf8 0%, #a78bfa 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                letter-spacing: -0.5px;
            }

            .badge {
                background: rgba(99, 102, 241, 0.1);
                border: 1px solid rgba(99, 102, 241, 0.2);
                color: #818cf8;
                padding: 0.35rem 0.75rem;
                border-radius: 9999px;
                font-size: 0.85rem;
                font-weight: 500;
            }

            main {
                max-width: 1200px;
                width: 100%;
                margin: 0 auto;
                padding: 0 1.5rem 3rem 1.5rem;
                flex-grow: 1;
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
            }

            @media (max-width: 900px) {
                main {
                    grid-template-columns: 1fr;
                }
            }

            .card {
                background: var(--panel);
                backdrop-filter: blur(16px);
                -webkit-backdrop-filter: blur(16px);
                border: 1px solid var(--border);
                border-radius: 1.25rem;
                padding: 2rem;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }

            .card-title {
                font-size: 1.25rem;
                font-weight: 600;
                margin-bottom: 0.5rem;
            }

            .dropzone {
                border: 2px dashed rgba(255, 255, 255, 0.15);
                border-radius: 1rem;
                padding: 3rem 1rem;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                background: rgba(255, 255, 255, 0.01);
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                gap: 1rem;
            }

            .dropzone:hover, .dropzone.dragover {
                border-color: var(--primary);
                background: var(--primary-glow);
                box-shadow: 0 0 20px rgba(99, 102, 241, 0.1);
            }

            .dropzone svg {
                width: 48px;
                height: 48px;
                color: var(--text-muted);
                transition: color 0.3s;
            }

            .dropzone:hover svg, .dropzone.dragover svg {
                color: var(--primary);
            }

            .dropzone p {
                font-size: 1rem;
                color: var(--text-muted);
            }

            .dropzone-sub {
                font-size: 0.8rem !important;
                color: rgba(156, 163, 175, 0.6) !important;
            }

            .preview-container {
                display: none;
                position: relative;
                width: 100%;
                border-radius: 0.75rem;
                overflow: hidden;
                border: 1px solid var(--border);
                aspect-ratio: 16/10;
                background: #000;
            }

            .preview-image {
                width: 100%;
                height: 100%;
                object-fit: contain;
            }

            .remove-btn {
                position: absolute;
                top: 10px;
                right: 10px;
                background: rgba(15, 23, 42, 0.8);
                border: 1px solid var(--border);
                border-radius: 50%;
                width: 32px;
                height: 32px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                color: var(--text-main);
                transition: background 0.2s;
            }

            .remove-btn:hover {
                background: var(--error);
            }

            button.btn-extract {
                background: var(--primary);
                color: #fff;
                border: none;
                padding: 0.85rem 1.5rem;
                font-size: 1rem;
                font-weight: 600;
                border-radius: 0.75rem;
                cursor: pointer;
                transition: all 0.2s;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 0.5rem;
                box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2);
            }

            button.btn-extract:hover {
                background: var(--primary-hover);
                transform: translateY(-1px);
            }

            button.btn-extract:disabled {
                background: rgba(255, 255, 255, 0.05);
                color: var(--text-muted);
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }

            /* Loader Animation */
            .loader {
                display: none;
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255,255,255,0.2);
                border-radius: 50%;
                border-top-color: #fff;
                animation: spin 0.8s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }

            /* Results Styling */
            .results-container {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
                height: 100%;
            }

            .tabs {
                display: flex;
                border-bottom: 1px solid var(--border);
                gap: 1.5rem;
            }

            .tab-btn {
                background: none;
                border: none;
                color: var(--text-muted);
                font-family: inherit;
                font-size: 0.95rem;
                font-weight: 500;
                padding-bottom: 0.75rem;
                cursor: pointer;
                position: relative;
                transition: color 0.2s;
            }

            .tab-btn:hover {
                color: var(--text-main);
            }

            .tab-btn.active {
                color: var(--primary);
            }

            .tab-btn.active::after {
                content: '';
                position: absolute;
                bottom: -1px;
                left: 0;
                right: 0;
                height: 2px;
                background: var(--primary);
                border-radius: 2px;
            }

            .tab-content {
                display: none;
                flex-grow: 1;
            }

            .tab-content.active {
                display: block;
            }

            .structured-fields {
                display: flex;
                flex-direction: column;
                gap: 1rem;
            }

            .field-row {
                background: rgba(255, 255, 255, 0.02);
                border: 1px solid var(--border);
                border-radius: 0.75rem;
                padding: 1rem;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .field-label {
                font-size: 0.85rem;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                color: var(--text-muted);
            }

            .field-value {
                font-size: 1rem;
                font-weight: 500;
            }

            .field-value.null-val {
                color: rgba(156, 163, 175, 0.4);
                font-style: italic;
            }

            .json-output {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid var(--border);
                border-radius: 0.75rem;
                padding: 1.25rem;
                overflow: auto;
                max-height: 400px;
                font-family: 'Fira Code', monospace;
                font-size: 0.9rem;
                color: #e2e8f0;
                white-space: pre-wrap;
            }

            .raw-text-output {
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid var(--border);
                border-radius: 0.75rem;
                padding: 1.25rem;
                font-family: inherit;
                line-height: 1.6;
                white-space: pre-wrap;
                max-height: 400px;
                overflow: auto;
                font-size: 0.95rem;
            }

            .empty-state {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: var(--text-muted);
                padding: 4rem 1rem;
                text-align: center;
                gap: 1rem;
            }

            .empty-state svg {
                width: 64px;
                height: 64px;
                color: rgba(255, 255, 255, 0.05);
            }

            footer {
                text-align: center;
                padding: 2rem;
                font-size: 0.85rem;
                color: var(--text-muted);
                border-top: 1px solid var(--border);
                margin-top: 2rem;
            }

            /* Custom styling for syntax highlighting in JSON */
            .json-key { color: #818cf8; }
            .json-string { color: #34d399; }
            .json-number { color: #fb7185; }
            .json-boolean { color: #f59e0b; }
            .json-null { color: #6b7280; }
        </style>
    </head>
    <body>
        <div class="bg-glow"></div>
        <div class="bg-glow-right"></div>

        <header>
            <div class="logo">QuickRuit OCR</div>
            <div class="badge">v1.0.0 (Local Engine)</div>
        </header>

        <main>
            <!-- Left Card: Upload & Preprocess -->
            <div class="card">
                <div>
                    <h2 class="card-title">Upload ID Document</h2>
                    <p style="font-size: 0.9rem; color: var(--text-muted);">Supported formats: PNG, JPG, JPEG, WEBP. Performs automatic skew correction, rotation, and custom filtering local-side.</p>
                </div>

                <div class="dropzone" id="dropzone">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path>
                    </svg>
                    <p>Drag and drop your file here, or click to browse</p>
                    <p class="dropzone-sub">Files are processed instantly on your machine</p>
                </div>

                <div class="preview-container" id="preview-container">
                    <img src="" alt="Upload Preview" class="preview-image" id="preview-image">
                    <div class="remove-btn" id="remove-btn" title="Remove image">
                        <svg style="width:16px;height:16px" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                    </div>
                </div>

                <input type="file" id="file-input" style="display: none;" accept="image/*">

                <button class="btn-extract" id="extract-btn" disabled>
                    <div class="loader" id="btn-loader"></div>
                    <span id="btn-text">Extract Data</span>
                </button>
            </div>

            <!-- Right Card: Extraction Results -->
            <div class="card">
                <div class="results-container">
                    <div class="tabs">
                        <button class="tab-btn active" onclick="switchTab('fields')">Structured Fields</button>
                        <button class="tab-btn" onclick="switchTab('json')">JSON Output</button>
                        <button class="tab-btn" onclick="switchTab('raw')">Raw OCR Text</button>
                    </div>

                    <div id="results-content" style="flex-grow: 1;">
                        <div class="empty-state" id="empty-state">
                            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                            </svg>
                            <p>Upload and run extract to see structured results</p>
                        </div>

                        <!-- Tab 1: Fields -->
                        <div class="tab-content active" id="tab-fields">
                            <div class="structured-fields" id="fields-list">
                                <!-- Populated dynamically -->
                            </div>
                        </div>

                        <!-- Tab 2: JSON -->
                        <div class="tab-content" id="tab-json">
                            <pre class="json-output" id="json-block"><code>{}</code></pre>
                        </div>

                        <!-- Tab 3: Raw Text -->
                        <div class="tab-content" id="tab-raw">
                            <div class="raw-text-output" id="raw-text-block"></div>
                        </div>
                    </div>
                </div>
            </div>
        </main>

        <footer>
            Built with FastAPI, OpenCV, and Tesseract OCR
        </footer>

        <script>
            const dropzone = document.getElementById('dropzone');
            const fileInput = document.getElementById('file-input');
            const previewContainer = document.getElementById('preview-container');
            const previewImage = document.getElementById('preview-image');
            const removeBtn = document.getElementById('remove-btn');
            const extractBtn = document.getElementById('extract-btn');
            const btnLoader = document.getElementById('btn-loader');
            const btnText = document.getElementById('btn-text');
            const emptyState = document.getElementById('empty-state');
            const fieldsList = document.getElementById('fields-list');
            const jsonBlock = document.getElementById('json-block');
            const rawTextBlock = document.getElementById('raw-text-block');

            let selectedFile = null;

            // Trigger browse
            dropzone.addEventListener('click', () => fileInput.click());

            // Handle file selection
            fileInput.addEventListener('change', (e) => {
                if (e.target.files.length > 0) {
                    handleFile(e.target.files[0]);
                }
            });

            // Drag and drop handlers
            ['dragenter', 'dragover'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropzone.classList.add('dragover');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropzone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    dropzone.classList.remove('dragover');
                }, false);
            });

            dropzone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt.files;
                if (files.length > 0) {
                    handleFile(files[0]);
                }
            });

            function handleFile(file) {
                if (!file.type.startsWith('image/')) {
                    alert('Please select an image file (PNG, JPG, WEBP).');
                    return;
                }
                selectedFile = file;
                const reader = new FileReader();
                reader.onload = (e) => {
                    previewImage.src = e.target.result;
                    dropzone.style.display = 'none';
                    previewContainer.style.display = 'block';
                    extractBtn.disabled = false;
                };
                reader.readAsDataURL(file);
            }

            // Remove file
            removeBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                selectedFile = null;
                fileInput.value = '';
                previewImage.src = '';
                previewContainer.style.display = 'none';
                dropzone.style.display = 'flex';
                extractBtn.disabled = true;
                resetResults();
            });

            function resetResults() {
                emptyState.style.display = 'flex';
                fieldsList.innerHTML = '';
                jsonBlock.innerHTML = '<code>{}</code>';
                rawTextBlock.innerHTML = '';
                document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
                document.getElementById('tab-fields').classList.add('active');
                document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
                document.querySelectorAll('.tab-btn')[0].classList.add('active');
            }

            // Tabs implementation
            window.switchTab = function(tabName) {
                document.querySelectorAll('.tab-btn').forEach(btn => {
                    btn.classList.remove('active');
                });
                document.querySelectorAll('.tab-content').forEach(content => {
                    content.classList.remove('active');
                });

                if (tabName === 'fields') {
                    document.getElementById('tab-fields').classList.add('active');
                    event.target.classList.add('active');
                } else if (tabName === 'json') {
                    document.getElementById('tab-json').classList.add('active');
                    event.target.classList.add('active');
                } else if (tabName === 'raw') {
                    document.getElementById('tab-raw').classList.add('active');
                    event.target.classList.add('active');
                }
            };

            // Call Extraction API
            extractBtn.addEventListener('click', async () => {
                if (!selectedFile) return;
                
                // Show loading
                extractBtn.disabled = true;
                btnLoader.style.display = 'inline-block';
                btnText.textContent = 'Processing OCR...';

                const formData = new FormData();
                formData.append('file', selectedFile);

                try {
                    const response = await fetch('/extract', {
                        method: 'POST',
                        body: formData
                    });

                    const result = await response.json();
                    
                    // Hide loading
                    extractBtn.disabled = false;
                    btnLoader.style.display = 'none';
                    btnText.textContent = 'Extract Data';

                    if (result.success) {
                        renderResults(result);
                    } else {
                        alert('Extraction failed: ' + (result.error || 'Unknown error'));
                    }
                } catch (error) {
                    extractBtn.disabled = false;
                    btnLoader.style.display = 'none';
                    btnText.textContent = 'Extract Data';
                    alert('Error connecting to the API server: ' + error.message);
                }
            });

            function syntaxHighlight(json) {
                if (typeof json != 'string') {
                    json = JSON.stringify(json, undefined, 2);
                }
                json = json.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
                return json.replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, function (match) {
                    var cls = 'number';
                    if (/^"/.test(match)) {
                        if (/:$/.test(match)) {
                            cls = 'key';
                        } else {
                            cls = 'string';
                        }
                    } else if (/true|false/.test(match)) {
                        cls = 'boolean';
                    } else if (/null/.test(match)) {
                        cls = 'null';
                    }
                    return '<span class="json-' + cls + '">' + match + '</span>';
                });
            }

            function renderResults(res) {
                emptyState.style.display = 'none';
                
                // 1. Render Fields Tab
                const fields = res.data;
                const fieldLabels = {
                    name: 'Name',
                    id_number: 'ID/Document Number',
                    date_of_birth: 'Date of Birth',
                    gender: 'Gender'
                };

                let html = '';
                for (const [key, value] of Object.entries(fields)) {
                    const label = fieldLabels[key] || key;
                    const displayVal = value !== null ? value : 'Not detected';
                    const valClass = value !== null ? '' : 'null-val';
                    html += `
                        <div class="field-row">
                            <span class="field-label">${label}</span>
                            <span class="field-value ${valClass}">${displayVal}</span>
                        </div>
                    `;
                }
                fieldsList.innerHTML = html;

                // 2. Render JSON Tab
                jsonBlock.innerHTML = syntaxHighlight(res);

                // 3. Render Raw Text
                rawTextBlock.textContent = res.raw_text || 'No text extracted.';
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
