import io
from unittest.mock import patch
from PIL import Image
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_endpoint():
    """
    Verifies that the health check endpoint returns 200 and status ok.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_invalid_file_extension():
    """
    Verifies that uploading a non-image file type returns a failure.
    """
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = client.post("/extract", files=files)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is False
    assert "Unsupported file format" in res_json["error"]

def test_corrupted_image():
    """
    Verifies that uploading a non-image payload with an image extension fails validation.
    """
    files = {"file": ("test.png", b"not an image", "image/png")}
    response = client.post("/extract", files=files)
    assert response.status_code == 200
    res_json = response.json()
    assert res_json["success"] is False
    assert "Invalid or corrupted image" in res_json["error"]

def test_valid_extraction_pan_card():
    """
    Verifies the extraction pipeline structure using a simulated PAN Card response.
    Mocks Tesseract dependency so testing works without local Tesseract installation.
    """
    # Create small dummy image in memory
    img = Image.new("RGB", (100, 100), color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte = img_byte_arr.getvalue()
    
    dummy_ocr_text = (
        "INCOME TAX DEPARTMENT\n"
        "GOVT. OF INDIA\n"
        "RAHUL KUMAR\n"
        "RAMESH KUMAR\n"
        "DOB: 15/08/1991\n"
        "PAN: ABCDE1234F\n"
    )
    
    with patch("app.ocr.pytesseract.image_to_osd", return_value="Rotate: 0"), \
         patch("app.ocr.pytesseract.image_to_string", return_value=dummy_ocr_text):
        
        files = {"file": ("pan.png", img_byte, "image/png")}
        response = client.post("/extract", files=files)
        
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["success"] is True
        assert res_json["data"]["name"] == "RAHUL KUMAR"
        assert res_json["data"]["id_number"] == "ABCDE1234F"
        assert res_json["data"]["date_of_birth"] == "15/08/1991"
        assert res_json["data"]["gender"] is None
        assert "RAHUL KUMAR" in res_json["raw_text"]

def test_valid_extraction_aadhaar_card():
    """
    Verifies the extraction pipeline structure using a simulated Aadhaar Card response
    containing typical fields and checking OCR error correction (FEMA1E -> Female).
    """
    # Create small dummy image in memory
    img = Image.new("RGB", (100, 100), color="white")
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    img_byte = img_byte_arr.getvalue()
    
    dummy_ocr_text = (
        "GOVERNMENT OF INDIA\n"
        "Suneeta Sharma\n"
        "DOB: 01-01-1985\n"
        "GENDER: FEMA1E\n"
        "1234 5678 9012\n"
    )
    
    with patch("app.ocr.pytesseract.image_to_osd", return_value="Rotate: 0"), \
         patch("app.ocr.pytesseract.image_to_string", return_value=dummy_ocr_text):
        
        files = {"file": ("aadhaar.png", img_byte, "image/png")}
        response = client.post("/extract", files=files)
        
        assert response.status_code == 200
        res_json = response.json()
        assert res_json["success"] is True
        assert res_json["data"]["name"] == "Suneeta Sharma"
        assert res_json["data"]["id_number"] == "1234 5678 9012"
        assert res_json["data"]["date_of_birth"] == "01/01/1985"
        assert res_json["data"]["gender"] == "Female"
