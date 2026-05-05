from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import yt_dlp
import uuid
import os

app = Flask(__name__)
CORS(app)

DOWNLOADS_DIR = "downloads"
os.makedirs(DOWNLOADS_DIR, exist_ok=True)

@app.route('/info', methods=['POST', 'GET'])
def get_info():
    if request.method == 'GET':
        return jsonify({'status': 'API funcionando! Use POST com {"url": "link"}'})
    
    try:
        data = request.get_json()
        url = data.get('url')
        
        if not url:
            return jsonify({'error': 'URL nao fornecida'}), 400
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
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

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.get_json()
        url = data.get('url')
        is_audio = data.get('is_audio', False)
        
        if not url:
            return jsonify({'error': 'URL nao fornecida'}), 400
        
        uid = uuid.uuid4().hex
        filename = f"{uid}.{'mp3' if is_audio else 'mp4'}"
        filepath = os.path.join(DOWNLOADS_DIR, filename)
        
        ydl_opts = {
            'outtmpl': filepath,
            'quiet': True,
            'no_warnings': True,
        }
        
        if is_audio:
            ydl_opts['format'] = 'bestaudio/best'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
            }]
        else:
            ydl_opts['format'] = 'best[ext=mp4]/best'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        
        return send_file(filepath, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
