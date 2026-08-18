from pydantic import BaseModel, Field
from typing import Optional

class ExtractedData(BaseModel):
    name: Optional[str] = Field(None, description="Extracted name, or null if not detected")
    id_number: Optional[str] = Field(None, description="Extracted ID number (PAN or Aadhaar), or null if not detected")
    date_of_birth: Optional[str] = Field(None, description="Extracted Date of Birth (DD/MM/YYYY format), or null if not detected")
    gender: Optional[str] = Field(None, description="Extracted gender (Male, Female, or Transgender), or null if not detected")

class OCRResponse(BaseModel):
    success: bool = Field(..., description="Indicates if the OCR operation was successful")
    data: Optional[ExtractedData] = Field(None, description="Extracted structural fields")
    raw_text: Optional[str] = Field(None, description="Raw text extracted by Tesseract OCR")
    error: Optional[str] = Field(None, description="Error message in case of failure")
