from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
import json
from PIL import Image
import io
import base64
import os

app = Flask(__name__)
CORS(app)

# ---- CONFIG ----
IMG_SIZE = (128, 128)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "plant_disease_model.keras")
CLASS_PATH = os.path.join(os.path.dirname(__file__), "class_names.json")

# ---- GLOBALS (lazy load) ----
model = None
class_names = None


def load_resources():
    global model, class_names

    if model is None:
        model = tf.keras.models.load_model(MODEL_PATH)

    if class_names is None:
        with open(CLASS_PATH, "r") as f:
            class_names = json.load(f)


def preprocess_image(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize(IMG_SIZE)
    arr = np.array(img, dtype=np.float32) 
    arr = np.expand_dims(arr, axis=0)
    return arr


@app.route("/predict", methods=["POST"])
def predict():
    load_resources()

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    image_bytes = file.read()

    if len(image_bytes) == 0:
        return jsonify({"error": "Empty file"}), 400

    try:
        tensor = preprocess_image(image_bytes)

        predictions = model.predict(tensor, verbose=0)[0]
        top3_idx = predictions.argsort()[-3:][::-1]

        results = [
            {
                "class": class_names[i],
                "confidence": round(float(predictions[i]) * 100, 2)
            }
            for i in top3_idx
        ]

        encoded_img = base64.b64encode(image_bytes).decode("utf-8")

        return jsonify({
            "predictions": results,
            "image_b64": encoded_img
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/classes", methods=["GET"])
def get_classes():
    load_resources()
    return jsonify({"classes": class_names, "count": len(class_names)})


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": model is not None
    })


# ---- ENTRY POINT (IMPORTANT FOR HOSTING) ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)