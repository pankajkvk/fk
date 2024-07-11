import face_recognition
import cv2
import numpy as np

def match_identity(doc_path: str, video_face: np.ndarray) -> float:
    doc_image = cv2.imread(doc_path)
    doc_face = extract_face(doc_image)
    
    if doc_face is None or video_face is None:
        return 0.0
    
    doc_encoding = face_recognition.face_encodings(doc_face)[0]
    video_encoding = face_recognition.face_encodings(video_face)[0]
    
    similarity = face_recognition.face_distance([doc_encoding], video_encoding)[0]
    
    return 1 - similarity

def extract_face(image: np.ndarray) -> np.ndarray:
    face_locations = face_recognition.face_locations(image)
    if face_locations:
        top, right, bottom, left = face_locations[0]
        face_image = image[top:bottom, left:right]
        return face_image
    return None