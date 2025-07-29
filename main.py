from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import io
from PIL import Image
from background_remover import BackgroundRemover

# Initialize FastAPI application without documentation
app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

# CORS - disabled by default, but ready for configuration
# Uncomment the lines below if you need to enable CORS
"""
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure os origins permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
"""

# Initialize the background remover
bg_remover = BackgroundRemover()

@app.get("/ping")
async def ping():
    """Health check endpoint"""
    return {"status": "ok", "message": "Background Free API is running"}

@app.post("/remove-background")
async def remove_background(file: UploadFile = File(...)):
    """
    Remove the background from an image
    
    Args:
        file: Image file (PNG, JPG, JPEG)
    
    Returns:
        Image with removed background in PNG format
    """
    # Verify if the file is an image
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=400, 
            detail="File must be an image (PNG, JPG, JPEG)"
        )
    
    try:
        # Read the image from the uploaded file
        image_bytes = await file.read()
        input_image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if input_image.mode != 'RGB':
            input_image = input_image.convert('RGB')
        
        # Process the image
        result_image = bg_remover.remove_background(input_image)
        
        # Convert result to bytes
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
            detail=f"Error processing the image: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)