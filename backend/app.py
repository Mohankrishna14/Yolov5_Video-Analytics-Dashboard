import os
import shutil
from uuid import uuid4
from typing import Optional, List

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, ImageDraw
import torch

app = FastAPI(title="YOLOv5 Image Inference")

# Outputs directory
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")

# CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def load_yolov5_model(device: str):
    """
    Load YOLOv5 via torch.hub. This will download the model the first time.
    device: 'cpu' or 'cuda:0' etc.
    """
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.to(device)
    model.eval()
    return model

@app.post("/predict-image")
async def predict_image(file: UploadFile = File(...), use_gpu: Optional[str] = Form("false")):
    """
    Predict on uploaded image.
    - file: uploaded image
    - use_gpu: "true" or "false" (form field)
    """
    warnings: List[str] = []
    try:
        use_gpu_bool = str(use_gpu).lower() in ("1", "true", "yes")
    except:
        use_gpu_bool = False

    # Save input
    ext = os.path.splitext(file.filename)[1] or ".jpg"
    file_id = uuid4().hex
    input_path = os.path.join(OUTPUT_DIR, f"{file_id}_input{ext}")
    output_path = os.path.join(OUTPUT_DIR, f"{file_id}_output.jpg")

    with open(input_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Select device
    device = "cpu"
    if use_gpu_bool:
        if torch.cuda.is_available():
            device = "cuda:0"
        else:
            warnings.append("Requested GPU but CUDA is not available; falling back to CPU")

    # Load model (cached by torch.hub between calls)
    try:
        model = load_yolov5_model(device)
    except Exception as e:
        return JSONResponse({"status": "error", "error": f"Failed to load model: {e}"}, status_code=500)

    # Run inference
    try:
        results = model(input_path, size=640)  # size can be tuned
        # Save annotated image using results.render()
        annotated_imgs = results.render()  # list of numpy arrays (RGB)
        if len(annotated_imgs) > 0:
            import numpy as np
            arr = annotated_imgs[0]
            im = Image.fromarray(arr)
            im.save(output_path, "JPEG")
        else:
            # fallback: annotate manually
            with Image.open(input_path) as im:
                draw = ImageDraw.Draw(im)
                w, h = im.size
                draw.text((10, 10), "No detections", fill="red")
                im.convert("RGB").save(output_path, "JPEG")

    except Exception as e:
        return JSONResponse({"status": "error", "error": f"Inference failed: {e}"}, status_code=500)

    host = os.environ.get("BACKEND_HOST", "http://localhost:8000")
    output_url = f"{host}/outputs/{os.path.basename(output_path)}"
    return {"status": "ok", "output_url": output_url, "warnings": warnings}
