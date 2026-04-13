"""Dependency injection and singleton patterns for model loading"""
from typing import Optional

from app.core.config import settings
from app.models.generator import Generator
from app.services.inference import InferenceService


class ModelManager:
    """Singleton manager for model lifecycle and loading."""
    
    _instance: Optional["ModelManager"] = None
    _generator: Optional[Generator] = None
    _inference_service: Optional[InferenceService] = None
    
    def __new__(cls) -> "ModelManager":
        """Ensure only one instance exists (singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def initialize(self) -> None:
        """Initialize and load all models once."""
        if self._inference_service is not None:
            return  # Already initialized
        
        self._generator = Generator(
            noise_dim=settings.NOISE_DIM,
            text_embedding_dim=settings.TEXT_EMBEDDING_DIM
        )
        self._generator.load_weights(settings.MODEL_WEIGHTS_PATH)
        self._generator.to(settings.DEVICE)
        self._generator.eval()
        
        self._inference_service = InferenceService(
            generator=self._generator,
            device=settings.DEVICE
        )
    
    def get_inference_service(self) -> InferenceService:
        """Get the inference service (lazy initialization if needed)."""
        if self._inference_service is None:
            self.initialize()
        return self._inference_service
    
    def cleanup(self) -> None:
        """Cleanup resources."""
        if self._generator is not None:
            del self._generator
            self._generator = None
        if self._inference_service is not None:
            del self._inference_service
            self._inference_service = None


# Global model manager instance
model_manager = ModelManager()


async def get_inference_service() -> InferenceService:
    """FastAPI dependency for getting the inference service."""
    return model_manager.get_inference_service()
