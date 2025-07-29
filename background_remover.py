import torch
from transformers import AutoModelForImageSegmentation, AutoProcessor
from PIL import Image
import numpy as np
from torchvision import transforms

class BackgroundRemover:
    def __init__(self):
        """Initialize the RMBG-1.4 model from BriaAI for Background Free"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = "briaai/RMBG-1.4"
        
        print(f"Loading model {self.model_name} on device: {self.device}")
        
        # Load the model and processor
        self.model = AutoModelForImageSegmentation.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        # Move model to appropriate device
        self.model.to(self.device)
        self.model.eval()
        
        print("Model loaded successfully!")
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove the background from an image
        
        Args:
            image: PIL Image in RGB format
            
        Returns:
            PIL Image with removed background (RGBA)
        """
        # Preprocess the image
        inputs = self.processor(image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Make prediction
        with torch.no_grad():
            predictions = self.model(**inputs)
        
        # Process output mask
        mask = predictions.logits
        mask = torch.sigmoid(mask)
        mask = mask.cpu().numpy().squeeze()
        
        # Resize mask to original image size
        mask = Image.fromarray((mask * 255).astype(np.uint8))
        mask = mask.resize(image.size, Image.LANCZOS)
        
        # Apply mask to original image
        # Convert image to RGBA
        image_rgba = image.convert("RGBA")
        
        # Apply mask as alpha channel
        image_rgba.putalpha(mask)
        
        return image_rgba
    
    def __del__(self):
        """Clean up resources when the object is destroyed"""
        if hasattr(self, 'model'):
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()