import torch
import io
from torchvision.utils import save_image
from model import Generator
from transformers import CLIPTextModel, CLIPTokenizer

class GANInference:
    def __init__(self, weights_path):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load CLIP for text processing
        self.tokenizer = CLIPTokenizer.from_pretrained("openai/clip-vit-base-patch32")
        self.text_encoder = CLIPTextModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
        
        # Initialize and load Generator
        self.generator = Generator().to(self.device)
        self.generator.load_state_dict(torch.load(weights_path, map_location=self.device))
        self.generator.eval()

    @torch.no_grad()
    def generate_image(self, prompt):
        # 1. Tokenize and embed text
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(self.device)
        text_embedding = self.text_encoder(**inputs).pooler_output
        
        # 2. Sample noise
        noise = torch.randn(1, 100).to(self.device)
        
        # 3. Generate
        generated_tensor = self.generator(noise, text_embedding)
        
        # 4. Convert tensor to raw image bytes
        buffer = io.BytesIO()
        save_image(generated_tensor, buffer, format="JPEG", normalize=True, value_range=(-1, 1))
        buffer.seek(0)
        
        return buffer