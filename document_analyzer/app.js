/* ==========================================
   DOCMIND AI APPLICATION LOGIC (app.js)
   ========================================== */

// Configure PDF.js Worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js';

// --- STATE MANAGEMENT ---
const state = {
    files: [],            // Array of uploaded documents
    activeFileId: null,   // Selected document ID
    activePageNum: 1,     // PDF active page
    settings: {
        provider: 'gemini',
        geminiKey: '',
        openaiKey: '',
        model: 'gemini-3.5-flash',
        systemPrompt: 'You are an advanced AI Document Analyzer. Answer questions using ONLY the facts extracted from the uploaded document(s). If the information is not contained in the text, politely state that you cannot find it. Quote relevant passages, maintain precision, and avoid hallucinating.'
    },
    chatHistory: {
        global: [
            {
                role: 'assistant',
                content: 'Hello! I am your AI Document Analyzer Agent. Upload documents (PDF, PNG, JPG, WEBP) to get started. Once uploaded, I will perform OCR and analyze them. You can then ask questions about any document or all of them together.'
            }
        ]
    },
    // Scanner specific state
    scanner: {
        img: null,            // Image element being scanned
        canvas: null,         // Scanner HTML canvas
        ctx: null,            // Canvas context
        corners: [],          // [{x, y}, ...] 4 control handles
        draggedCornerIdx: -1, // Currently dragged corner index
        scale: 1,             // Scale of image inside canvas
        offsetX: 0,
        offsetY: 0,
        originalWidth: 0,
        originalHeight: 0
    }
};

// Available AI Models configuration
const modelConfigs = {
    gemini: [
        { name: 'Gemini 3.5 Flash (Fast, GA)', id: 'gemini-3.5-flash' },
        { name: 'Gemini 3.5 Flash Lite (Low Latency)', id: 'gemini-3.5-flash-lite' },
        { name: 'Gemini 1.5 Flash (Legacy)', id: 'gemini-1.5-flash' },
        { name: 'Gemini 1.5 Pro (Powerful, Detailed)', id: 'gemini-1.5-pro' }
    ],
    openai: [
        { name: 'GPT-4o (Smartest)', id: 'gpt-4o' },
        { name: 'GPT-4o Mini (Cost-efficient)', id: 'gpt-4o-mini' }
    ]
};

// Initialize settings from localStorage on load
function loadSettings() {
    const saved = localStorage.getItem('docmind_settings');
    if (saved) {
        try {
            state.settings = { ...state.settings, ...JSON.parse(saved) };
        } catch (e) {
            console.error('Failed to parse settings from localStorage:', e);
        }
    }
}

function saveSettings() {
    localStorage.setItem('docmind_settings', JSON.stringify(state.settings));
}

// --- DOM ELEMENTS ---
const dragDropZone = document.getElementById('drag-drop-zone');
const fileInput = document.getElementById('file-input');
const cameraScanBtn = document.getElementById('camera-scan-btn');
const docListEl = document.getElementById('document-list-el');
const docCounter = document.getElementById('doc-counter');
const emptyDocsEl = document.getElementById('empty-docs-el');
const themeToggleBtn = document.getElementById('theme-toggle-btn');
const openSettingsBtn = document.getElementById('open-settings-btn');
const closeSettingsBtn = document.getElementById('close-settings-btn');
const settingsModal = document.getElementById('settings-modal');
const saveSettingsBtn = document.getElementById('save-settings-btn');
const resetSettingsBtn = document.getElementById('reset-settings-btn');

const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const previewViewportEl = document.getElementById('preview-viewport-el');
const pdfPagination = document.getElementById('pdf-pagination');
const prevPageBtn = document.getElementById('prev-page-btn');
const nextPageBtn = document.getElementById('next-page-btn');
const currentPageNumEl = document.getElementById('current-page-num');
const totalPagesNumEl = document.getElementById('total-pages-num');

const scannerTabTrigger = document.getElementById('scanner-tab-trigger');
const scannerCanvas = document.getElementById('scanner-canvas');
const scannerAutoDetect = document.getElementById('scanner-auto-detect');
const scannerRotate = document.getElementById('scanner-rotate');
const scannerCropBtn = document.getElementById('scanner-crop-btn');
const brightnessSlider = document.getElementById('brightness-slider');
const brightnessVal = document.getElementById('brightness-val');
const contrastSlider = document.getElementById('contrast-slider');
const contrastVal = document.getElementById('contrast-val');
const filterBtns = document.querySelectorAll('.filter-btn-opt');
const scannerProcessFinal = document.getElementById('scanner-process-final');
const scannerCancel = document.getElementById('scanner-cancel');

const ocrSearchInput = document.getElementById('ocr-search-input');
const ocrCopyBtn = document.getElementById('ocr-copy-btn');
const ocrDownloadBtn = document.getElementById('ocr-download-btn');
const ocrProgressOverlay = document.getElementById('ocr-progress-overlay-el');
const ocrStatusMessage = document.getElementById('ocr-status-message');
const ocrProgressBarFill = document.getElementById('ocr-progress-bar-fill-el');
const ocrProgressPercent = document.getElementById('ocr-progress-percent');
const ocrTextDisplayEl = document.getElementById('ocr-text-display-el');

const chatScopeSelect = document.getElementById('chat-scope-select');
const chatMessagesEl = document.getElementById('chat-messages-el');
const chatInputTextarea = document.getElementById('chat-input-textarea');
const chatForm = document.getElementById('chat-form');
const voiceInputBtn = document.getElementById('voice-input-btn');
const exportChatBtn = document.getElementById('export-chat-btn');
const presetsContainer = document.getElementById('presets-el');

// Modal Fields
const apiProviderRadios = document.getElementsByName('api-provider');
const geminiKeyGroup = document.getElementById('gemini-key-group');
const openaiKeyGroup = document.getElementById('openai-key-group');
const geminiApiKeyInput = document.getElementById('gemini-api-key-input');
const openaiApiKeyInput = document.getElementById('openai-api-key-input');
const modelSelect = document.getElementById('model-select');
const systemPromptInput = document.getElementById('system-prompt-input');

// --- SETUP ON INITIAL LOAD ---
window.addEventListener('DOMContentLoaded', () => {
    loadSettings();
    initializeUI();
    setupEventListeners();
    lucide.createIcons();
});

function initializeUI() {
    // Apply theme
    const darkTheme = state.settings.theme === 'light' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', darkTheme);
    
    // Set API Key values in inputs
    geminiApiKeyInput.value = state.settings.geminiKey || '';
    openaiApiKeyInput.value = state.settings.openaiKey || '';
    systemPromptInput.value = state.settings.systemPrompt || '';

    // Check correct radio button
    const provider = state.settings.provider || 'gemini';
    document.querySelector(`input[name="api-provider"][value="${provider}"]`).checked = true;
    toggleProviderGroups(provider);
    populateModels(provider, state.settings.model);
}

function toggleProviderGroups(provider) {
    if (provider === 'gemini') {
        geminiKeyGroup.style.display = 'flex';
        openaiKeyGroup.style.display = 'none';
    } else {
        geminiKeyGroup.style.display = 'none';
        openaiKeyGroup.style.display = 'flex';
    }
}

function populateModels(provider, selectedModelId) {
    modelSelect.innerHTML = '';
    const configs = modelConfigs[provider] || [];
    configs.forEach(cfg => {
        const opt = document.createElement('option');
        opt.value = cfg.id;
        opt.textContent = cfg.name;
        if (cfg.id === selectedModelId) {
            opt.selected = true;
        }
        modelSelect.appendChild(opt);
    });
}

