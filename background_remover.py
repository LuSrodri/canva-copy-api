from PIL import Image
from transformers import pipeline

class BackgroundRemover:
    def __init__(self):
        """Initialize the RMBG-1.4 model from BriaAI for Background Free"""
        self.model_name = "briaai/RMBG-1.4"
        
        print(f"Loading model {self.model_name}...")
        
        # Load the model using the image-segmentation pipeline
        self.pipe = pipeline(
            "image-segmentation",
            model=self.model_name,
            trust_remote_code=True
        )
        
        print("Model loaded successfully!")
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove the background from an image
        
        Args:
            image: PIL Image in any format
            
        Returns:
            PIL Image with removed background (RGBA)
        """
        # Make prediction using the pipeline
        result = self.pipe(image)
        
        return result
    
    def __del__(self):
        """Clean up resources when the object is destroyed"""
        if hasattr(self, 'pipe'):
            del self.pipe