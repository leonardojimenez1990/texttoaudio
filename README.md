# Flask Web App Starter

A Flask starter template as per [these docs](https://flask.palletsprojects.com/en/3.0.x/quickstart/#a-minimal-application).

## Getting Started

Previews should run automatically when starting a workspace.


# Text-to-Speech Platform 🎵

Una plataforma completa de conversión de texto a audio con interfaz web moderna y API RESTful. Convierte cualquier texto en audio de alta calidad con soporte multi-idioma y funcionalidades avanzadas.

## 🚀 Características

### ✨ Funcionalidades Principales
- **🎤 Conversión TTS**: Genera audio MP3 de alta calidad usando Google Text-to-Speech
- **🌍 Multi-idioma**: Soporte para 10 idiomas (Español, Inglés, Francés, Alemán, Italiano, Portugués, Ruso, Japonés, Coreano, Chino)
- **⚡ Control de velocidad**: Ajusta la velocidad de reproducción de 0.5x a 2.0x
- **📦 Procesamiento por lotes**: Genera hasta 10 archivos de audio simultáneamente
- **📜 Historial persistente**: Guarda y accede a generaciones anteriores
- **📝 Plantillas predefinidas**: Templates listos para podcasts, notificaciones, tutoriales

### 🎨 Interfaz de Usuario
- **📱 Responsive**: Interfaz adaptable a móviles y desktop
- **🎯 Intuitiva**: Diseño limpio y fácil de usar
- **⏱️ Tiempo real**: Contador de caracteres y feedback instantáneo
- **🎵 Reproductor integrado**: Controls de audio HTML5 nativos
- **📥 Descarga directa**: Enlaces de descarga de archivos MP3

### 🔧 Tecnología
- **🖼️ Frontend**: Streamlit + HTML/CSS personalizado
- **⚙️ Backend**: Flask API RESTful
- **🗄️ Base de datos**: SQLite con threading seguro
- **🎧 Audio**: gTTS + pydub para procesamiento
- **🚀 Deployment**: Gunicorn/Waitress ready

## 🛠️ Instalación

### Prerrequisitos
- Python 3.8+
- pip
- Virtual environment (recomendado)

### Configuración Local

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd texttoaudio
```

2. **Crear entorno virtual**
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# o
.venv\Scripts\activate     # Windows
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Inicializar base de datos**
```bash
# La base de datos se crea automáticamente al ejecutar
```

## 🚀 Uso

### Método 1: Aplicación Streamlit (Recomendado)

```bash
# Ejecutar aplicación principal
streamlit run main.py
```

La aplicación estará disponible en `http://localhost:8501`

### Método 2: API Flask

```bash
# Desarrollo
chmod +x devserver.sh
./devserver.sh

# Producción
gunicorn main_flask:app
```

La API estará disponible en `http://localhost:5000`

## 📖 Guía de Uso

### Interfaz Streamlit

1. **Seleccionar idioma** en la barra lateral
2. **Ajustar velocidad** con el slider
3. **Elegir plantilla** predefinida (opcional)
4. **Escribir texto** (máximo 5000 caracteres)
5. **Generar audio** con el botón principal
6. **Reproducir y descargar** el archivo generado

### Modo Lote

1. Ir a la pestaña **"📦 Modo Lote"**
2. **Especificar número** de textos (1-10)
3. **Escribir cada texto** en las áreas correspondientes
4. **Generar lote** - se creará un ZIP con todos los audios
5. **Descargar ZIP** con todos los archivos

### Historial

- Accede a la pestaña **"📜 Historial"**
- Ve todas las generaciones anteriores
- Reproduce archivos directamente
- Descarga archivos individuales

## 🔌 API Reference

### Endpoints Principales

#### Generar Audio Individual
```http
POST /generate_audio
Content-Type: application/json

{
  "text": "Texto a convertir",
  "lang": "es",
  "speed": 1.0
}
```

#### Generar Lote
```http
POST /generate_batch_audio
Content-Type: application/json

{
  "texts": ["Texto 1", "Texto 2", "Texto 3"],
  "lang": "es"
}
```

#### Obtener Historial
```http
GET /history
```

#### Health Check
```http
GET /health
```

#### Información del Sistema
```http
GET /system_info
```

### Idiomas Soportados

| Código | Idioma |
|--------|---------|
| `es` | Español |
| `en` | English |
| `fr` | Français |
| `de` | Deutsch |
| `it` | Italiano |
| `pt` | Português |
| `ru` | Русский |
| `ja` | 日本語 |
| `ko` | 한국어 |
| `zh` | 中文 |

## 🏗️ Arquitectura

### Estructura del Proyecto

```
texttoaudio/
├── 📄 main.py              # Aplicación Streamlit principal
├── 📄 main_flask.py        # API Flask backend
├── 📄 config.py            # Configuraciones por entorno
├── 📄 wsgi.py             # Entry point WSGI
├── 📄 requirements.txt     # Dependencias Python
├── 📄 devserver.sh        # Script de desarrollo
├── 🗄️ tts_history.db      # Base de datos SQLite
├── 📁 audio_files/        # Archivos generados
│   └── 🎵 *.mp3          # Archivos de audio
├── 📁 src/               # Frontend assets
│   ├── 📄 index.html     # Interfaz web
│   ├── 📄 style.css      # Estilos CSS
│   └── 📁 public/        # Archivos públicos
└── 📁 __pycache__/       # Cache Python
```

### Base de Datos

**Tabla `audio_history`:**
```sql
CREATE TABLE audio_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    text TEXT NOT NULL,
    language TEXT NOT NULL,
    filename TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_favorite BOOLEAN DEFAULT FALSE
);
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Configuración Flask
FLASK_CONFIG=development  # development, production, testing
FLASK_DEBUG=True         # Solo desarrollo
SECRET_KEY=your-secret-key

# Configuración servidor
PORT=5000
HOST=0.0.0.0
```

### Configuración de Producción

1. **Usar Gunicorn**
```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 main_flask:app
```

2. **Configurar Nginx** (opcional)
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /src/ {
        alias /path/to/your/app/src/;
        expires 1h;
    }
}
```

## 🧪 Testing

### Ejecutar Tests (futuro)
```bash
# Unit tests
python -m pytest tests/