// --- EVENT LISTENERS ---
function setupEventListeners() {
    // Theme Toggle
    themeToggleBtn.addEventListener('click', () => {
        let currentTheme = document.documentElement.getAttribute('data-theme');
        let newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        document.documentElement.setAttribute('data-theme', newTheme);
        state.settings.theme = newTheme;
        saveSettings();
    });

    // Settings Modal
    openSettingsBtn.addEventListener('click', () => {
        initializeUI(); // Reset to current state
        settingsModal.style.display = 'flex';
    });
    
    const closeModal = () => settingsModal.style.display = 'none';
    closeSettingsBtn.addEventListener('click', closeModal);
    settingsModal.addEventListener('click', (e) => {
        if (e.target === settingsModal) closeModal();
    });

    // Toggle API Provider selection
    Array.from(apiProviderRadios).forEach(radio => {
        radio.addEventListener('change', (e) => {
            const provider = e.target.value;
            toggleProviderGroups(provider);
            populateModels(provider, provider === 'gemini' ? 'gemini-3.5-flash' : 'gpt-4o-mini');
        });
    });

    // Password view toggle
    document.querySelectorAll('.toggle-password-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const inputId = btn.getAttribute('data-input-id');
            const input = document.getElementById(inputId);
            const icon = btn.querySelector('i');
            if (input.type === 'password') {
                input.type = 'text';
                icon.setAttribute('data-lucide', 'eye-off');
            } else {
                input.type = 'password';
                icon.setAttribute('data-lucide', 'eye');
            }
            lucide.createIcons();
        });
    });

    // Save Settings
    saveSettingsBtn.addEventListener('click', () => {
        const provider = document.querySelector('input[name="api-provider"]:checked').value;
        state.settings.provider = provider;
        state.settings.geminiKey = geminiApiKeyInput.value.trim();
        state.settings.openaiKey = openaiApiKeyInput.value.trim();
        state.settings.model = modelSelect.value;
        state.settings.systemPrompt = systemPromptInput.value.trim();
        saveSettings();
        closeModal();
        addToast('Settings saved successfully!', 'success');
    });

    // Reset settings
    resetSettingsBtn.addEventListener('click', () => {
        if (confirm('Are you sure you want to reset settings to defaults?')) {
            state.settings = {
                provider: 'gemini',
                geminiKey: '',
                openaiKey: '',
                model: 'gemini-1.5-flash',
                systemPrompt: 'You are an advanced AI Document Analyzer. Answer questions using ONLY the facts extracted from the uploaded document(s). If the information is not contained in the text, politely state that you cannot find it. Quote relevant passages, maintain precision, and avoid hallucinating.'
            };
            saveSettings();
            initializeUI();
            addToast('Settings reset to defaults', 'info');
        }
    });

    // Tabs
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            switchTab(tabId);
        });
    });

    // Drag and Drop Upload
    dragDropZone.addEventListener('click', () => fileInput.click());
    
    dragDropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dragDropZone.classList.add('dragover');
    });

    dragDropZone.addEventListener('dragleave', () => {
        dragDropZone.classList.remove('dragover');
    });

    dragDropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dragDropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleUploadedFiles(e.dataTransfer.files);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleUploadedFiles(e.target.files);
        }
    });

    // Camera Scan trigger
    cameraScanBtn.addEventListener('click', () => {
        // Create an input file with capture="camera" attribute for mobile scan
        const captureInput = document.createElement('input');
        captureInput.type = 'file';
        captureInput.accept = 'image/*';
        captureInput.capture = 'environment';
        captureInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleUploadedFiles(e.target.files);
            }
        });
        captureInput.click();
    });

    // PDF Pagination
    prevPageBtn.addEventListener('click', () => changePdfPage(-1));
    nextPageBtn.addEventListener('click', () => changePdfPage(1));

    // Chat submit
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        submitChatMessage();
    });

    // Chat textarea auto height
    chatInputTextarea.addEventListener('input', () => {
        chatInputTextarea.style.height = 'auto';
        chatInputTextarea.style.height = (chatInputTextarea.scrollHeight - 6) + 'px';
    });

    chatInputTextarea.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });

    // Voice recognition (Speech to text)
    setupVoiceInput();

    // Export Chat PDF
    exportChatBtn.addEventListener('click', exportChatHistoryAsPDF);

    // Preset prompts
    presetsContainer.addEventListener('click', (e) => {
        const chip = e.target.closest('.preset-chip');
        if (chip) {
            const promptText = chip.getAttribute('data-prompt');
            chatInputTextarea.value = promptText;
            chatInputTextarea.dispatchEvent(new Event('input'));
            chatInputTextarea.focus();
        }
    });

    // OCR actions
    ocrCopyBtn.addEventListener('click', () => {
        const text = ocrTextDisplayEl.innerText;
        if (text) {
            navigator.clipboard.writeText(text)
                .then(() => addToast('Text copied to clipboard!', 'success'))
                .catch(() => addToast('Failed to copy text', 'error'));
        }
    });

    ocrDownloadBtn.addEventListener('click', () => {
        const text = ocrTextDisplayEl.innerText;
        if (!text) return;
        const activeFile = getActiveFile();
        const filename = activeFile ? `${activeFile.name.split('.')[0]}_extracted.txt` : 'extracted_text.txt';
        const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
    });

    // Search within OCR Text
    ocrSearchInput.addEventListener('input', (e) => {
        const query = e.target.value.trim().toLowerCase();
        highlightOcrText(query);
    });

    // Scanner Canvas interactions
    setupScannerEventListeners();
}

function switchTab(tabId) {
    tabBtns.forEach(b => {
        if (b.getAttribute('data-tab') === tabId) b.classList.add('active');
        else b.classList.remove('active');
    });
    tabContents.forEach(c => {
        if (c.id === tabId) c.classList.add('active');
        else c.classList.remove('active');
    });
}

