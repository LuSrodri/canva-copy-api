from contextlib import nullcontext
import torch
import numpy as np
from PIL import Image
from sam2.sam2_image_predictor import SAM2ImagePredictor
from transformers import pipeline

class BackgroundRemover:
    def __init__(self):
        """Initialize the SAM2 model and RMBG for background removal"""
        self.model_name = "facebook/sam2.1-hiera-tiny"
        
        print(f"Loading SAM2 model {self.model_name}...")
        
        # Check if CUDA is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {self.device}")
        
        # Load the SAM2 model with explicit device
        self.predictor = SAM2ImagePredictor.from_pretrained(self.model_name, device=self.device)
        
        print("SAM2 model loaded successfully!")

        self.rmbg_name = "briaai/RMBG-1.4"

        print(f"Loading RMBG model {self.rmbg_name}...")

        rmbg_device = 0 if self.device == "cuda" else -1
        self.rmbg = pipeline("image-segmentation",
                            model=self.rmbg_name,
                            trust_remote_code=True,
                            device=rmbg_device)
        
        print("RMBG loaded successfully!")
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove the background from an image using SAM2
        
        Args:
            image: PIL Image in any format
            
        Returns:
            PIL Image with removed background (RGBA)
        """
        numpy_image = np.array(image.convert("RGB"))
        height, width = numpy_image.shape[:2]

        box = np.array([
            0,
            0,
            int(width),
            int(height)
        ], dtype=np.float32)

        autocast_context = torch.autocast("cuda", dtype=torch.bfloat16) if self.device == "cuda" else nullcontext()

        with torch.inference_mode(), autocast_context:
            self.predictor.set_image(numpy_image)

            masks, scores, logits = self.predictor.predict(
                box=box,
                multimask_output=False,
                return_logits=True
            )

            best_index = int(np.argmax(scores))

            masks, scores, logits = self.predictor.predict(
                box=box,
                mask_input = logits[best_index:best_index+1],
                multimask_output=False,
                return_logits=True
            )

            best_index = int(np.argmax(scores))

            masks, scores, _ = self.predictor.predict(
                box=box,
                mask_input = logits[best_index:best_index+1],
                multimask_output=False
            )

        best_index = int(np.argmax(scores))
        mask_2d = masks[best_index].astype(np.uint8)
        mask_2d = 1 - mask_2d

        alpha_channel = (mask_2d * 255).astype(np.uint8)[..., None]
        rgba_image = np.concatenate([numpy_image, alpha_channel], axis=-1)

        pre_processed_image = Image.fromarray(rgba_image, mode="RGBA")

        # post_processed_image = self.rmbg(pre_processed_image)

        return pre_processed_image
    
    def __del__(self):
        """Clean up resources when the object is destroyed"""
        if hasattr(self, 'predictor'):
            del self.predictor