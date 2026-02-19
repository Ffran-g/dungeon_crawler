"""
Configuración global del juego
"""

import os

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SAVES_DIR = os.path.join(ASSETS_DIR, "saves")
FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")

# Asegurar que existan los directorios
os.makedirs(SAVES_DIR, exist_ok=True)
os.makedirs(FONTS_DIR, exist_ok=True)

# Configuración de fuente
DEFAULT_FONT = "consolas"
DEFAULT_FONT_SIZE = 18
TITLE_FONT_SIZE = 32
SMALL_FONT_SIZE = 14

# Configuración de sonido (placeholder para futura implementación)
SOUND_ENABLED = True
MUSIC_ENABLED = True

# Configuración de pantalla
FULLSCREEN = False
RESIZABLE = False

# Debug
DEBUG_MODE = False
SHOW_FPS = False

# Opciones de juego
SKIP_TUTORIAL = False
AUTO_SAVE_ENABLED = True

# Configuración de combate
SHOW_DAMAGE_NUMBERS = True
ANIMATION_SPEED = 0.5  # segundos

# Configuración de IA
AI_THINK_TIME = 500  # milisegundos
