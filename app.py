from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import uuid
import os

app = Flask(__name__)
CORS(app)  # Libera seu app Android acessar

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@app.route('/info', methods=['POST'])
def get_info():
    url = request.json['url']
    with yt_dlp.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        return jsonify({
            'title': info.get('title', 'Sem título'),
            'thumbnail': info.get('thumbnail', ''),
            'duration': info.get('duration', 0),
            'author': info.get('uploader', 'Desconhecido')
        })

@app.route('/download', methods=['POST'])
def download():
    url = request.json['url']
    is_audio = request.json.get('is_audio', False)
    
    uid = uuid.uuid4().hex
    filename = f"{uid}.{'mp3' if is_audio else 'mp4'}"
    filepath = os.path.join(DOWNLOADS_DIR, filename)
    
    opts = {
        'outtmpl': filepath,
        'quiet': True,
    }
    
    if is_audio:
        opts['format'] = 'bestaudio/best'
        opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    else:
        opts['format'] = 'best[ext=mp4]/best'
    
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)
    
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)