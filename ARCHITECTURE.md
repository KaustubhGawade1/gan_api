# GAN Backend API - Architecture & Design

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    FastAPI Application                  │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │  API Router (APIRouter)                          │   │
│  │  - GET  /health                                  │   │
│  │  - POST /generate (JSON → Image)                 │   │
│  │  - GET  / (Root Info)                            │   │
│  └──────────────────────────────────────────────────┘   │
│                       ↓                                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Dependency Injection (FastAPI Depends)          │   │
│  │  - get_inference_service()                       │   │
│  └──────────────────────────────────────────────────┘   │
│                       ↓                                   │
│  ┌──────────────────────────────────────────────────┐   │
│  │  ModelManager (Singleton)                        │   │
│  │  - initialize() → Load models once               │   │
│  │  - get_inference_service()                       │   │
│  │  - cleanup()                                     │   │
│  └──────────────────────────────────────────────────┘   │
│           ↙                                  ↘            │
│  ┌─────────────────┐              ┌──────────────────┐  │
│  │  InferenceService│              │ Generator Model  │  │
│  │  - encode_text() │              │ - forward()      │  │
│  │  - generate_img()│              │ - load_weights() │  │
│  │  - tensor_pil()  │              │ - save_weights() │  │
│  └─────────────────┘              └──────────────────┘  │
│           ↓                              ↓                │
│  ┌─────────────────────────────────────────────────┐   │
│  │  External Models (HuggingFace)                   │   │
│  │  - CLIP Text Model (openai/clip-vit-base-...)   │   │
│  │  - CLIP Processor                                │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
└─────────────────────────────────────────────────────────┘
         ↓                          ↓
    ┌────────┐              ┌────────────┐
    │  CUDA  │              │    CPU     │
    │  GPU   │              │  Inference │
    └────────┘              └────────────┘
```

## Request-Response Flow

### 1. Health Check
```
GET /api/v1/health
    ↓
    Status 200 OK
    {
        "status": "healthy",
        "version": "1.0.0"
    }
```

### 2. Image Generation
```
POST /api/v1/generate
Content-Type: application/json

{
    "prompt": "A beautiful sunset",
    "seed": 42,
    "guidance_scale": 1.0
}
    ↓
    InferenceService.generate_image_bytes()
        ├→ encode_text(prompt) using CLIP
        ├→ generate random noise
        ├→ Generator.forward(noise, text_embedding)
        ├→ denormalize tensor [-1,1] → [0,255]
        ├→ tensor_to_pil(tensor)
        ├→ image_to_bytes(pil_image, format='JPEG')
        └→ return bytes
    ↓
    Status 200 OK
    Content-Type: image/jpeg
    [raw JPEG bytes]
```

## Module Breakdown

### `app/main.py`
- FastAPI application factory
- Lifespan management (startup/shutdown)
- CORS middleware configuration
- GZIP compression middleware
- Root endpoint
- Uvicorn server entry point

**Key Features:**
- Singleton model initialization on startup
- Graceful cleanup on shutdown
- Type hints for all functions

### `app/api/routes.py`
- APIRouter instance with `/api/v1` prefix
- Health check endpoint
- Image generation endpoint
- Error handling with HTTP exceptions
- Request/response validation via Pydantic

**Key Features:**
- Streaming response for memory efficiency
- Comprehensive error messages
- Input validation

### `app/core/config.py`
- Pydantic Settings for configuration management
- Environment variable support
- Device auto-detection (CUDA/CPU)
- Default values for all settings

**Configuration Variables:**
- `APP_NAME`, `APP_VERSION`
- `DEBUG` mode toggle
- `API_PREFIX`, `HOST`, `PORT`
- `DEVICE`, `MODEL_WEIGHTS_PATH`
- `CLIP_MODEL_NAME`, `TEXT_EMBEDDING_DIM`
- `NOISE_DIM`, `IMAGE_SIZE`, `JPEG_QUALITY`

### `app/core/dependencies.py`
- ModelManager singleton class
- Lazy initialization of models
- FastAPI dependency for injection
- Lifecycle management (initialize, cleanup)

**Pattern:** Singleton ensures models load only once

### `app/models/generator.py`
- PyTorch Generator model
- Conditional GAN architecture
- Noise + text embedding inputs
- Image output (256×256×3)

**Architecture:**
```
Input: [noise (100), text_embedding (512)]
    ↓
MLP Projection: [512, 512] → combine
    ↓
Dense Layer: 2048 → 512×4×4
    ↓
Reshape: (512, 4, 4)
    ↓
Transposed Convolution Stack (6 layers):
  - Conv(512→256): 4×4 → 8×8
  - Conv(256→128): 8×8 → 16×16
  - Conv(128→64): 16×16 → 32×32
  - Conv(64→32): 32×32 → 64×64
  - Conv(32→16): 64×64 → 128×128
  - Conv(16→3): 128×128 → 256×256 + Tanh
    ↓
