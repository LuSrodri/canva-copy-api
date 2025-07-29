import torch
from transformers import AutoModelForImageSegmentation, AutoProcessor
from PIL import Image
import numpy as np
from torchvision import transforms

class BackgroundRemover:
    def __init__(self):
        """Inicializa o modelo RMBG-1.4 da BriaAI"""
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_name = "briaai/RMBG-1.4"
        
        print(f"Carregando modelo {self.model_name} no dispositivo: {self.device}")
        
        # Carregar o modelo e o processador
        self.model = AutoModelForImageSegmentation.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        self.processor = AutoProcessor.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )
        
        # Mover modelo para o dispositivo apropriado
        self.model.to(self.device)
        self.model.eval()
        
        print("Modelo carregado com sucesso!")
    
    def remove_background(self, image: Image.Image) -> Image.Image:
        """
        Remove o background de uma imagem
        
        Args:
            image: Imagem PIL em formato RGB
            
        Returns:
            Imagem PIL com background removido (RGBA)
        """
        # Preprocessar a imagem
        inputs = self.processor(image, return_tensors="pt")
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        
        # Fazer a predição
        with torch.no_grad():
            predictions = self.model(**inputs)
        
        # Processar a máscara de saída
        mask = predictions.logits
        mask = torch.sigmoid(mask)
        mask = mask.cpu().numpy().squeeze()
        
        # Redimensionar a máscara para o tamanho original da imagem
        mask = Image.fromarray((mask * 255).astype(np.uint8))
        mask = mask.resize(image.size, Image.LANCZOS)
        
        # Aplicar a máscara à imagem original
        # Converter imagem para RGBA
        image_rgba = image.convert("RGBA")
        
        # Aplicar a máscara como canal alpha
        image_rgba.putalpha(mask)
        
        return image_rgba
    
    def __del__(self):
        """Limpar recursos quando o objeto é destruído"""
        if hasattr(self, 'model'):
            del self.model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()