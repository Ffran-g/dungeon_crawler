"""
Renderizador UI - Interfaz con gráficos geométricos estilo Roguelike
"""

import pygame
from typing import List, Tuple, Optional, Any, Dict

from src.core.constants import *
from src.core.config import TITLE_FONT_SIZE, SMALL_FONT_SIZE
from src.systems.save_system import SaveSystem
from src.ui.sprite_manager import sprite_manager


class TextRenderer:
    """Renderizador de texto ASCII"""
    
    def __init__(self, screen: pygame.Surface, font: pygame.font.Font):
        self.screen = screen
        self.font = font
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
    
    def draw_text(self, text: str, x: int, y: int, 
                  color: Tuple[int, int, int] = COLOR_TEXT,
                  center: bool = False, background: Optional[Tuple[int, int, int]] = None,
                  size: int = 28):
        """Dibuja texto en pantalla"""
        font = pygame.font.Font(None, size)
        surface = font.render(text, True, color)
        
        if center:
            rect = surface.get_rect(center=(x, y))
            self.screen.blit(surface, rect)
        else:
            self.screen.blit(surface, (x, y))
        
        if background:
            bg_rect = surface.get_rect()
            bg_rect.topleft = (x, y)
            pygame.draw.rect(self.screen, background, bg_rect)
    
    def draw_title(self, text: str, x: int, y: int, color: Tuple[int, int, int] = COLOR_TEXT, size: int = 36):
        """Dibuja título"""
        font = pygame.font.Font(None, size)
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=(x, y))
        self.screen.blit(surface, rect)
    
    def draw_box(self, x: int, y: int, width: int, height: int,
                 border_color: Tuple[int, int, int] = COLOR_BORDER,
                 fill_color: Optional[Tuple[int, int, int]] = COLOR_BLACK):
        """Dibuja una caja con borde"""
        if fill_color:
            pygame.draw.rect(self.screen, fill_color, (x, y, width, height))
        
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), UI_BORDER)
    
    def draw_text_box(self, text: str, x: int, y: int, width: int, height: int,
                      border_color: Tuple[int, int, int] = COLOR_BORDER,
                      fill_color: Optional[Tuple[int, int, int]] = COLOR_BLACK,
                      text_color: Tuple[int, int, int] = COLOR_TEXT):
        """Dibuja una caja con texto"""
        self.draw_box(x, y, width, height, border_color, fill_color)
        
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if self.font.size(test_line)[0] < width - UI_PADDING * 2:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        line_height = self.font.get_height()
        start_y = y + UI_PADDING
        
        for i, line in enumerate(lines):
            if start_y + i * line_height < y + height - UI_PADDING:
                self.draw_text(line, x + UI_PADDING, start_y + i * line_height, text_color)


