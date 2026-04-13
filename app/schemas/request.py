"""Pydantic schemas for request/response validation"""
from typing import Optional

from pydantic import BaseModel, Field


class GenerateRequest(BaseModel):
    """Schema for image generation request."""
    
    prompt: str = Field(
        ...,
        description="Text description of the image to generate",
        min_length=1,
        max_length=500,
    )
    seed: int = Field(
        default=42,
        description="Random seed for reproducibility",
        ge=0,
    )
    guidance_scale: float = Field(
        default=1.0,
        description="Classifier-free guidance scale (1.0 = no guidance)",
        ge=0.0,
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A beautiful sunset over the ocean with mountains in the background",
                "seed": 42,
                "guidance_scale": 1.0,
            }
        }


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str = Field(description="Health status")
    version: str = Field(description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
            }
        }


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    
    detail: str = Field(description="Error message")
    error_code: Optional[str] = Field(
        default=None,
        description="Error code for client-side handling"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid prompt provided",
                "error_code": "INVALID_INPUT",
            }
        }
