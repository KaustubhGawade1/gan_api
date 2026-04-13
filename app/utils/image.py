"""Utility functions for image processing"""
import io
from typing import Optional

import torch
from PIL import Image


def tensor_to_image(
    tensor: torch.Tensor,
    denormalize: bool = True,
) -> Image.Image:
    """
    Convert PyTorch tensor to PIL Image.
    
    Args:
        tensor: Image tensor of shape (3, H, W) or (1, 3, H, W)
        denormalize: If True, assumes values in [-1, 1], converts to [0, 255]
    
    Returns:
        PIL Image in RGB mode
    """
    # Handle batch dimension
    if tensor.dim() == 4:
        tensor = tensor[0]
    
    # Move to CPU and detach
    tensor = tensor.cpu().detach()
    
    # Transpose to (H, W, 3)
    if tensor.dim() == 3:
        tensor = tensor.permute(1, 2, 0)
    
    # Denormalize if needed
    if denormalize:
        tensor = (tensor + 1) / 2
    
    # Clamp to [0, 1]
    tensor = torch.clamp(tensor, 0, 1)
    
    # Convert to numpy
    image_np = tensor.numpy()
    
    # Scale to [0, 255] if not already
    if image_np.max() <= 1.0:
        image_np = (image_np * 255).astype("uint8")
    else:
        image_np = image_np.astype("uint8")
    
    # Create PIL Image
    pil_image = Image.fromarray(image_np, mode="RGB")
    
    return pil_image


def image_to_bytes(
    image: Image.Image,
    format: str = "JPEG",
    quality: int = 95,
) -> bytes:
    """
    Convert PIL Image to bytes.
    
    Args:
        image: PIL Image
        format: Output format ("JPEG" or "PNG")
        quality: JPEG quality (1-100), ignored for PNG
    
    Returns:
        Image bytes
    """
    buffer = io.BytesIO()
    
    if format.upper() == "JPEG":
        # Ensure image is RGB for JPEG
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(buffer, format="JPEG", quality=quality, optimize=True)
    elif format.upper() == "PNG":
        image.save(buffer, format="PNG", optimize=True)
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    buffer.seek(0)
    return buffer.getvalue()


def validate_image_tensor(
    tensor: torch.Tensor,
    expected_channels: int = 3,
    expected_size: Optional[int] = 256,
) -> bool:
    """
    Validate image tensor shape and values.
    
    Args:
        tensor: Image tensor
        expected_channels: Expected number of channels
        expected_size: Expected spatial dimensions (square images)
    
    Returns:
        True if valid, False otherwise
    """
    # Check dimensions
    if tensor.dim() not in [3, 4]:
        return False
    
    # Check channels
    if tensor.dim() == 3:
        if tensor.shape[0] != expected_channels:
            return False
        height, width = tensor.shape[1:]
    else:
        if tensor.shape[1] != expected_channels:
            return False
        height, width = tensor.shape[2:]
    
    # Check spatial dimensions if specified
    if expected_size is not None:
        if height != expected_size or width != expected_size:
            return False
    
    return True
