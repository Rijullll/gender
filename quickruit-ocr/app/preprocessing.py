import cv2
import numpy as np

def validate_image(file_bytes: bytes) -> np.ndarray:
    """
    Decodes the uploaded bytes into an image and validates its format.
    Raises ValueError if the image is invalid or corrupted.
    """
    nparr = np.frombuffer(file_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Invalid or corrupted image file.")
    return img

def resize_image(img: np.ndarray, target_max_dim: int = 1800) -> np.ndarray:
    """
    Resizes/upscales the image to ensure high resolution for OCR (target max dimension of 1800px).
    Preserves the aspect ratio.
    """
    h, w = img.shape[:2]
    current_max = max(h, w)
    if current_max < target_max_dim:
        scale = target_max_dim / current_max
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    return img

def to_grayscale(img: np.ndarray) -> np.ndarray:
    """
    Converts a color image to grayscale.
    """
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img

def reduce_noise(img: np.ndarray) -> np.ndarray:
    """
    Reduces image noise using a bilateral filter.
    Bilateral filter is preferred for OCR as it smooths flat regions while preserving sharp edges.
    """
    return cv2.bilateralFilter(img, 9, 75, 75)

def deskew(img: np.ndarray) -> np.ndarray:
    """
    Detects skew angle and rotates the image to correct rotation.
    Only corrects fine skew within [-45, 45] degrees.
    """
    # Create binary inverted image for coordinate detection
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Get coordinates of all text pixels
    pts = np.column_stack(np.where(thresh > 0))
    if len(pts) == 0:
        return img
    
    # Get rotated bounding box
    rect = cv2.minAreaRect(pts)
    angle = rect[-1]
    
    # Normalize skew angle
    if angle < -45:
        angle = -(90 + angle)
    elif angle > 45:
        angle = 90 - angle
    else:
        angle = -angle
        
    # Only rotate if the angle is notable (between 0.2 and 45 degrees)
    if abs(angle) < 0.2 or abs(angle) > 45:
        return img
        
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Perform rotation using border replication to avoid black borders
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def threshold_image(img: np.ndarray, method: str = "adaptive") -> np.ndarray:
    """
    Applies binarization (Otsu or Adaptive Thresholding).
    Grayscale images are converted to binary black-and-white.
    """
    if method == "otsu":
        _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh
    else:
        # Gaussian Adaptive thresholding handles uneven lighting better
        return cv2.adaptiveThreshold(
            img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

def preprocess_pipeline(img: np.ndarray, threshold_method: str = "adaptive") -> tuple[np.ndarray, np.ndarray]:
    """
    Runs the complete preprocessing pipeline.
    Returns a tuple of (grayscale_image, binary_image).
    """
    # 1. Resize/upscale
    resized = resize_image(img)
    
    # 2. Grayscale conversion
    gray = to_grayscale(resized)
    
    # 3. Noise reduction
    denoised = reduce_noise(gray)
    
    # 4. Deskew
    deskewed = deskew(denoised)
    
    # 5. Thresholding
    binary = threshold_image(deskewed, method=threshold_method)
    
    return deskewed, binary
