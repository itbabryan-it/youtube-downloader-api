from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import tempfile
import os

app = FastAPI()

@app.get("/")
def home():
    return {"status": "API TikTok online"}

@app.get("/baixar")
def baixar(url: str = Query(...)):
    pasta = tempfile.mkdtemp()
    saida = os.path.join(pasta, "%(title)s.%(ext)s")

    opts = {
        "outtmpl": saida,
        "format": "best[ext=mp4]/best",
        "noplaylist": True,
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            arquivo = ydl.prepare_filename(info)

        return FileResponse(
            arquivo,
            media_type="video/mp4",
            filename="tiktok.mp4"
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"erro": str(e)}
        )
