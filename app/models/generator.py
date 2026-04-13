"""PyTorch Generator model for conditional GAN"""
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn


class Generator(nn.Module):
    """
    Conditional GAN Generator that takes:
    - Noise vector (latent code)
    - Text embedding (condition from CLIP)
    """
    
    def __init__(
        self,
        noise_dim: int = 100,
        text_embedding_dim: int = 512,
        generated_image_size: int = 256,
        num_channels: int = 3,
    ):
        super().__init__()
        
        self.noise_dim = noise_dim
        self.text_embedding_dim = text_embedding_dim
        self.generated_image_size = generated_image_size
        self.num_channels = num_channels
        
        # Projection and fusion of noise and text embedding
        self.projection_dim = 512
        
        # Project text embedding
        self.text_projection = nn.Sequential(
            nn.Linear(text_embedding_dim, self.projection_dim),
            nn.ReLU(inplace=True),
        )
        
        # Project noise
        self.noise_projection = nn.Sequential(
            nn.Linear(noise_dim, self.projection_dim),
            nn.ReLU(inplace=True),
        )
        
        # Fused representation
        combined_dim = self.projection_dim * 2
        
        # Initial dense layer to generate initial spatial feature map
        # (4, 4, 512)
        self.initial_dense = nn.Sequential(
            nn.Linear(combined_dim, 4 * 4 * 512),
            nn.ReLU(inplace=True),
        )
        
        # Transposed convolutional layers to upsample
        self.conv_layers = nn.Sequential(
            # (4, 4, 512) -> (8, 8, 256)
            nn.ConvTranspose2d(512, 256, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            # (8, 8, 256) -> (16, 16, 128)
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            # (16, 16, 128) -> (32, 32, 64)
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            
            # (32, 32, 64) -> (64, 64, 32)
            nn.ConvTranspose2d(64, 32, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            
            # (64, 64, 32) -> (128, 128, 16)
            nn.ConvTranspose2d(32, 16, kernel_size=4, stride=2, padding=1, bias=False),
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),
            
            # (128, 128, 16) -> (256, 256, 3)
            nn.ConvTranspose2d(16, num_channels, kernel_size=4, stride=2, padding=1, bias=False),
            nn.Tanh(),  # Output in [-1, 1]
        )
        
        self.device_type: Optional[str] = None
    
    def forward(self, noise: torch.Tensor, text_embedding: torch.Tensor) -> torch.Tensor:
        """
        Generate image from noise and text embedding.
        
        Args:
            noise: (batch_size, noise_dim) tensor
            text_embedding: (batch_size, text_embedding_dim) tensor
        
        Returns:
            Generated image tensor of shape (batch_size, 3, 256, 256)
        """
        # Project inputs
        text_proj = self.text_projection(text_embedding)  # (batch, projection_dim)
        noise_proj = self.noise_projection(noise)  # (batch, projection_dim)
        
        # Concatenate projections
        combined = torch.cat([text_proj, noise_proj], dim=1)  # (batch, 2 * projection_dim)
        
        # Dense layer to generate initial feature map
        features = self.initial_dense(combined)  # (batch, 4 * 4 * 512)
        features = features.view(-1, 512, 4, 4)  # (batch, 512, 4, 4)
        
        # Convolutional upsampling to generate image
        image = self.conv_layers(features)  # (batch, 3, 256, 256)
        
        return image
    
    def load_weights(self, path: str) -> None:
        """Load pre-trained weights from file."""
        weights_path = Path(path)
        if weights_path.exists():
            state_dict = torch.load(weights_path, map_location=self.device_type)
            self.load_state_dict(state_dict, strict=False)
        else:
            print(f"Warning: Weights file not found at {path}. Using random initialization.")
    
    def save_weights(self, path: str) -> None:
        """Save model weights to file."""
        weights_path = Path(path)
        weights_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.state_dict(), weights_path)