// --- FILE UPLOADS HANDLING ---
async function handleUploadedFiles(fileList) {
    for (let i = 0; i < fileList.length; i++) {
        const file = fileList[i];
        const fileId = 'doc_' + Date.now() + '_' + Math.random().toString(36).substr(2, 5);
        
        // Initial File entry in state
        const fileObject = {
            id: fileId,
            name: file.name,
            size: formatFileSize(file.size),
            type: file.type,
            status: 'processing', // processing, done, error
            ocrConfidence: 0,
            fullText: '',
            pages: [], // canvases/images or HTML5 canvas representations
            summary: '',
            docType: 'Unknown',
            metadata: {}
        };
        
        state.files.push(fileObject);
        updateDocumentListUI();
        setActiveDocument(fileId);

        try {
            if (file.type === 'application/pdf') {
                await processPdfFile(file, fileObject);
            } else if (file.type.startsWith('image/')) {
                await processImageFile(file, fileObject);
            } else {
                throw new Error('Unsupported file type.');
            }
        } catch (error) {
            console.error('File processing error:', error);
            fileObject.status = 'error';
            addToast(`Error processing ${file.name}: ${error.message}`, 'error');
            updateDocumentListUI();
        }
    }
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

// --- PDF PROCESSING ---
async function processPdfFile(file, fileObject) {
    const arrayBuffer = await file.arrayBuffer();
    const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
    
    fileObject.totalPages = pdf.numPages;
    fileObject.pagesText = new Array(pdf.numPages).fill('');
    fileObject.pagesImages = []; // Cache scaled canvases
    
    addToast(`Loaded PDF: ${file.name} (${pdf.numPages} pages)`, 'info');

    // Display progress
    showOcrProgress(true, 'Reading PDF pages...');
    
    // Render all pages to canvases in high resolution for OCR
    for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
        updateOcrProgressMessage(`Rendering page ${pageNum} of ${pdf.numPages}...`, (pageNum / pdf.numPages) * 30);
        
        const page = await pdf.getPage(pageNum);
        // Scale to 2.0 for higher OCR accuracy
        const viewport = page.getViewport({ scale: 2.0 });
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.width = viewport.width;
        canvas.height = viewport.height;
        
        await page.render({ canvasContext: ctx, viewport: viewport }).promise;
        fileObject.pagesImages.push(canvas);
    }
    
    // Run OCR page by page
    let aggregatedText = '';
    let totalConfidence = 0;
    
    for (let pIdx = 0; pIdx < fileObject.pagesImages.length; pIdx++) {
        const pageNum = pIdx + 1;
        const pageCanvas = fileObject.pagesImages[pIdx];
        
        updateOcrProgressMessage(`Running OCR on page ${pageNum} of ${pdf.numPages}...`, 30 + (pageNum / pdf.numPages) * 70);
        
        const ocrResult = await performOCROnCanvas(pageCanvas, (percent) => {
            const pagePortion = 70 / pdf.numPages;
            const currentProgress = 30 + (pIdx * pagePortion) + (percent * pagePortion / 100);
            updateOcrProgressPercent(currentProgress);
        });
        
        fileObject.pagesText[pIdx] = ocrResult.text;
        aggregatedText += `--- PAGE ${pageNum} ---\n` + ocrResult.text + '\n\n';
        totalConfidence += ocrResult.confidence;
    }
    
    fileObject.fullText = aggregatedText;
    fileObject.ocrConfidence = Math.round(totalConfidence / pdf.numPages);
    fileObject.status = 'done';
    
    showOcrProgress(false);
    updateDocumentListUI();
    renderActiveDocumentPreview();
    
    // Switch to OCR text view
    ocrTextDisplayEl.innerText = fileObject.fullText;
    
    // Trigger AI summarization and classification
    addToast('OCR Complete! Running AI summarization...', 'success');
    await runAiDocumentAnalysis(fileObject);
}

// --- IMAGE PROCESSING ---
async function processImageFile(file, fileObject) {
    const reader = new FileReader();
    reader.onload = function(event) {
        const img = new Image();
        img.onload = function() {
            // Setup scanner editor
            setupScanner(img, fileObject);
        };
        img.src = event.target.result;
    };
    reader.readAsDataURL(file);
}

function setupScanner(img, fileObject) {
    state.scanner.img = img;
    state.scanner.fileObject = fileObject;
    
    // Reveal Scanner tab button
    scannerTabTrigger.style.display = 'flex';
    switchTab('tab-scanner');
    
    // Clear sliders & filters
    brightnessSlider.value = 0;
    brightnessVal.textContent = '0%';
    contrastSlider.value = 0;
    contrastVal.textContent = '0%';
    filterBtns.forEach(b => {
        if (b.getAttribute('data-filter') === 'none') b.classList.add('active');
        else b.classList.remove('active');
    });
    
    // Size canvas
    const maxW = 700;
    const maxH = 500;
    let w = img.naturalWidth;
    let h = img.naturalHeight;
    
    // Scale down image to fit preview boundaries
    let scale = 1;
    if (w > maxW || h > maxH) {
        const scaleX = maxW / w;
        const scaleY = maxH / h;
        scale = Math.min(scaleX, scaleY);
        w = w * scale;
        h = h * scale;
    }
    
    state.scanner.canvas = scannerCanvas;
    state.scanner.ctx = scannerCanvas.getContext('2d');
    scannerCanvas.width = w;
    scannerCanvas.height = h;
    state.scanner.scale = scale;
    state.scanner.originalWidth = img.naturalWidth;
    state.scanner.originalHeight = img.naturalHeight;
    
    // Default Crop Handles (translucent draggable markers, 10% margins)
    const marginW = w * 0.1;
    const marginH = h * 0.1;
    state.scanner.corners = [
        { x: marginW, y: marginH },         // Top-Left
        { x: w - marginW, y: marginH },     // Top-Right
        { x: w - marginW, y: h - marginH }, // Bottom-Right
        { x: marginW, y: h - marginH }      // Bottom-Left
    ];
    
    drawScannerState();
}

function drawScannerState() {
    const s = state.scanner;
    if (!s.img || !s.ctx) return;
    
    // Clear
    s.ctx.clearRect(0, 0, s.canvas.width, s.canvas.height);
    
    // Draw Image scaled
    s.ctx.drawImage(s.img, 0, 0, s.canvas.width, s.canvas.height);
    
    // Draw Translucent selection overlay
    s.ctx.fillStyle = 'rgba(59, 130, 246, 0.25)';
    s.ctx.strokeStyle = '#3b82f6';
    s.ctx.lineWidth = 2;
    
    s.ctx.beginPath();
    s.ctx.moveTo(s.corners[0].x, s.corners[0].y);
    s.ctx.lineTo(s.corners[1].x, s.corners[1].y);
    s.ctx.lineTo(s.corners[2].x, s.corners[2].y);
    s.ctx.lineTo(s.corners[3].x, s.corners[3].y);
    s.ctx.closePath();
    s.ctx.fill();
    s.ctx.stroke();
    
    // Draw line guidelines connecting diagonals
    s.ctx.strokeStyle = 'rgba(59, 130, 246, 0.4)';
    s.ctx.lineWidth = 1;
    s.ctx.beginPath();
    s.ctx.moveTo(s.corners[0].x, s.corners[0].y);
    s.ctx.lineTo(s.corners[2].x, s.corners[2].y);
    s.ctx.moveTo(s.corners[1].x, s.corners[1].y);
    s.ctx.lineTo(s.corners[3].x, s.corners[3].y);
    s.ctx.stroke();

    // Draw handles (circles)
    s.corners.forEach((pt, idx) => {
        s.ctx.fillStyle = idx === s.draggedCornerIdx ? '#2563eb' : '#ffffff';
        s.ctx.strokeStyle = '#3b82f6';
        s.ctx.lineWidth = 3;
        s.ctx.beginPath();
        s.ctx.arc(pt.x, pt.y, 8, 0, Math.PI * 2);
        s.ctx.fill();
        s.ctx.stroke();
    });
}