Output: (3, 256, 256) in [-1, 1] range
```

### `app/services/inference.py`
- InferenceService class
- CLIP model loading and caching
- Text encoding pipeline
- Image generation orchestration
- Tensor/PIL/bytes conversion utilities

**Key Methods:**
- `encode_text(prompt)`: CLIP → normalized embedding
- `generate_image(prompt, seed)`: orchestrates full pipeline
- `generate_image_bytes(prompt, format)`: returns raw bytes
- `_tensor_to_pil()`: tensor → PIL Image
- `_image_to_bytes()`: PIL → JPEG/PNG bytes

### `app/schemas/request.py`
- Pydantic models for request/response validation
- `GenerateRequest`: prompt, seed, guidance_scale
- `HealthResponse`: status, version
- `ErrorResponse`: error details

**Features:**
- Field validation (min_length, max_length, ge, etc.)
- JSON schema examples for documentation

### `app/utils/image.py`
- Image utility functions
- Tensor ↔ PIL conversions
- Tensor ↔ Bytes conversions
- Image validation

## Design Patterns

### 1. **Singleton Pattern** (ModelManager)
- Ensures models load only once during app startup
- Prevents repeated initialization costs
- Thread-safe on app startup

```python
model_manager = ModelManager()
model_manager.initialize()  # Once on startup
inference_service = model_manager.get_inference_service()  # Every request
```

### 2. **Dependency Injection** (FastAPI Depends)
- Decouples route handlers from services
- Enables easy testing and mocking
- FastAPI manages lifecycle

```python
@router.post("/generate")
async def generate_image(
    request: GenerateRequest,
    inference_service: InferenceService = Depends(get_inference_service),
):
    # inference_service is provided automatically
```

### 3. **Factory Pattern** (create_app)
- Encapsulates app configuration
- Enables multiple app instances if needed
- Cleaner separation of concerns

```python
def create_app() -> FastAPI:
    app = FastAPI(...)
    app.add_middleware(...)
    app.include_router(...)
    return app

app = create_app()
```

## Error Handling

### HTTP Status Codes
- **200 OK**: Successful image generation
- **400 Bad Request**: Invalid input (empty prompt, invalid seed, etc.)
- **422 Unprocessable Entity**: Validation failure (missing field, wrong type)
- **500 Internal Server Error**: Model inference failure, CUDA OOM, etc.

### Error Response Format
```json
{
    "detail": "Descriptive error message",
    "error_code": "ERROR_CODE"  # Optional
}
```

## Performance Characteristics

### Memory Usage
- **Startup**: ~4GB (GPU) or ~2GB (CPU)
  - CLIP model: ~343MB
  - Generator: ~128MB
  - PyTorch runtime: ~1-3GB
- **Per Request**: ~2GB temporary (GPU), ~1GB (CPU)

### Latency
- **GPU (CUDA)**: 2-5 seconds
  - Text encoding: 100-300ms
  - Image generation: 1.5-4s
- **CPU**: 15-30 seconds
  - Text encoding: 500-1000ms
  - Image generation: 10-25s

### Throughput
- **Sequential**: 12-30 requests/minute (GPU)
- **Concurrent**: Limited by available VRAM
  - Multi-worker Gunicorn: ~2-4 workers recommended
  - CUDA streams for batching: Possible future enhancement

## Deployment Options

### 1. Development
```bash
uvicorn app.main:app --reload
```

### 2. Production (Single Worker)
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Production (Multi-Worker)
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
```

### 4. Docker
```bash
docker build -t gan-backend .
docker run --gpus all -p 8000:8000 gan-backend
```

### 5. Kubernetes
See helm deployment configurations

## Testing Strategy

### Unit Tests
- Model initialization and forward pass
- Utility functions (tensor conversions)
- Configuration loading

### Integration Tests
- API endpoint responses
- Error handling
- Request/response validation

### Load Tests
- Concurrent request handling
- Memory usage under load
- GPU memory management

## Security Considerations

### Input Validation
- ✅ Prompt length: max 500 characters
- ✅ Seed: non-negative integer
- ✅ Guidance scale: non-negative float

### Authentication
- ❌ Currently none (add JWT for production)

### Rate Limiting
- ❌ Currently none (add redis-backed limiter)

### CORS
- ⚠️ Currently allows all origins (restrict for production)

## Future Enhancements

1. **Batch Generation**: Support multiple prompts per request
2. **Model Caching**: Cache text embeddings for repeated prompts
3. **Advanced Guidance**: Implement classifier-free guidance
4. **Model Variants**: Support multiple model sizes (tiny, small, large)
5. **Prompt Engineering**: Auto-enhance prompts with templates
6. **Async Queue**: Background task queue for long generations
7. **WebSocket Support**: Real-time streaming of generation progress
8. **Model Distillation**: Smaller, faster models for edge deployment
