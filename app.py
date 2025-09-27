from flask import Flask, request, jsonify , send_from_directory
from functions.extraction import extract_license_info
import os
import base64
from flask_cors import CORS , cross_origin

app = Flask(__name__)

CORS(app , resources={r"/*": {"origins": "*"}})

@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/extract", methods=["POST"])
@cross_origin()
def extract_license():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    save_path = os.path.join("uploads", image_file.filename)
    os.makedirs("uploads", exist_ok=True)
    image_file.save(save_path)

    result = extract_license_info(save_path)

    face_path = "driving_face/driving_face.png"
    face_base64 = None
    if os.path.exists(face_path):
        with open(face_path, "rb") as img_file:
            face_base64 = base64.b64encode(img_file.read()).decode("utf-8")

    return jsonify({
        "extracted_data": result,
        "face_image_base64": face_base64
    })

if __name__ == "__main__":
    app.run()
