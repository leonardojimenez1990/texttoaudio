import os
from gtts import gTTS
from flask import Flask, request, jsonify, send_file, send_from_directory
import sqlite3
from datetime import datetime
import time
from pydub import AudioSegment
import zipfile

app = Flask(__name__)

# Configuración mejorada de rutas y carpetas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_FOLDER = os.path.join(BASE_DIR, 'src')
PUBLIC_FOLDER = os.path.join(STATIC_FOLDER, 'public')
AUDIO_FILE = os.path.join(PUBLIC_FOLDER, 'tts_audio.mp3')

# Crear directorios si no existen
os.makedirs(PUBLIC_FOLDER, exist_ok=True)

# Servir archivos estáticos desde /src
@app.route('/src/<path:filename>')
def static_files(filename):
    return send_from_directory(STATIC_FOLDER, filename)

# Servir favicon
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(STATIC_FOLDER, 'favicon.ico')

# Ruta al frontend
@app.route("/")
def index():
    index_path = os.path.join(STATIC_FOLDER, 'index.html')
    if os.path.exists(index_path):
        return send_file(index_path)
    else:
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Text to Speech</title>
            <link rel="stylesheet" href="/src/style.css">
        </head>
        <body>
            <h1>Text to Speech Service</h1>
            <p>Coloca tu archivo index.html en la carpeta 'src'</p>
        </body>
        </html>
        """, 200

# Endpoint para generar audio con validaciones mejoradas
@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    try:
        # Validar Content-Type
        if not request.is_json:
            return jsonify({"error": "Content-Type debe ser application/json"}), 400
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "No se recibieron datos JSON válidos"}), 400
        
        text = data.get('text', '').strip()
        lang = data.get('lang', 'es')
        
        # Nuevos parámetros de configuración
        speed = data.get('speed', 1.0)  # Velocidad de habla
        voice_type = data.get('voice_type', 'default')  # Tipo de voz
        
        # Validaciones
        if not text:
            return jsonify({"error": "El texto no puede estar vacío."}), 400
        
        if len(text) > 5000:  # Límite de caracteres
            return jsonify({"error": "El texto es demasiado largo (máximo 5000 caracteres)."}), 400
        
        # Expandir idiomas soportados
        supported_languages = {
            'es': 'Spanish',
            'en': 'English', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
        
        if lang not in supported_languages:
            return jsonify({"error": f"Idioma no soportado. Idiomas disponibles: {list(supported_languages.keys())}"}), 400
            
        # Validar velocidad
        if not 0.5 <= speed <= 2.0:
            return jsonify({"error": "La velocidad debe estar entre 0.5 y 2.0"}), 400
            
        # Configurar gTTS con parámetros avanzados
        tts = gTTS(text=text, lang=lang, slow=(speed < 0.8))
        tts.save(AUDIO_FILE)
        
        # Guardar en historial
        save_to_history(text, lang, AUDIO_FILE)
        
        return send_file(AUDIO_FILE, mimetype='audio/mpeg', as_attachment=False)
        
    except ValueError as e:
        return jsonify({"error": f"Error de datos: {str(e)}"}), 400
    except Exception as e:
        app.logger.error(f"Error generando audio: {str(e)}")
        return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/generate_batch_audio', methods=['POST'])
def generate_batch_audio():
    try:
        data = request.get_json()
        texts = data.get('texts', [])
        lang = data.get('lang', 'es')
        
        if not texts or len(texts) > 10:
            return jsonify({"error": "Debe proporcionar entre 1 y 10 textos"}), 400
        
        audio_files = []
        
        for i, text in enumerate(texts):
            if len(text.strip()) == 0:
                continue
                
            filename = f"batch_audio_{i+1}_{int(time.time())}.mp3"
            filepath = os.path.join(PUBLIC_FOLDER, filename)
            
            tts = gTTS(text=text.strip(), lang=lang)
            tts.save(filepath)
            
            audio_files.append({
                'index': i+1,
                'filename': filename,
                'text_preview': text[:50] + '...' if len(text) > 50 else text
            })
        
        return jsonify({
            "success": True,
            "files": audio_files,
            "total": len(audio_files)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Inicializar base de datos
def init_db():
    conn = sqlite3.connect('tts_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audio_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            language TEXT NOT NULL,
            filename TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favorite BOOLEAN DEFAULT FALSE
        )
    ''')
    conn.commit()
    conn.close()

def save_to_history(text, language, filename):
    conn = sqlite3.connect('tts_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO audio_history (text, language, filename)
        VALUES (?, ?, ?)
    ''', (text, language, filename))
    conn.commit()
    conn.close()

@app.route('/history', methods=['GET'])
def get_history():
    conn = sqlite3.connect('tts_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM audio_history ORDER BY created_at DESC LIMIT 50')
    history = cursor.fetchall()
    conn.close()
    
    return jsonify([{
        'id': h[0], 'text': h[1], 'language': h[2], 
        'filename': h[3], 'created_at': h[4], 'is_favorite': h[5]
    } for h in history])

@app.route('/toggle_favorite/<int:audio_id>', methods=['POST'])
def toggle_favorite(audio_id):
    conn = sqlite3.connect('tts_history.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE audio_history SET is_favorite = NOT is_favorite WHERE id = ?', (audio_id,))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

TEMPLATES = {
    'podcast_intro': "Bienvenidos a nuestro podcast. Hoy hablaremos sobre...",
    'notification': "Atención: Tiene una nueva notificación...",
    'announcement': "Estimados usuarios, queremos anunciar que...",
    'tutorial': "En este tutorial aprenderemos paso a paso cómo..."
}

@app.route('/templates', methods=['GET'])
def get_templates():
    return jsonify(TEMPLATES)

# Manejo de errores globales
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Recurso no encontrado"}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({"error": "Error interno del servidor"}), 500

@app.route('/export_audio', methods=['POST'])
def export_audio():
    try:
        data = request.get_json()
        format_type = data.get('format', 'mp3')  # mp3, wav, ogg
        quality = data.get('quality', 'medium')  # low, medium, high
        
        if format_type not in ['mp3', 'wav', 'ogg']:
            return jsonify({"error": "Formato no soportado"}), 400
            
        # Configurar calidad según el tipo
        export_params = {
            'mp3': {'format': 'mp3', 'bitrate': '128k' if quality == 'medium' else '64k' if quality == 'low' else '192k'},
            'wav': {'format': 'wav'},
            'ogg': {'format': 'ogg', 'codec': 'libvorbis'}
        }
        
        # Procesar y exportar archivo
        # ... código de procesamiento ...
        
        return send_file(exported_file, as_attachment=True)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Inicializar base de datos
    init_db()
    
    # Configuración más robusta
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print(f"Iniciando servidor en puerto {port}")
    print(f"Carpeta estática: {STATIC_FOLDER}")
    print(f"Carpeta pública: {PUBLIC_FOLDER}")
    
    app.run(
        host='0.0.0.0', 
        port=port, 
        debug=debug,
        threaded=True  # Mejor manejo de concurrencia
    )