function setupScannerEventListeners() {
    const s = state.scanner;
    
    const getMousePos = (e) => {
        const rect = scannerCanvas.getBoundingClientRect();
        return {
            x: (e.clientX - rect.left) * (scannerCanvas.width / rect.width),
            y: (e.clientY - rect.top) * (scannerCanvas.height / rect.height)
        };
    };

    scannerCanvas.addEventListener('mousedown', (e) => {
        const mouse = getMousePos(e);
        // Find if we are clicking close to any corner handle (threshold = 12 pixels)
        s.draggedCornerIdx = s.corners.findIndex(pt => {
            const dist = Math.hypot(pt.x - mouse.x, pt.y - mouse.y);
            return dist < 15;
        });
        if (s.draggedCornerIdx !== -1) {
            drawScannerState();
        }
    });

    scannerCanvas.addEventListener('mousemove', (e) => {
        if (s.draggedCornerIdx === -1) return;
        const mouse = getMousePos(e);
        
        // Boundary limit inside canvas
        s.corners[s.draggedCornerIdx].x = Math.max(0, Math.min(scannerCanvas.width, mouse.x));
        s.corners[s.draggedCornerIdx].y = Math.max(0, Math.min(scannerCanvas.height, mouse.y));
        
        drawScannerState();
    });

    window.addEventListener('mouseup', () => {
        if (s.draggedCornerIdx !== -1) {
            s.draggedCornerIdx = -1;
            drawScannerState();
        }
    });

    // Touch support for mobiles
    scannerCanvas.addEventListener('touchstart', (e) => {
        if (e.touches.length === 0) return;
        const t = e.touches[0];
        const rect = scannerCanvas.getBoundingClientRect();
        const pos = {
            x: (t.clientX - rect.left) * (scannerCanvas.width / rect.width),
            y: (t.clientY - rect.top) * (scannerCanvas.height / rect.height)
        };
        s.draggedCornerIdx = s.corners.findIndex(pt => Math.hypot(pt.x - pos.x, pt.y - pos.y) < 22);
        if (s.draggedCornerIdx !== -1) e.preventDefault();
    }, { passive: false });

    scannerCanvas.addEventListener('touchmove', (e) => {
        if (s.draggedCornerIdx === -1 || e.touches.length === 0) return;
        const t = e.touches[0];
        const rect = scannerCanvas.getBoundingClientRect();
        const pos = {
            x: (t.clientX - rect.left) * (scannerCanvas.width / rect.width),
            y: (t.clientY - rect.top) * (scannerCanvas.height / rect.height)
        };
        s.corners[s.draggedCornerIdx].x = Math.max(0, Math.min(scannerCanvas.width, pos.x));
        s.corners[s.draggedCornerIdx].y = Math.max(0, Math.min(scannerCanvas.height, pos.y));
        drawScannerState();
        e.preventDefault();
    }, { passive: false });

    scannerCanvas.addEventListener('touchend', () => {
        s.draggedCornerIdx = -1;
    });

    // Auto edge detection heuristic (Reset button)
    scannerAutoDetect.addEventListener('click', () => {
        if (!s.img) return;
        const w = scannerCanvas.width;
        const h = scannerCanvas.height;
        const marginW = w * 0.05;
        const marginH = h * 0.05;
        s.corners = [
            { x: marginW, y: marginH },
            { x: w - marginW, y: marginH },
            { x: w - marginW, y: h - marginH },
            { x: marginW, y: h - marginH }
        ];
        drawScannerState();
        addToast('Reset cropping corners to margins', 'info');
    });

    // Rotate clockwise 90 degrees
    scannerRotate.addEventListener('click', () => {
        if (!s.img) return;
        
        // Create an offscreen rotation
        const offCanvas = document.createElement('canvas');
        offCanvas.width = s.img.naturalHeight;
        offCanvas.height = s.img.naturalWidth;
        const offCtx = offCanvas.getContext('2d');
        
        offCtx.translate(offCanvas.width / 2, offCanvas.height / 2);
        offCtx.rotate(Math.PI / 2);
        offCtx.drawImage(s.img, -s.img.naturalWidth / 2, -s.img.naturalHeight / 2);
        
        // Recreate temporary image
        const rotatedImg = new Image();
        rotatedImg.onload = () => {
            setupScanner(rotatedImg, s.fileObject);
        };
        rotatedImg.src = offCanvas.toDataURL();
    });

    // Sliders
    brightnessSlider.addEventListener('input', (e) => {
        brightnessVal.textContent = e.target.value + '%';
    });
    contrastSlider.addEventListener('input', (e) => {
        contrastVal.textContent = e.target.value + '%';
    });

    // Filter Buttons selector
    filterBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
        });
    });

    // Cancel Scan
    scannerCancel.addEventListener('click', () => {
        // Remove processing item from state
        state.files = state.files.filter(f => f.id !== s.fileObject.id);
        updateDocumentListUI();
        scannerTabTrigger.style.display = 'none';
        switchTab('tab-preview');
        // Clear scanner state
        s.img = null;
        s.fileObject = null;
        addToast('Scanner canceled', 'info');
    });

    // Crop, Enhance & Finalize OCR
    scannerProcessFinal.addEventListener('click', async () => {
        if (!s.img) return;
        
        try {
            // 1. Perspective Crop & Straighten
            const croppedCanvas = processPerspectiveWarp();
            
            // 2. Apply enhancements (brightness, contrast, filters) to cropped canvas
            applyImageEnhancements(croppedCanvas);
            
            const fileObject = s.fileObject;
            
            // Store page representations
            fileObject.pagesText = [''];
            fileObject.pagesImages = [croppedCanvas];
            fileObject.totalPages = 1;
            
            // Hide Scanner tab
            scannerTabTrigger.style.display = 'none';
            switchTab('tab-ocr');
            
            // Start OCR
            showOcrProgress(true, 'Running OCR on scanned image...');
            const ocrResult = await performOCROnCanvas(croppedCanvas, (percent) => {
                updateOcrProgressPercent(percent);
            });
            
            fileObject.fullText = ocrResult.text;
            fileObject.ocrConfidence = ocrResult.confidence;
            fileObject.status = 'done';
            
            showOcrProgress(false);
            updateDocumentListUI();
            renderActiveDocumentPreview();
            ocrTextDisplayEl.innerText = fileObject.fullText;
            
            // Clear Scanner memory
            s.img = null;
            s.fileObject = null;
            
            addToast('Scan OCR Complete! Launching AI analysis...', 'success');
            await runAiDocumentAnalysis(fileObject);
            
        } catch (error) {
            console.error('Scan processing failure:', error);
            s.fileObject.status = 'error';
            updateDocumentListUI();
            addToast('Scan compilation failed: ' + error.message, 'error');
            switchTab('tab-preview');
        }
    });
}

