#!/usr/bin/env python3
"""
WSGI entry point para producción
Optimizado para Streamlit Cloud y otros entornos
"""
import os
import sys

# Agregar el directorio del proyecto al path
project_dir = os.path.dirname(__file__)
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

# Importar la aplicación
try:
    from main import app
    
    # Configurar para entorno de producción
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'fallback-secret-key'),
        DEBUG=False,
        TESTING=False
    )
    
    # Aplicación WSGI
    application = app
    
except ImportError as e:
    print(f"Error importando aplicación: {e}")
    raise

if __name__ == "__main__":
    # Solo para testing directo del wsgi
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)