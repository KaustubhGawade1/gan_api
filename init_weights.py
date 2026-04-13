"""Script to initialize and save random model weights for testing"""
import torch
from pathlib import Path
from app.models.generator import Generator


def create_dummy_weights():
    """Create dummy generator weights for testing."""
    weights_dir = Path(__file__).parent / "weights"
    weights_dir.mkdir(exist_ok=True)
    
    weights_path = weights_dir / "generator.pth"
    
    # Create model
    generator = Generator(
        noise_dim=100,
        text_embedding_dim=512,
        generated_image_size=256,
        num_channels=3,
    )
    
    # Save weights
    generator.save_weights(str(weights_path))
    print(f"✅ Dummy weights saved to {weights_path}")


if __name__ == "__main__":
    create_dummy_weights()
