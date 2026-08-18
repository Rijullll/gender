import os
import cv2
import numpy as np
import pytesseract

# Configure path to Tesseract executable if set in environment variables
# Example: TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
TESSERACT_CMD = os.getenv("TESSERACT_CMD")
if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def rotate_by_osd(img: np.ndarray) -> np.ndarray:
    """
    Detects if the image is rotated (90, 180, 270 degrees) using Tesseract OSD
    and corrects the orientation using OpenCV.
    """
    try:
        # Ensure we run OSD on a grayscale version
        gray = img
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
        # OSD requires text-filled images. Check if there are reasonable dimensions.
        h, w = gray.shape[:2]
        if h < 200 or w < 200:
            return img

        osd_data = pytesseract.image_to_osd(gray)
        rotation_angle = 0
        for line in osd_data.split("\n"):
            if "Rotate:" in line:
                rotation_angle = int(line.split(":")[-1].strip())
                break
        
        if rotation_angle == 90:
            return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        elif rotation_angle == 180:
            return cv2.rotate(img, cv2.ROTATE_180)
        elif rotation_angle == 270:
            return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    except Exception:
        # Fall back if OSD fails (e.g. not enough text, or OSD language pack missing)
        pass
    return img

def execute_ocr(binary_img: np.ndarray, gray_img: np.ndarray = None) -> str:
    """
    Executes Tesseract OCR on the preprocessed image.
    Uses '--oem 3 --psm 6' configuration.
    Includes fallbacks (e.g., trying grayscale image, changing PSM) if text output is poor.
    """
    config = "--oem 3 --psm 6"
    try:
        text = pytesseract.image_to_string(binary_img, config=config)
    except Exception as e:
        raise RuntimeError(
            f"Tesseract OCR execution failed. Ensure Tesseract is installed and path is configured. Error: {str(e)}"
        )

    # Fallback 1: If text is extremely short, try grayscale image (binarization might have washed out text)
    min_alnum_chars = 15
    text_alnum_count = len([c for c in text if c.isalnum()])
    
    if text_alnum_count < min_alnum_chars and gray_img is not None:
        try:
            gray_text = pytesseract.image_to_string(gray_img, config=config)
            gray_alnum_count = len([c for c in gray_text if c.isalnum()])
            if gray_alnum_count > text_alnum_count:
                text = gray_text
                text_alnum_count = gray_alnum_count
        except Exception:
            pass

    # Fallback 2: If text is still sparse, try PSM 11 (Sparse text, find as much text as possible)
    if text_alnum_count < min_alnum_chars:
        try:
            sparse_text = pytesseract.image_to_string(binary_img, config="--oem 3 --psm 11")
            sparse_alnum_count = len([c for c in sparse_text if c.isalnum()])
            if sparse_alnum_count > text_alnum_count:
                text = sparse_text
        except Exception:
            pass

    return text.strip()
