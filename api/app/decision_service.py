def calculate_approval_score(document_score: float, ocr_score: float, liveness_score: float, cross_verify_score: float, face_match_score: float) -> float:
    weights = {
        'document': 0.30,
        'ocr': 0.20,
        'liveness': 0.15,
        'cross_verify': 0.20,
        'face_match': 0.15
    }
    
    final_score = (
        document_score * weights['document'] +
        ocr_score * weights['ocr'] +
        liveness_score * weights['liveness'] +
        cross_verify_score * weights['cross_verify'] +
        face_match_score * weights['face_match']
    )
    
    return final_score

def make_decision(score: float) -> str:
    if score >= 0.90:
        return "Approved"
    elif score >= 0.70:
        return "Manual Review"
    else:
        return "Rejected"