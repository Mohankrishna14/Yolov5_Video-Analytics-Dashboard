# YOLOv5 Image Inference — React + FastAPI (CPU / GPU)

This project adds a minimal React frontend and FastAPI backend to run YOLOv5 image inference (selectable CPU/GPU).

Branches:
- image-inference-cpu-gpu — (branch prepared) contains the new frontend and backend.

Contents:
- backend/ : FastAPI server that runs YOLOv5 and serves annotated outputs
- frontend/: Vite + React app to upload images and request inference
- docker-compose.yml (optional): run backend and frontend in containers

Quick local (Python) run — CPU:
1. Backend
   - cd backend
   - python -m venv .venv && source .venv/bin/activate
   - pip install -r requirements.txt
   - uvicorn app:app --host 0.0.0.0 --port 8000

2. Frontend
   - cd frontend
   - npm install
   - npm run dev (Vite default port 5173)

3. Open frontend at http://localhost:5173

GPU notes:
- If you want GPU inference, ensure torch with CUDA is installed in the backend environment and a compatible GPU + drivers are present.
- The inference endpoint accepts a JSON/field `use_gpu` (true/false). If true, the backend will attempt to use `cuda:0`. If torch.cuda.is_available() is false, it falls back to CPU and returns a warning in the response.

Example curl (image upload):
```
curl -X POST "http://localhost:8000/predict-image" \
  -F "file=@/path/to/image.jpg" \
  -F "use_gpu=false"
```

The endpoint returns JSON:
{
  "status": "ok",
  "output_url": "http://localhost:8000/outputs/....jpg",
  "warnings": [...]
}

Docker:
- backend/Dockerfile (CPU) — builds a CPU container.
- backend/Dockerfile.gpu — base on CUDA image; make sure to use nvidia runtime when running.
