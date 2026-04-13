from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel
from inference import GANInference

app = FastAPI(title="Conditional GAN API")
inference_engine = GANInference(weights_path="weights/generator.pth")

class GenerationRequest(BaseModel):
    prompt: str

@app.post("/generate")
async def generate(request: GenerationRequest):
    # Generate the image buffer
    image_buffer = inference_engine.generate_image(request.prompt)
    
    # Return the raw image bytes with the correct MIME type
    return Response(content=image_buffer.getvalue(), media_type="image/jpeg")

# Run via: uvicorn main:app --host 0.0.0.0 --port 8000