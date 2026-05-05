from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import uuid
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

def get_ytdl_opts(download: bool = False, is_audio: bool = False, filepath: str = None):
    opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': not download,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'skip': ['hls', 'dash']
            }
        }
    }
    
    if download:
        opts['outtmpl'] = filepath
        opts['extract_flat'] = False
        
        if is_audio:
            opts['format'] = 'bestaudio/best'
            opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        else:
            opts['format'] = 'best[ext=mp4]/best'
    
    return opts

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "status": "API Online!",
        "mensagem": 'Use POST em /info com {"url": "link_do_video"} para obter informações'
    })

@app.route('/info', methods=['POST', 'OPTIONS'])
def get_info():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
            
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL nao fornecida'}), 400
        
        ydl_opts = get_ytdl_opts(download=False)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            return jsonify({
                'title': info.get('title', 'Titulo nao disponivel'),
                'thumbnail': info.get('thumbnail', ''),
                'duration': info.get('duration', 0),
                'success': True
            })
    except Exception as e:
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON'}), 400
            
        url = data.get('url')
        if not url:
            return jsonify({'error': 'URL nao fornecida'}), 400
            
        is_audio = data.get('is_audio', False)
        
        uid = uuid.uuid4().hex
        filename = f"{uid}.{'mp3' if is_audio else 'mp4'}"
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        
        ydl_opts = get_ytdl_opts(download=True, is_audio=is_audio, filepath=filepath)
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