// --- PROJECTIVE TRANSFORMATION (PERSPECTIVE WARP) ---
function processPerspectiveWarp() {
    const s = state.scanner;
    const img = s.img;
    
    // Scale coordinate factors from display canvas back to original natural image dimensions
    const scaleFactorX = s.originalWidth / s.canvas.width;
    const scaleFactorY = s.originalHeight / s.canvas.height;
    
    // Draggable coordinates mapped back to natural dimensions
    const p0 = { x: s.corners[0].x * scaleFactorX, y: s.corners[0].y * scaleFactorY }; // TL
    const p1 = { x: s.corners[1].x * scaleFactorX, y: s.corners[1].y * scaleFactorY }; // TR
    const p2 = { x: s.corners[2].x * scaleFactorX, y: s.corners[2].y * scaleFactorY }; // BR
    const p3 = { x: s.corners[3].x * scaleFactorX, y: s.corners[3].y * scaleFactorY }; // BL
    
    // Compute destination width & height based on average distance between vertices
    const topWidth = Math.hypot(p1.x - p0.x, p1.y - p0.y);
    const bottomWidth = Math.hypot(p2.x - p3.x, p2.y - p3.y);
    const destWidth = Math.round(Math.max(topWidth, bottomWidth));
    
    const leftHeight = Math.hypot(p3.x - p0.x, p3.y - p0.y);
    const rightHeight = Math.hypot(p2.x - p1.x, p2.y - p1.y);
    const destHeight = Math.round(Math.max(leftHeight, rightHeight));
    
    // Create high-res destination canvas
    const destCanvas = document.createElement('canvas');
    destCanvas.width = destWidth;
    destCanvas.height = destHeight;
    const destCtx = destCanvas.getContext('2d');
    
    // Original high-res source image drawn on a canvas
    const srcCanvas = document.createElement('canvas');
    srcCanvas.width = s.originalWidth;
    srcCanvas.height = s.originalHeight;
    const srcCtx = srcCanvas.getContext('2d');
    srcCtx.drawImage(img, 0, 0);
    const srcData = srcCtx.getImageData(0, 0, srcCanvas.width, srcCanvas.height);
    
    // Solve perspective matrix mapping dest coordinate (x_d, y_d) -> source coordinate (x_s, y_s)
    const destPoints = [
        { x: 0, y: 0 },
        { x: destWidth, y: 0 },
        { x: destWidth, y: destHeight },
        { x: 0, y: destHeight }
    ];
    const srcPoints = [p0, p1, p2, p3];
    
    const matrix = getPerspectiveTransformMatrix(destPoints, srcPoints);
    if (!matrix) {
        throw new Error('Geometric singularity: Coordinates are linear or overlap.');
    }
    
    const destData = destCtx.createImageData(destWidth, destHeight);
    
    const [a, b, c, d, e, f, g, h] = matrix;
    
    // Bilinear or Nearest Neighbor backward warp mapping
    for (let y = 0; y < destHeight; y++) {
        for (let x = 0; x < destWidth; x++) {
            const w_val = g * x + h * y + 1;
            const srcX = Math.round((a * x + b * y + c) / w_val);
            const srcY = Math.round((d * x + e * y + f) / w_val);
            
            // Check bounding limits
            if (srcX >= 0 && srcX < srcCanvas.width && srcY >= 0 && srcY < srcCanvas.height) {
                const destOffset = (y * destWidth + x) * 4;
                const srcOffset = (srcY * srcCanvas.width + srcX) * 4;
                
                destData.data[destOffset] = srcData.data[srcOffset];         // R
                destData.data[destOffset + 1] = srcData.data[srcOffset + 1]; // G
                destData.data[destOffset + 2] = srcData.data[srcOffset + 2]; // B
                destData.data[destOffset + 3] = srcData.data[srcOffset + 3]; // A
            }
        }
    }
    
    destCtx.putImageData(destData, 0, 0);
    return destCanvas;
}

// Solve linear systems using Gaussian Elimination to calculate projective mapping variables [a..h]
function getPerspectiveTransformMatrix(dest, src) {
    const A = [];
    const B = [];
    
    for (let i = 0; i < 4; i++) {
        const x_d = dest[i].x;
        const y_d = dest[i].y;
        const x_s = src[i].x;
        const y_s = src[i].y;
        
        A.push([x_d, y_d, 1, 0, 0, 0, -x_d * x_s, -y_d * x_s]);
        B.push(x_s);
        
        A.push([0, 0, 0, x_d, y_d, 1, -x_d * y_s, -y_d * y_s]);
        B.push(y_s);
    }
    
    return solveLinearSystem(A, B);
}

function solveLinearSystem(A, B) {
    const n = B.length;
    for (let i = 0; i < n; i++) {
        let maxRow = i;
        for (let j = i + 1; j < n; j++) {
            if (Math.abs(A[j][i]) > Math.abs(A[maxRow][i])) {
                maxRow = j;
            }
        }
        
        const tempRowA = A[i]; A[i] = A[maxRow]; A[maxRow] = tempRowA;
        const tempB = B[i]; B[i] = B[maxRow]; B[maxRow] = tempB;
        
        if (Math.abs(A[i][i]) < 1e-12) return null; // Singular
        
        for (let j = i + 1; j < n; j++) {
            const factor = A[j][i] / A[i][i];
            B[j] -= factor * B[i];
            for (let k = i; k < n; k++) {
                A[j][k] -= factor * A[i][k];
            }
        }
    }
    
    const X = new Array(n).fill(0);
    for (let i = n - 1; i >= 0; i--) {
        let sum = 0;
        for (let j = i + 1; j < n; j++) {
            sum += A[i][j] * X[j];
        }
        X[i] = (B[i] - sum) / A[i][i];
    }
    return X;
}

// --- IMAGE ENHANCEMENTS AND FILTERS ---
function applyImageEnhancements(canvas) {
    const ctx = canvas.getContext('2d');
    const imgData = ctx.getImageData(0, 0, canvas.width, canvas.height);
    const d = imgData.data;
    
    const brightness = parseInt(brightnessSlider.value); // -100 to 100
    const contrast = parseInt(contrastSlider.value);     // -100 to 100
    const filter = document.querySelector('.filter-btn-opt.active').getAttribute('data-filter');
    
    // Contrast formula factor
    const contrastFactor = (259 * (contrast + 255)) / (255 * (259 - contrast));
    
    for (let i = 0; i < d.length; i += 4) {
        let r = d[i];
        let g = d[i+1];
        let b = d[i+2];
        
        // 1. Brightness
        if (brightness !== 0) {
            r += brightness * 2.55;
            g += brightness * 2.55;
            b += brightness * 2.55;
        }
        
        // 2. Contrast
        if (contrast !== 0) {
            r = contrastFactor * (r - 128) + 128;
            g = contrastFactor * (g - 128) + 128;
            b = contrastFactor * (b - 128) + 128;
        }
        
        // Cap values
        r = Math.max(0, Math.min(255, r));
        g = Math.max(0, Math.min(255, g));
        b = Math.max(0, Math.min(255, b));
        
        // 3. Filters
        if (filter === 'grayscale' || filter === 'high-contrast') {
            const gray = 0.299 * r + 0.587 * g + 0.114 * b;
            
            if (filter === 'high-contrast') {
                // Adaptive Binarization threshold around center 128
                const binarized = gray > 128 ? 255 : 0;
                r = g = b = binarized;
            } else {
                r = g = b = gray;
            }
        }
        
        d[i] = r;
        d[i+1] = g;
        d[i+2] = b;
    }
    
    ctx.putImageData(imgData, 0, 0);
}

// --- CLIENT SIDE TESSERACT OCR CORE ---
async function performOCROnCanvas(canvas, onProgressCallback) {
    const worker = await Tesseract.createWorker('eng', 1, {
        logger: m => {
            if (m.status === 'recognizing') {
                onProgressCallback(Math.round(m.progress * 100));
            }
        }
    });
    
    try {
        const { data } = await worker.recognize(canvas);
        return {
            text: data.text || '',
            confidence: data.confidence || 0
        };
    } finally {
        await worker.terminate();
    }
}

function showOcrProgress(show, message = 'Processing OCR...') {
    if (show) {
        ocrStatusMessage.textContent = message;
        ocrProgressBarFill.style.width = '0%';
        ocrProgressPercent.textContent = '0%';
        ocrProgressOverlay.style.display = 'flex';
    } else {
        ocrProgressOverlay.style.display = 'none';
    }
}

function updateOcrProgressMessage(msg, overallPercent) {
    ocrStatusMessage.textContent = msg;
    updateOcrProgressPercent(overallPercent);
}

function updateOcrProgressPercent(percent) {
    const clamped = Math.round(Math.max(0, Math.min(100, percent)));
    ocrProgressBarFill.style.width = clamped + '%';
    ocrProgressPercent.textContent = clamped + '%';
}

