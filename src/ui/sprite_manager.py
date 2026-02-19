"""
Sistema de carga de sprites con fallback a dibujos generados
"""
import os
import pygame
from typing import Optional, Dict


class SpriteManager:
    """Gestor de sprites con fallback"""
    
    def __init__(self, base_path: str = "assets/sprites"):
        self.base_path = base_path
        self.cache: Dict[str, pygame.Surface] = {}
        self._load_colors()
    
    def _load_colors(self):
        """Carga colores base"""
        self.colors = {
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (200, 50, 50),
            "green": (50, 200, 50),
            "blue": (50, 50, 200),
            "yellow": (255, 255, 0),
            "cyan": (0, 255, 255),
            "orange": (255, 165, 0),
            "purple": (148, 0, 211),
            "gray": (128, 128, 128),
            "dark_gray": (60, 60, 60),
            "gold": (255, 215, 0),
        }
    
    def load_sprite(self, category: str, name: str, size: tuple = (32, 32), subfolder: str = None) -> Optional[pygame.Surface]:
        """
        Carga un sprite desde archivo o retorna None si no existe
        category: 'entities', 'ui', 'tiles', 'items'
        subfolder: subcarpeta dentro de category
        name: nombre del archivo sin extensión
        """
        cache_key = f"{category}/{subfolder}/{name}_{size[0]}x{size[1]}" if subfolder else f"{category}/{name}_{size[0]}x{size[1]}"
        
        # Verificar cache
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Buscar archivo
        exts = ['.png', '.jpg', '.jpeg', '.bmp']
        
        # Construir ruta de búsqueda
        if subfolder:
            search_path = os.path.join(self.base_path, category, subfolder)
        else:
            search_path = os.path.join(self.base_path, category)
        
        for ext in exts:
            filename = f"{name}{ext}"
            path = os.path.join(search_path, filename)
            if os.path.exists(path):
                try:
                    sprite = pygame.image.load(path).convert_alpha()
                    # Escalar manteniendo aspect ratio
                    sprite = self._scale_sprite(sprite, size)
                    self.cache[cache_key] = sprite
                    return sprite
                except Exception as e:
                    print(f"Error cargando sprite {path}: {e}")
        
        return None
    
    def _scale_sprite(self, sprite: pygame.Surface, size: tuple) -> pygame.Surface:
        """Escala un sprite manteniendo su proporción"""
        original_width = sprite.get_width()
        original_height = sprite.get_height()
        
        target_width, target_height = size
        
        # Calcular escala para ajustar dentro del tamaño objetivo
        scale = min(target_width / original_width, target_height / original_height)
        
        new_width = int(original_width * scale)
        new_height = int(original_height * scale)
        
        scaled = pygame.transform.scale(sprite, (new_width, new_height))
        
        # Crear superficie del tamaño objetivo con transparencia
        result = pygame.Surface(size, pygame.SRCALPHA)
        
        # Centrar el sprite
        x_offset = (target_width - new_width) // 2
        y_offset = (target_height - new_height) // 2
        
        result.blit(scaled, (x_offset, y_offset))
        
        return result
    
    def get_player_sprite(self, class_id: str, size: tuple = (32, 32)) -> Optional[pygame.Surface]:
        """Carga sprite del jugador según su clase"""
        class_map = {
            "warrior": "Guerrero",
            "mage": "Mago", 
            "rogue": "Picaro",
            "warlock": "Brujo",
        }
        return self.load_sprite("entities", class_map.get(class_id, "player"), size, subfolder="personajes")
    
    def get_enemy_sprite(self, enemy_name: str, enemy_type: str = None, size: tuple = (32, 32)) -> Optional[pygame.Surface]:
        """Carga sprite de enemigo según su nombre"""
        
        if not enemy_name:
            return None
        
        # Normalizar el nombre: quitar tildes, espacios a guiones, minúsculas
        def normalize(name: str) -> str:
            # Quitar tildes y caracteres especiales
            name = name.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
            name = name.replace('Á', 'A').replace('É', 'E').replace('Í', 'I').replace('Ó', 'O').replace('Ú', 'U')
            name = name.replace('ñ', 'n').replace('Ñ', 'N')
            # Reemplazar espacios y caracteres especiales con guiones bajos
            name = name.replace(' ', '_')
            return name.lower()
        
        normalized_name = normalize(enemy_name)
        
        # Buscar por nombre normalizado en todas las carpetas
        for subfolder in ["enemigos/basicos", "enemigos/elites", "enemigos/boss"]:
            sprite = self.load_sprite("entities", normalized_name, size, subfolder=subfolder)
            if sprite:
                return sprite
            # Intentar con sufijo _1 si no encuentra
            sprite = self.load_sprite("entities", f"{normalized_name}_1", size, subfolder=subfolder)
            if sprite:
                return sprite
        
        # Si no encuentra, intentar por tipo
        if enemy_type:
            type_to_folder = {
                "elite": "enemigos/elites",
                "boss": "enemigos/boss",
            }
            folder = type_to_folder.get(enemy_type)
            if folder:
                # Cargar un sprite genérico según el tipo
                if enemy_type == "boss":
                    return self.load_sprite("entities", "dragon_anciano", size, subfolder=folder)
                elif enemy_type == "elite":
                    return self.load_sprite("entities", "orco_berserker", size, subfolder=folder)
        
        return None
    
    def get_enemy_tile_sprite(self, enemy_type: str, size: tuple = (32, 32)) -> Optional[pygame.Surface]:
        """Carga sprite de enemigo para el mapa"""
        tile_map = {
            "basic": "enemigo_basico",
            "elite": "enemigo_elite",
            "boss": "enemigo_boss",
        }
        sprite_name = tile_map.get(enemy_type, "enemigo_basico")
        return self.load_sprite("tiles", sprite_name, size)
    
    def get_map_tile_sprite(self, tile_type: str, size: tuple = (32, 32)) -> Optional[pygame.Surface]:
        """Carga sprite de tile del mapa"""
        tile_map = {
            "stairs": "escaleras",
            "sanctuary": "santuario",
            "treasure": "tesoro",
            "merchant": "tienda",
            "trap": "trampa",
            "start": "escaleras",
        }
        sprite_name = tile_map.get(tile_type)
        if sprite_name:
            return self.load_sprite("tiles", sprite_name, size)
        return None
    
    def get_item_sprite(self, item_type: str, size: tuple = (32, 32)) -> Optional[pygame.Surface]:
        """Carga sprite de item"""
        return self.load_sprite("items", f"item_{item_type}", size)
    
    def get_tile_sprite(self, tile_type: str, size: tuple = (32, 32)) -> Optional[pygame.Surface]:
        """Carga sprite de tile"""
        return self.load_sprite("tiles", f"tile_{tile_type}", size)
    
    def get_ui_sprite(self, name: str, size: tuple = (32, 32)) -> Optional[pygame.Surface]:
        """Carga sprite de UI"""
        return self.load_sprite("ui", name, size)
    
    def get_stat_icon(self, stat_type: str, size: tuple = (24, 24)) -> Optional[pygame.Surface]:
        """Carga sprite de icono de stat (ataque, defensa, oro)"""
        icon_map = {
            "attack": "ataque",
            "defense": "defensa",
            "gold": "oro",
        }
        sprite_name = icon_map.get(stat_type)
        if sprite_name:
            return self.load_sprite("ui", sprite_name, size)
        return None
    
    def clear_cache(self):
        """Limpia la cache de sprites"""
        self.cache.clear()


# Instancia global
sprite_manager = SpriteManager()
