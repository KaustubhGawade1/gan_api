"""
Example script demonstrating how to use the GAN Backend API
"""
import requests
from pathlib import Path
from typing import Optional


class GANAPIClient:
    """Simple client for the GAN Backend API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the API
        """
        self.base_url = base_url.rstrip("/")
        self.api_prefix = "/api/v1"
    
    def health_check(self) -> dict:
        """Check if the API is healthy."""
        url = f"{self.base_url}{self.api_prefix}/health"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    
    def generate_image(
        self,
        prompt: str,
        seed: int = 42,
        guidance_scale: float = 1.0,
        output_path: Optional[str] = None,
    ) -> bytes:
        """
        Generate an image from a text prompt.
        
        Args:
            prompt: Text description of the desired image
            seed: Random seed for reproducibility
            guidance_scale: Guidance scale for generation
            output_path: Optional path to save the image
        
        Returns:
            Image bytes (JPEG)
        """
        url = f"{self.base_url}{self.api_prefix}/generate"
        
        payload = {
            "prompt": prompt,
            "seed": seed,
            "guidance_scale": guidance_scale,
        }
        
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        image_bytes = response.content
        
        # Save to file if path provided
        if output_path:
            Path(output_path).write_bytes(image_bytes)
            print(f"✅ Image saved to {output_path}")
        
        return image_bytes


def main():
    """Example usage of the API client."""
    
    # Initialize client
    client = GANAPIClient("http://localhost:8000")
    
    # Check health
    print("🔍 Checking API health...")
    health = client.health_check()
    print(f"✅ API Status: {health['status']}")
    print(f"   Version: {health['version']}\n")
    
    # Example prompts
    prompts = [
        "A serene landscape with mountains and a lake at sunset",
        "A futuristic city with flying cars and neon lights",
        "A cozy cabin in the snow with warm light from windows",
        "An abstract painting with vibrant colors and geometric shapes",
    ]
    
    # Generate multiple images
    for i, prompt in enumerate(prompts, 1):
        print(f"🎨 Generating image {i}/{len(prompts)}...")
        print(f"   Prompt: {prompt}")
        
        try:
            output_file = f"generated_image_{i}.jpg"
            image_bytes = client.generate_image(
                prompt=prompt,
                seed=42 + i,
                output_path=output_file,
            )
            print(f"   Size: {len(image_bytes)} bytes\n")
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error: {e}\n")
            continue
    
    print("✨ All done!")


if __name__ == "__main__":
    main()
