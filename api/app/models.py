from pydantic import BaseModel
from typing import Dict, Any

class DocumentInfo(BaseModel):
    name: str
    dob: str
    address: str
    id_number: str
    ocr_confidence: float

class VerificationResult(BaseModel):
    final_score: float
    decision: str
    document_score: float
    ocr_score: float
    liveness_score: float
    cross_verify_score: float
    face_match_score: float