// --- ACTIVE DOCUMENT MANAGEMENT ---
function getActiveFile() {
    return state.files.find(f => f.id === state.activeFileId);
}

function setActiveDocument(fileId) {
    state.activeFileId = fileId;
    state.activePageNum = 1;
    
    // Highlight in list
    document.querySelectorAll('.doc-item').forEach(item => {
        if (item.getAttribute('data-id') === fileId) item.classList.add('active');
        else item.classList.remove('active');
    });

    const activeFile = getActiveFile();
    if (!activeFile) return;

    // Reset pagination displays
    if (activeFile.type === 'application/pdf') {
        pdfPagination.style.display = 'flex';
        currentPageNumEl.textContent = '1';
        totalPagesNumEl.textContent = activeFile.totalPages;
    } else {
        pdfPagination.style.display = 'none';
    }

    renderActiveDocumentPreview();

    // Populate OCR tab text
    ocrTextDisplayEl.innerText = activeFile.fullText || '';
    ocrSearchInput.value = '';

    // Switch chat messages view if scoped to Active
    renderChatMessages();
}

function changePdfPage(dir) {
    const activeFile = getActiveFile();
    if (!activeFile || activeFile.type !== 'application/pdf') return;

    const newPage = state.activePageNum + dir;
    if (newPage >= 1 && newPage <= activeFile.totalPages) {
        state.activePageNum = newPage;
        currentPageNumEl.textContent = newPage;
        renderActiveDocumentPreview();
    }
}

function renderActiveDocumentPreview() {
    const activeFile = getActiveFile();
    previewViewportEl.innerHTML = ''; // Clear

    if (!activeFile) {
        previewViewportEl.innerHTML = `
            <div class="viewer-placeholder">
                <i data-lucide="file-up" class="placeholder-icon"></i>
                <h3>Document Viewer</h3>
                <p>Select or upload a document to view its content.</p>
            </div>`;
        lucide.createIcons();
        return;
    }

    if (activeFile.status === 'processing') {
        previewViewportEl.innerHTML = `
            <div class="viewer-placeholder">
                <div class="spinner"></div>
                <h3>Extracting Document</h3>
                <p>Please wait. Performing OCR and key details structural parsing...</p>
            </div>`;
        return;
    }

    if (activeFile.status === 'error') {
        previewViewportEl.innerHTML = `
            <div class="viewer-placeholder" style="color: var(--status-error);">
                <i data-lucide="alert-circle" class="placeholder-icon" style="color: var(--status-error);"></i>
                <h3>Failed to load document</h3>
                <p>The processing engine encountered errors during OCR extraction.</p>
            </div>`;
        lucide.createIcons();
        return;
    }

    // Display Active Page preview
    if (activeFile.type === 'application/pdf') {
        const pageCanvas = activeFile.pagesImages[state.activePageNum - 1];
        if (pageCanvas) {
            // Render canvas copy in preview
            const canvasCopy = document.createElement('canvas');
            canvasCopy.className = 'preview-canvas';
            canvasCopy.width = pageCanvas.width;
            canvasCopy.height = pageCanvas.height;
            const ctx = canvasCopy.getContext('2d');
            ctx.drawImage(pageCanvas, 0, 0);
            previewViewportEl.appendChild(canvasCopy);
        }
    } else {
        // Image type
        const imgCanvas = activeFile.pagesImages[0];
        if (imgCanvas) {
            const canvasCopy = document.createElement('canvas');
            canvasCopy.className = 'preview-canvas';
            canvasCopy.width = imgCanvas.width;
            canvasCopy.height = imgCanvas.height;
            const ctx = canvasCopy.getContext('2d');
            ctx.drawImage(imgCanvas, 0, 0);
            previewViewportEl.appendChild(canvasCopy);
        }
    }
}

function updateDocumentListUI() {
    docCounter.textContent = state.files.length;
    
    if (state.files.length === 0) {
        emptyDocsEl.style.display = 'flex';
        return;
    }
    
    emptyDocsEl.style.display = 'none';
    
    // Preserving selection index or rendering lists
    const currentListHtmls = state.files.map(file => {
        const isActive = file.id === state.activeFileId ? 'active' : '';
        let badgeClass = 'processing';
        let badgeText = 'OCR';
        
        if (file.status === 'done') {
            badgeClass = 'done';
            badgeText = `${file.ocrConfidence}%`;
        } else if (file.status === 'error') {
            badgeClass = 'error';
            badgeText = 'FAIL';
        }

        const iconType = file.type === 'application/pdf' ? 'file-text' : 'image';

        return `
            <div class="doc-item ${isActive}" data-id="${file.id}">
                <div class="doc-item-icon">
                    <i data-lucide="${iconType}"></i>
                </div>
                <div class="doc-item-details">
                    <div class="doc-item-name" title="${escapeHtml(file.name)}">${escapeHtml(file.name)}</div>
                    <div class="doc-item-meta">
                        <span>${file.size}</span>
                        <span>•</span>
                        <span class="doc-badge ${badgeClass}">${badgeText}</span>
                    </div>
                </div>
                <button class="doc-item-remove-btn" data-id="${file.id}" title="Remove Document">
                    <i data-lucide="trash-2"></i>
                </button>
            </div>
        `;
    }).join('');

    docListEl.innerHTML = currentListHtmls;
    lucide.createIcons();

    // Hook listeners
    docListEl.querySelectorAll('.doc-item').forEach(item => {
        item.addEventListener('click', (e) => {
            if (e.target.closest('.doc-item-remove-btn')) {
                const id = e.target.closest('.doc-item-remove-btn').getAttribute('data-id');
                removeDocument(id);
                e.stopPropagation();
                return;
            }
            const fileId = item.getAttribute('data-id');
            setActiveDocument(fileId);
        });
    });
}

function removeDocument(fileId) {
    if (confirm('Are you sure you want to delete this document?')) {
        state.files = state.files.filter(f => f.id !== fileId);
        delete state.chatHistory[fileId];
        
        if (state.activeFileId === fileId) {
            state.activeFileId = state.files.length > 0 ? state.files[0].id : null;
        }
        
        updateDocumentListUI();
        setActiveDocument(state.activeFileId);
        addToast('Document removed', 'info');
    }
}

// --- SEARCH TEXT HIGHLIGHT ---
function highlightOcrText(query) {
    const textDisplay = ocrTextDisplayEl;
    const activeFile = getActiveFile();
    if (!activeFile || !activeFile.fullText) return;

    if (!query) {
        textDisplay.innerText = activeFile.fullText;
        return;
    }

    const text = activeFile.fullText;
    const regex = new RegExp(`(${escapeRegex(query)})`, 'gi');
    const highlighted = text.replace(regex, '<mark class="highlight">$1</mark>');
    textDisplay.innerHTML = highlighted;
}

function escapeRegex(string) {
    return string.replace(/[/\-\\^$*+?.()|[\]{}]/g, '\\$&');
}

