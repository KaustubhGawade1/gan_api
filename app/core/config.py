"""Application configuration settings"""
import os
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # App metadata
    APP_NAME: str = "GAN Backend API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API settings
    API_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Model settings
    MODEL_WEIGHTS_PATH: str = os.getenv(
        "MODEL_WEIGHTS_PATH",
        str(Path(__file__).parent.parent.parent / "weights" / "generator.pth")
    )
    DEVICE: Optional[str] = os.getenv("DEVICE", "cuda" if torch_available() else "cpu")
    
    # CLIP model settings
    CLIP_MODEL_NAME: str = "openai/clip-vit-base-patch32"
    TEXT_EMBEDDING_DIM: int = 512
    
    # Generator settings
    NOISE_DIM: int = 100
    NUM_CLASSES: int = 1000  # ImageNet classes
    
    # Inference settings
    IMAGE_SIZE: int = 256
    OUTPUT_FORMAT: str = "jpeg"  # jpeg format for raw bytes
    JPEG_QUALITY: int = 95
    
    class Config:
        env_file = ".env"
        case_sensitive = True


def torch_available() -> bool:
    """Check if torch is available and if CUDA is accessible."""
    try:
        import torch
        return torch.cuda.is_available()
    except ImportError:
        return False


# Global settings instance
settings = Settings()
