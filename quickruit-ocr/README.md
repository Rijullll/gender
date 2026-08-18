# Standalone OCR Data Extraction API

A lightweight, high-performance standalone REST API built with **FastAPI**, **OpenCV**, and **Tesseract OCR** (`pytesseract`) to extract structured data (Name, ID number, Date of Birth, and Gender) from ID card images (e.g. Aadhaar, PAN cards).

It includes a modern, responsive **glassmorphic web interface** served directly at the root (`GET /`) for demoing and quick validation.

---

## Architecture Flow

```
+------------------+     +-----------------------+     +-------------------+
|  Image Upload    | --> |  Image Validation     | --> |  Orientation (OSD)|
|  (multipart/form)|     |  (cv2.imdecode check) |     |  (Auto-rotate)    |
+------------------+     +-----------------------+     +-------------------+
                                                                 |
                                                                 v
+------------------+     +-----------------------+     +-------------------+
|   Clean Text     | <-- |      Tesseract        | <-- |   Preprocessing   |
|   (Regex parser) |     |      (--psm 6)        |     |   (Noise/Skew/Th) |
+------------------+     +-----------------------+     +-------------------+
        |
        v
+------------------+
|    JSON Response |
+------------------+
```

### Preprocessing Pipeline Explanation
1. **Validation**: Uses OpenCV to verify and decode raw image bytes.
2. **Upscaling**: Auto-scales low-resolution scans (target max dimension of 1800px) keeping aspect ratio to ensure characters have enough pixels for accurate OCR.
3. **Grayscale**: Converts the image to 8-bit single channel for simpler processing.
4. **Noise Reduction**: Uses a bilateral filter that smooths textures (like paper grain or noise) while keeping character edges sharp.
5. **Orientation & Deskewing**:
   - Corrects gross rotation (90°, 180°, 270°) using Tesseract's **OSD (Orientation & Script Detection)**.
   - Corrects fine skew tilts (between -45° and 45° degrees) by finding the minimum area bounding box on thresholded text pixels and applying affine transformations.
6. **Binarization**: Applies **Adaptive Gaussian Thresholding** to create a clean black-and-white binary mask, handling shadows and uneven lighting conditions.

---

## Setup & Installation

### 1. Prerequisites (Tesseract OCR Engine)
The API runs Tesseract locally. You must install the Tesseract binary:

#### **Windows**
1. Download the installer from [UB Mannheim's Tesseract Page](https://github.com/UB-Mannheim/tesseract/wiki).
2. Install the application.
3. Locate the installation directory (usually `C:\Program Files\Tesseract-OCR\tesseract.exe`).
4. Set the environment variable `TESSERACT_CMD` pointing to `tesseract.exe` path, or add the folder to your system `PATH`.

#### **Ubuntu/Debian**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
```

#### **macOS**
```bash
brew install tesseract
```

---

### 2. Local Python Setup
Initialize a virtual environment and install the required Python packages:

```bash
# Navigate to the project root
cd quickruit-ocr

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate # Linux/macOS

# Install dependencies
pip install -r requirements.txt
```

---

## Running the API

### Run locally (Uvicorn)
Start the server in reload/development mode:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

* **Web UI**: Access `http://127.0.0.1:8000/` in your browser.
* **API Docs (Swagger)**: Access `http://127.0.0.1:8000/docs`.

### Run via Docker
To run without installing Tesseract locally:
```bash
# Build the image
docker build -t quickruit-ocr .

# Run the container
docker run -d -p 8000:8000 quickruit-ocr
```

---

## API Documentation & cURL Example

### 1. Health Check
* **Endpoint**: `GET /health`
* **Response**:
```json
{
  "status": "ok"
}
```

### 2. Data Extraction
* **Endpoint**: `POST /extract`
* **Payload**: `multipart/form-data` with `file` key containing the image.

#### **cURL Example**
```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/extract' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@/path/to/id_card.png;type=image/png'
```

#### **Success Response Schema**
```json
{
  "success": true,
  "data": {
    "name": "SUNIL KUMAR",
    "id_number": "1234 5678 9012",
    "date_of_birth": "12/03/1994",
    "gender": "Male"
  },
  "raw_text": "GOVERNMENT OF INDIA\nSUNIL KUMAR\nDOB: 12/03/1994\nGENDER: MALE\n1234 5678 9012\n"
}
```

---

## Performance Limitations & Scaling to 10k+ Documents/Hour

### Local Instance Limitations
1. **CPU Bound**: Tesseract OCR is highly CPU intensive. In a synchronous/single-worker FastAPI setup, concurrent uploads will block the main thread, leading to spikes in latency.
2. **Memory Footprint**: Loading multiple large image arrays with OpenCV concurrently can cause memory spikes.

### Architectural Scale Guide (10,000 documents/hour)
To achieve a throughput of 10,000 documents/hour (approx. **2.8 documents/second** continuously), implement the following distributed architecture:

```
                  +--------------------------------+
                  |     FastAPI Edge Router        | (Stateless API nodes)
                  +--------------------------------+
                                  |
                                  v (Enqueue Task)
                  +--------------------------------+
                  |      Redis / RabbitMQ Queue    | (Broker)
                  +--------------------------------+
                                  |
                  +---------------+---------------+
                  |                               |
                  v                               v
         +-----------------+             +-----------------+
         |  Celery Worker  |             |  Celery Worker  | (GPU or Multi-Core CPU
         |  (OCR Node 1)   |             |  (OCR Node 2)   |  running Celery/RQ)
         +-----------------+             +-----------------+
                  |                               |
                  +---------------+---------------+
                                  |
                                  v (Store result)
                  +--------------------------------+
                  |  Redis / PostgreSQL Result db  |
                  +--------------------------------+
```

1. **Decouple API from Processing (Asynchronous Tasks)**:
   - Change `POST /extract` to initiate a background job, returning a `task_id` and HTTP 202 immediately.
   - Offload the actual image decode, OpenCV preprocessing, and OCR to a backend job queue like **Celery**, **Dramatiq**, or **Redis Queue (RQ)**.

2. **Distributed Processing Nodes (Workers)**:
   - Run workers on CPU-optimized nodes (4+ cores).
   - Tesseract supports parallel execution inside a single run, but to avoid conflicts and utilize system resources better, set the environment variable `OMP_THREAD_LIMIT=1` to restrict Tesseract to 1 thread, and scale out the number of concurrent Celery worker processes instead.

3. **Horizontal Scaling**:
   - Deploy worker nodes inside a Kubernetes cluster configured with an **HPA (Horizontal Pod Autoscaler)** based on queue depth metrics.
   - Keep the API server lightweight (stateless) and scale it independently behind an Nginx or Traefik load balancer.

4. **Result Storage**:
   - Save processed JSON results to a high-speed database (e.g., Redis or MongoDB) indexed by `task_id`.
   - Provide a `GET /task/{task_id}` polling endpoint or configure a webhook callback to deliver the JSON payload back to the client once processing completes.