// --- AI LLM CONNECTOR ---
async function runAiDocumentAnalysis(fileObject) {
    const apiKey = getApiKey();
    if (!apiKey) {
        addToast('Please input an API key in Settings to trigger automated AI Summarization.', 'warn');
        return;
    }

    // Auto classify and summarize
    const prompt = `Analyze this document. Perform the following steps:
1. Identify the Document Type (e.g. Invoice, Receipt, Article, Contract, Letter, Handwritten Note).
2. Generate a concise Summary (3-5 sentences).
3. Identify 3 to 5 Key Topics/Themes.
4. Extract essential Metadata fields (like dates, total amounts, names, deadlines) if visible.

Format your output in clean HTML with structured divs.

Document text:
${fileObject.fullText.substring(0, 15000)}`; // limit token load

    try {
        const responseText = await callLLM(prompt, 'Summarizer Mode');
        
        fileObject.summary = responseText;
        
        // Parse metadata properties roughly if LLM returned structured tags (optional enhancement)
        fileObject.docType = parseDocType(responseText);

        // Feed Summary directly as Greeting message inside file specific chat history
        state.chatHistory[fileObject.id] = [
            {
                role: 'assistant',
                content: `### Document Analyzed: **${escapeHtml(fileObject.name)}**\n\n${responseText}`
            }
        ];
        
        renderChatMessages();
    } catch (e) {
        console.error('AI Document Analysis failed:', e);
        addToast('AI Document Analysis failed. Custom query still available.', 'error');
        state.chatHistory[fileObject.id] = [
            {
                role: 'assistant',
                content: `Failed to generate AI analysis summary. OCR extracted content is ready. Feel free to ask questions manually.`
            }
        ];
        renderChatMessages();
    }
}

function parseDocType(text) {
    // Simple heuristic parser for LLM html/text outputs
    const match = text.match(/Document Type:?\s*\*?([a-zA-Z\s]+)/i) || text.match(/Type:?\s*\*?([a-zA-Z\s]+)/i);
    return match ? match[1].trim() : 'Document';
}

function getApiKey() {
    const prov = state.settings.provider;
    return prov === 'gemini' ? state.settings.geminiKey : state.settings.openaiKey;
}

async function callLLM(prompt, modeName = 'AI Chat') {
    const provider = state.settings.provider;
    const apiKey = getApiKey();
    const model = state.settings.model;
    const sysPrompt = state.settings.systemPrompt;

    if (!apiKey) {
        throw new Error('API Key missing. Open Settings to set it.');
    }

    if (provider === 'gemini') {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${apiKey}`;
        
        // Format history content if any
        const contents = [];
        
        // Incorporate System prompt inside message context for Gemini (or use systemInstruction property)
        // Newer Gemini API models support systemInstruction
        const payload = {
            contents: [
                {
                    role: 'user',
                    parts: [{ text: `${sysPrompt}\n\nTask: ${prompt}` }]
                }
            ],
            generationConfig: {
                temperature: 0.2
            }
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errBody = await response.text();
            throw new Error(`Gemini API error: ${response.status} - ${errBody}`);
        }

        const data = await response.json();
        if (data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts[0]) {
            return data.candidates[0].content.parts[0].text;
        } else {
            throw new Error('Malformed API response.');
        }
    } else {
        // OpenAI API
        const url = 'https://api.openai.com/v1/chat/completions';
        const payload = {
            model: model,
            messages: [
                { role: 'system', content: sysPrompt },
                { role: 'user', content: prompt }
            ],
            temperature: 0.2
        };

        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${apiKey}`
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const errBody = await response.text();
            throw new Error(`OpenAI API error: ${response.status} - ${errBody}`);
        }

        const data = await response.json();
        return data.choices[0].message.content;
    }
}

// --- CHAT INTERFACE AND LOGIC ---
async function submitChatMessage() {
    const text = chatInputTextarea.value.trim();
    if (!text) return;

    // Reset height
    chatInputTextarea.value = '';
    chatInputTextarea.dispatchEvent(new Event('input'));

    const scope = chatScopeSelect.value;
    const activeFile = getActiveFile();
    
    // Require document uploaded if scoped to active
    if (scope === 'active' && !activeFile) {
        addToast('Please upload and select a document first', 'warn');
        return;
    }
    
    // API key verification
    if (!getApiKey()) {
        addToast('AI key missing. Please insert key in Settings.', 'error');
        settingsModal.style.display = 'flex';
        return;
    }

    const currentScopeId = scope === 'active' ? activeFile.id : 'global';
    
    // Add user message to history
    if (!state.chatHistory[currentScopeId]) {
        state.chatHistory[currentScopeId] = [];
    }
    
    state.chatHistory[currentScopeId].push({
        role: 'user',
        content: text
    });
    
    renderChatMessages();
    
    // Render typing indicator
    showTypingIndicator(true);

    try {
        // Prepare context prompt
        let contextText = '';
        if (scope === 'active') {
            contextText = `Active Document Name: ${activeFile.name}\nExtracted Text:\n${activeFile.fullText}`;
        } else {
            // All documents
            const loadedDocsText = state.files
                .filter(f => f.status === 'done')
                .map((f, i) => `Document [${i+1}] Name: ${f.name}\nExtracted Text:\n${f.fullText}\n---`)
                .join('\n\n');
            contextText = `All Uploaded Documents:\n${loadedDocsText}`;
        }

        // Build composite prompt
        const prompt = `Below is the context extracted from the document(s). Answer the user's question using ONLY this facts. If not found in the documents, declare that you cannot find it. Avoid hallucinations. Quote sections of document details when needed.

--- CONTEXT ---
${contextText.substring(0, 30000)}

--- CONVERSATION HISTORY ---
${formatHistoryForContext(state.chatHistory[currentScopeId].slice(-6, -1))}

--- USER QUESTION ---
${text}`;

        const aiResponse = await callLLM(prompt);
        
        state.chatHistory[currentScopeId].push({
            role: 'assistant',
            content: aiResponse
        });
        
    } catch (error) {
        console.error('LLM error:', error);
        state.chatHistory[currentScopeId].push({
            role: 'assistant',
            content: `⚠️ Error communicating with AI model: ${error.message}`
        });
    } finally {
        showTypingIndicator(false);
        renderChatMessages();
    }
}

function formatHistoryForContext(messages) {
    return messages.map(m => `${m.role === 'user' ? 'User' : 'Assistant'}: ${m.content}`).join('\n');
}

