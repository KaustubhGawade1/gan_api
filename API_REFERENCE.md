# API Reference Guide

## Base URL
```
http://localhost:8000
API Prefix: /api/v1
```

## Endpoints

### 1. Health Check

**Endpoint:** `GET /api/v1/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Status Code:** 200 OK

---

### 2. Generate Image

**Endpoint:** `POST /api/v1/generate`

Generate an image from a text prompt using the conditional GAN.

**Request Header:**
```
Content-Type: application/json
```

**Request Body:**
```json
{
  "prompt": "A beautiful sunset over the ocean with mountains in the background",
  "seed": 42,
  "guidance_scale": 1.0
}
```

**Request Parameters:**

| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| `prompt` | string | Yes | - | 1-500 characters |
| `seed` | integer | No | 42 | Non-negative |
| `guidance_scale` | float | No | 1.0 | Non-negative |

**Response:**
- **Status Code:** 200 OK
- **Content-Type:** image/jpeg
- **Body:** Raw JPEG image bytes (256×256 RGB)

**Error Responses:**

**400 Bad Request** - Invalid input
```json
{
  "detail": "Prompt cannot be empty"
}
```

**422 Unprocessable Entity** - Validation error
```json
{
  "detail": [
    {
      "loc": ["body", "prompt"],
      "msg": "ensure this value has at most 500 characters",
      "type": "value_error.string.max_length"
    }
  ]
}
```

**500 Internal Server Error** - Server error
```json
{
  "detail": "Generation error: CUDA out of memory"
}
```

---

### 3. Root Endpoint

**Endpoint:** `GET /`

Get API information and available endpoints.

**Response:**
```json
{
  "message": "Welcome to GAN Backend API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/v1/health",
  "generate": "/api/v1/generate"
}
```

**Status Code:** 200 OK

---

## Usage Examples

### cURL

#### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

#### Generate Image
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A beautiful sunset"}' \
  --output image.jpg
```

#### Generate with Custom Seed
```bash
curl -X POST http://localhost:8000/api/v1/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A futuristic city",
    "seed": 123,
    "guidance_scale": 1.5
  }' \
  --output image.jpg
```

### Python Requests

```python
import requests
from pathlib import Path

# Health check
response = requests.get("http://localhost:8000/api/v1/health")
print(response.json())
# Output: {'status': 'healthy', 'version': '1.0.0'}

# Generate image
response = requests.post(
    "http://localhost:8000/api/v1/generate",
    json={
        "prompt": "A beautiful sunset over the ocean",
        "seed": 42
    }
)

if response.status_code == 200:
    Path("image.jpg").write_bytes(response.content)
    print("✅ Image saved!")
else:
    print(f"❌ Error: {response.json()}")
```

### Python Httpx (Async)

```python
import httpx
from pathlib import Path

async def generate_image(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/api/v1/generate",
            json={"prompt": prompt}
        )
        if response.status_code == 200:
            Path("image.jpg").write_bytes(response.content)
            return "✅ Image saved!"
        return f"❌ Error: {response.text}"

# Usage
import asyncio
asyncio.run(generate_image("A beautiful sunset"))
```

### JavaScript/Node.js

```javascript
const axios = require('axios');
const fs = require('fs');

async function generateImage(prompt) {
  try {
    const response = await axios.post(
      'http://localhost:8000/api/v1/generate',
      { prompt: prompt },
      { responseType: 'arraybuffer' }
    );
    
    fs.writeFileSync('image.jpg', response.data);
    console.log('✅ Image saved!');
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message);
  }
}

generateImage('A beautiful sunset');
```

### JavaScript Fetch API

```javascript
async function generateImage(prompt) {
  const response = await fetch('http://localhost:8000/api/v1/generate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt: prompt })
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('❌ Error:', error.detail);
    return;
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'generated.jpg';
  a.click();
}

generateImage('A futuristic city with flying cars');
```

### PowerShell

```powershell
# Health check
Invoke-RestMethod -Uri "http://localhost:8000/api/v1/health" `
  -Method Get | ConvertTo-Json

# Generate image
$response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/generate" `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{"prompt" = "A beautiful sunset"} | ConvertTo-Json)

$response | Out-File -FilePath "image.jpg" -Encoding Byte
```

---

## Prompt Examples

Try these prompts for different image styles:

### Landscapes
- "A serene lake surrounded by snow-capped mountains at sunset"
- "A dense forest with sunlight filtering through the trees"
- "A vast desert with sand dunes under a starry night sky"

### Urban
- "A modern city skyline at night with neon lights"
- "A busy street market with colorful stalls and people"
- "An ancient castle on a hilltop overlooking a medieval town"

### Abstract
- "An abstract painting with vibrant colors and geometric shapes"
- "A swirling galaxy of colors and light"
- "Fractal patterns in blues and purples"

### Fantasy
- "A dragon flying over a castle in the clouds"
- "A mystical forest with glowing magical creatures"
- "An underwater city with bioluminescent coral"

### Portraits
- "A portrait of a woman with renaissance-style clothing"
- "A cyberpunk android with glowing eyes"
- "A wise old wizard with a long beard"

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Debug mode
DEBUG=False

# API settings
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000

# Device: 'cuda' or 'cpu'
DEVICE=cuda

# Model paths and names
MODEL_WEIGHTS_PATH=./weights/generator.pth
CLIP_MODEL_NAME=openai/clip-vit-base-patch32

# Generation settings
IMAGE_SIZE=256
JPEG_QUALITY=95
NOISE_DIM=100
```

