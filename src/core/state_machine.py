"""
Máquina de estados para manejar el flujo del juego
"""

from enum import Enum, auto
from typing import Dict, Any, Callable, Optional


class GameState(Enum):
    """Estados posibles del juego"""
    MAIN_MENU = auto()
    SELECT_CLASS = auto()
    NEW_GAME = auto()
    DUNGEON = auto()
    COMBAT = auto()
    MERCHANT = auto()
    EVENT = auto()
    INVENTORY = auto()
    EQUIPMENT = auto()
    PAUSE = auto()
    VICTORY = auto()
    DEFEAT = auto()
    SETTINGS = auto()
    LOAD_GAME = auto()
    SAVE_GAME = auto()
    BOSS_INTRO = auto()


class StateMachine:
    """
    Implementa el patrón State Machine.
    Maneja las transiciones entre estados del juego.
    """
    
    def __init__(self):
        self.current_state = GameState.MAIN_MENU
        self.previous_state: Optional[GameState] = None
        self.state_data: Dict[str, Any] = {}
        self.state_handlers: Dict[GameState, Callable] = {}
        self.transition_handlers: Dict[tuple, Callable] = {}
    
    def register_state(self, state: GameState, handler: Callable) -> None:
        """Registra una función handler para un estado"""
        self.state_handlers[state] = handler
    
    def register_transition(self, from_state: GameState, to_state: GameState, 
                           handler: Callable) -> None:
        """Registra una función que se ejecuta al cambiar de estado"""
        key = (from_state, to_state)
        self.transition_handlers[key] = handler
    
    def change_state(self, new_state: GameState, data: Optional[Dict[str, Any]] = None) -> None:
        """
        Cambia de estado, ejecutando las transiciones apropiadas
        """
        from_state = self.current_state
        
        # Ejecutar transición si existe
        transition_key = (from_state, new_state)
        if transition_key in self.transition_handlers:
            self.transition_handlers[transition_key]()
        
        # Guardar estado anterior
        self.previous_state = from_state
        
        # Actualizar estado actual
        self.current_state = new_state
        
        # Actualizar datos si se proporcionan
        if data:
            self.state_data.update(data)
        
        # Limpiar datos específicos del estado si es necesario
        self._cleanup_state_data(new_state)
    
    def _cleanup_state_data(self, state: GameState) -> None:
        """Limpia datos que no son necesarios para ciertos estados"""
        cleanup_keys = {
            GameState.MAIN_MENU: ["enemy", "room", "player_action"],
            GameState.COMBAT: [],
            GameState.DUNGEON: [],
        }
        
        if state in cleanup_keys:
            for key in cleanup_keys[state]:
                if key in self.state_data:
                    del self.state_data[key]
    
    def get_state(self) -> GameState:
        """Retorna el estado actual"""
        return self.current_state
    
    def get_previous_state(self) -> Optional[GameState]:
        """Retorna el estado anterior"""
        return self.previous_state
    
    def is_state(self, state: GameState) -> bool:
        """Verifica si está en un estado específico"""
        return self.current_state == state
    
    def get_data(self, key: str, default: Any = None) -> Any:
        """Obtiene un dato del estado"""
        return self.state_data.get(key, default)
    
    def set_data(self, key: str, value: Any) -> None:
        """Establece un dato del estado"""
        self.state_data[key] = value
    
    def update_data(self, data: Dict[str, Any]) -> None:
        """Actualiza múltiples datos del estado"""
        self.state_data.update(data)
    
    def can_transition(self, from_state: GameState, to_state: GameState) -> bool:
        """
        Verifica si una transición es válida
        """
        valid_transitions = {
            GameState.MAIN_MENU: [GameState.SELECT_CLASS, GameState.LOAD_GAME, GameState.SETTINGS],
            GameState.SELECT_CLASS: [GameState.NEW_GAME, GameState.MAIN_MENU],
            GameState.NEW_GAME: [GameState.DUNGEON],
            GameState.DUNGEON: [GameState.COMBAT, GameState.MERCHANT, GameState.EVENT, 
                               GameState.DUNGEON, GameState.PAUSE, GameState.VICTORY,
                               GameState.INVENTORY, GameState.EQUIPMENT, GameState.BOSS_INTRO],
            GameState.BOSS_INTRO: [GameState.COMBAT, GameState.DUNGEON],
            GameState.COMBAT: [GameState.DUNGEON, GameState.VICTORY, GameState.DEFEAT],
            GameState.MERCHANT: [GameState.DUNGEON, GameState.PAUSE],
            GameState.EVENT: [GameState.DUNGEON, GameState.PAUSE],
            GameState.INVENTORY: [GameState.DUNGEON, GameState.EQUIPMENT, GameState.PAUSE],
            GameState.EQUIPMENT: [GameState.DUNGEON, GameState.INVENTORY, GameState.PAUSE],
            GameState.PAUSE: [GameState.DUNGEON, GameState.COMBAT, GameState.MERCHANT,
                            GameState.EVENT, GameState.INVENTORY, GameState.EQUIPMENT,
                            GameState.MAIN_MENU, GameState.SAVE_GAME],
            GameState.VICTORY: [GameState.MAIN_MENU],
            GameState.DEFEAT: [GameState.MAIN_MENU, GameState.LOAD_GAME],
            GameState.SETTINGS: [GameState.MAIN_MENU],
            GameState.LOAD_GAME: [GameState.DUNGEON, GameState.MAIN_MENU],
            GameState.SAVE_GAME: [GameState.PAUSE, GameState.DUNGEON],
        }
        
        return to_state in valid_transitions.get(from_state, [])
    
    def get_valid_transitions(self) -> list:
        """Retorna lista de transiciones válidas desde el estado actual"""
        valid_transitions = {
            GameState.MAIN_MENU: [GameState.SELECT_CLASS, GameState.LOAD_GAME, GameState.SETTINGS],
            GameState.SELECT_CLASS: [GameState.NEW_GAME, GameState.MAIN_MENU],
            GameState.NEW_GAME: [GameState.DUNGEON],
            GameState.DUNGEON: [GameState.COMBAT, GameState.MERCHANT, GameState.EVENT,
                               GameState.PAUSE, GameState.VICTORY, GameState.INVENTORY, 
                               GameState.EQUIPMENT],
            GameState.COMBAT: [GameState.DUNGEON, GameState.VICTORY, GameState.DEFEAT],
            GameState.MERCHANT: [GameState.DUNGEON, GameState.PAUSE],
            GameState.EVENT: [GameState.DUNGEON, GameState.PAUSE],
            GameState.PAUSE: [GameState.DUNGEON, GameState.MAIN_MENU, GameState.SAVE_GAME],
            GameState.VICTORY: [GameState.MAIN_MENU],
            GameState.DEFEAT: [GameState.MAIN_MENU, GameState.LOAD_GAME],
        }
        
        return valid_transitions.get(self.current_state, [])
