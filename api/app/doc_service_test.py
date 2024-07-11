import cv2
import numpy as np
import pytesseract
from pyzbar import pyzbar
from app.models import DocumentInfo
import re
from dateutil import parser
import nltk
from nltk.corpus import words
import string
from typing import Tuple

# Download necessary NLTK data
nltk.download('words')
english_words = set(words.words())

def extract_document_info(image_path: str) -> Tuple[DocumentInfo, float, float]:
    image = cv2.imread(image_path)
    
    # Extract text using OCR
    text = extract_english_text(image)
    
    # Extract information
    name = extract_name(text)
    dob = extract_dob(text)
    address = extract_address(text)
    id_number = extract_id_number(text)
    
    # Calculate OCR confidence
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
    ocr_confidence = calculate_ocr_confidence(ocr_data)
    
    info = DocumentInfo(
        name=name,
        dob=dob,
        address=address,
        id_number=id_number,
        ocr_confidence=ocr_confidence
    )
    
    tampering_score = check_tampering(image)
    security_score = validate_security_features(image)
    
    return info, tampering_score, security_score

def extract_english_text(image: np.ndarray) -> str:
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to preprocess the image
    threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
    
    # Perform text extraction with Tesseract
    custom_config = r'--oem 3 --psm 6 -l eng'
    text = pytesseract.image_to_string(threshold, config=custom_config)
    
    # Filter out non-English words and special characters
    words = text.split()
    english_text = ' '.join([word for word in words if word.lower() in english_words or not word.isalpha()])
    
    return english_text

def extract_name(text: str) -> str:
    # Use regex to find potential names (assuming names are in title case)
    name_pattern = r'\b[A-Z][a-z]+ (?:[A-Z][a-z]+ )*[A-Z][a-z]+\b'
    potential_names = re.findall(name_pattern, text)
    
    # Return the longest potential name (assuming it's the full name)
    return max(potential_names, key=len, default="")

def extract_dob(text: str) -> str:
    # Use regex to find potential dates
    date_pattern = r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'
    potential_dates = re.findall(date_pattern, text)
    
    # Parse and validate dates
    for date_str in potential_dates:
        try:
            date = parser.parse(date_str)
            if 1900 < date.year < 2100:  # Assuming birthdates are within this range
                return date.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    return ""

def extract_address(text: str) -> str:
    # Use regex to find potential addresses
    address_pattern = r'\d+\s+(?:[\w\s,]+\s+){1,3}(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Court|Ct|Place|Pl)\b'
    potential_addresses = re.findall(address_pattern, text, re.IGNORECASE)
    
    # Return the longest potential address
    return max(potential_addresses, key=len, default="")

def extract_id_number(text: str) -> str:
    # Use regex to find potential ID numbers (assuming a common format)
    id_pattern = r'\b(?:\d{3}-\d{2}-\d{4}|\d{9})\b'
    potential_ids = re.findall(id_pattern, text)
    
    # Return the first potential ID found
    return potential_ids[0] if potential_ids else ""

def calculate_ocr_confidence(ocr_data: dict) -> float:
    confidences = [float(conf) for conf in ocr_data['conf'] if conf != '-1']
    return sum(confidences) / len(confidences) if confidences else 0.0

def check_tampering(image: np.ndarray) -> float:
    # Convert image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Compute the Laplacian of the image and calculate the variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    laplacian_var = np.var(laplacian)
    
    # Normalize the score (higher variance indicates less tampering)
    score = min(laplacian_var / 500, 1.0)
    
    # Check for abrupt color changes
    edges = cv2.Canny(image, 100, 200)
    edge_density = np.sum(edges) / (image.shape[0] * image.shape[1])
    edge_score = 1.0 - min(edge_density / 0.1, 1.0)
    
    # Combine scores
    final_score = (score + edge_score) / 2
    
    return final_score

def validate_security_features(image: np.ndarray) -> float:
    score = 0.0
    
    # Check for barcodes or QR codes
    barcodes = pyzbar.decode(image)
    if barcodes:
        score += 0.5
    
    # Check for hologram-like features (simplified)
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_rainbow = np.array([0, 100, 100])
    upper_rainbow = np.array([180, 255, 255])
    mask = cv2.inRange(hsv, lower_rainbow, upper_rainbow)
    rainbow_ratio = np.sum(mask) / (image.shape[0] * image.shape[1])
    if rainbow_ratio > 0.05:
        score += 0.3
    
    # Check for microprint (simplified)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    microprint_ratio = np.sum(edges) / (image.shape[0] * image.shape[1])
    if 0.1 < microprint_ratio < 0.3:
        score += 0.2
    
    return min(score, 1.0)