### Python Settings

Access settings in code:

```python
from app.core.config import settings

print(settings.APP_NAME)           # "GAN Backend API"
print(settings.DEVICE)              # "cuda" or "cpu"
print(settings.TEXT_EMBEDDING_DIM)  # 512
print(settings.NOISE_DIM)           # 100
```

---

## Request/Response Validation

### Valid Request
```json
{
  "prompt": "A beautiful sunset",
  "seed": 42,
  "guidance_scale": 1.0
}
```

### Invalid Requests and Errors

**Empty Prompt**
```json
{
  "prompt": "",
  "seed": 42
}
```
Response: `{"detail": "Prompt cannot be empty"}`

**Prompt Too Long**
```json
{
  "prompt": "A" × 501  // 501 characters
}
```
Response: `{"detail": [..., "ensure this value has at most 500 characters"]}`

**Wrong Data Type**
```json
{
  "prompt": 123,  // Should be string
  "seed": "not a number"  // Should be integer
}
```
Response: `{"detail": [...]}`

**Missing Required Field**
```json
{
  "seed": 42
}
```
Response: `{"detail": [{"loc": ["body", "prompt"], "msg": "field required"}]}`

---

## Performance Notes

### Typical Response Times

| Scenario | GPU (CUDA) | CPU |
|----------|-----------|-----|
| Simple prompt | 2-3s | 15-20s |
| Complex prompt | 3-5s | 20-30s |
| With text encoding | +100-300ms | +500-1000ms |

### Tips for Faster Generation

1. **Use GPU**: ~3-5x faster than CPU
2. **Simpler Prompts**: Shorter prompts may generate faster
3. **Reuse Seed**: Same seed = reproducible results
4. **Concurrent Requests**: Limited by device memory

---

## Error Handling

### Common HTTP Status Codes

| Code | Meaning | Example |
|------|---------|---------|
| 200 | Success | Image generated successfully |
| 400 | Bad Request | Empty prompt, invalid input |
| 422 | Validation Error | Wrong data type, missing field |
| 500 | Server Error | CUDA out of memory, model load failed |

### Error Response Format

```json
{
  "detail": "Human-readable error message"
}
```

### Handling Errors in Code

```python
import requests
from requests.exceptions import RequestException

try:
    response = requests.post(
        "http://localhost:8000/api/v1/generate",
        json={"prompt": "A sunset"}
    )
    response.raise_for_status()
    
    with open("image.jpg", "wb") as f:
        f.write(response.content)

except requests.exceptions.Timeout:
    print("❌ Request timed out")
except requests.exceptions.HTTPError as e:
    print(f"❌ HTTP Error: {e.response.status_code}")
    print(f"   Message: {e.response.json()['detail']}")
except RequestException as e:
    print(f"❌ Connection Error: {e}")
```

---

## Rate Limiting (Future Enhancement)

Currently not implemented. To add rate limiting:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/generate")
@limiter.limit("5/minute")
async def generate_image(...):
    pass
```

---

## Authentication (Future Enhancement)

Currently not implemented. To add JWT authentication:

```python
from fastapi.security import HTTPBearer
from fastapi import HTTPException, status

security = HTTPBearer()

@router.post("/generate")
async def generate_image(
    credentials: HTTPAuthCredentials = Depends(security)
):
    token = credentials.credentials
    # Validate token...
    pass
```

---

## Webhooks/Callbacks (Future Enhancement)

For async image generation:

```json
{
  "prompt": "A beautiful sunset",
  "callback_url": "https://your-service.com/webhook"
}
```

Would POST result image to callback URL when done.

---

## API Testing

### Using FastAPI TestClient

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_generate():
    response = client.post(
        "/api/v1/generate",
        json={"prompt": "A test"}
    )
    assert response.status_code in [200, 500]  # 200 if weights exist
```

---

## Monitoring & Logging

### Check Health Regularly

```python
import requests
import time

def monitor_health(interval=60):
    while True:
        try:
            response = requests.get(
                "http://localhost:8000/api/v1/health",
                timeout=5
            )
            if response.status_code == 200:
                print("✅ API is healthy")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
        
        time.sleep(interval)

monitor_health()
```

---

## Support & Documentation

- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json
- **README**: See `README.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Deployment**: See `DEPLOYMENT.md`

---

**Happy generating! 🎨**
