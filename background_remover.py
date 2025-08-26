from PIL import Image
import torch
from torchvision import transforms
from transformers import AutoModelForImageSegmentation

class BackgroundRemover:
    def __init__(self):
        """Initialize the model for background remover"""
        # Load the model
        self.model_name = "ZhengPeng7/BiRefNet-matting"
        print(f"Loading local model from {self.model_name}...")
        self.model = AutoModelForImageSegmentation.from_pretrained(
            self.model_name, 
            trust_remote_code=True
        )
        
        # Set precision and device
        torch.set_float32_matmul_precision('high')
        
        # Automatically detect device (GPU if available, CPU otherwise)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing settings
        self.image_size = (1024, 1024)
        self.transform_image = transforms.Compose([
            transforms.Resize(self.image_size),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
        ])
        
        print("Model loaded successfully!")
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove the background from an image
        
        Args:
            image: PIL Image in any format
            
        Returns:
            PIL Image with removed background (RGBA)
        """
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Store original size for later
        original_size = image.size
        
        # Preprocess the image
        input_tensor = self.transform_image(image).unsqueeze(0).to(self.device)
        
        # Make prediction
        with torch.no_grad():
            preds = self.model(input_tensor)[-1].sigmoid().cpu()
        
        # Get the mask
        pred = preds[0].squeeze()
        pred_pil = transforms.ToPILImage()(pred)
        
        # Resize mask to original image size
        mask = pred_pil.resize(original_size)
        
        # Apply the mask to create transparent background
        result_image = image.copy()
        result_image.putalpha(mask)
        
        return result_image
    
    def __del__(self):
        """Clean up resources when the object is destroyed"""
        if hasattr(self, 'model'):
            del self.model