class ShapeRenderer:
    """Renderizador de formas geométricas con soporte para sprites"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.sprites = sprite_manager
    
    def draw_character(self, x: int, y: int, size: int, color: Tuple[int, int, int], is_player: bool = True, class_id: str = None, enemy_name: str = None, enemy_category: str = None):
        """Dibuja un personaje - intenta usar sprite si existe, si no usa forma geométrica"""
        
        # Intentar cargar sprite
        sprite = None
        if is_player and class_id:
            sprite = self.sprites.get_player_sprite(class_id, (size, size))
        elif not is_player and enemy_name:
            # enemy_name puede ser el nombre del enemigo
            sprite = self.sprites.get_enemy_sprite(enemy_name, enemy_category, (size, size))
        
        if sprite:
            self.screen.blit(sprite, (x, y))
            return
        
        # Fallback: dibujar forma geométrica
        if is_player:
            # Jugador: círculo azul
            pygame.draw.circle(self.screen, color, (x + size//2, y + size//2), size//2 - 2)
            pygame.draw.circle(self.screen, COLOR_WHITE, (x + size//2, y + size//2), size//2 - 2, 2)
        else:
            # Enemigo: cuadrado rojo
            pygame.draw.rect(self.screen, color, (x + 4, y + 4, size - 8, size - 8))
            pygame.draw.rect(self.screen, COLOR_WHITE, (x + 4, y + 4, size - 8, size - 8), 2)
    
    def draw_hp_bar_shapes(self, x: int, y: int, width: int, height: int, 
                          current: int, maximum: int, color: Tuple[int, int, int]):
        """Dibuja barra de HP con formas"""
        if maximum <= 0:
            return
        
        # Fondo
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (x, y, width, height))
        
        # Barra
        fill_width = int((current / maximum) * width)
        if fill_width > 0:
            pygame.draw.rect(self.screen, color, (x, y, fill_width, height))
        
        # Borde
        pygame.draw.rect(self.screen, COLOR_WHITE, (x, y, width, height), 2)
    
    def draw_sword(self, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Dibuja una espada"""
        # Hoja
        pygame.draw.polygon(self.screen, color, [
            (x + size//2, y),
            (x + size//2 + 6, y + size//3),
            (x + size//2 + 4, y + size//3 + 4),
            (x + size//2 - 4, y + size//3 + 4),
            (x + size//2 - 6, y + size//3),
        ])
        # Mango
        pygame.draw.rect(self.screen, COLOR_BROWN, (x + size//2 - 2, y + size//3 + 4, 4, size//3))
        # Guarda
        pygame.draw.rect(self.screen, COLOR_YELLOW, (x + size//2 - 6, y + size//3 + 2, 12, 3))
    
    def draw_shield(self, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Dibuja un escudo"""
        pygame.draw.ellipse(self.screen, color, (x + 4, y, size - 8, size - 4))
        pygame.draw.ellipse(self.screen, COLOR_WHITE, (x + 4, y, size - 8, size - 4), 2)
    
    def draw_potion(self, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Dibuja una poción"""
        # Frasco
        pygame.draw.rect(self.screen, color, (x + size//3, y, size//3, size//2))
        # Cuello
        pygame.draw.rect(self.screen, color, (x + size//2 - 2, y - size//4, 4, size//4))
        # Tapón
        pygame.draw.rect(self.screen, COLOR_BROWN, (x + size//2 - 3, y - size//4 - 3, 6, 4))
    
    def draw_chest(self, x: int, y: int, size: int, color: Tuple[int, int, int]):
        """Dibuja un cofre"""
        # Caja
        pygame.draw.rect(self.screen, color, (x + 2, y + size//3, size - 4, size//2 + size//6))
        # Tapa
        pygame.draw.rect(self.screen, color, (x, y, size - 2, size//3))
        # Línea de apertura
        pygame.draw.line(self.screen, COLOR_BLACK, (x + 2, y + size//3), (x + size - 4, y + size//3), 2)
        # Candado
        pygame.draw.rect(self.screen, COLOR_YELLOW, (x + size//2 - 4, y + size//3 - 2, 8, 8))
    
    def draw_trap(self, x: int, y: int, size: int):
        """Dibuja una trampa"""
        # Estrellas de peligro
        for i in range(3):
            star_x = x + size//4 + i * size//4
            star_y = y + size//2
            pygame.draw.circle(self.screen, COLOR_RED, (star_x, star_y), 3)
        # Líneas de trampa
        pygame.draw.line(self.screen, COLOR_DARK_GRAY, (x, y + size//2), (x + size, y + size//2), 3)
    
    def draw_cross(self, x: int, y: int, size: int, color: tuple = COLOR_GREEN):
        """Dibuja una cruz"""
        center_x, center_y = x + size//2, y + size//2
        pygame.draw.rect(self.screen, color, (center_x - 3, center_y - size//3, 6, size//1.5))
        pygame.draw.rect(self.screen, color, (center_x - size//3, center_y - 3, size//1.5, 6))
    
    def draw_skull(self, x: int, y: int, size: int):
        """Dibuja una calavera"""
        center_x, center_y = x + size//2, y + size//2
        radius = size // 3
        
        # Cráneo
        pygame.draw.circle(self.screen, COLOR_WHITE, (center_x, center_y - 2), radius)
        # Ojos
        pygame.draw.circle(self.screen, (20, 20, 20), (center_x - radius//3, center_y - 2), radius//4)
        pygame.draw.circle(self.screen, (20, 20, 20), (center_x + radius//3, center_y - 2), radius//4)
        # Nariz
        pygame.draw.polygon(self.screen, (20, 20, 20), [
            (center_x, center_y + 2),
            (center_x - 3, center_y + radius//2),
            (center_x + 3, center_y + radius//2),
        ])
        # Dientes
        pygame.draw.line(self.screen, (20, 20, 20), (center_x - radius//3, center_y + radius//2), (center_x - radius//3, center_y + radius), 2)
        pygame.draw.line(self.screen, (20, 20, 20), (center_x + radius//3, center_y + radius//2), (center_x + radius//3, center_y + radius), 2)
    
    def draw_merchant(self, x: int, y: int, size: int):
        """Dibuja un mercader"""
        # Tienda/carpa
        pygame.draw.polygon(self.screen, COLOR_ORANGE, [
            (x, y + size),
            (x + size//2, y),
            (x + size, y + size),
        ])
        # Entrada
        pygame.draw.rect(self.screen, COLOR_BROWN, (x + size//3, y + size//2, size//3, size//2))
    
    def draw_stairs(self, x: int, y: int, size: int):
        """Dibuja unas escaleras"""
        # Escaleras hacia abajo
        steps = 4
        step_height = size // (steps * 2)
        for i in range(steps):
            step_y = y + size - (i + 1) * step_height * 2
            pygame.draw.rect(self.screen, COLOR_WHITE, 
                           (x + i * 3, step_y, size - i * 6, step_height * 2), 1)
        # Indicador de dirección
        pygame.draw.polygon(self.screen, COLOR_CYAN, [
            (x + size//2, y + 5),
            (x + size//2 - 5, y + 15),
            (x + size//2 + 5, y + 15),
        ])


class UIRenderer:
    """
    Renderizador de componentes UI - Diseño centrado y organizado
    """
    
    def __init__(self, screen: pygame.Surface, text_renderer: TextRenderer):
        self.screen = screen
        self.tr = text_renderer
        self.shape = ShapeRenderer(screen)
        self.sprites = sprite_manager
        
        # Layout constants
        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.panel_width = 220
        self.sidebar_width = 250
    
    def draw_hp_bar(self, x: int, y: int, width: int, current: int, maximum: int,
                    color: Tuple[int, int, int] = COLOR_HP_BAR,
                    bg_color: Tuple[int, int, int] = COLOR_HP_BAR_BG):
        """Dibuja una barra de HP"""
        self.shape.draw_hp_bar_shapes(x, y, width, 20, current, maximum, color)
        self.tr.draw_text(f"{current}/{maximum}", x + width // 2, y + 10, COLOR_WHITE, center=True)
    
    def draw_mana_bar(self, x: int, y: int, width: int, current: int, maximum: int, color: tuple = COLOR_MANA_BAR):
        """Dibuja una barra de Mana"""
        self.shape.draw_hp_bar_shapes(x, y, width, 20, current, maximum, color)
        self.tr.draw_text(f"{current}/{maximum}", x + width // 2, y + 10, COLOR_WHITE, center=True)
    
    def draw_xp_bar(self, x: int, y: int, width: int, current: int, maximum: int):
        """Dibuja una barra de XP"""
        self.shape.draw_hp_bar_shapes(x, y, width, 15, current, maximum, COLOR_XP_BAR)
    
    def draw_player_stats(self, player: Any, x: int, y: int):
        """Dibuja stats del jugador - Diseño mejorado"""
        panel_w = self.panel_width + 20
        panel_h = 260
        
        # Fondo con gradiente sutil
        self.tr.draw_box(x, y, panel_w, panel_h, COLOR_BORDER, (12, 12, 20))
        
        # Borde decorativo superior
        pygame.draw.rect(self.screen, COLOR_CYAN, (x, y, panel_w, 3))
        
        # Título con fondo
        pygame.draw.rect(self.screen, (30, 30, 45), (x + 5, y + 5, panel_w - 10, 22))
        self.tr.draw_text("▀ JUGADOR ▀", x + panel_w//2, y + 8, COLOR_YELLOW, center=True)
        
        # Sprite del jugador - más grande
        sprite_x = x + panel_w // 2 - 40
        self.shape.draw_character(sprite_x, y + 35, 75, COLOR_CYAN, is_player=True, class_id=getattr(player, 'class_id', None))
        
        # Nombre y clase con estilo
        info_center = x + panel_w // 2
        self.tr.draw_text(f"✦ {player.name} ✦", info_center, y + 100, COLOR_WHITE, center=True)
        self.tr.draw_text(f"{player.player_class.name}", info_center, y + 118, COLOR_GRAY, center=True)
        
        # Nivel con badge
        level_bg_x = x + panel_w - 50
        pygame.draw.rect(self.screen, (40, 40, 60), (level_bg_x, y + 115, 40, 18))
        pygame.draw.rect(self.screen, COLOR_YELLOW, (level_bg_x, y + 115, 40, 18), 1)
        self.tr.draw_text(f"LVL {player.level}", level_bg_x + 20, y + 120, COLOR_YELLOW, center=True)
        
        # HP bar - más prominente
        bar_x = x + 12
        bar_w = panel_w - 24
        bar_y = y + 140
        
        # Fondo de la barra
        pygame.draw.rect(self.screen, (30, 20, 20), (bar_x, bar_y, bar_w, 24))
        
        # Barra de HP real
        hp_percent = player.current_hp / player.effective_max_hp if player.effective_max_hp > 0 else 0
        hp_bar_w = int(bar_w * hp_percent)
        
        # Color de la barra según porcentaje de vida
        if hp_percent > 0.6:
            hp_color = COLOR_HP_BAR
        elif hp_percent > 0.3:
            hp_color = COLOR_ORANGE
        else:
            hp_color = COLOR_RED
            
        pygame.draw.rect(self.screen, hp_color, (bar_x + 2, bar_y + 2, max(0, hp_bar_w - 4), 20))
        
        # Borde
        pygame.draw.rect(self.screen, COLOR_BORDER, (bar_x, bar_y, bar_w, 24), 2)
        
        # Texto de HP
        self.tr.draw_text(f"♥ {player.current_hp}/{player.effective_max_hp}", bar_x + bar_w//2, bar_y + 12, COLOR_WHITE, center=True)
        
        # Mana/Concentración - segunda barra
        mana_y = y + 170
        pygame.draw.rect(self.screen, (20, 20, 35), (bar_x, mana_y, bar_w, 20))
        
        if player.class_id == "warrior":
            conc = getattr(player, 'current_concentration', 0)
            max_conc = getattr(player, 'max_concentration', 10)
            conc_ready = getattr(player, 'concentration_ready', False)
            bar_color = COLOR_YELLOW if conc_ready else (80, 80, 180)
            mana_percent = conc / max_conc if max_conc > 0 else 0
            mana_text = f"⚔ {conc}/{max_conc}"
        else:
            mana_percent = player.current_mana / player.max_mana if player.max_mana > 0 else 0
            bar_color = COLOR_MANA_BAR
            mana_text = f"♦ {player.current_mana}/{player.max_mana}"
        
        mana_bar_w = int(bar_w * mana_percent)
        pygame.draw.rect(self.screen, bar_color, (bar_x + 2, mana_y + 2, max(0, mana_bar_w - 4), 16))
        pygame.draw.rect(self.screen, COLOR_BORDER, (bar_x, mana_y, bar_w, 20), 2)
        self.tr.draw_text(mana_text, bar_x + bar_w//2, mana_y + 10, COLOR_WHITE, center=True)
        
        # Barra de XP
        xp_y = y + 195
        pygame.draw.rect(self.screen, (25, 20, 40), (bar_x, xp_y, bar_w, 16))
        
        xp_percent = player.xp / player.xp_to_next_level if player.xp_to_next_level > 0 else 0
        xp_bar_w = int(bar_w * xp_percent)
        
        # Color de XP según progreso
        xp_color = (180, 100, 255)  # Púrpura
        pygame.draw.rect(self.screen, xp_color, (bar_x + 2, xp_y + 2, max(0, xp_bar_w - 4), 12))
        pygame.draw.rect(self.screen, COLOR_BORDER, (bar_x, xp_y, bar_w, 16), 1)
        
        self.tr.draw_text(f"Exp: {player.xp}/{player.xp_to_next_level}", bar_x + bar_w//2, xp_y + 4, COLOR_WHITE, center=True)
        
        # Stats row - mejorado con iconos
        stats_y = y + panel_h - 28
        
        # Fondo para stats
        pygame.draw.rect(self.screen, (25, 25, 35), (x + 5, stats_y - 3, panel_w - 10, 22))
        
        # ATQ con icono
        atk_box_w = 50
        atk_box_h = 18
        atk_box_x = x + (panel_w // 2) - atk_box_w - 3
        pygame.draw.rect(self.screen, (60, 30, 30), (atk_box_x, stats_y, atk_box_w, atk_box_h))
        pygame.draw.rect(self.screen, COLOR_RED, (atk_box_x, stats_y, atk_box_w, atk_box_h), 1)
        # Intentar cargar sprite de ataque
        atk_icon = self.sprites.get_stat_icon("attack", (14, 14))
        if atk_icon:
            self.screen.blit(atk_icon, (atk_box_x + 2, stats_y + 2))
            self.tr.draw_text(f"{player.attack}", atk_box_x + atk_box_w//2 + 5, stats_y + 4, COLOR_RED, center=True)
        else:
            self.tr.draw_text(f"⚔ {player.attack}", atk_box_x + atk_box_w//2, stats_y + 4, COLOR_RED, center=True)
        
        # DEF con icono
        def_box_w = 50
        def_box_x = x + (panel_w // 2) + 3
        pygame.draw.rect(self.screen, (30, 30, 60), (def_box_x, stats_y, def_box_w, atk_box_h))
        pygame.draw.rect(self.screen, COLOR_BLUE, (def_box_x, stats_y, def_box_w, atk_box_h), 1)
        def_icon = self.sprites.get_stat_icon("defense", (14, 14))
        if def_icon:
            self.screen.blit(def_icon, (def_box_x + 2, stats_y + 2))
            self.tr.draw_text(f"{player.defense}", def_box_x + def_box_w//2 + 5, stats_y + 4, COLOR_BLUE, center=True)
        else:
            self.tr.draw_text(f"🛡 {player.defense}", def_box_x + def_box_w//2, stats_y + 4, COLOR_BLUE, center=True)
        
        # Oro con icono - centrado abajo
        gold_box_w = 70
        gold_box_x = x + (panel_w - gold_box_w) // 2
        gold_box_y = stats_y + 20
        pygame.draw.rect(self.screen, (60, 60, 30), (gold_box_x, gold_box_y, gold_box_w, 16))
        pygame.draw.rect(self.screen, COLOR_YELLOW, (gold_box_x, gold_box_y, gold_box_w, 16), 1)
        gold_icon = self.sprites.get_stat_icon("gold", (14, 14))
        if gold_icon:
            self.screen.blit(gold_icon, (gold_box_x + 2, gold_box_y + 1))
            self.tr.draw_text(f"{player.gold}", gold_box_x + gold_box_w//2 + 8, gold_box_y + 3, COLOR_YELLOW, center=True)
        else:
            gold_text = f"💰 {player.gold}"
            self.tr.draw_text(gold_text, gold_box_x + gold_box_w//2, gold_box_y + 3, COLOR_YELLOW, center=True)
    
    def draw_enemy_info(self, enemy: Any, x: int, y: int):
        """Dibuja información del enemigo"""
        self.tr.draw_box(x, y, 280, 140)
        
        # Sprite del enemigo
        enemy_color = COLOR_RED
        # Sprite del enemigo - más grande
        enemy_color = COLOR_RED
        if enemy.enemy_type == ENEMY_TYPE_ELITE:
            enemy_color = COLOR_ORANGE
        elif enemy.enemy_type == ENEMY_TYPE_BOSS:
            enemy_color = (128, 0, 128)  # Púrpura para bosses
        
        # Determinar categoría del enemigo para el sprite
        enemy_category = enemy.enemy_type
        # Usar original_name si existe (para bosses enfurecidos)
        sprite_name = getattr(enemy, 'original_name', None) or enemy.name
        self.shape.draw_character(x + 20, y + 20, 80, enemy_color, is_player=False, enemy_name=sprite_name, enemy_category=enemy_category)
        
        info_x = x + 110
        
        # Nombre
        self.tr.draw_text(f"{enemy.name}", info_x, y + 20, COLOR_YELLOW if enemy.enemy_type == ENEMY_TYPE_BOSS else COLOR_TEXT)
        
        # Tipo
        type_text = {"basic": "Básico", "elite": "Élite", "boss": "JEFE"}.get(enemy.enemy_type, "Unknown")
        self.tr.draw_text(f"Tipo: {type_text}", info_x, y + 40, enemy_color)
        
        # HP
        self.tr.draw_text("HP:", info_x, y + 60)
        self.draw_hp_bar(info_x + 30, y + 60, 150, enemy.current_hp, enemy.max_hp, enemy_color)
        
        # Stats
        stats_y = y + 90
        self.tr.draw_text(f"ATQ: {enemy.atk}", info_x, stats_y, COLOR_RED)
        self.tr.draw_text(f"DEF: {enemy.defense}", info_x + 80, stats_y, COLOR_BLUE)
        
        # Recompensas
        self.tr.draw_text(f"Oro: {enemy.gold_reward} | XP: {enemy.xp_reward}", info_x, stats_y + 25, COLOR_YELLOW)
    
    def draw_combat_log(self, messages: List[str], x: int, y: int, width: int, height: int):
        """Dibuja el log de combate"""
        self.tr.draw_box(x, y, width, height)
        
        line_height = self.tr.font.get_height()
        start_y = y + UI_PADDING
        
        for i, msg in enumerate(messages[-8:]):
            if start_y + i * line_height < y + height - UI_PADDING:
                color = COLOR_TEXT
                msg_lower = msg.lower()
                if "crítico" in msg_lower or "¡" in msg:
                    color = COLOR_YELLOW
                elif "atacas" in msg_lower:
                    color = COLOR_GREEN
                elif "mueres" in msg_lower or "derrotado" in msg_lower or "game over" in msg_lower:
                    color = COLOR_RED
                elif "curas" in msg_lower or "victoria" in msg_lower:
                    color = COLOR_GREEN
                
                self.tr.draw_text(msg, x + UI_PADDING, start_y + i * line_height, color)
    
    def draw_dungeon_info(self, dungeon: Any, x: int, y: int):
        """Dibuja información de la mazmorra - Panel lateral derecho"""
        panel_w = self.sidebar_width
        panel_h = 140
        
        self.tr.draw_box(x, y, panel_w, panel_h, COLOR_BORDER, (15, 15, 25))
        
        status = dungeon.get_dungeon_status()
        
        # Título del piso
        self.tr.draw_text(f"PISO {status['current_floor']} / {status['max_floors']}", 
                         x + panel_w//2, y + 12, COLOR_YELLOW, center=True)
        
        # Barra de progreso
        bar_x = x + 15
        bar_y = y + 35
        bar_w = panel_w - 30
        bar_h = 16
        
        # Fondo
        pygame.draw.rect(self.screen, COLOR_DARK_GRAY, (bar_x, bar_y, bar_w, bar_h))
        # Progreso
        progress = status['cleared_rooms'] / status['total_rooms'] if status['total_rooms'] > 0 else 0
        fill = int(progress * bar_w)
        pygame.draw.rect(self.screen, COLOR_GREEN, (bar_x, bar_y, fill, bar_h))
        # Borde
        pygame.draw.rect(self.screen, COLOR_WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
        
        # Texto de progreso
        self.tr.draw_text(f"Salas: {status['cleared_rooms']}/{status['total_rooms']}", 
                         x + panel_w//2, y + 58, COLOR_GRAY, center=True)
        
        # Estado de escaleras
        stairs_text = "Desbloqueadas" if status.get('stairs_unlocked', False) else "Bloqueadas"
        stairs_color = COLOR_GREEN if status.get('stairs_unlocked', False) else COLOR_RED
        self.tr.draw_text(f"Escaleras: {stairs_text}", x + panel_w//2, y + 78, stairs_color, center=True)
        
        # Enemigos restantes
        elite_text = f"Elites: {status.get('elites_defeated', 0)}/{status.get('total_elites', 0)}"
        self.tr.draw_text(elite_text, x + panel_w//2, y + 100, COLOR_ORANGE, center=True)
    
    def draw_dungeon_view(self, dungeon: Any, player: Any):
        """Dibuja la vista de la mazmorra como grid 9x9 - Centrado"""
        from src.systems.dungeon import GRID_SIZE, CENTER
        
        # Calcular posición centrada
        cell_size = 50
        grid_size_px = cell_size * GRID_SIZE
        
        # Centrar el grid en la pantalla
        grid_x = (SCREEN_WIDTH - grid_size_px) // 2
        grid_y = (SCREEN_HEIGHT - grid_size_px) // 2 - 30
        
        # Marco decorativo alrededor del grid
        frame_pad = 8
        pygame.draw.rect(self.screen, (20, 20, 35), 
                        (grid_x - frame_pad, grid_y - frame_pad, 
                         grid_size_px + frame_pad*2, grid_size_px + frame_pad*2))
        
        # Título del piso centrado sobre el grid
        self.tr.draw_title(f"PISO {dungeon.current_floor}", SCREEN_WIDTH // 2, int(grid_y - 25), COLOR_YELLOW)
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_x = grid_x + x * cell_size
                cell_y = grid_y + y * cell_size
                
                room = dungeon.get_room(x, y)
                
                if not room or room.is_empty():
                    pygame.draw.rect(self.screen, (15, 15, 20), 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1))
                    continue
                
                if room.visible:
                    bg_color = (35, 35, 45)
                elif room.visited:
                    bg_color = (25, 25, 30)
                else:
                    bg_color = (18, 18, 22)
                
                pygame.draw.rect(self.screen, bg_color, 
                               (cell_x, cell_y, cell_size - 1, cell_size - 1))
                
                # Dibujar contenido de la celda
                if x == dungeon.player_x and y == dungeon.player_y:
                    # Jugador
                    pygame.draw.rect(self.screen, COLOR_CYAN, 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                    self.shape.draw_character(cell_x + 8, cell_y + 8, 34, COLOR_CYAN, True)
                elif not room.cleared and room.discovered and room.is_combat_room() and room.enemy:
                    enemy_color = COLOR_RED
                    enemy = room.enemy[0] if isinstance(room.enemy, list) else room.enemy
                    if enemy.enemy_type == ENEMY_TYPE_ELITE:
                        enemy_color = COLOR_ORANGE
                    elif enemy.enemy_type == ENEMY_TYPE_BOSS:
                        enemy_color = (148, 0, 211)
                    pygame.draw.rect(self.screen, enemy_color, 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                    # Usar sprite de tile del enemigo
                    enemy_tile = self.sprites.get_enemy_tile_sprite(enemy.enemy_type, (cell_size - 2, cell_size - 2))
                    if enemy_tile:
                        self.screen.blit(enemy_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_character(cell_x + 8, cell_y + 8, 34, enemy_color, False)
                elif room.discovered and room.room_type == ROOM_TYPE_TREASURE:
                    pygame.draw.rect(self.screen, COLOR_YELLOW, 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                    treasure_tile = self.sprites.get_map_tile_sprite("treasure", (cell_size - 2, cell_size - 2))
                    if treasure_tile:
                        self.screen.blit(treasure_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_chest(cell_x + 10, cell_y + 10, 30, COLOR_YELLOW)
                elif room.discovered and room.has_stairs and room.room_type == ROOM_TYPE_STAIRS:
                    pygame.draw.rect(self.screen, COLOR_CYAN, 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                    stairs_tile = self.sprites.get_map_tile_sprite("stairs", (cell_size - 2, cell_size - 2))
                    if stairs_tile:
                        self.screen.blit(stairs_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_stairs(cell_x + 10, cell_y + 10, 30)
                elif room.discovered and room.room_type == ROOM_TYPE_SANCTUARY:
                    pygame.draw.rect(self.screen, COLOR_GREEN, 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                    sanctuary_tile = self.sprites.get_map_tile_sprite("sanctuary", (cell_size - 2, cell_size - 2))
                    if sanctuary_tile:
                        self.screen.blit(sanctuary_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_cross(cell_x + 10, cell_y + 10, 30)
                elif room.discovered and room.room_type == ROOM_TYPE_MERCHANT:
                    pygame.draw.rect(self.screen, COLOR_ORANGE, 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                    merchant_tile = self.sprites.get_map_tile_sprite("merchant", (cell_size - 2, cell_size - 2))
                    if merchant_tile:
                        self.screen.blit(merchant_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_merchant(cell_x + 10, cell_y + 10, 30)
                elif room.entered and room.room_type == ROOM_TYPE_TRAP:
                    pygame.draw.rect(self.screen, COLOR_RED, 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                    trap_tile = self.sprites.get_map_tile_sprite("trap", (cell_size - 2, cell_size - 2))
                    if trap_tile:
                        self.screen.blit(trap_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_trap(cell_x + 10, cell_y + 10, 30)
                elif room.room_type == "start":
                    pygame.draw.rect(self.screen, (50, 50, 80), 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 2)
                elif room.cleared:
                    pygame.draw.rect(self.screen, (40, 40, 50), 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 1)
                else:
                    pygame.draw.rect(self.screen, (50, 55, 65), 
                                   (cell_x, cell_y, cell_size - 1, cell_size - 1), 1)
        
        # Instrucciones centradas debajo del grid
        self.tr.draw_text("Flechas: Mover | Enter: Entrar | I: Inventario | Esc: Pausa", 
                         SCREEN_WIDTH // 2, grid_y + grid_size_px + 20, COLOR_GRAY, center=True)


class MenuRenderer:
    """Renderizador de menús"""
    
    def __init__(self, screen: pygame.Surface, text_renderer: TextRenderer):
        self.screen = screen
        self.tr = text_renderer
        self.shape = ShapeRenderer(screen)
        self.sprites = sprite_manager
    
    def draw_main_menu(self, selected: int = 0):
        """Dibuja el menú principal - Diseño lateral y título impactante"""
        # Fondo oscuro (limpia cualquier rastro anterior)
        self.screen.fill((10, 10, 15))
        
        # Fondo con imagen
        bg = self.sprites.load_sprite("background", "menu", (SCREEN_WIDTH, SCREEN_HEIGHT))
        if bg:
            self.screen.blit(bg, (0, 0))
        
        # Título grande y impactante - lado izquierdo
        title_x = 110
        self.tr.draw_title("DUNGEON", title_x, 60, COLOR_YELLOW, size=48)
        self.tr.draw_title("CRAWLER", title_x, 115, COLOR_YELLOW, size=48)
        
        # Subtítulo con efecto
        self.tr.draw_text("Roguelike RPG", title_x, 175, COLOR_GRAY, size=20)
        
        # Menú lateral izquierdo
        menu_x = 50
        menu_y = 250
        menu_w = 280
        
        # Opciones del menú
        options = ["Nueva Partida", "Cargar Partida", "Salir"]
        
        for i, option in enumerate(options):
            y_pos = menu_y + i * 60
            
            # Iconos para cada opción
            icons = ["⚔", "📜", "✖"]
            
            # Fondo de selección
            if i == selected:
                pygame.draw.rect(self.screen, (40, 40, 55), (menu_x - 15, y_pos - 10, menu_w + 30, 50))
                pygame.draw.rect(self.screen, COLOR_YELLOW, (menu_x - 15, y_pos - 10, menu_w + 30, 50), 2)
                color = COLOR_YELLOW
            else:
                color = COLOR_TEXT
            
            # Dibujar opción
            self.tr.draw_text(f"{icons[i]}  {option}", menu_x + 20, y_pos + 12, color, size=24)
        
        # Controles en la parte inferior
        self.tr.draw_text("[FLECHAS] Navegar  [ENTER] Seleccionar", 50, SCREEN_HEIGHT - 50, COLOR_DARK_GRAY)
        
        # Versión
        self.tr.draw_text("v1.0.0", SCREEN_WIDTH - 60, SCREEN_HEIGHT - 25, COLOR_DARK_GRAY)
    
    def draw_class_selection(self, selected: int = 0, class_info: Optional[Dict] = None):
        """Dibuja selección de clase - Diseño centrado"""
        self.screen.fill((10, 10, 15))
        
        center_x = SCREEN_WIDTH // 2
        
        # Título
        self.tr.draw_title("ELIGE TU CLASE", center_x, 40, COLOR_YELLOW)
        
        classes_data = [
            ("warrior", "Guerrero", "Alto HP y defensa", COLOR_RED),
            ("mage", "Mago", "Alto daño mágico", COLOR_BLUE),
            ("rogue", "Pícaro", "Veloz y crítico", COLOR_GREEN),
            ("warlock", "Brujo", "Usa vida para magia", COLOR_MAGENTA),
        ]
        
        # Grid 2x2 de clases
        card_w = 220
        card_h = 150
        spacing = 30
        grid_w = card_w * 2 + spacing
        start_x = (SCREEN_WIDTH - grid_w) // 2
        start_y = 80
        
        # Dibujar cada clase
        for i, (class_id, name, desc, color) in enumerate(classes_data):
            col = i % 2
            row = i // 2
            x_base = start_x + col * (card_w + spacing)
            y_base = start_y + row * (card_h + spacing)
            
            # Fondo de selección
            if i == selected:
                self.tr.draw_box(x_base - 8, y_base - 8, card_w + 16, card_h + 16, COLOR_YELLOW, (30, 30, 45))
            else:
                self.tr.draw_box(x_base - 8, y_base - 8, card_w + 16, card_h + 16, COLOR_BORDER, (18, 18, 25))
            
            # Icono representativo - intentar cargar sprite del personaje
            icon_x = x_base + card_w // 2
            sprite = self.sprites.get_player_sprite(class_id, (80, 80))
            if sprite:
                self.screen.blit(sprite, (icon_x - 40, y_base + 15))
            else:
                # Fallback: dibujar forma geométrica
                if class_id == "warrior":
                    self.shape.draw_sword(icon_x - 15, y_base + 20, 30, color)
                elif class_id == "mage":
                    self.shape.draw_character(icon_x, y_base + 25, 30, color, True)
                elif class_id == "rogue":
                    self.shape.draw_character(icon_x, y_base + 25, 30, color, True)
                elif class_id == "warlock":
                    self.shape.draw_skull(icon_x - 15, y_base + 20, 30)
            
            # Nombre - debajo del icono
            self.tr.draw_text(name, icon_x, y_base + 100, color, center=True)
            # Descripción - debajo del nombre
            self.tr.draw_text(desc, icon_x, y_base + 120, COLOR_GRAY, center=True)
        
        # Panel de información de la clase seleccionada
        if class_info:
            info_w = 600
            info_h = 180
            info_x = (SCREEN_WIDTH - info_w) // 2
            info_y = start_y + card_h * 2 + spacing + 20
            
            self.tr.draw_box(info_x, info_y, info_w, info_h, COLOR_BORDER, (20, 20, 30))
            
            # Nombre y descripción
            self.tr.draw_title(class_info["name"], info_x + 30, info_y + 15, COLOR_YELLOW)
            self.tr.draw_text(class_info["description"], info_x + 30, info_y + 45, COLOR_GRAY)
            
            # Estadísticas
            if "stats" in class_info:
                stats = class_info["stats"]
                stats_text = f"HP: {stats.get('hp', 0)}   ATQ: {stats.get('atk', 0)}   DEF: {stats.get('def', 0)}"
                self.tr.draw_text(stats_text, info_x + 30, info_y + 75, COLOR_WHITE)
            
            # Habilidades
            if "skills" in class_info:
                self.tr.draw_text("HABILIDADES:", info_x + 30, info_y + 105, COLOR_CYAN)
                for i, skill in enumerate(class_info["skills"]):
                    skill_y = info_y + 125 + (i // 2) * 18
                    skill_x = info_x + 30 + (i % 2) * 280
                    self.tr.draw_text(f"• {skill['name']}", skill_x, skill_y, COLOR_GRAY)
        
        self.tr.draw_text("[FLECHAS] Navegar  [ENTER] Seleccionar  [ESC] Volver", center_x, SCREEN_HEIGHT - 30, COLOR_GRAY, center=True)
    
    def draw_difficulty_selection(self, selected: int = 0):
        """Dibuja selección de dificultad - Diseño centrado"""
        self.screen.fill((10, 10, 15))
        
        center_x = SCREEN_WIDTH // 2
        
        # Marco decorativo
        panel_w = 450
        panel_h = 320
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 40
        
        pygame.draw.rect(self.screen, (20, 20, 30), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, COLOR_YELLOW, (panel_x, panel_y, panel_w, panel_h), 2)
        
        self.tr.draw_title("ELIGE DIFICULTAD", center_x, panel_y + 30, COLOR_YELLOW)
        
        difficulties = [
            ("1. Fácil", "Para jugadores nuevos", COLOR_GREEN),
            ("2. Normal", "Dificultad estándar", COLOR_BLUE),
            ("3. Difícil", "Para veteranos", COLOR_ORANGE),
            ("4. Pesadilla", "Sobrevivir es un logro", COLOR_RED),
        ]
        
        for i, (name, desc, color) in enumerate(difficulties):
            y_pos = panel_y + 80 + i * 55
            
            if i == selected:
                pygame.draw.rect(self.screen, (35, 35, 50), (panel_x + 30, y_pos - 5, panel_w - 60, 45))
                pygame.draw.rect(self.screen, color, (panel_x + 30, y_pos - 5, panel_w - 60, 45), 2)
            
            self.tr.draw_text(name, center_x, y_pos + 5, color if i == selected else COLOR_TEXT, center=True)
            self.tr.draw_text(desc, center_x, y_pos + 25, COLOR_GRAY, center=True)
    
    def draw_inventory(self, player: Any, selected: int = 0, x: int = 100, y: int = 100, view_mode: str = "inventory"):
        """Dibuja el inventario - Diseño centrado
        view_mode: "inventory" o "equipment"
        """
        # Calcular posición centrada
        inv_w = 700
        inv_h = 500
        inv_x = (SCREEN_WIDTH - inv_w) // 2
        inv_y = (SCREEN_HEIGHT - inv_h) // 2 - 30
        
        # Fondo
        self.screen.fill((10, 10, 15))
        
        # Título según modo
        title = "EQUIPAMIENTO" if view_mode == "equipment" else "INVENTARIO"
        
        # Marco decorativo
        pygame.draw.rect(self.screen, (20, 20, 30), (inv_x - 10, inv_y - 10, inv_w + 20, inv_h + 20))
        pygame.draw.rect(self.screen, COLOR_YELLOW, (inv_x - 10, inv_y - 10, inv_w + 20, inv_h + 20), 2)
        
        self.tr.draw_text(title, SCREEN_WIDTH // 2, inv_y + 5, COLOR_YELLOW, center=True)
        
        # Instrucciones
        if view_mode == "inventory":
            self.tr.draw_text("[E] Equip  [ENTER] Equipar  [ESC] Salir", SCREEN_WIDTH // 2, inv_y + 35, COLOR_GRAY, center=True)
        else:
            self.tr.draw_text("[E] Inventario  [ESC] Salir", SCREEN_WIDTH // 2, inv_y + 35, COLOR_GRAY, center=True)
        
        if view_mode == "equipment":
            # Vista de equipamiento - 4 slots en fila
            eq = player.equipment
            slot_w = 160
            slot_h = 300
            spacing = 10
            total_w = slot_w * 4 + spacing * 3
            slot_start_x = (SCREEN_WIDTH - total_w) // 2
            slot_y = inv_y + 70
            
            slots = [
                ("Arma", eq.weapon),
                ("Armadura", eq.armor),
                ("Accesorio 1", eq.accessory_1),
                ("Accesorio 2", eq.accessory_2),
            ]
            
            for i, (slot_name, item) in enumerate(slots):
                slot_x = slot_start_x + i * (slot_w + spacing)
                box_color = COLOR_HIGHLIGHT if i == selected else COLOR_BORDER
                self.tr.draw_box(slot_x, slot_y, slot_w, slot_h, box_color, (20, 20, 25))
                self.tr.draw_text(slot_name, slot_x + slot_w//2, slot_y + 10, COLOR_GRAY, center=True)
                
                if item:
                    item_color = RARITY_COLORS.get(item.rarity, COLOR_WHITE)
                    if item.item_type == ITEM_TYPE_WEAPON:
                        self.shape.draw_sword(slot_x + slot_w//2 - 20, slot_y + 60, 40, item_color)
                    elif item.item_type == ITEM_TYPE_ARMOR:
                        self.shape.draw_shield(slot_x + slot_w//2 - 20, slot_y + 60, 40, item_color)
                    else:
                        self.shape.draw_character(slot_x + slot_w//2 - 20, slot_y + 60, 40, item_color, True)
                    
                    self.tr.draw_text(item.name, slot_x + slot_w//2, slot_y + 110, item_color, center=True)
                    stats_str = ", ".join([f"{k}: {v}" for k, v in item.stats.items()])
                    self.tr.draw_text(stats_str, slot_x + slot_w//2, slot_y + 140, COLOR_GRAY, center=True)
                else:
                    self.tr.draw_text("---", slot_x + slot_w//2, slot_y + 80, COLOR_DARK_GRAY, center=True)
            
            return
        
        # Vista de inventario normal - grid de 4x5
        slot_w = 160
        slot_h = 70
        spacing = 10
        cols = 4
        rows = 4
        total_w = slot_w * cols + spacing * (cols - 1)
        slot_start_x = (SCREEN_WIDTH - total_w) // 2
        slot_start_y = inv_y + 70
        
        # Dibujar slots
        for i in range(INVENTORY_MAX_SLOTS):
            col = i % cols
            row = i // cols
            slot_x = slot_start_x + col * (slot_w + spacing)
            slot_y = slot_start_y + row * (slot_h + spacing)
            
            # Color del slot
            slot_color = COLOR_HIGHLIGHT if i == selected else COLOR_BORDER
            
            pygame.draw.rect(self.screen, slot_color, (slot_x, slot_y, slot_w, slot_h), 2)
            
            if i < len(player.inventory):
                item = player.inventory[i]
                item_color = RARITY_COLORS.get(item.rarity, COLOR_WHITE)
                
                # Icono según tipo
                if item.item_type == ITEM_TYPE_WEAPON:
                    self.shape.draw_sword(slot_x + 5, slot_y + 10, 30, item_color)
                elif item.item_type == ITEM_TYPE_ARMOR:
                    self.shape.draw_shield(slot_x + 5, slot_y + 10, 30, item_color)
                elif item.item_type == ITEM_TYPE_CONSUMABLE:
                    self.shape.draw_potion(slot_x + 5, slot_y + 10, 30, item_color)
                else:
                    self.shape.draw_character(slot_x + 5, slot_y + 10, 30, item_color, True)
                
                self.tr.draw_text(f"[{i+1}] {item.name[:12]}", slot_x + 40, slot_y + 10, item_color)
                self.tr.draw_text(f"{item.item_type}", slot_x + 40, slot_y + 30, COLOR_GRAY)
            else:
                self.tr.draw_text(f"[{i+1}] ---", slot_x + 40, slot_y + 20, COLOR_DARK_GRAY)
        
        # Info del item seleccionado
        if selected < len(player.inventory):
            item = player.inventory[selected]
            self.tr.draw_box(x + 400, y + 350, 380, 140)
            self.tr.draw_text(item.name, x + 420, y + 360, RARITY_COLORS.get(item.rarity, COLOR_WHITE))
            self.tr.draw_text(item.description, x + 420, y + 380, COLOR_GRAY)
            
            stats_str = ", ".join([f"{k}: {v}" for k, v in item.stats.items()])
            self.tr.draw_text(f"Stats: {stats_str}", x + 420, y + 410, COLOR_TEXT)
            self.tr.draw_text(f"Valor: {item.value} oro", x + 420, y + 440, COLOR_YELLOW)
        
        # Equipamiento
        eq_x = x + 20
        eq_y = y + 350
        self.tr.draw_text("EQUIPADOS:", eq_x, eq_y, COLOR_YELLOW)
        
        eq_items = [
            ("Arma", player.equipment.weapon),
            ("Armadura", player.equipment.armor),
            ("Acc 1", player.equipment.accessory_1),
            ("Acc 2", player.equipment.accessory_2),
        ]
        
        for i, (slot_name, item) in enumerate(eq_items):
            y_offset = eq_y + 25 + i * 25
            item_name = item.name if item else "---"
            color = RARITY_COLORS.get(item.rarity, COLOR_TEXT) if item else COLOR_DARK_GRAY
            self.tr.draw_text(f"{slot_name}: {item_name}", eq_x, y_offset, color)
    
    def draw_save_slots(self, saves_info: List[Dict], selected: int = 0):
        """Dibuja slots de guardado - Diseño centrado"""
        self.screen.fill((10, 10, 15))
        
        center_x = SCREEN_WIDTH // 2
        
        self.tr.draw_title("CARGAR PARTIDA", center_x, 50, COLOR_YELLOW)
        
        # Slots centrados
        slot_w = 450
        slot_h = 110
        spacing = 20
        start_y = 100
        
        # Obtener slots ocupados
        used_slots = [info.get("slot", i+1) for i, info in enumerate(saves_info)]
        
        for i in range(3):
            y = start_y + i * (slot_h + spacing)
            x = center_x - slot_w // 2
            
            box_color = COLOR_HIGHLIGHT if i == selected else COLOR_BORDER
            
            if i < len(saves_info):
                info = saves_info[i]
                fill_color = (25, 25, 35)
            else:
                fill_color = (15, 15, 20)
                info = None
            
            self.tr.draw_box(x, y, slot_w, slot_h, box_color, fill_color)
            
            if info:
                self.tr.draw_text(f"Slot {i+1}: {info['player_name']}", center_x, y + 15, COLOR_YELLOW, center=True)
                self.tr.draw_text(f"Clase: {info['player_class']}  |  Nivel: {info['level']}", center_x, y + 40, COLOR_GRAY, center=True)
                self.tr.draw_text(f"Piso: {info['floor']}/{info['max_floors']}", center_x, y + 60, COLOR_GRAY, center=True)
                self.tr.draw_text(f"Guardado: {SaveSystem.format_timestamp(info['timestamp'])}", center_x, y + 85, COLOR_DARK_GRAY, center=True)
            else:
                self.tr.draw_text(f"Slot {i+1}: [Vacío]", center_x, y + 45, COLOR_DARK_GRAY, center=True)
            
            # Si está seleccionado y tiene datos, mostrar opción de borrar
            if i == selected and info:
                self.tr.draw_text("[X] Borrar", center_x, y + 100, COLOR_RED, center=True)
        
        # Instrucciones
        self.tr.draw_text("[FLECHAS] Navegar  [ENTER] Cargar  [X] Borrar  [ESC] Volver", center_x, SCREEN_HEIGHT - 40, COLOR_GRAY, center=True)
    
    def draw_combat_menu(self, combat_system: Any, selected: int = 0, skill_selected: int = 0):
        """Dibuja el menú de combate - Diseño centrado"""
        center_x = SCREEN_WIDTH // 2
        
        # Acciones en barra inferior - centradas
        actions = ["ATACAR", "DEFENDER", "OBJETO", "HUIR"]
        
        btn_w = 150
        btn_h = 45
        spacing = 20
        total_w = btn_w * 4 + spacing * 3
        start_x = (SCREEN_WIDTH - total_w) // 2
        y = 480
        
        for i, action in enumerate(actions):
            color = COLOR_HIGHLIGHT if i == selected else COLOR_TEXT
            x = start_x + i * (btn_w + spacing)
            
            btn_color = (50, 55, 75) if i == selected else (25, 30, 40)
            pygame.draw.rect(self.screen, btn_color, (x, y, btn_w, btn_h))
            pygame.draw.rect(self.screen, color, (x, y, btn_w, btn_h), 2)
            
            self.tr.draw_text(action, x + btn_w // 2, y + btn_h // 2, color, center=True)
        
        # Panel de habilidades (cuando está en ATACAR)
        if selected == 0:
            skills = combat_system.player.get_skills_info()
            
            # Fondo del panel de habilidades - centrado
            panel_w = 500
            panel_h = 130
            panel_x = (SCREEN_WIDTH - panel_w) // 2
            panel_y = 540
            
            pygame.draw.rect(self.screen, (20, 20, 30), (panel_x, panel_y, panel_w, panel_h))
            pygame.draw.rect(self.screen, COLOR_BORDER, (panel_x, panel_y, panel_w, panel_h), 2)
            
            self.tr.draw_text("HABILIDADES:", panel_x + 15, panel_y + 8, COLOR_YELLOW)
            
            for i, skill in enumerate(skills):
                if skill["on_cooldown"]:
                    color = COLOR_DARK_GRAY
                else:
                    color = COLOR_GREEN if i == skill_selected else COLOR_TEXT
                
                x_pos = panel_x + 20 + (i % 2) * 240
                y_pos = panel_y + 30 + (i // 2) * 30
                
                prefix = ">" if i == skill_selected else " "
                mana_text = f" ({skill['mana_cost']} MP)" if skill['mana_cost'] > 0 else ""
                cd_text = f" CD:{skill['cooldown']}" if skill['cooldown'] > 0 else ""
                
                self.tr.draw_text(f"{prefix}[{i+1}] {skill['name']}{mana_text}{cd_text}", x_pos, y_pos, color)
            
            # Descripción de la habilidad seleccionada
            if skills and skill_selected < len(skills):
                skill = skills[skill_selected]
                self.tr.draw_text(f"  {skill['description']}", panel_x + 15, panel_y + panel_h - 20, COLOR_GRAY)
    
    # Panel de objetos (cuando está en OBJETO)
        elif selected == 2:
            # Mostrar pociones en el inventario
            pygame.draw.rect(self.screen, (20, 20, 30), (40, 475, 350, 150))
            pygame.draw.rect(self.screen, COLOR_BORDER, (40, 475, 350, 150), 2)
            
            self.tr.draw_text("OBJETOS:", 50, 480, COLOR_YELLOW)
            
            consumables = [item for item in combat_system.player.inventory 
                          if item.item_type == ITEM_TYPE_CONSUMABLE]
            
            if consumables:
                for i, item in enumerate(consumables[:4]):
                    color = COLOR_CYAN if i == 0 else COLOR_TEXT
                    y_pos = 505 + i * 30
                    
                    heal_text = f"+{item.stats.get('heal', 0)} HP" if 'heal' in item.stats else ""
                    self.tr.draw_text(f"[{i+1}] {item.name} {heal_text}", 50, y_pos, color)
            else:
                self.tr.draw_text("No tienes objetos", 50, 505, COLOR_DARK_GRAY)
    
    def draw_dungeon_view(self, dungeon: Any, player: Any):
        """Dibuja la vista de la mazmorra como grid 9x9"""
        from src.systems.dungeon import GRID_SIZE, CENTER
        
        # Posición del grid
        grid_x = 380
        grid_y = 100
        cell_size = 55
        
        # Título
        title_x = grid_x + cell_size * 4 + cell_size // 2
        title_y = int(grid_y - 30)
        self.tr.draw_title(f"PISO {dungeon.current_floor}", title_x, title_y, COLOR_YELLOW)
        
        # Fondo del grid
        pygame.draw.rect(self.screen, (15, 15, 20), 
                        (grid_x - 5, grid_y - 5, cell_size * GRID_SIZE + 10, cell_size * GRID_SIZE + 10))
        
        # Dibujar cada celda
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                cell_x = grid_x + x * cell_size
                cell_y = grid_y + y * cell_size
                
                room = dungeon.get_room(x, y)
                
                if not room or room.is_empty():
                    # Celda vacía
                    pygame.draw.rect(self.screen, (25, 25, 30), 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2))
                    continue
                
                # Fondo de la celda
                if room.visible:
                    bg_color = (40, 40, 50)
                elif room.visited:
                    bg_color = (30, 30, 35)
                else:
                    bg_color = COLOR_BLACK  # Salas no accesibles totally black
                
                pygame.draw.rect(self.screen, bg_color, 
                               (cell_x, cell_y, cell_size - 2, cell_size - 2))
                
                # Borde según estado
                if x == dungeon.player_x and y == dungeon.player_y:
                    # Posición del jugador
                    pygame.draw.rect(self.screen, COLOR_CYAN, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 3)
                    self.shape.draw_character(cell_x + 10, cell_y + 10, 35, COLOR_CYAN, True)
                elif room.discovered and room.is_combat_room() and room.enemy:
                    # Enemigo presente - usar sprite de tile
                    enemy_color = COLOR_RED
                    # Obtener el tipo de enemigo (puede ser lista o objeto)
                    enemy = room.enemy[0] if isinstance(room.enemy, list) else room.enemy
                    if enemy.enemy_type == ENEMY_TYPE_ELITE:
                        enemy_color = COLOR_ORANGE
                    elif enemy.enemy_type == ENEMY_TYPE_BOSS:
                        enemy_color = (128, 0, 128)
                    pygame.draw.rect(self.screen, enemy_color, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                    # Usar sprite de tile del enemigo - ocupa toda la celda
                    enemy_tile = self.sprites.get_enemy_tile_sprite(enemy.enemy_type, (cell_size - 2, cell_size - 2))
                    if enemy_tile:
                        self.screen.blit(enemy_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_character(cell_x + 10, cell_y + 10, 35, enemy_color, False)
                elif room.discovered and room.room_type == ROOM_TYPE_TREASURE:
                    pygame.draw.rect(self.screen, COLOR_YELLOW, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                    treasure_tile = self.sprites.get_map_tile_sprite("treasure", (cell_size - 2, cell_size - 2))
                    if treasure_tile:
                        self.screen.blit(treasure_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_chest(cell_x + 12, cell_y + 12, 30, COLOR_YELLOW)
                elif room.discovered and room.has_stairs and room.room_type == ROOM_TYPE_STAIRS:
                    pygame.draw.rect(self.screen, COLOR_BLUE, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                    stairs_tile = self.sprites.get_map_tile_sprite("stairs", (cell_size - 2, cell_size - 2))
                    if stairs_tile:
                        self.screen.blit(stairs_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_stairs(cell_x + 12, cell_y + 12, 30)
                elif room.entered and room.room_type == ROOM_TYPE_TRAP:
                    pygame.draw.rect(self.screen, COLOR_RED, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                    trap_tile = self.sprites.get_map_tile_sprite("trap", (cell_size - 2, cell_size - 2))
                    if trap_tile:
                        self.screen.blit(trap_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_trap(cell_x + 12, cell_y + 12, 30)
                elif room.discovered and room.room_type == ROOM_TYPE_SANCTUARY:
                    pygame.draw.rect(self.screen, COLOR_GREEN, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                    sanctuary_tile = self.sprites.get_map_tile_sprite("sanctuary", (cell_size - 2, cell_size - 2))
                    if sanctuary_tile:
                        self.screen.blit(sanctuary_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_cross(cell_x + 12, cell_y + 12, 30)
                elif room.discovered and room.room_type == ROOM_TYPE_MERCHANT:
                    pygame.draw.rect(self.screen, COLOR_ORANGE, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                    merchant_tile = self.sprites.get_map_tile_sprite("merchant", (cell_size - 2, cell_size - 2))
                    if merchant_tile:
                        self.screen.blit(merchant_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_merchant(cell_x + 12, cell_y + 12, 30)
                elif room.visible and room.has_stairs:
                    pygame.draw.rect(self.screen, COLOR_CYAN, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                    stairs_tile = self.sprites.get_map_tile_sprite("stairs", (cell_size - 2, cell_size - 2))
                    if stairs_tile:
                        self.screen.blit(stairs_tile, (cell_x, cell_y))
                    else:
                        self.shape.draw_stairs(cell_x + 10, cell_y + 10, 30)
                elif room.room_type == "start":
                    pygame.draw.rect(self.screen, COLOR_BLUE, 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 2)
                elif room.cleared:
                    pygame.draw.rect(self.screen, (50, 50, 50), 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 1)
                else:
                    pygame.draw.rect(self.screen, (60, 60, 70), 
                                   (cell_x, cell_y, cell_size - 2, cell_size - 2), 1)
        
        # Instrucciones
        self.tr.draw_text("Usa flechas para moverte", grid_x + cell_size * 4, grid_y + cell_size * GRID_SIZE + 15, COLOR_GRAY, center=True)
        self.tr.draw_text("ENTER = Entrar en sala", grid_x + cell_size * 4, grid_y + cell_size * GRID_SIZE + 35, COLOR_GRAY, center=True)
    
    def draw_victory(self):
        """Dibuja pantalla de victoria - Diseño centrado"""
        self.screen.fill((10, 10, 15))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Marco decorativo
        panel_w = 500
        panel_h = 250
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = center_y - panel_h // 2
        
        pygame.draw.rect(self.screen, (20, 25, 20), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, COLOR_GREEN, (panel_x, panel_y, panel_w, panel_h), 3)
        
        # Efecto visual - estrellas doradas
        for i in range(8):
            x = panel_x + 50 + i * 55
            self.shape.draw_character(x, panel_y + 40, 30, COLOR_YELLOW, True)
        
        self.tr.draw_title("¡VICTORIA!", center_x, panel_y + 80, COLOR_YELLOW)
        self.tr.draw_title("Has completado la mazmorra", center_x, panel_y + 130, COLOR_GREEN)
        
        self.tr.draw_text("Presiona ENTER para volver al menú", center_x, panel_y + panel_h - 30, COLOR_GRAY, center=True)
    
    def draw_defeat(self):
        """Dibuja pantalla de derrota - Diseño centrado"""
        self.screen.fill((15, 10, 10))
        
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Marco decorativo
        panel_w = 500
        panel_h = 220
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = center_y - panel_h // 2
        
        pygame.draw.rect(self.screen, (30, 15, 15), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, COLOR_RED, (panel_x, panel_y, panel_w, panel_h), 3)
        
        # Efecto visual
        self.shape.draw_character(center_x, panel_y + 50, 80, COLOR_RED, False)
        
        self.tr.draw_title("GAME OVER", center_x, panel_y + 80, COLOR_RED)
        self.tr.draw_text("Has sido derrotado en la mazmorra...", center_x, panel_y + 130, COLOR_GRAY, center=True)
        self.tr.draw_text("[ENTER] Volver al menú", center_x, panel_y + panel_h - 30, COLOR_GRAY, center=True)
    
    def draw_pause_menu(self, selected: int = 0):
        """Dibuja menú de pausa - Diseño centrado"""
        # Overlay con transparencia
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLOR_BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Panel centrado
        panel_w = 320
        panel_h = 280
        panel_x = (SCREEN_WIDTH - panel_w) // 2
        panel_y = (SCREEN_HEIGHT - panel_h) // 2 - 30
        
        # Fondo del panel
        pygame.draw.rect(self.screen, (20, 20, 30), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, COLOR_YELLOW, (panel_x, panel_y, panel_w, panel_h), 2)
        
        center_x = SCREEN_WIDTH // 2
        
        self.tr.draw_title("PAUSA", center_x, panel_y + 20, COLOR_YELLOW)
        
        options = ["Continuar", "Inventario", "Guardar", "Menú Principal"]
        
        for i, option in enumerate(options):
            color = COLOR_HIGHLIGHT if i == selected else COLOR_TEXT
            y_pos = panel_y + 70 + i * 45
            
            # Fondo de selección
            if i == selected:
                pygame.draw.rect(self.screen, (40, 40, 55), (panel_x + 20, y_pos - 5, panel_w - 40, 35))
                pygame.draw.rect(self.screen, COLOR_YELLOW, (panel_x + 20, y_pos - 5, panel_w - 40, 35), 2)
            
            self.tr.draw_text(option, center_x, y_pos + 10, color, center=True)
