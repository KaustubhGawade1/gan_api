"""Inference service for text-to-image generation"""
from typing import Tuple

import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPProcessor, CLIPTextModel

from app.core.config import settings
from app.models.generator import Generator


class InferenceService:
    """Service for handling inference with CLIP embeddings and GAN generation."""
    
    def __init__(self, generator: Generator, device: str):
        """
        Initialize inference service.
        
        Args:
            generator: Generator model instance
            device: Device to run inference on ("cuda" or "cpu")
        """
        self.generator = generator
        self.device = device
        
        # Load CLIP model and processor
        self.text_model = CLIPTextModel.from_pretrained(settings.CLIP_MODEL_NAME)
        self.processor = CLIPProcessor.from_pretrained(settings.CLIP_MODEL_NAME)
        
        # Move CLIP to device
        self.text_model = self.text_model.to(device)
        self.text_model.eval()
    
    def encode_text(self, prompt: str) -> torch.Tensor:
        """
        Encode text prompt to embedding using CLIP.
        
        Args:
            prompt: Text description
        
        Returns:
            Text embedding of shape (1, 512)
        """
        with torch.no_grad():
            inputs = self.processor(text=[prompt], return_tensors="pt", padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            outputs = self.text_model(**inputs)
            text_embedding = outputs.text_embeds  # (1, 512)
            
            # Normalize embedding
            text_embedding = F.normalize(text_embedding, p=2, dim=1)
        
        return text_embedding
    
    def generate_image(
        self,
        prompt: str,
        seed: int = 42,
        guidance_scale: float = 1.0,
    ) -> Tuple[torch.Tensor, Image.Image]:
        """
        Generate image from text prompt.
        
        Args:
            prompt: Text description of the desired image
            seed: Random seed for reproducibility
            guidance_scale: Classifier-free guidance scale (1.0 = no guidance)
        
        Returns:
            Tuple of (tensor, PIL Image)
        """
        # Set seed for reproducibility
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed(seed)
        
        # Encode text prompt
        text_embedding = self.encode_text(prompt)  # (1, 512)
        text_embedding = text_embedding.to(self.device)
        
        # Generate noise
        batch_size = 1
        noise = torch.randn(batch_size, settings.NOISE_DIM, device=self.device)
        
        # Generate image
        with torch.no_grad():
            image_tensor = self.generator(noise, text_embedding)  # (1, 3, 256, 256)
        
        # Denormalize from [-1, 1] to [0, 1]
        image_tensor = (image_tensor + 1) / 2
        image_tensor = torch.clamp(image_tensor, 0, 1)
        
        # Convert to PIL Image
        pil_image = self._tensor_to_pil(image_tensor)
        
        return image_tensor, pil_image
    
    def _tensor_to_pil(self, tensor: torch.Tensor) -> Image.Image:
        """
        Convert image tensor to PIL Image.
        
        Args:
            tensor: Image tensor of shape (1, 3, H, W) with values in [0, 1]
        
        Returns:
            PIL Image
        """
        # Take first element of batch if batch size > 1
        if tensor.dim() == 4:
            tensor = tensor[0]  # (3, H, W)
        
        # Move to CPU and detach
        tensor = tensor.cpu().detach()
        
        # Convert to numpy and transpose to (H, W, 3)
        image_np = tensor.permute(1, 2, 0).numpy()
        
        # Scale to [0, 255]
        image_np = (image_np * 255).astype("uint8")
        
        # Create PIL Image
        pil_image = Image.fromarray(image_np, mode="RGB")
        
        return pil_image
    
    def generate_image_bytes(
        self,
        prompt: str,
        seed: int = 42,
        format: str = "jpeg",
        quality: int = 95,
    ) -> bytes:
        """
        Generate image and return as raw bytes.
        
        Args:
            prompt: Text description
            seed: Random seed
            format: Image format ("jpeg" or "png")
            quality: JPEG quality (1-100)
        
        Returns:
            Raw image bytes
        """
        _, pil_image = self.generate_image(prompt=prompt, seed=seed)
        
        # Convert to bytes
        if format.lower() == "jpeg":
            image_bytes = self._image_to_bytes(pil_image, format="JPEG", quality=quality)
        elif format.lower() == "png":
            image_bytes = self._image_to_bytes(pil_image, format="PNG")
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        return image_bytes
    
    @staticmethod
    def _image_to_bytes(
        image: Image.Image,
        format: str = "JPEG",
        quality: int = 95,
    ) -> bytes:
        """
        Convert PIL Image to bytes.
        
        Args:
            image: PIL Image
            format: Image format
            quality: JPEG quality
        
        Returns:
            Image bytes
        """
        import io
        
        buffer = io.BytesIO()
        if format == "JPEG":
            image.save(buffer, format=format, quality=quality)
        else:
            image.save(buffer, format=format)
        
        buffer.seek(0)
        return buffer.getvalue()
