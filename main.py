from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image
from background_remover import BackgroundRemover

# Inicializar a aplicação FastAPI sem documentação
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# CORS - desabilitado por padrão, mas pronto para configuração
# Descomente as linhas abaixo se precisar habilitar CORS
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure os origins permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

# Inicializar o removedor de background
bg_remover = BackgroundRemover()

@app.get("/ping")
async def ping():
    """Endpoint de health check"""
    return {"status": "ok", "message": "Background Remover API is running"}

@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    """
    Remove o background de uma imagem
    
    Args:
        file: Arquivo de imagem (PNG, JPG, JPEG)
    
    Returns:
        Imagem com background removido em formato PNG
    """
    # Verificar se o arquivo é uma imagem
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="Arquivo deve ser uma imagem (PNG, JPG, JPEG)"
        )
    
    try:
        # Ler a imagem do arquivo enviado
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # Converter para RGB se necessário
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        
        # Processar a imagem
        result_image = bg_remover.remove_background(input_image)
        
        # Converter resultado para bytes
        output_buffer = io.BytesIO()
        result_image.save(output_buffer, format='PNG')
        output_buffer.seek(0)
        
        return Response(
            content=output_buffer.getvalue(),
            media_type="image/png",
            headers={"Content-Disposition": "attachment; filename=no_background.png"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar a imagem: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)