# Coverage
python -m pytest --cov=main tests/
```

### Testing Manual API
```bash
# Test health check
curl http://localhost:5000/health

# Test audio generation
curl -X POST http://localhost:5000/generate_audio \
  -H "Content-Type: application/json" \
  -d '{"text":"Hola mundo","lang":"es"}'
```

## 📊 Monitoreo

### Logs
- Los logs se guardan en `logs/` (crear directorio)
- Niveles: INFO, WARNING, ERROR
- Rotación automática cuando alcanza 10MB

### Métricas
- Health check endpoint: `/health`
- System info: `/system_info`
- Database status incluido

## 🔒 Seguridad

### Implementadas
- ✅ Validación de input
- ✅ Límites de caracteres
- ✅ Sanitización de archivos
- ✅ Error handling seguro

### Por Implementar
- 🔄 Rate limiting
- 🔄 Autenticación
- 🔄 HTTPS enforcing
- 🔄 Input sanitization avanzada

## 🚀 Deployment

### Streamlit Cloud
```bash
# Configurar secrets en Streamlit Cloud
# Hacer push al repositorio
# Conectar con Streamlit Cloud
```

### Docker (opcional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main_flask:app"]
```

### Heroku
```bash
# Crear Procfile
echo "web: gunicorn main_flask:app" > Procfile

# Deploy
git push heroku main
```

## 🛣️ Roadmap

### v1.1 (Próximo)
- [ ] Sistema de cache Redis
- [ ] Rate limiting API
- [ ] Unit tests completos
- [ ] Logging estructurado

### v1.2 (Futuro)
- [ ] Autenticación JWT
- [ ] Múltiples voces TTS
- [ ] Análisis de sentiment
- [ ] Webhooks

### v2.0 (Largo plazo)
- [ ] IA voice cloning
- [ ] Real-time streaming
- [ ] Mobile app
- [ ] Analytics dashboard

## 🤝 Contribución

1. Fork el proyecto
2. Crear branch (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Estándares de Código
- PEP 8 para Python
- Docstrings para funciones
- Type hints recomendados
- Tests para nuevas features

## 📝 Changelog

### v1.0.0 (Actual)
- ✅ Generación TTS básica
- ✅ Interfaz Streamlit
- ✅ API Flask
- ✅ Soporte multi-idioma
- ✅ Procesamiento por lotes
- ✅ Historial persistente
- ✅ Sistema de plantillas

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

## 🙏 Reconocimientos

- **Google Text-to-Speech** - Motor TTS principal
- **Streamlit** - Framework de interfaz
- **Flask** - API backend
- **pydub** - Procesamiento de audio

## 📞 Soporte

¿Necesitas ayuda? Aquí tienes algunas opciones:

- 📧 **Email**: [leonardojimenez1990@gmail.com]
- 🐛 **Issues**: [GitHub Issues](https://github.com/leonardojimenez1990/texttoaudio/issues)
- 💬 **linkedin**: [Servidor de linkedin](https://www.linkedin.com/in/leonardo-jim%C3%A9nez-pearce-18488611b/)

---

**¡Convierte texto en audio de manera fácil y profesional!** 🎵

*Hecho con ❤️ usando Python, Streamlit y Flask*