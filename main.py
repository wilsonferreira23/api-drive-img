from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
import requests
import re
from io import BytesIO

app = FastAPI()

def convert_drive_link_to_direct(image_url: str) -> str:
    # Extraindo o FILE_ID do link do Google Drive
    match = re.search(r"https://drive\.google\.com/(?:file/d/|open\?id=)([\w-]+)", image_url)
    if match:
        file_id = match.group(1)
        return f"https://drive.google.com/uc?export=download&id={file_id}"
    raise ValueError("Link do Google Drive inválido ou não compatível.")

@app.get("/get-image")
async def get_image(image_url: str):
    try:
        # Converter link do Google Drive, se necessário
        if "drive.google.com" in image_url:
            image_url = convert_drive_link_to_direct(image_url)
        
        # Baixar a imagem
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Converter o conteúdo para um buffer em memória
        image_buffer = BytesIO(response.content)
        image_buffer.seek(0)  # Certifique-se de que o ponteiro esteja no início
        
        # Retornar como StreamingResponse
        return StreamingResponse(image_buffer, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar a imagem: {str(e)}")
