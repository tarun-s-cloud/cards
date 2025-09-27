import cv2
import pytesseract
import re
import json
import base64
import os

pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

def preprocess_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.resize(img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31, 2
    )
    return img, gray, thresh

def extract_face_and_text(image_path):
    img, gray_for_face, processed = preprocess_image(image_path)
    results = {}

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = face_cascade.detectMultiScale(gray_for_face, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

    if len(faces) > 0:
        os.makedirs("driving_face", exist_ok=True)  # ensure folder exists
        for (x, y, w, h) in faces:
            pad = 50
            x1 = max(0, x - pad)
            y1 = max(0, y - pad)
            x2 = min(img.shape[1], x + w + pad)
            y2 = min(img.shape[0], y + h + pad)
            face_img = img[y1:y2, x1:x2]
            face_path = os.path.join("driving_face", "driving_face.png")
            cv2.imwrite(face_path, face_img)

            results["Face_Image"] = face_path
            break
    else:
        results["Face_Image"] = None

    text = pytesseract.image_to_string(processed, lang="eng")
    return text

def driving_license_info(text):
    data = {}
    name_match = re.search(r"Name[:\-]?\s*([A-Za-z ]+)", text, re.IGNORECASE)
    father_match = re.search(r"(Father'?s Name|S/W/D of)[:\-]?\s*([A-Za-z ]+)", text, re.IGNORECASE)
    dob_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
    licence_match = re.search(r"(DL|Licence|License)\s*[:\-]?\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
    address_match = re.search(r"Address[:\-]?\s*(.+)", text, re.IGNORECASE)

    if name_match:
        data["Name"] = name_match.group(1).strip()
    if father_match:
        data["Father_Name"] = father_match.group(2).strip()
    if dob_match:
        data["DOB"] = dob_match.group(1).strip()
    if licence_match:
        data["Licence_No"] = licence_match.group(2).strip()
    if address_match:
        data["Address"] = address_match.group(1).strip()

    if not data:
        data["Raw_Text"] = text.strip()

    return data

def image_to_base64(img_path):
    with open(img_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def extract_license_info(image_path):
    text = extract_face_and_text(image_path)
    parsed_data = driving_license_info(text)
    return parsed_data