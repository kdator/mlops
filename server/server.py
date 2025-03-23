from fastapi import FastAPI, File, UploadFile
import numpy as np
import torch
from PIL import Image
import io
import time
from prometheus_client import Counter, Summary, Histogram
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

REQUEST_COUNT = Counter("preprocess_requests_total", "Total number of preprocess requests")
REQUEST_TIME = Summary("preprocess_request_processing_seconds", "Time spent processing preprocess request")
REQUEST_HISTOGRAM = Histogram(
    "preprocess_request_duration_seconds", "Histogram for preprocess request duration",
    buckets=[0.1, 0.5, 0.9, 0.99]
)

def preprocess_image(image_bytes):
    image = Image.open(io.BytesIO(image_bytes)).convert("L")
    image = image.resize((28, 28))

    img_array = np.array(image) / 255.0  
    img_tensor = torch.tensor(img_array, dtype=torch.float32).unsqueeze(0).unsqueeze(0) 

    return img_tensor.tolist()

@app.post("/preprocess")
async def preprocess(file: UploadFile = File(...)):
    REQUEST_COUNT.inc()
    start_time = time.time()
    
    image_bytes = await file.read()
    processed_image = preprocess_image(image_bytes)
    
    duration = time.time() - start_time
    REQUEST_TIME.observe(duration)
    REQUEST_HISTOGRAM.observe(duration)
    
    return {"processed_image": processed_image}

@app.get("/inf/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        REQUEST_TIME.observe(duration)
        REQUEST_HISTOGRAM.observe(duration)
        return response

app.add_middleware(MetricsMiddleware)
