import re
from typing import Optional

def clean_text(text: str) -> str:
    """
    Standardizes whitespace, normalizes characters, and removes junk.
    """
    if not text:
        return ""
    # Normalize multiple spaces and tabs to a single space
    text = re.sub(r"[ \t]+", " ", text)
    # Remove multiple consecutive newlines
    text = re.sub(r"\n+", "\n", text)
    return text.strip()

def extract_name(text: str) -> Optional[str]:
    """
    Extracts the name from Aadhaar or PAN card text structure.
    Uses heuristic line filtering to find the cardholder's name.
    """
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    
    # Common words found in ID cards that are not names
    noise_keywords = [
        "government", "india", "unique", "identification", "authority",
        "income", "tax", "department", "govt", "permanent", "account",
        "card", "number", "father", "signature", "address", "holder",
        "director", "enrollment", "male", "female", "transgender",
        "s/o", "d/o", "w/o", "c/o", "care of", "son of", "daughter of",
        "wife of", "husband of", "dob", "date of birth", "year of birth", "yob"
    ]
    
    candidate_lines = []
    for line in lines:
        line_lower = line.lower()
        
        # Skip lines containing noise keywords
        if any(keyword in line_lower for keyword in noise_keywords):
            continue
            
        # Clean line to keep only alphabetic characters, spaces, dots, dashes, and single quotes
        cleaned = "".join([c for c in line if c.isalpha() or c.isspace() or c in [".", "'", "-"]]).strip()
        cleaned = " ".join(cleaned.split())  # Normalize inner spaces
        
        if not cleaned:
            continue
            
        # Skip if the line originally had digits (like card numbers or dates)
        if any(c.isdigit() for c in line):
            continue
            
        # Name length limits
        if len(cleaned) < 3 or len(cleaned) > 40:
            continue
            
        # Name should be 1 to 5 words
        words = cleaned.split()
        if len(words) < 1 or len(words) > 5:
            continue
            
        candidate_lines.append(cleaned)
        
    if not candidate_lines:
        return None
        
    # Return the first candidate line (usually the cardholder's name)
    return candidate_lines[0]

def extract_id_number(text: str) -> Optional[str]:
    """
    Extracts PAN or Aadhaar card numbers.
    Aadhaar format: 12 digits (often grouped in 4s: XXXX XXXX XXXX).
    PAN format: 5 letters, 4 numbers, 1 letter (ABCDE1234F).
    """
    # 1. Look for Aadhaar number
    # Match 12 digits with optional spaces or dashes
    aadhaar_pattern = r"\b\d{4}\s?\d{4}\s?\d{4}\b"
    aadhaar_matches = re.findall(aadhaar_pattern, text)
    if aadhaar_matches:
        # Standardize format to "XXXX XXXX XXXX"
        digits = re.sub(r"\D", "", aadhaar_matches[0])
        return f"{digits[:4]} {digits[4:8]} {digits[8:]}"
        
    # 2. Look for PAN card number
    text_upper = text.upper()
    pan_pattern = r"\b[A-Z]{5}\d{4}[A-Z]\b"
    pan_matches = re.findall(pan_pattern, text_upper)
    if pan_matches:
        return pan_matches[0]
        
    # Fallback PAN: spacing or minor OCR issues
    pan_spaced_pattern = r"\b[A-Z]{5}\s*\d{4}\s*[A-Z]\b"
    pan_spaced_matches = re.findall(pan_spaced_pattern, text_upper)
    if pan_spaced_matches:
        return re.sub(r"\s+", "", pan_spaced_matches[0])
        
    return None

def extract_date_of_birth(text: str) -> Optional[str]:
    """
    Extracts Date of Birth (DOB) or Year of Birth (YOB).
    Returns standardized DD/MM/YYYY format (or YYYY if only year is available).
    """
    # 1. Match standard date patterns: DD/MM/YYYY, DD-MM-YYYY, DD.MM.YYYY
    date_pattern = r"\b(0[1-9]|[12]\d|3[01])[-/.](0[1-9]|1[0-2])[-/.](19|20)\d{2}\b"
    matches = re.finditer(date_pattern, text)
    full_matches = [m.group(0) for m in matches]
    if full_matches:
        # Standardize separators to "/"
        return re.sub(r"[-.]", "/", full_matches[0])
        
    # 2. Fallback to Year of Birth (YOB) e.g., "Year of Birth : 1990" or "YOB: 1990"
    yob_pattern = r"(?:YEAR OF BIRTH|YOB|BIRTH|YEAR)\s*[:\-\s]\s*((?:19|20)\d{2})\b"
    yob_matches = re.findall(yob_pattern, text.upper())
    if yob_matches:
        return yob_matches[0]
        
    return None

def extract_gender(text: str) -> Optional[str]:
    """
    Extracts gender: Male, Female, or Transgender.
    Corrects common OCR misspellings such as MAIE or FEMAIE.
    """
    text_upper = text.upper()
    
    # 1. Standard matches with word boundaries
    if re.search(r"\bFEMALE\b", text_upper):
        return "Female"
    if re.search(r"\bMALE\b", text_upper):
        return "Male"
    if re.search(r"\bTRANSGENDER\b", text_upper):
        return "Transgender"
        
    # 2. OCR misread matches (common I/L/1 confusion)
    if re.search(r"\bFEMA[IL1]E\b", text_upper):
        return "Female"
    if re.search(r"\bMA[IL1]E\b", text_upper):
        return "Male"
        
    return None
