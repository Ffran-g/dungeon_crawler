"""
Dungeon Crawler - Juego Principal
Punto de entrada del juego
"""

import pygame
import sys
from typing import Optional, Any, Dict, List

from src.core.constants import *
from src.core.state_machine import StateMachine, GameState
from src.core.config import *
from src.entities.player import Player, CLASSES
from src.entities.enemy import EnemyFactory, ENEMY_TYPE_BASIC, ENEMY_TYPE_ELITE, ENEMY_TYPE_BOSS
from src.entities.item import ItemGenerator, CONSUMABLES, WEAPONS, Item
from src.systems.combat import CombatSystem
from src.systems.dungeon import Dungeon
from src.systems.save_system import SaveSystem
from src.ui.renderer import TextRenderer, UIRenderer, MenuRenderer
from src.ui.sprite_manager import sprite_manager


class Game:
    """
    Clase principal del juego
    Controla el flujo y coordina todos los sistemas
    """
    
    def __init__(self):
        # Inicializar Pygame
        pygame.init()
        
        # Configurar pantalla
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Crawler - Roguelike RPG")
        
        # Fuentes
        self.font = pygame.font.SysFont(DEFAULT_FONT, DEFAULT_FONT_SIZE)
        
        # Renderizadores
        self.text_renderer = TextRenderer(self.screen, self.font)
        self.ui_renderer = UIRenderer(self.screen, self.text_renderer)
        self.menu_renderer = MenuRenderer(self.screen, self.text_renderer)
        
        # Máquina de estados
        self.state_machine = StateMachine()
        
        # Sistemas del juego
        self.save_system = SaveSystem()
        
        # Datos del juego
        self.player: Optional[Player] = None
        self.dungeon: Optional[Dungeon] = None
        self.message: Optional[str] = None  # Mensaje temporal para el jugador
        self.combat: Optional[CombatSystem] = None
        
        # UI state
        self.menu_selected = 0
        self.input_buffer = ""
        self.player_name = ""
        self.merchant_items = []  # Items a la venta
        self.merchant_mode = "buy"  # "buy" o "sell"
        self.inventory_view = "inventory"  # "inventory" o "equipment"
        
        # Enemy turn delay
        self.enemy_turn_pending = False
        self.enemy_turn_start_time = 0
        self.ENEMY_TURN_DELAY = 3000  # 3 segundos antes del turno del enemigo
        
        # Boss intro
        self.boss_intro_phase = 0  # 0 = no activo, 1 = primera imagen, 2 = segunda, 3 = combate
        self.boss_intro_enemy = None  # Enemy que será fought
        
        # Boss intro textos temáticos
        self.boss_intro_texts = {
            "Dragón Ancianos": [
                "Las leyendas hablan de un dragón milenario que duerme en las profundidades...",
                "Su aliento de fuego ha incinerado a countless guerreros osados.",
                "¡El Dragón Ancianos despierta! ¡Prepárate para la batalla!"
            ],
            "Lich Señor": [
                "En las sombras más profundas mora un maestro de la magia oscura...",
                "Su poder sobre la vida y la muerte es absolute. Los mortifagos le sirven.",
                "¡El Lich Señor te desafía! ¡Lucha o sé corrompido por la oscuridad!"
            ],
            "Demonio Infernal": [
                "Del abysso más profundo emerge un ser de destrucción pura...",
                "Su fury es legendaria. Los que lo enfrentan no encuentran redemption.",
                "¡El Demonio Infernal rugió! ¡Tu alma será su próximo trophy!"
            ]
        }
        
        # Game stats
        self.game_stats = {
            "total_kills": 0,
            "total_damage_dealt": 0,
            "total_damage_taken": 0,
            "floors_cleared": 0,
            "playtime_seconds": 0,
        }
        
        # Clock
        self.clock = pygame.time.Clock()
        self.running = True
    
    def run(self):
        """Loop principal del juego"""
        while self.running:
            self._handle_events()
            self._update()
            self._render()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self):
        """Maneja los eventos de entrada"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event.key)
    
    def _handle_keydown(self, key: int):
        """Maneja teclas según el estado actual"""
        state = self.state_machine.get_state()
        
        if state == GameState.MAIN_MENU:
            self._handle_main_menu_input(key)
        
        elif state == GameState.SELECT_CLASS:
            self._handle_class_selection_input(key)
        
        elif state == GameState.NEW_GAME:
            self._handle_new_game_input(key)
        
        elif state == GameState.DUNGEON:
            self._handle_dungeon_input(key)
        
        elif state == GameState.COMBAT:
            self._handle_combat_input(key)
        
        elif state == GameState.PAUSE:
            self._handle_pause_input(key)
        
        elif state == GameState.INVENTORY:
            self._handle_inventory_input(key)
        
        elif state == GameState.MERCHANT:
            self._handle_merchant_input(key)
        
        elif state == GameState.LOAD_GAME:
            self._handle_load_game_input(key)
        
        elif state == GameState.VICTORY:
            if key == pygame.K_RETURN:
                self.state_machine.change_state(GameState.MAIN_MENU)
        
        elif state == GameState.DEFEAT:
            if key == pygame.K_RETURN:
                self.state_machine.change_state(GameState.MAIN_MENU)
        
        elif state == GameState.BOSS_INTRO:
            self._handle_boss_intro_input(key)
    
    def _handle_boss_intro_input(self, key: int):
        """Maneja entrada en la intro del boss"""
        if key == pygame.K_RETURN:
            if self.boss_intro_phase < 3:
                self.boss_intro_phase += 1
            else:
                # Iniciar combate
                room = self.dungeon.get_current_room() if self.dungeon else None
                if room:
                    enemies = room.get_enemies_list()
                    self._start_combat(enemies, can_flee=False)
    
    def _handle_main_menu_input(self, key: int):
        """Maneja entrada en menú principal"""
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % 3
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % 3
        elif key == pygame.K_RETURN:
            if self.menu_selected == 0:
                self.state_machine.change_state(GameState.SELECT_CLASS)
            elif self.menu_selected == 1:
                self.state_machine.change_state(GameState.LOAD_GAME)
            elif self.menu_selected == 2:
                self.running = False
    
    def _handle_class_selection_input(self, key: int):
        """Maneja entrada en selección de clase"""
        classes = ["warrior", "mage", "rogue", "warlock"]
        
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % 4
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % 4
        elif key == pygame.K_1 or (key == pygame.K_RETURN and self.menu_selected == 0):
            self._start_new_game("warrior")
        elif key == pygame.K_2 or (key == pygame.K_RETURN and self.menu_selected == 1):
            self._start_new_game("mage")
        elif key == pygame.K_3 or (key == pygame.K_RETURN and self.menu_selected == 2):
            self._start_new_game("rogue")
        elif key == pygame.K_4 or (key == pygame.K_RETURN and self.menu_selected == 3):
            self._start_new_game("warlock")
        elif key == pygame.K_ESCAPE:
            self.state_machine.change_state(GameState.MAIN_MENU)
    
    def _handle_new_game_input(self, key: int):
        """Maneja entrada para nombre del jugador"""
        if key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif key == pygame.K_RETURN:
            if self.player_name.strip():
                if self.player:
                    self.player.name = self.player_name
                self._start_dungeon()
        elif key == pygame.K_ESCAPE:
            self.state_machine.change_state(GameState.SELECT_CLASS)
        else:
            # Agregar carácter si es válido
            char = pygame.key.name(key)
            if len(char) == 1 and char.isalnum() and len(self.player_name) < PLAYER_NAME_MAX_LENGTH:
                self.player_name += char
    
    def _handle_dungeon_input(self, key: int):
        """Maneja entrada en la mazmorra"""
        if not self.dungeon:
            return
        
        # Cerrar mensaje si existe
        if self.message:
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self.message = None
            return
        
        if key == pygame.K_ESCAPE:
            self.state_machine.change_state(GameState.PAUSE)
        elif key == pygame.K_i:
            self.state_machine.change_state(GameState.INVENTORY)
        elif key == pygame.K_e:
            self.state_machine.change_state(GameState.EQUIPMENT)
        elif key == pygame.K_UP:
            room_type = self.dungeon.move_player(0, -1)
            if room_type == ROOM_TYPE_TRAP:
                room = self.dungeon.get_current_room()
                if room:
                    self._trigger_trap(room.event_data)
        elif key == pygame.K_DOWN:
            room_type = self.dungeon.move_player(0, 1)
            if room_type == ROOM_TYPE_TRAP:
                room = self.dungeon.get_current_room()
                if room:
                    self._trigger_trap(room.event_data)
        elif key == pygame.K_LEFT:
            room_type = self.dungeon.move_player(-1, 0)
            if room_type == ROOM_TYPE_TRAP:
                room = self.dungeon.get_current_room()
                if room:
                    self._trigger_trap(room.event_data)
        elif key == pygame.K_RIGHT:
            room_type = self.dungeon.move_player(1, 0)
            if room_type == ROOM_TYPE_TRAP:
                room = self.dungeon.get_current_room()
                if room:
                    self._trigger_trap(room.event_data)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Entrar a la sala actual
            self._enter_current_room()
    
    def _handle_combat_input(self, key: int):
        """Maneja entrada en combate"""
        if not self.combat:
            return
        
        if self.combat.combat_over:
            if key == pygame.K_RETURN:
                if self.combat.victory:
                    self._handle_combat_victory()
                else:
                    self.state_machine.change_state(GameState.DEFEAT)
            return
        
        if not self.combat.player_turn:
            return
        
        # Activar delay del turno del enemigo ANTES de cualquier acción
        self.combat.enemy_turn_delayed = True
        self.enemy_turn_pending = True
        self.enemy_turn_start_time = pygame.time.get_ticks()
        
        # Cambiar objetivo (si hay múltiples enemigos)
        alive_enemies = self.combat.get_alive_enemies()
        if len(alive_enemies) > 1:
            if key == pygame.K_q:
                self.combat.target_index = (self.combat.target_index - 1) % len(alive_enemies)
                return
            elif key == pygame.K_e:
                self.combat.target_index = (self.combat.target_index + 1) % len(alive_enemies)
                return
        
        # Navegar por el menu
        if key == pygame.K_LEFT:
            self.menu_selected = (self.menu_selected - 1) % 4
        elif key == pygame.K_RIGHT:
            self.menu_selected = (self.menu_selected + 1) % 4
        # Ejecutar accion segun opcion del menu
        elif key == pygame.K_RETURN:
            if self.menu_selected == 0:
                # ATACAR - entrar submenu habilidades
                pass  # Esperar a que seleccione habilidad
            elif self.menu_selected == 1:
                # DEFENDER
                self.combat.player_defend()
            elif self.menu_selected == 2:
                # OBJETO - mostrar inventario de objetos
                pass  # Por implementar
            elif self.menu_selected == 3:
                # HUIR
                result = self.combat.player_run()
                if result.messages:
                    self.combat.log.add(result.messages[0])
                if self.combat.combat_over:
                    self.state_machine.change_state(GameState.DUNGEON)
        
        # Si esta seleccionado OBJETO (opcion 2), las teclas 1-4 usan objetos
        if self.menu_selected == 2:
            if key == pygame.K_1:
                self._use_item_combat(0)
                self._end_player_turn()
            elif key == pygame.K_2:
                self._use_item_combat(1)
                self._end_player_turn()
            elif key == pygame.K_3:
                self._use_item_combat(2)
                self._end_player_turn()
            elif key == pygame.K_4:
                self._use_item_combat(3)
                self._end_player_turn()
        elif key == pygame.K_1:
            self._combat_action(0)
            self._end_player_turn()
        elif key == pygame.K_2:
            self._combat_action(1)
            self._end_player_turn()
        elif key == pygame.K_3:
            self._combat_action(2)
            self._end_player_turn()
        elif key == pygame.K_4:
            self._combat_action(3)
            self._end_player_turn()
        elif key == pygame.K_d:
            self.combat.player_defend()
            self._end_player_turn()
        elif key == pygame.K_r:
            result = self.combat.player_run()
            if result.messages:
                self.combat.log.add(result.messages[0])
            if self.combat.combat_over:
                self.state_machine.change_state(GameState.DUNGEON)
            else:
                self._end_player_turn()
    
    def _handle_pause_input(self, key: int):
        """Maneja entrada en menú de pausa"""
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % 4
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % 4
        elif key == pygame.K_ESCAPE:
            self._resume_game()
        elif key == pygame.K_RETURN:
            if self.menu_selected == 0:  # Continuar
                self._resume_game()
            elif self.menu_selected == 1:  # Inventario
                self.state_machine.change_state(GameState.INVENTORY)
            elif self.menu_selected == 2:  # Guardar
                self._save_game()  # Sin argumento - encuentra slot automáticamente
            elif self.menu_selected == 3:  # Menú Principal
                self.state_machine.change_state(GameState.MAIN_MENU)
    
    def _handle_inventory_input(self, key: int):
        """Maneja entrada en inventario"""
        if self.message:
            if key == pygame.K_RETURN:
                self.message = None
            return
        
        if key == pygame.K_ESCAPE:
            self.state_machine.change_state(GameState.DUNGEON)
        elif key == pygame.K_e:
            # Cambiar entre inventario y equipamiento
            if self.inventory_view == "inventory":
                self.inventory_view = "equipment"
            else:
                self.inventory_view = "inventory"
            self.menu_selected = 0
        elif key == pygame.K_UP:
            max_slots = INVENTORY_MAX_SLOTS if self.inventory_view == "inventory" else 4
            self.menu_selected = (self.menu_selected - 1) % max_slots
        elif key == pygame.K_DOWN:
            max_slots = INVENTORY_MAX_SLOTS if self.inventory_view == "inventory" else 4
            self.menu_selected = (self.menu_selected + 1) % max_slots
        elif key == pygame.K_RETURN and self.inventory_view == "inventory":
            self._equip_item(self.menu_selected)
    
    def _handle_merchant_input(self, key: int):
        """Maneja entrada en el mercader"""
        if self.message:
            if key == pygame.K_RETURN:
                self.message = None
            return
        
        if key == pygame.K_ESCAPE:
            self.state_machine.change_state(GameState.DUNGEON)
        elif key == pygame.K_b:
            self.merchant_mode = "buy"
            self.menu_selected = 0
        elif key == pygame.K_v:
            self.merchant_mode = "sell"
            self.menu_selected = 0
        elif key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % 8
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % 8
        elif key == pygame.K_RETURN:
            if self.merchant_mode == "buy":
                self._buy_item(self.menu_selected)
            else:
                self._sell_item(self.menu_selected)
        elif key == pygame.K_u and self.player and self.menu_selected < len(self.player.inventory):
            # Usar item
            self._use_item(self.menu_selected)
    
    def _handle_load_game_input(self, key: int):
        """Maneja entrada en carga de juego"""
        saves_info = self.save_system.get_all_saves_info()
        
        if key == pygame.K_UP:
            self.menu_selected = (self.menu_selected - 1) % 3
        elif key == pygame.K_DOWN:
            self.menu_selected = (self.menu_selected + 1) % 3
        elif key == pygame.K_ESCAPE:
            self.state_machine.change_state(GameState.MAIN_MENU)
        elif key == pygame.K_RETURN:
            if self.menu_selected < 3:
                # Intentar cargar el slot seleccionado
                save_data = self.save_system.load_game(self.menu_selected + 1)
                if save_data:
                    self._load_game(save_data)
        elif key == pygame.K_DELETE or key == pygame.K_x:
            # Borrar la partida seleccionada
            if self.menu_selected < 3:
                slot_to_delete = self.menu_selected + 1
                self.save_system.delete_save(slot_to_delete)
    
    def _update(self):
        """Actualiza el estado del juego"""
        # Manejar delay del turno del enemigo
        if (self.enemy_turn_pending and 
            self.combat and 
            self.state_machine.get_state() == GameState.COMBAT):
            
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.enemy_turn_start_time
            
            if elapsed >= self.ENEMY_TURN_DELAY:
                self._execute_enemy_turn_immediate()
                self.enemy_turn_pending = False
    
    def _render(self):
        """Renderiza el juego según el estado"""
        state = self.state_machine.get_state()
        
        if state == GameState.MAIN_MENU:
            self.menu_renderer.draw_main_menu(self.menu_selected)
        
        elif state == GameState.SELECT_CLASS:
            selected_class = ["warrior", "mage", "rogue", "warlock"][self.menu_selected]
            class_info = None
            if selected_class in CLASSES:
                cls = CLASSES[selected_class]
                skills_list = []
                for skill in cls.skills:
                    skills_list.append({
                        "name": skill.name,
                        "description": skill.description
                    })
                class_info = {
                    "name": cls.name,
                    "description": cls.description,
                    "stats": cls.base_stats,
                    "skills": skills_list,
                }
            self.menu_renderer.draw_class_selection(self.menu_selected, class_info)
        
        elif state == GameState.NEW_GAME:
            self.screen.fill((10, 10, 15))
            
            center_x = SCREEN_WIDTH // 2
            center_y = SCREEN_HEIGHT // 2
            
            # Marco decorativo
            panel_w = 400
            panel_h = 180
            panel_x = center_x - panel_w // 2
            panel_y = center_y - panel_h // 2 - 30
            
            pygame.draw.rect(self.screen, (20, 20, 30), (panel_x, panel_y, panel_w, panel_h))
            pygame.draw.rect(self.screen, COLOR_YELLOW, (panel_x, panel_y, panel_w, panel_h), 2)
            
            self.text_renderer.draw_title("NOMBRE DEL PERSONAJE", center_x, panel_y + 25, COLOR_YELLOW)
            
            # Nombre con cursor parpadeante
            name_display = self.player_name + "_" if len(self.player_name) < PLAYER_NAME_MAX_LENGTH else self.player_name
            self.text_renderer.draw_text(name_display, center_x, panel_y + 75, COLOR_WHITE, center=True)
            
            # Instrucciones
            self.text_renderer.draw_text("[ENTER] Comenzar  [ESC] Volver", center_x, panel_y + panel_h - 25, COLOR_GRAY, center=True)
        
        elif state == GameState.DUNGEON:
            self._render_dungeon()
        
        elif state == GameState.COMBAT:
            self._render_combat()
        
        elif state == GameState.PAUSE:
            self._render_dungeon()
            self.menu_renderer.draw_pause_menu(self.menu_selected)
        
        elif state == GameState.INVENTORY:
            self._render_dungeon()
            self.menu_renderer.draw_inventory(self.player, self.menu_selected, view_mode=self.inventory_view)
        
        elif state == GameState.MERCHANT:
            self.screen.fill(COLOR_BLACK)
            self._render_merchant()
        
        elif state == GameState.LOAD_GAME:
            saves = self.save_system.get_all_saves_info()
            self.menu_renderer.draw_save_slots(saves, self.menu_selected)
            
            # Mostrar mensaje si existe
            if self.message:
                self.text_renderer.draw_box(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 30, 300, 50, COLOR_YELLOW, (30, 20, 20))
                self.text_renderer.draw_text(self.message, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 5, COLOR_YELLOW, center=True)
        
        elif state == GameState.VICTORY:
            self.menu_renderer.draw_victory()
        
        elif state == GameState.DEFEAT:
            self.menu_renderer.draw_defeat()
        
        elif state == GameState.BOSS_INTRO:
            self._render_boss_intro()
        
        pygame.display.flip()
    
    def _render_dungeon(self):
        """Renderiza la vista de la mazmorra"""
        # Fondo negro base
        self.screen.fill(COLOR_BLACK)
        
        # Imagen de fondo según el piso
        if self.dungeon and self.dungeon.current_floor <= 4:
            bg = sprite_manager.load_sprite("background", "dungeon_1-4", (SCREEN_WIDTH, SCREEN_HEIGHT))
        else:
            bg = sprite_manager.load_sprite("background", "dungeon_5-8", (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if bg:
            self.screen.blit(bg, (0, 0))
        
        if not self.dungeon:
            return
        
        room = self.dungeon.get_current_room()
        
        room_type_names = {
            ROOM_TYPE_COMBAT_BASIC: "Combate",
            ROOM_TYPE_COMBAT_ELITE: "Combate Élite",
            ROOM_TYPE_COMBAT_BOSS: "JEFE",
            ROOM_TYPE_TREASURE: "Tesoro",
            ROOM_TYPE_TRAP: "Trampa",
            ROOM_TYPE_MERCHANT: "Mercader",
            ROOM_TYPE_SANCTUARY: "Santuario",
            "start": "Inicio",
        }
        
        # Panel izquierdo - Stats del jugador
        self.ui_renderer.draw_player_stats(self.player, 8, 65)
        
        # Panel derecho - Info de la mazmorra
        self.ui_renderer.draw_dungeon_info(self.dungeon, SCREEN_WIDTH - 268, 65)
        
        # Grid centrado de la mazmorra
        self.ui_renderer.draw_dungeon_view(self.dungeon, self.player)
        
        # Info de la sala actual arriba del grid
        if room:
            room_name = room_type_names.get(room.room_type, room.room_type)
            self.text_renderer.draw_text(f"Sala: {room_name}", SCREEN_WIDTH // 2, 45, COLOR_TEXT, center=True)
        
        # Mensaje temporal
        if self.message:
            self.text_renderer.draw_box(250, 250, 400, 80, COLOR_RED, (20, 20, 20))
            self.text_renderer.draw_text(self.message, 450, 290, COLOR_RED, center=True)
            self.text_renderer.draw_text("[ENTER] Continuar", 450, 310, COLOR_GRAY, center=True)
    
    def _render_merchant(self):
        """Renderiza el menú del mercader - Diseño centrado"""
        from src.core.constants import RARITY_COLORS
        
        self.screen.fill((10, 10, 15))
        
        center_x = SCREEN_WIDTH // 2
        
        # Marco decorativo
        panel_w = 700
        panel_h = 520
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = 50
        
        pygame.draw.rect(self.screen, (20, 20, 30), (panel_x - 10, panel_y - 10, panel_w + 20, panel_h + 20))
        pygame.draw.rect(self.screen, COLOR_YELLOW, (panel_x - 10, panel_y - 10, panel_w + 20, panel_h + 20), 2)
        
        # Título
        self.text_renderer.draw_title("MERCADER", center_x, panel_y + 10, COLOR_YELLOW)
        
        # Oro del jugador
        gold_text = f"Oro: {self.player.gold if self.player else 0}"
        self.text_renderer.draw_text(gold_text, panel_x + 20, panel_y + 50, COLOR_YELLOW)
        
        # Opciones de compra/venta
        mode_color_buy = COLOR_GREEN if self.merchant_mode == "buy" else COLOR_GRAY
        mode_color_sell = COLOR_GREEN if self.merchant_mode == "sell" else COLOR_GRAY
        self.text_renderer.draw_text("[B] Comprar  [V] Vender", center_x, panel_y + 50, COLOR_GRAY, center=True)
        
        # Items
        if self.merchant_mode == "buy":
            items = self.merchant_items
            title = "Items en venta:"
        else:
            items = self.player.inventory if self.player and hasattr(self.player, 'inventory') else []
            title = "Tu inventario (venta):"
        
        self.text_renderer.draw_text(title, panel_x + 20, panel_y + 85, COLOR_WHITE)
        
        # Dibujar items
        item_w = panel_w - 40
        item_h = 45
        for i, item in enumerate(items[:8]):
            item_y = panel_y + 110 + i * (item_h + 5)
            selected = (i == self.menu_selected)
            
            box_color = COLOR_HIGHLIGHT if selected else COLOR_BORDER
            item_color = RARITY_COLORS.get(item.rarity, COLOR_WHITE)
            
            pygame.draw.rect(self.screen, box_color, (panel_x + 20, item_y, item_w, item_h), 2)
            
            self.text_renderer.draw_text(f"[{i+1}] {item.name}", panel_x + 35, item_y + 12, item_color)
            stats_str = ", ".join([f"{k}: {v}" for k, v in item.stats.items()])
            self.text_renderer.draw_text(f"{stats_str}", panel_x + 280, item_y + 12, COLOR_GRAY)
            
            if self.merchant_mode == "buy":
                player_gold = self.player.gold if self.player else 0
                price_color = COLOR_YELLOW if player_gold >= item.value else COLOR_RED
                self.text_renderer.draw_text(f"{item.value} oro", panel_x + item_w - 10, item_y + 12, price_color)
            else:
                sell_price = item.value // 2
                self.text_renderer.draw_text(f"+{sell_price} oro", panel_x + item_w - 10, item_y + 12, COLOR_YELLOW)
        
        # Instrucciones
        self.text_renderer.draw_text("[ENTER] Comprar/Vender  [U] Usar item  [ESC] Salir", center_x, panel_y + panel_h + 5, COLOR_GRAY, center=True)
        
        # Mensaje
        if self.message:
            self.text_renderer.draw_box(center_x - 150, panel_y + panel_h - 40, 300, 35, COLOR_RED, (30, 20, 20))
            self.text_renderer.draw_text(self.message, center_x, panel_y + panel_h - 25, COLOR_RED, center=True)
    
    def _render_treasure_event(self, event_data):
        """Renderiza evento de tesoro"""
        x, y = 400, 150
        self.text_renderer.draw_box(x, y, 350, 200)
        
        self.text_renderer.draw_text("¡TESORO ENCONTRADO!", x + 20, y + 20, COLOR_YELLOW)
        
        if "item" in event_data:
            item = event_data["item"]
            self.text_renderer.draw_text(f"Item: {item.name}", x + 20, y + 50)
        
        if "gold" in event_data:
            self.text_renderer.draw_text(f"Oro: {event_data['gold']}", x + 20, y + 80, COLOR_YELLOW)
        
        self.text_renderer.draw_text("[ENTER] Recoger", x + 20, y + 160, COLOR_GREEN)
    
    def _render_trap_event(self, event_data):
        """Renderiza evento de trampa"""
        x, y = 400, 150
        self.text_renderer.draw_box(x, y, 350, 150)
        
        name = event_data.get("name", "Trampa")
        desc = event_data.get("description", "")
        damage = event_data.get("damage", 0)
        
        self.text_renderer.draw_text(f"¡{name}!", x + 20, y + 20, COLOR_RED)
        self.text_renderer.draw_text(desc, x + 20, y + 50, COLOR_GRAY)
        self.text_renderer.draw_text(f"Daño: {damage}", x + 20, y + 80, COLOR_RED)

    def _render_boss_intro(self):
        """Renderiza la intro del boss"""
        if not self.boss_intro_enemy:
            return
        
        enemy_name = getattr(self.boss_intro_enemy, 'original_name', None) or self.boss_intro_enemy.name
        
        # Mapear nombre a carpeta
        folder_map = {
            "Dragón Ancianos": "dragon",
            "Lich Señor": "lich",
            "Demonio Infernal": "infernal_demon",
        }
        folder = folder_map.get(enemy_name, "dragon")
        
        # Cargar imagen según la fase
        img_name = f"{folder}_{self.boss_intro_phase}"
        bg = sprite_manager.load_sprite("background", img_name, (SCREEN_WIDTH, SCREEN_HEIGHT), subfolder=f"boss_fight/{folder}")
        
        # Fondo
        self.screen.fill(COLOR_BLACK)
        
        if bg:
            # Centrar imagen (subirla un poco)
            self.screen.blit(bg, (0, -100))
        
        # Obtener texto según el boss y fase
        texts = self.boss_intro_texts.get(enemy_name, ["", "", ""])
        current_text = texts[self.boss_intro_phase - 1] if self.boss_intro_phase <= len(texts) else ""
        
        # Dibujar cuadro de texto abajo
        text_box_h = 100
        text_box_y = SCREEN_HEIGHT - text_box_h - 20
        
        self.text_renderer.draw_box(50, text_box_y, SCREEN_WIDTH - 100, text_box_h, COLOR_BORDER, (10, 10, 15))
        
        # Texto temático
        self.text_renderer.draw_text(current_text, SCREEN_WIDTH // 2, text_box_y + 30, COLOR_WHITE, center=True)
        
        # Instrucciones
        if self.boss_intro_phase < 3:
            self.text_renderer.draw_text("[ENTER] Continuar", SCREEN_WIDTH // 2, text_box_y + 70, COLOR_GRAY, center=True)
        else:
            self.text_renderer.draw_text("¡COMBATE!", SCREEN_WIDTH // 2, text_box_y + 70, COLOR_YELLOW, center=True)

    def _render_combat(self):
        """Renderiza la vista de combate - Diseño centrado"""
        # Fondo negro base
        self.screen.fill(COLOR_BLACK)
        
        # Imagen de fondo según el tipo de enemigo
        bg_name = "combat_enemy_basic"
        bg_subfolder = None
        
        # Verificar si hay enemigos elites
        if self.combat:
            enemies = self.combat.get_alive_enemies()
            if enemies:
                enemy = enemies[0]
                if enemy.enemy_type == ENEMY_TYPE_BOSS:
                    # Cargar fondo de boss
                    boss_name = getattr(enemy, 'original_name', None) or enemy.name
                    boss_bg_map = {
                        "Dragón Ancianos": "dragon",
                        "Lich Señor": "lich",
                        "Demonio Infernal": "infernal_demon",
                    }
                    folder = boss_bg_map.get(boss_name, "dragon")
                    bg_name = f"{folder}_3"
                    bg_subfolder = f"boss_fight/{folder}"
                elif enemy.enemy_type == ENEMY_TYPE_ELITE:
                    # Mapear nombre de enemigo elite a archivo de fondo
                    elite_bg_map = {
                        "Orco Berserker": "orco_berserker",
                        "Trol": "troll",
                        "Nigromante": "nigromante",
                        "Vampiro": "vampiro",
                    }
                    bg_name = elite_bg_map.get(enemy.name, "combat_enemy_basic")
                    bg_subfolder = "elite_fights"
        
        if bg_subfolder:
            bg = sprite_manager.load_sprite("background", bg_name, (SCREEN_WIDTH, SCREEN_HEIGHT), subfolder=bg_subfolder)
        else:
            bg = sprite_manager.load_sprite("background", bg_name, (SCREEN_WIDTH, SCREEN_HEIGHT))
        
        if bg:
            self.screen.blit(bg, (0, -150))

        if not self.combat:
            return

        center_x = SCREEN_WIDTH // 2
        
        # Título del combate
        turn_text = f"COMBATE - Turno {self.combat.turn_count}"
        if self.combat.player_turn:
            turn_text += " - TU TURNO"
        else:
            turn_text += " - ENEMIGO"

        title_color = COLOR_GREEN if self.combat.player_turn else COLOR_RED
        self.text_renderer.draw_title(turn_text, center_x, 25, title_color)

        # Layout: Jugador a la izquierda, Enemigo(s) a la derecha, Log abajo
        # Jugador
        self.ui_renderer.draw_player_stats(self.player, 15, 70)
        
        # Enemigos a la derecha
        enemies = self.combat.get_alive_enemies()
        if enemies:
            enemy_panel_x = SCREEN_WIDTH - 310
            for i, enemy in enumerate(enemies):
                y_pos = 70 + i * 160
                self.ui_renderer.draw_enemy_info(enemy, enemy_panel_x, y_pos)
                
                # Indicador de objetivo seleccionado
                if i == self.combat.target_index:
                    pygame.draw.rect(self.screen, COLOR_YELLOW, (enemy_panel_x - 5, y_pos - 5, 295, 150), 3)
        
        # Instrucciones para seleccionar objetivo
        if len(enemies) > 1 and self.combat.player_turn:
            self.text_renderer.draw_text("Objetivo: [Q/E] cambiar", 15, 60, COLOR_YELLOW)

        # Log de combate - centrado abajo
        log_x = center_x - 250
        log_y = 330
        messages = self.combat.log.get_recent(6)
        if messages:
            self.ui_renderer.draw_combat_log(messages, log_x, log_y, 500, 140)

        # Menú de combate (solo si es tu turno)
        if self.combat.player_turn and not self.combat.combat_over:
            # Resetear flag de delay al inicio del turno del jugador
            self.enemy_turn_pending = False
            self.menu_renderer.draw_combat_menu(self.combat, self.menu_selected)
        elif self.enemy_turn_pending and not self.combat.combat_over:
            # Mostrar countdown antes del turno del enemigo
            elapsed = pygame.time.get_ticks() - self.enemy_turn_start_time
            remaining = max(0, (self.ENEMY_TURN_DELAY - elapsed) // 100)
            
            self.text_renderer.draw_title(f"Turno del enemigo en... {remaining}", center_x, 280, COLOR_RED)
            
            # Barra de progreso del delay
            bar_w = 300
            bar_h = 15
            bar_x = center_x - bar_w // 2
            bar_y = 310
            progress = min(1.0, elapsed / self.ENEMY_TURN_DELAY)
            
            pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(self.screen, COLOR_RED, (bar_x, bar_y, int(bar_w * progress), bar_h))
            pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
        elif not self.combat.player_turn and not self.combat.combat_over:
            self.text_renderer.draw_title("Turno del enemigo...", center_x, 280, COLOR_RED)
            self.text_renderer.draw_text("Espera...", center_x, 310, COLOR_GRAY, center=True)

        # Fin del combate
        if self.combat.combat_over:
            if self.combat.victory:
                self.text_renderer.draw_title("¡VICTORIA!", center_x, 280, COLOR_GREEN)
            else:
                self.text_renderer.draw_title("¡DERROTA!", center_x, 280, COLOR_RED)
            self.text_renderer.draw_text("[ENTER] Continuar", center_x, 320, COLOR_GRAY, center=True)

        pygame.display.flip()

    # =========================================================================
    # ACCIONES DEL JUEGO
    # =========================================================================
    
    def _start_new_game(self, class_id: str):
        """Inicia un nuevo juego"""
        self.player = Player("Hero", class_id)

        self.player.inventory = []
        self.player.equipment.weapon = None
        self.player.equipment.armor = None
        self.player.equipment.accessory_1 = None
        self.player.equipment.accessory_2 = None

        health_potion = Item(
            id="starter_health_potion",
            name="Poción de Vida",
            item_type=ITEM_TYPE_CONSUMABLE,
            rarity=RARITY_COMMON,
            description="Restaura 30 HP",
            stats={"heal": 30},
            value=20,
            stackable=True,
            max_stack=5,
        )

        if class_id == "warrior":
            weapon = Item(
                id="starter_warrior_weapon",
                name="Espada Oxidada",
                item_type=ITEM_TYPE_WEAPON,
                rarity=RARITY_COMMON,
                description="Una espada vieja y oxidada",
                stats={"atk": 3},
                value=10,
            )
            armor = Item(
                id="starter_warrior_armor",
                name="Armadura de Cuero",
                item_type=ITEM_TYPE_ARMOR,
                rarity=RARITY_COMMON,
                description="Armadura básica de cuero",
                stats={"def": 2},
                value=15,
            )
            self.player.equipment.weapon = weapon
            self.player.equipment.armor = armor
            self.player.add_item(health_potion)

        elif class_id == "rogue":
            weapon = Item(
                id="starter_rogue_weapon",
                name="Daga Oxidada",
                item_type=ITEM_TYPE_WEAPON,
                rarity=RARITY_COMMON,
                description="Una daga vieja y mellada",
                stats={"atk": 2},
                value=8,
            )
            armor = Item(
                id="starter_rogue_armor",
                name="Túnica Raída",
                item_type=ITEM_TYPE_ARMOR,
                rarity=RARITY_COMMON,
                description="Una túnica gastada",
                stats={"def": 1},
                value=10,
            )
            self.player.equipment.weapon = weapon
            self.player.equipment.armor = armor
            self.player.add_item(health_potion)

        elif class_id == "mage":
            weapon = Item(
                id="starter_mage_weapon",
                name="Bastón Viejo",
                item_type=ITEM_TYPE_WEAPON,
                rarity=RARITY_COMMON,
                description="Un bastón gastado",
                stats={"atk": 1},
                value=5,
            )
            accessory = Item(
                id="starter_mage_accessory",
                name="Anillo Simple",
                item_type=ITEM_TYPE_ACCESSORY,
                rarity=RARITY_COMMON,
                description="Un anillo insignificante",
                stats={"atk": 1},
                value=5,
            )
            self.player.equipment.weapon = weapon
            self.player.equipment.accessory_1 = accessory

            mana_potion = Item(
                id="starter_mana_potion",
                name="Poción de Mana",
                item_type=ITEM_TYPE_CONSUMABLE,
                rarity=RARITY_COMMON,
                description="Restaura 25 Mana",
                stats={"mana": 25},
                value=25,
                stackable=True,
                max_stack=5,
            )
            self.player.add_item(health_potion)
            self.player.add_item(mana_potion)

        elif class_id == "warlock":
            weapon = Item(
                id="starter_warlock_weapon",
                name="Daga Oxidada",
                item_type=ITEM_TYPE_WEAPON,
                rarity=RARITY_COMMON,
                description="Una daga vieja y mellada",
                stats={"atk": 2},
                value=8,
            )
            accessory = Item(
                id="starter_warlock_accessory",
                name="Amuleto Básico",
                item_type=ITEM_TYPE_ACCESSORY,
                rarity=RARITY_COMMON,
                description="Un amuleto simple",
                stats={"atk": 1},
                value=5,
            )
            self.player.equipment.weapon = weapon
            self.player.equipment.accessory_1 = accessory

            health_potion_2 = Item(
                id="starter_health_potion_2",
                name="Poción de Vida",
                item_type=ITEM_TYPE_CONSUMABLE,
                rarity=RARITY_COMMON,
                description="Restaura 30 HP",
                stats={"heal": 30},
                value=20,
                stackable=True,
                max_stack=5,
            )
            self.player.add_item(health_potion)
            self.player.add_item(health_potion_2)

        self.player.update_stats_from_equipment()

        self.state_machine.change_state(GameState.NEW_GAME)
    
    def _start_dungeon(self):
        """Inicia la mazmorra"""
        player_class = self.player.class_id if self.player else "warrior"
        self.dungeon = Dungeon(difficulty=DIFFICULTY_NORMAL, player_class=player_class)
        self.state_machine.change_state(GameState.DUNGEON)
    
    def _enter_current_room(self):
        """Entra a la sala actual del jugador"""
        if not self.dungeon:
            return
        
        room = self.dungeon.get_current_room()
        
        if not room or room.is_empty():
            return
        
        # Marcar como entradogit
        room.entered = True
        
        # Procesar según tipo de sala
        if room.has_stairs and self.dungeon.stairs_unlocked:
            # Las escaleras preguntan si quieres pasar (solo si están desbloqueadas)
            self._handle_stairs()
            return
        elif room.has_stairs and not self.dungeon.stairs_unlocked:
            # Las escaleras están bloqueadas - mostrar mensaje
            self.message = "Derrota a los más fuertes para avanzar"
            return
        
        # Si ya está cleared, no hacer nada (o mostrar info)
        if room.cleared:
            return
        
        # Procesar según tipo de sala
        if room.is_combat_room() and room.has_enemies():
            enemies = room.get_enemies_list()
            enemy = room.enemy[0] if isinstance(room.enemy, list) else room.enemy
            
            # Si es boss (piso 7-8), mostrar intro primero
            if room.is_boss_room() or (self.dungeon.current_floor >= 7 and enemy and 
                       hasattr(enemy, 'enemy_type') and enemy.enemy_type == ENEMY_TYPE_BOSS):
                self.boss_intro_phase = 1
                self.boss_intro_enemy = enemy
                self.state_machine.change_state(GameState.BOSS_INTRO)
                return
            
            can_flee = True
            self._start_combat(enemies, can_flee)
        elif room.room_type == ROOM_TYPE_TREASURE:
            self._collect_treasure(room.event_data)
        elif room.room_type == ROOM_TYPE_TRAP:
            self._trigger_trap(room.event_data)
        elif room.room_type == ROOM_TYPE_SANCTUARY:
            self._use_sanctuary(room.event_data)
        elif room.room_type == ROOM_TYPE_MERCHANT:
            self._open_merchant(room.event_data)
    
    def _start_combat(self, enemies: List, can_flee: bool = True):
        """Inicia combate"""
        if not self.player or not enemies:
            return
        self.combat = CombatSystem(self.player, enemies, can_flee=can_flee)
        self.state_machine.change_state(GameState.COMBAT)
    
    def _combat_action(self, skill_index: int):
        """Ejecuta acción de combate"""
        if not self.combat:
            return
        
        # Acción del jugador (ya incluye turno del enemigo automáticamente)
        result = self.combat.player_attack(skill_index)
    
    def _use_item_combat(self, item_index: int):
        """Usa un objeto en combate"""
        if not self.combat or not self.player or not hasattr(self.player, 'inventory'):
            return
        
        # Obtener objetos consumibles del inventario con su índice real
        consumables = []
        for i, item in enumerate(self.player.inventory):
            if item.item_type == ITEM_TYPE_CONSUMABLE:
                consumables.append((i, item))
        
        if not consumables:
            self.combat.log.add("No tienes objetos para usar.")
            return
        
        if item_index >= len(consumables):
            self.combat.log.add("No tienes ese objeto.")
            return
        
        # Obtener el índice real en el inventario
        real_index = consumables[item_index][0]
        
        # Usar el objeto en combate
        result = self.combat.player_use_item(real_index)
        
        if result.success:
            self.combat.log.add(result.messages[0] if result.messages else "Objeto usado.")
        else:
            self.combat.log.add(result.messages[0] if result.messages else "No se pudo usar el objeto.")
    
    def _execute_enemy_turn_immediate(self):
        """Ejecuta el turno del enemigo después del delay"""
        if not self.combat:
            self.enemy_turn_pending = False
            return
        
        # Resetear flag de delay
        self.enemy_turn_pending = False
        
        # Ejecutar el turno diferido del enemigo
        self.combat.execute_delayed_enemy_turn()
        
        # Forzar actualización de la pantalla
        self._render()
    
    def _end_player_turn(self):
        """Finaliza turno del jugador - inicia delay antes del turno del enemigo"""
        if not self.combat:
            return
        
        # Activar el delay antes del turno del enemigo
        if self.combat:
            self.combat.enemy_turn_delayed = True
        
        # Iniciar delay antes del turno del enemigo
        self.enemy_turn_pending = True
        self.enemy_turn_start_time = pygame.time.get_ticks()
    
    def _handle_combat_victory(self):
        """Maneja victoria en combate"""
        if not self.combat or not self.dungeon:
            self.state_machine.change_state(GameState.DUNGEON)
            return
        
        self.game_stats["total_kills"] += 1
        self.dungeon.clear_current_room()
        
        # Verificar si era el boss del piso 8
        if self.dungeon.current_floor == 8:
            # Ir directamente a las escaleras de victoria
            self.state_machine.change_state(GameState.VICTORY)
            return
        
        self.state_machine.change_state(GameState.DUNGEON)
    
    def _handle_stairs(self):
        """Maneja las escaleras al siguiente piso"""
        if not self.dungeon:
            return
        
        current_floor = self.dungeon.current_floor
        max_floors = self.dungeon.max_floors
        
        # Verificar si es el piso final (victoria)
        if current_floor == max_floors:
            self.state_machine.change_state(GameState.VICTORY)
            return
        
        # Avanzar al siguiente piso
        success = self.dungeon.next_floor()
        if success:
            self.game_stats["floors_cleared"] += 1
            # Mostrar mensaje de cambio de piso
            self.state_machine.change_state(GameState.DUNGEON)
    
    def _collect_treasure(self, event_data):
        """Recolecta tesoro"""
        if not event_data or not self.player or not self.dungeon:
            return
        
        # Oro
        gold = event_data.get("gold", 0)
        self.player.gold += gold
        
        # Item
        item = event_data.get("item")
        if item:
            if self.player.add_item(item):
                self.message = f"¡Tesoro! {gold} oro + {item.name}"
            else:
                # Inventario lleno, vender
                self.player.gold += item.value // 2
                self.message = f"¡Tesoro! {gold} oro (inventario lleno, +{item.value // 2} oro)"
        else:
            self.message = f"¡Tesoro! {gold} oro"
        
        self.dungeon.clear_current_room()
    
    def _trigger_trap(self, event_data):
        """Activa trampa"""
        if not self.player or not self.dungeon or not event_data:
            return
        
        damage = event_data.get("damage", 10)
        actual_damage = self.player.take_damage(damage)
        
        self.game_stats["total_damage_taken"] += actual_damage
        self.dungeon.clear_current_room()
    
    def _use_sanctuary(self, event_data):
        """Usa santuario - cura la mitad de la vida máxima"""
        if not self.player or not self.dungeon:
            return
        
        heal_amount = self.player.effective_max_hp // 2
        actual_heal = self.player.heal(heal_amount)
        self.message = f"Santuario: Has sido curado por {actual_heal} HP"
        
        self.dungeon.clear_current_room()
    
    def _open_merchant(self, event_data):
        """Abre la tienda del mercader"""
        self.merchant_items = event_data.get("items", [])
        self.merchant_mode = "buy"  # "buy" o "sell"
        self.state_machine.change_state(GameState.MERCHANT)
    
    def _buy_item(self, index: int):
        """Compra un item del mercader"""
        if not self.player or not self.merchant_items:
            return
        
        if index >= len(self.merchant_items):
            return
        
        item = self.merchant_items[index]
        if self.player.gold >= item.value:
            self.player.gold -= item.value
            
            # Si es un equipo, intentar equipar directamente
            slot = item.get_slot_type()
            if slot:
                old_item = self.player.equipment.equip_item(item, slot)
                if old_item:
                    self.player.add_item(old_item)
            else:
                self.player.add_item(item)
            
            self.merchant_items.pop(index)
            self.player.update_stats_from_equipment()
            self.message = f"Has comprado {item.name} por {item.value} oro"
        else:
            self.message = "No tienes suficiente oro"
    
    def _sell_item(self, index: int):
        """Vende un item al mercader"""
        if not self.player or not hasattr(self.player, 'inventory') or not self.player.inventory:
            return
        
        if index >= len(self.player.inventory) or len(self.player.inventory) == 0:
            return
        
        item = self.player.inventory[index]
        
        # Si el item está equipado, desequiparlo primero
        slot = item.get_slot_type()
        if slot:
            if slot == "weapon" and self.player.equipment.weapon == item:
                self.player.equipment.weapon = None
            elif slot == "armor" and self.player.equipment.armor == item:
                self.player.equipment.armor = None
            elif "accessory" in slot:
                if self.player.equipment.accessory_1 == item:
                    self.player.equipment.accessory_1 = None
                elif self.player.equipment.accessory_2 == item:
                    self.player.equipment.accessory_2 = None
        
        sell_price = item.value // 2
        self.player.gold += sell_price
        self.player.inventory.pop(index)
        self.player.update_stats_from_equipment()
        self.message = f"Has vendido {item.name} por {sell_price} oro"
        
        # Ajustar menu_selected si está fuera de rango
        if self.menu_selected >= len(self.player.inventory):
            self.menu_selected = max(0, len(self.player.inventory) - 1)
    
    def _equip_item(self, index: int):
        """Equipa un item del inventario"""
        if not self.player or not hasattr(self.player, 'inventory') or not self.player.inventory:
            return
        
        if index >= len(self.player.inventory):
            return
        
        item = self.player.inventory[index]
        slot = item.get_slot_type()
        
        if slot:
            # Verificar si es accessory y ya tiene uno
            if "accessory" in slot:
                if self.player.equipment.accessory_1:
                    slot = "accessory_2"
                else:
                    slot = "accessory_1"
            
            old_item = self.player.equipment.equip_item(item, slot)
            
            # Intercambiar
            self.player.remove_item(item)
            if old_item:
                self.player.add_item(old_item)
            
            self.player.update_stats_from_equipment()
    
    def _use_item(self, index: int):
        """Usa un item del inventario"""
        if not self.player or not hasattr(self.player, 'inventory') or not self.player.inventory:
            return
        
        if index >= len(self.player.inventory):
            return
        
        item = self.player.inventory[index]
        
        if item.item_type == ITEM_TYPE_CONSUMABLE:
            if "heal" in item.stats:
                self.player.heal(item.stats["heal"])
            if "mana" in item.stats:
                self.player.restore_mana(item.stats["mana"])
            
            self.player.remove_item(item)
    
    def _save_game(self, slot: int = None):
        """Guarda el juego - encuentra el slot automáticamente basado en el nombre del jugador"""
        if not self.player or not self.dungeon:
            return
        
        player_name = self.player.name
        
        # Si no se especifica slot, buscar automáticamente
        if slot is None:
            # Obtener info de todos los slots
            saves_info = self.save_system.get_all_saves_info()
            
            # Buscar si ya existe un guardado con el mismo nombre
            for i, info in enumerate(saves_info):
                if info.get("player_name") == player_name:
                    slot = i + 1  # Los slots son 1-indexed
                    break
            
            # Si no existe, usar el primer slot vacío
            if slot is None:
                used_slots = [info["slot"] for info in saves_info]
                for s in range(1, 4):
                    if s not in used_slots:
                        slot = s
                        break
                
                # Si todos los slots están llenos, usar el primero (sobrescribir)
                if slot is None:
                    slot = 1
        
        settings = {
            "difficulty": self.dungeon.difficulty if self.dungeon else DIFFICULTY_NORMAL,
        }
        
        success = self.save_system.save_game(
            slot, self.player, self.dungeon, self.game_stats, settings
        )
        
        if success:
            self.message = f"Partida guardada en slot {slot}"
            self.state_machine.change_state(GameState.DUNGEON)
    
    def _load_game(self, save_data: Dict):
        """Carga un juego guardado"""
        self.player = Player.from_dict(save_data["player"])
        self.dungeon = Dungeon.from_dict(save_data["dungeon"])
        self.game_stats = save_data.get("game_stats", {})
        
        self.state_machine.change_state(GameState.DUNGEON)
    
    def _resume_game(self):
        """Reanuda el juego"""
        if self.combat and not self.combat.combat_over:
            self.state_machine.change_state(GameState.COMBAT)
        else:
            self.state_machine.change_state(GameState.DUNGEON)


def main():
    """Punto de entrada"""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
