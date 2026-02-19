"""
Sistema de Guardado y Carga
"""

import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime

from src.core.config import SAVES_DIR
from src.core.constants import SAVE_FILE_PREFIX, SAVE_FILE_EXTENSION


class GameEncoder(json.JSONEncoder):
    """Encoder personalizado para objetos del juego"""
    def default(self, o):
        if hasattr(o, 'to_dict'):
            return o.to_dict()
        if hasattr(o, '__dict__'):
            return {"_type": type(o).__name__, **o.__dict__}
        return str(o)


class SaveSystem:
    """
    Sistema de guardado y carga de juegos
    """
    
    def __init__(self):
        self.save_slots: Dict[int, Dict[str, Any]] = {}
        self._load_all_slots()
    
    def _get_save_path(self, slot: int) -> str:
        """Obtiene la ruta del archivo de guardado"""
        filename = f"{SAVE_FILE_PREFIX}{slot}{SAVE_FILE_EXTENSION}"
        return os.path.join(SAVES_DIR, filename)
    
    def _load_all_slots(self) -> None:
        """Carga todos los slots de guardado"""
        for slot in range(1, 4):
            save_data = self._load_slot(slot)
            if save_data:
                self.save_slots[slot] = save_data
    
    def _load_slot(self, slot: int) -> Optional[Dict[str, Any]]:
        """Carga un slot específico"""
        path = self._get_save_path(slot)
        
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return None
        
        return None
    
    def save_game(self, slot: int, player: Any, dungeon: Any, 
                  game_stats: Dict[str, Any], 
                  settings: Dict[str, Any]) -> bool:
        """
        Guarda el juego en un slot
        
        Args:
            slot: Número de slot (1-3)
            player: Instancia del jugador
            dungeon: Instancia de la mazmorra
            game_stats: Estadísticas del juego
            settings: Configuraciones
        
        Returns:
            True si el guardado fue exitoso
        """
        if not 1 <= slot <= 3:
            return False
        
        save_data = {
            "player": player.to_dict(),
            "dungeon": dungeon.to_dict(),
            "game_stats": game_stats,
            "settings": settings,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
        }
        
        try:
            path = self._get_save_path(slot)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False, cls=GameEncoder)
            
            self.save_slots[slot] = save_data
            return True
        
        except IOError:
            return False
        except TypeError as e:
            print(f"Error de serialización: {e}")
            return False
    
    def load_game(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Carga un juego desde un slot
        
        Args:
            slot: Número de slot (1-3)
        
        Returns:
            Diccionario con los datos del juego o None si no existe
        """
        if not 1 <= slot <= 3:
            return None
        
        return self.save_slots.get(slot) or self._load_slot(slot)
    
    def delete_save(self, slot: int) -> bool:
        """Elimina un guardado"""
        if not 1 <= slot <= 3:
            return False
        
        path = self._get_save_path(slot)
        
        if os.path.exists(path):
            try:
                os.remove(path)
                if slot in self.save_slots:
                    del self.save_slots[slot]
                return True
            except IOError:
                return False
        
        return True
    
    def get_save_info(self, slot: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene información básica de un slot sin cargar todo el juego
        """
        save_data = self.load_game(slot)
        
        if not save_data:
            return None
        
        player_data = save_data.get("player", {})
        dungeon_data = save_data.get("dungeon", {})
        
        return {
            "slot": slot,
            "player_name": player_data.get("name", "Unknown"),
            "player_class": player_data.get("class_id", "Unknown"),
            "level": player_data.get("level", 1),
            "floor": dungeon_data.get("current_floor", 1),
            "max_floors": dungeon_data.get("max_floors", 8),
            "timestamp": save_data.get("timestamp", ""),
            "playtime": save_data.get("game_stats", {}).get("playtime_seconds", 0),
        }
    
    def get_all_saves_info(self) -> List[Dict[str, Any]]:
        """Obtiene información de todos los slots"""
        infos = []
        for slot in range(1, 4):
            info = self.get_save_info(slot)
            if info:
                infos.append(info)
        return infos
    
    def has_save(self, slot: int) -> bool:
        """Verifica si existe un guardado en el slot"""
        return slot in self.save_slots or os.path.exists(self._get_save_path(slot))
    
    @staticmethod
    def format_playtime(seconds: int) -> str:
        """Formatea el tiempo de juego"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    @staticmethod
    def format_timestamp(timestamp: str) -> str:
        """Formatea el timestamp"""
        try:
            dt = datetime.fromisoformat(timestamp)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return timestamp
