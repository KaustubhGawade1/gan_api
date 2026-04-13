import torch.nn as nn

class Generator(nn.Module):
    def __init__(self, noise_dim=100, embed_dim=512):
        super(Generator, self).__init__()
        # ... Your transposed convolution layers here ...
        
    def forward(self, noise, text_embedding):
        # ... forward pass logic ...
        return image