function renderChatMessages() {
    const scope = chatScopeSelect.value;
    const activeFile = getActiveFile();
    const currentScopeId = (scope === 'active' && activeFile) ? activeFile.id : 'global';
    
    const messages = state.chatHistory[currentScopeId] || [];
    
    chatMessagesEl.innerHTML = '';
    
    messages.forEach((msg, index) => {
        const isBot = msg.role === 'assistant';
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message ${isBot ? 'assistant-message' : 'user-message'}`;
        
        const avatarHtml = isBot ? '<i data-lucide="bot"></i>' : '<i data-lucide="user"></i>';
        
        // Simple Markdown parsing for headers, code snippets, lists, and bold text
        const parsedContent = parseSimpleMarkdown(msg.content);
        
        msgDiv.innerHTML = `
            <div class="msg-avatar">${avatarHtml}</div>
            <div class="msg-content">
                <div>${parsedContent}</div>
                <div class="msg-footer">
                    <button class="msg-action-btn copy-msg-btn" data-index="${index}" title="Copy response">
                        <i data-lucide="copy" style="width:11px;height:11px;"></i> Copy
                    </button>
                    ${isBot ? `
                    <button class="msg-action-btn speak-msg-btn" data-index="${index}" title="Listen aloud">
                        <i data-lucide="volume-2" style="width:11px;height:11px;"></i> Speak
                    </button>
                    ` : ''}
                </div>
            </div>
        `;
        
        chatMessagesEl.appendChild(msgDiv);
    });
    
    lucide.createIcons();
    scrollChatToBottom();
    
    // Add actions listeners
    chatMessagesEl.querySelectorAll('.copy-msg-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = btn.getAttribute('data-index');
            const content = messages[idx].content;
            navigator.clipboard.writeText(content)
                .then(() => addToast('Copied to clipboard!', 'success'));
        });
    });

    chatMessagesEl.querySelectorAll('.speak-msg-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const idx = btn.getAttribute('data-index');
            const content = messages[idx].content;
            speakText(content);
        });
    });
}

function showTypingIndicator(show) {
    const existing = document.getElementById('typing-indicator-el');
    if (show && !existing) {
        const div = document.createElement('div');
        div.className = 'chat-message assistant-message';
        div.id = 'typing-indicator-el';
        div.innerHTML = `
            <div class="msg-avatar"><i data-lucide="bot"></i></div>
            <div class="msg-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        chatMessagesEl.appendChild(div);
        lucide.createIcons();
        scrollChatToBottom();
    } else if (!show && existing) {
        existing.remove();
    }
}

function scrollChatToBottom() {
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
}

// --- VOICE & SOUND UTILITIES ---
let speechRecognitionObj = null;
function setupVoiceInput() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
        voiceInputBtn.style.display = 'none'; // Unsupported
        return;
    }

    speechRecognitionObj = new SpeechRecognition();
    speechRecognitionObj.continuous = false;
    speechRecognitionObj.lang = 'en-US';
    speechRecognitionObj.interimResults = false;
    speechRecognitionObj.maxAlternatives = 1;

    let isListening = false;

    voiceInputBtn.addEventListener('click', () => {
        if (!isListening) {
            speechRecognitionObj.start();
            voiceInputBtn.style.color = 'var(--status-error)';
            addToast('Listening... Speak now.', 'info');
        } else {
            speechRecognitionObj.stop();
        }
    });

    speechRecognitionObj.onstart = () => { isListening = true; };
    speechRecognitionObj.onend = () => {
        isListening = false;
        voiceInputBtn.style.color = 'var(--text-muted)';
    };

    speechRecognitionObj.onresult = (event) => {
        const text = event.results[0][0].transcript;
        chatInputTextarea.value += ' ' + text;
        chatInputTextarea.dispatchEvent(new Event('input'));
    };

    speechRecognitionObj.onerror = (e) => {
        console.error('Speech recognition error:', e);
        addToast('Voice input error: ' + e.error, 'error');
    };
}

function speakText(text) {
    if ('speechSynthesis' in window) {
        // Cancel ongoing speakings
        window.speechSynthesis.cancel();
        
        // Clean markdown tokens for voice
        const cleanText = text.replace(/[#*`_⚠️]/g, '').replace(/\[.*\]\(.*\)/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        window.speechSynthesis.speak(utterance);
        addToast('Speaking...', 'info');
    } else {
        addToast('Text-to-speech not supported in this browser', 'warn');
    }
}

// --- EXPORT CHAT AS PDF ---
function exportChatHistoryAsPDF() {
    const scope = chatScopeSelect.value;
    const activeFile = getActiveFile();
    const currentScopeId = (scope === 'active' && activeFile) ? activeFile.id : 'global';
    
    const messages = state.chatHistory[currentScopeId] || [];
    if (messages.length <= 1) {
        addToast('No chat history to export yet.', 'warn');
        return;
    }

    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    let y = 20;
    const margin = 20;
    const width = 170; // 210 (A4) - 40 margin
    
    // Title
    doc.setFont('Helvetica', 'bold');
    doc.setFontSize(16);
    doc.text('DocMind AI - Conversation Export', margin, y);
    y += 10;
    
    doc.setFont('Helvetica', 'normal');
    doc.setFontSize(10);
    doc.setTextColor(100);
    const scopeStr = scope === 'active' ? `Document: ${activeFile.name}` : 'Scope: All Documents';
    doc.text(`Exported on: ${new Date().toLocaleString()} | ${scopeStr}`, margin, y);
    y += 15;
    
    messages.forEach(msg => {
        const isBot = msg.role === 'assistant';
        
        // Set colors and font weight
        doc.setFont('Helvetica', 'bold');
        doc.setFontSize(11);
        if (isBot) {
            doc.setTextColor(37, 99, 235); // Blue
            doc.text('Assistant:', margin, y);
        } else {
            doc.setTextColor(15, 23, 42); // Black/Gray
            doc.text('You:', margin, y);
        }
        y += 6;
        
        // Message Content
        doc.setFont('Helvetica', 'normal');
        doc.setFontSize(10);
        doc.setTextColor(50);
        
        const lines = doc.splitTextToSize(msg.content, width);
        lines.forEach(line => {
            if (y > 280) {
                doc.addPage();
                y = 20;
            }
            doc.text(line, margin, y);
            y += 5;
        });
        
        y += 8; // spacing between bubbles
    });
    
    doc.save(`docmind_chat_${Date.now()}.pdf`);
    addToast('PDF downloaded successfully!', 'success');
}

// --- HELPER UTILITIES ---
function parseSimpleMarkdown(markdown) {
    if (!markdown) return '';
    let html = markdown
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // Bold
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        // Code Block
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        // Inline code
        .replace(/`(.*?)`/g, '<code>$1</code>')
        // Line breaks
        .replace(/\n/g, '<br>')
        // Lists
        .replace(/^\s*-\s+(.*?)$/gm, '<li>$1</li>');
        
    return html;
}

function escapeHtml(unsafe) {
    return unsafe
         .replace(/&/g, "&amp;")
         .replace(/</g, "&lt;")
         .replace(/>/g, "&gt;")
         .replace(/"/g, "&quot;")
         .replace(/'/g, "&#039;");
}

function addToast(message, type = 'info') {
    // Dynamically insert Toast elements at top right of viewport
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.style.position = 'fixed';
        container.style.top = '20px';
        container.style.right = '20px';
        container.style.zIndex = '9999';
        container.style.display = 'flex';
        container.style.flexDirection = 'column';
        container.style.gap = '10px';
        container.style.pointerEvents = 'none';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.style.pointerEvents = 'auto';
    toast.style.padding = '12px 20px';
    toast.style.borderRadius = 'var(--radius-md)';
    toast.style.fontSize = '13px';
    toast.style.fontWeight = '500';
    toast.style.boxShadow = 'var(--shadow-md)';
    toast.style.color = '#ffffff';
    toast.style.animation = 'slideUp 0.2s ease forwards';
    toast.style.display = 'flex';
    toast.style.alignItems = 'center';
    toast.style.gap = '8px';
    
    let color = '#3b82f6'; // info (Blue)
    let icon = 'info';
    if (type === 'success') {
        color = '#10b981'; // Green
        icon = 'check-circle';
    } else if (type === 'error') {
        color = '#ef4444'; // Red
        icon = 'alert-triangle';
    } else if (type === 'warn') {
        color = '#f59e0b'; // Amber
        icon = 'alert-circle';
    }
    
    toast.style.backgroundColor = color;
    toast.innerHTML = `<i data-lucide="${icon}" style="width:16px;height:16px;"></i> ${message}`;
    
    container.appendChild(toast);
    lucide.createIcons();

    // Fade out after 4 seconds
    setTimeout(() => {
        toast.style.transition = 'opacity 0.5s ease';
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}
