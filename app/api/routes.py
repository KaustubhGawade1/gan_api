"""API routes for image generation"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.core.config import settings
from app.core.dependencies import get_inference_service
from app.schemas.request import GenerateRequest, HealthResponse
from app.services.inference import InferenceService

router = APIRouter(prefix=settings.API_PREFIX, tags=["generation"])


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running and healthy",
)
async def health_check() -> HealthResponse:
    """Check the health status of the API."""
    return HealthResponse(
        status="healthy",
        version=settings.APP_VERSION,
    )


@router.post(
    "/generate",
    status_code=status.HTTP_200_OK,
    summary="Generate Image from Text",
    description="Generate an image from a text prompt using conditional GAN",
    responses={
        200: {
            "description": "Successfully generated image",
            "content": {"image/jpeg": {}},
        },
        400: {"description": "Invalid request parameters"},
        500: {"description": "Internal server error during generation"},
    },
)
async def generate_image(
    request: GenerateRequest,
    inference_service: InferenceService = Depends(get_inference_service),
) -> StreamingResponse:
    """
    Generate an image from a text prompt.
    
    - **prompt**: Text description of the image (required)
    - **seed**: Random seed for reproducibility (default: 42)
    - **guidance_scale**: Guidance scale for generation (default: 1.0)
    
    Returns raw JPEG image bytes.
    """
    try:
        # Validate request
        if not request.prompt or not request.prompt.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Prompt cannot be empty",
            )
        
        # Generate image bytes
        image_bytes = inference_service.generate_image_bytes(
            prompt=request.prompt,
            seed=request.seed,
            format=settings.OUTPUT_FORMAT,
            quality=settings.JPEG_QUALITY,
        )
        
        # Return as streaming response for memory efficiency
        return StreamingResponse(
            iter([image_bytes]),
            media_type="image/jpeg",
            headers={
                "Content-Disposition": 'inline; filename="generated_image.jpg"',
                "Cache-Control": "no-cache, no-store, must-revalidate",
            },
        )
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )
