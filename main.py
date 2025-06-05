import streamlit as st
import os
import time
import sqlite3
from datetime import datetime
from gtts import gTTS
import zipfile
import io
import base64

# Configuración de la página
st.set_page_config(
    page_title="Text-to-Speech Platform",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_FOLDER = os.path.join(BASE_DIR, 'audio_files')
os.makedirs(PUBLIC_FOLDER, exist_ok=True)

# Inicializar base de datos
@st.cache_resource
def init_db():
    try:
        conn = sqlite3.connect('tts_history.db', check_same_thread=False)
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
        return True
    except Exception as e:
        st.error(f"❌ Error inicializando base de datos: {e}")
        return False

def save_to_history(text, language, filename):
    try:
        conn = sqlite3.connect('tts_history.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audio_history (text, language, filename)
            VALUES (?, ?, ?)
        ''', (text, language, filename))
        conn.commit()
        conn.close()
    except Exception as e:
        st.error(f"Error guardando en historial: {e}")

def get_history():
    try:
        conn = sqlite3.connect('tts_history.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM audio_history ORDER BY created_at DESC LIMIT 20')
        history = cursor.fetchall()
        conn.close()
        return history
    except Exception as e:
        st.error(f"Error obteniendo historial: {e}")
        return []

def get_audio_download_link(file_path, file_name):
    """Generar enlace de descarga para archivo de audio"""
    with open(file_path, "rb") as f:
        audio_bytes = f.read()
    
    b64 = base64.b64encode(audio_bytes).decode()
    return f'<a href="data:audio/mp3;base64,{b64}" download="{file_name}">📥 Descargar {file_name}</a>'

def generate_audio(text, language, speed=1.0):
    """Generar archivo de audio"""
    try:
        # Validaciones
        if not text.strip():
            st.error("❌ El texto no puede estar vacío")
            return None
            
        if len(text) > 5000:
            st.error("❌ El texto es demasiado largo (máximo 5000 caracteres)")
            return None
        
        # Generar nombre único
        timestamp = int(time.time())
        filename = f'tts_audio_{timestamp}.mp3'
        filepath = os.path.join(PUBLIC_FOLDER, filename)
        
        # Crear progreso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        status_text.text("🎤 Generando audio...")
        progress_bar.progress(30)
        
        # Generar TTS
        tts = gTTS(text=text, lang=language, slow=(speed < 0.8))
        
        progress_bar.progress(70)
        status_text.text("💾 Guardando archivo...")
        
        tts.save(filepath)
        
        progress_bar.progress(90)
        status_text.text("📝 Guardando en historial...")
        
        # Guardar en historial
        save_to_history(text, language, filename)
        
        progress_bar.progress(100)
        status_text.text("✅ ¡Audio generado exitosamente!")
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return filepath, filename
        
    except Exception as e:
        st.error(f"❌ Error generando audio: {str(e)}")
        return None

def generate_batch_audio(texts, language):
    """Generar múltiples archivos de audio"""
    try:
        if not texts or len(texts) > 10:
            st.error("❌ Debe proporcionar entre 1 y 10 textos")
            return None
            
        timestamp = int(time.time())
        zip_filename = f"batch_audio_{timestamp}.zip"
        zip_filepath = os.path.join(PUBLIC_FOLDER, zip_filename)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with zipfile.ZipFile(zip_filepath, 'w') as zip_file:
            total_texts = len([t for t in texts if t.strip()])
            
            for i, text in enumerate(texts):
                if not text.strip():
                    continue
                    
                status_text.text(f"🎤 Generando audio {i+1}/{total_texts}...")
                progress = int((i / total_texts) * 100)
                progress_bar.progress(progress)
                
                filename = f"batch_audio_{i+1}_{timestamp}.mp3"
                filepath = os.path.join(PUBLIC_FOLDER, filename)
                
                tts = gTTS(text=text.strip(), lang=language)
                tts.save(filepath)
                
                # Agregar al ZIP
                zip_file.write(filepath, filename)
                
                # Limpiar archivo temporal
                os.remove(filepath)
        
        progress_bar.progress(100)
        status_text.text("✅ ¡Archivos generados exitosamente!")
        
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
        
        return zip_filepath, zip_filename
        
    except Exception as e:
        st.error(f"❌ Error generando archivos: {str(e)}")
        return None

# Inicializar base de datos
init_db()

# Interfaz principal
def main():
    # Header
    st.title("🎵 Text-to-Speech Platform")
    st.markdown("### Convierte cualquier texto en audio de alta calidad")
    st.markdown("---")
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selección de idioma
        languages = {
            'es': 'Español',
            'en': 'English',
            'fr': 'Français',
            'de': 'Deutsch',
            'it': 'Italiano',
            'pt': 'Português',
            'ru': 'Русский',
            'ja': '日本語',
            'ko': '한국어',
            'zh': '中文'
        }
        
        selected_lang = st.selectbox(
            "🌍 Idioma",
            options=list(languages.keys()),
            format_func=lambda x: languages[x],
            index=0
        )
        
        # Control de velocidad
        speed = st.slider(
            "🔊 Velocidad",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        st.markdown("---")
        
        # Plantillas predefinidas
        st.subheader("📝 Plantillas")
        templates = {
            'Personalizado': '',
            'Podcast Intro': "Bienvenidos a nuestro podcast. Hoy hablaremos sobre...",
            'Notificación': "Atención: Tiene una nueva notificación...",
            'Anuncio': "Estimados usuarios, queremos anunciar que...",
            'Tutorial': "En este tutorial aprenderemos paso a paso cómo...",
            'Saludo': "¡Hola! Bienvenido a nuestra plataforma.",
            'Despedida': "Gracias por usar nuestro servicio. ¡Hasta pronto!"
        }
        
        selected_template = st.selectbox("Seleccionar plantilla", list(templates.keys()))
    
    # Tabs principales
    tab1, tab2, tab3 = st.tabs(["🎤 Generar Audio", "📦 Modo Lote", "📜 Historial"])
    
    with tab1:
        st.header("🎤 Generación Individual")
        
        # Área de texto
        default_text = templates[selected_template] if selected_template != 'Personalizado' else ''
        
        text_input = st.text_area(
            "Ingresa tu texto:",
            value=default_text,
            height=150,
            max_chars=5000,
            help="Máximo 5000 caracteres"
        )
        
        # Contador de caracteres
        char_count = len(text_input)
        if char_count > 4500:
            st.warning(f"⚠️ {char_count}/5000 caracteres (cerca del límite)")
        else:
            st.info(f"📝 {char_count}/5000 caracteres")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if st.button("🎤 Generar Audio", type="primary", use_container_width=True):
                if text_input.strip():
                    result = generate_audio(text_input, selected_lang, speed)
                    if result:
                        filepath, filename = result
                        
                        # Mostrar reproductor
                        st.success("✅ Audio generado exitosamente")
                        
                        # Reproducir audio
                        with open(filepath, 'rb') as audio_file:
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format='audio/mp3')
                        
                        # Enlace de descarga
                        download_link = get_audio_download_link(filepath, filename)
                        st.markdown(download_link, unsafe_allow_html=True)
                else:
                    st.error("❌ Por favor, ingresa algún texto")
        
        with col2:
            if st.button("🗑️ Limpiar", use_container_width=True):
                st.rerun()
    
    with tab2:
        st.header("📦 Generación por Lotes")
        st.markdown("Genera múltiples archivos de audio a la vez")
        
        # Número de textos
        num_texts = st.number_input("Número de textos", min_value=1, max_value=10, value=3)
        
        texts = []
        for i in range(num_texts):
            text = st.text_area(
                f"Texto {i+1}:",
                key=f"batch_text_{i}",
                height=80,
                max_chars=1000
            )
            texts.append(text)
        
        if st.button("📦 Generar Lote", type="primary"):
            valid_texts = [t for t in texts if t.strip()]
            if valid_texts:
                result = generate_batch_audio(valid_texts, selected_lang)
                if result:
                    zip_filepath, zip_filename = result
                    
                    st.success(f"✅ Generados {len(valid_texts)} archivos de audio")
                    
                    # Enlace de descarga del ZIP
                    with open(zip_filepath, 'rb') as zip_file:
                        zip_bytes = zip_file.read()
                    
                    st.download_button(
                        label="📥 Descargar ZIP",
                        data=zip_bytes,
                        file_name=zip_filename,
                        mime="application/zip"
                    )
            else:
                st.error("❌ Por favor, ingresa al menos un texto")
    
    with tab3:
        st.header("📜 Historial de Audio")
        
        history = get_history()
        
        if history:
            for item in history:
                id_audio, text, language, filename, created_at, is_favorite = item
                
                with st.expander(f"🎵 {text[:50]}..." if len(text) > 50 else f"🎵 {text}"):
                    col1, col2, col3 = st.columns([3, 1, 1])
                    
                    with col1:
                        st.write(f"**Texto:** {text}")
                        st.write(f"**Idioma:** {languages.get(language, language)}")
                        st.write(f"**Fecha:** {created_at}")
                    
                    with col2:
                        # Reproducir si el archivo existe
                        filepath = os.path.join(PUBLIC_FOLDER, filename)
                        if os.path.exists(filepath):
                            with open(filepath, 'rb') as audio_file:
                                audio_bytes = audio_file.read()
                                st.audio(audio_bytes, format='audio/mp3')
                    
                    with col3:
                        if os.path.exists(filepath):
                            download_link = get_audio_download_link(filepath, filename)
                            st.markdown(download_link, unsafe_allow_html=True)
                        else:
                            st.write("❌ Archivo no disponible")
        else:
            st.info("📭 No hay archivos en el historial")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: gray;'>"
        "🎵 Text-to-Speech Platform - Convierte texto a audio fácilmente"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()