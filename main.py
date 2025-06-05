# app.py - Backend Flask para Text-to-Speech con integración frontend

import os
from gtts import gTTS
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

# Rutas y carpetas
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'src')
AUDIO_FILE = os.path.join(STATIC_FOLDER, 'public', 'tts_audio.mp3')

# Ruta al frontend
@app.route("/")
def index():
    return send_file(os.path.join(STATIC_FOLDER, 'index.html'))

# Endpoint para generar audio
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    data = request.json
    text = data.get('text', '')
    lang = data.get('lang', 'es')

    if not text.strip():
        return jsonify({"error": "El texto no puede estar vacío."}), 400

    try:
        tts = gTTS(text=text, lang=lang)
        tts.save(AUDIO_FILE)
        return send_file(AUDIO_FILE, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
