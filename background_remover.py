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
        
        # L4-specific optimizations
        torch.set_float32_matmul_precision('high')
        torch.backends.cudnn.benchmark = True  # Optimize for consistent input sizes
        torch.backends.cuda.matmul.allow_tf32 = True  # Enable TF32 for L4
        torch.backends.cudnn.allow_tf32 = True
        
        # Automatically detect device (GPU if available, CPU otherwise)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Using device: {self.device}")
        
        # Enable mixed precision for L4
        self.use_amp = torch.cuda.is_available()
        self.scaler = torch.cuda.amp.GradScaler() if self.use_amp else None
        
        self.model.to(self.device)
        self.model.eval()
        
        # Compile model for better performance (PyTorch 2.0+)
        if hasattr(torch, 'compile') and torch.cuda.is_available():
            try:
                self.model = torch.compile(self.model, mode='reduce-overhead')
                print("Model compiled successfully for better performance!")
            except Exception as e:
                print(f"Model compilation failed, continuing with standard model: {e}")
                pass
        
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
        input_tensor = self.transform_image(image).unsqueeze(0).to(self.device, non_blocking=True)
        
        # Make prediction with automatic mixed precision for L4
        with torch.no_grad():
            if self.use_amp:
                with torch.cuda.amp.autocast():
                    preds = self.model(input_tensor)[-1].sigmoid()
                    preds = preds.cpu()
            else:
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
    
    def clear_gpu_cache(self):
        """Clear GPU cache to free memory"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    
    def __del__(self):
        """Clean up resources when the object is destroyed"""
        if hasattr(self, 'model'):
            del self.model
        self.clear_gpu_cache()