#!/usr/bin/env python3
"""
WSGI entry point para producción
"""
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(__file__))

from main import app

if __name__ == "__main__":
    app.run()