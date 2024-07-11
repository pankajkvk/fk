from fastapi import FastAPI, File, UploadFile
from app.schemas import VerificationResult
from app.services.document_service import extract_document_info
from app.services.video_service import process_video
from app.services.cross_verification_service import cross_verify
from app.services.identity_matching_service import match_identity
from app.services.decision_service import calculate_approval_score, make_decision
import tempfile
import os

app = FastAPI()

@app.post("/verify", response_model=VerificationResult)
async def verify(document: UploadFile = File(...), video: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(document.filename)[1]) as tmp_document:
        tmp_document.write(await document.read())
        tmp_document_path = tmp_document.name

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(video.filename)[1]) as tmp_video:
        tmp_video.write(await video.read())
        tmp_video_path = tmp_video.name

    try:
        # Document verification
        doc_info, tampering_score, security_score = extract_document_info(tmp_document_path)
        document_score = (tampering_score + security_score) / 2

        # Video verification
        liveness_score, video_face, spoken_text = process_video(tmp_video_path)

        # Cross-verification
        cross_verify_score = cross_verify(doc_info, spoken_text)

        # Identity matching
        face_match_score = match_identity(tmp_document_path, video_face)

        # Calculate final score
        ocr_score = doc_info['ocr_confidence']
        final_score = calculate_approval_score(document_score, ocr_score, liveness_score, cross_verify_score, face_match_score)

        # Make decision
        decision = make_decision(final_score)

        return VerificationResult(
            final_score=final_score,
            decision=decision,
            document_score=document_score,
            ocr_score=ocr_score,
            liveness_score=liveness_score,
            cross_verify_score=cross_verify_score,
            face_match_score=face_match_score
        )
    finally:
        os.unlink(tmp_document_path)
        os.unlink(tmp_video_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)