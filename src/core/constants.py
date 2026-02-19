"""
Constantes del juego - Valores fundamentales que no cambian durante la ejecución
"""

# ============================================================================
# CONSTANTES DE VENTANA Y PANTALLA
# ============================================================================

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# Área de juego (el resto es UI)
GAME_AREA_WIDTH = 700
GAME_AREA_HEIGHT = 600
UI_PANEL_WIDTH = 300

# ============================================================================
# CONSTANTES DEL JUGADOR
# ============================================================================

PLAYER_NAME_MAX_LENGTH = 15
INVENTORY_MAX_SLOTS = 20

# Stats máximos
MAX_STAT_VALUE = 100
MIN_STAT_VALUE = 1

# Stats base para cada clase
BASE_STATS = {
    "warrior": {"hp": 120, "atk": 15, "def": 10},
    "mage": {"hp": 80, "atk": 20, "def": 5},
    "rogue": {"hp": 90, "atk": 12, "def": 0},
    "warlock": {"hp": 110, "atk": 14, "def": 6},
}

# ============================================================================
# CONSTANTES DE LA MAZMORRA
# ============================================================================

MAX_DUNGEON_FLOORS = 8
ROOMS_PER_FLOOR = 5

# Tipos de salas
ROOM_TYPE_COMBAT_BASIC = "combat_basic"
ROOM_TYPE_COMBAT_ELITE = "combat_elite"
ROOM_TYPE_COMBAT_BOSS = "combat_boss"
ROOM_TYPE_TREASURE = "treasure"
ROOM_TYPE_TRAP = "trap"
ROOM_TYPE_MERCHANT = "merchant"
ROOM_TYPE_SANCTUARY = "sanctuary"
ROOM_TYPE_STAIRS = "stairs"

# Probabilidades de eventos por tipo de piso (pesos, no porcentajes)
EVENT_WEIGHTS_EASY = {
    ROOM_TYPE_COMBAT_BASIC: 50,
    ROOM_TYPE_TREASURE: 15,
    ROOM_TYPE_TRAP: 15,
    ROOM_TYPE_MERCHANT: 10,
    ROOM_TYPE_SANCTUARY: 10,
}

EVENT_WEIGHTS_MID = {
    ROOM_TYPE_COMBAT_BASIC: 15,
    ROOM_TYPE_COMBAT_ELITE: 40,
    ROOM_TYPE_TREASURE: 15,
    ROOM_TYPE_TRAP: 15,
    ROOM_TYPE_MERCHANT: 10,
    ROOM_TYPE_SANCTUARY: 5,
}

EVENT_WEIGHTS_BOSS = {
    ROOM_TYPE_COMBAT_BOSS: 100,
}

# ============================================================================
# CONSTANTES DE COMBATE
# ============================================================================

# Daño mínimo para evitar 0 damage
MIN_DAMAGE = 1

# Multiplicadores de daño
CRITICAL_HIT_MULTIPLIER = 1.5
DEFENSE_DAMAGE_REDUCTION = 0.5

# Probabilidades
CRITICAL_HIT_CHANCE = 0.1
HIT_CHANCE_BASE = 0.9

# ============================================================================
# CONSTANTES DE DIFICULTAD
# ============================================================================

DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"
DIFFICULTY_NIGHTMARE = "nightmare"

DIFFICULTY_MULTIPLIERS = {
    DIFFICULTY_EASY: 0.7,
    DIFFICULTY_NORMAL: 1.0,
    DIFFICULTY_HARD: 1.3,
    DIFFICULTY_NIGHTMARE: 1.5,
}

# ============================================================================
# CONSTANTES DE ITEMS
# ============================================================================

# Tipos de items
ITEM_TYPE_WEAPON = "weapon"
ITEM_TYPE_ARMOR = "armor"
ITEM_TYPE_ACCESSORY = "accessory"
ITEM_TYPE_CONSUMABLE = "consumable"
ITEM_TYPE_MATERIAL = "material"

# Rarezas
RARITY_COMMON = "common"
RARITY_UNCOMMON = "uncommon"
RARITY_RARE = "rare"
RARITY_EPIC = "epic"
RARITY_LEGENDARY = "legendary"

RARITY_COLORS = {
    RARITY_COMMON: (192, 192, 192),
    RARITY_UNCOMMON: (0, 255, 0),
    RARITY_RARE: (0, 0, 255),
    RARITY_EPIC: (128, 0, 128),
    RARITY_LEGENDARY: (255, 165, 0),
}

RARITY_MULTIPLIERS = {
    RARITY_COMMON: 1.0,
    RARITY_UNCOMMON: 1.5,
    RARITY_RARE: 2.0,
    RARITY_EPIC: 3.0,
    RARITY_LEGENDARY: 5.0,
}

# Slots de equipamiento
EQUIP_SLOT_WEAPON = "weapon"
EQUIP_SLOT_ARMOR = "armor"
EQUIP_SLOT_ACCESSORY_1 = "accessory_1"
EQUIP_SLOT_ACCESSORY_2 = "accessory_2"

# ============================================================================
# CONSTANTES DE ENEMIGOS
# ============================================================================

# Tipos de enemigos
ENEMY_TYPE_BASIC = "basic"
ENEMY_TYPE_ELITE = "elite"
ENEMY_TYPE_BOSS = "boss"

# Nombres de enemigos básicos
BASIC_ENEMY_NAMES = ["Goblin", "Rata Gigante", "Esqueleto", "Orco", "Zombi"]

# Nombres de enemigos elite
ELITE_ENEMY_NAMES = ["Orco Berserker", "Trol", "Nigromante", "Vampiro"]

# Nombres de bosses
BOSS_ENEMY_NAMES = ["Dragón Ancianos", "Lich Señor", "Demonio Infernal"]

# ============================================================================
# CONSTANTES DE GUARDADO
# ============================================================================

MAX_SAVE_SLOTS = 3
SAVE_FILE_PREFIX = "save_slot_"
SAVE_FILE_EXTENSION = ".json"
# ============================================================================

UI_PADDING = 10
UI_BORDER = 2

# Colores (formato RGB)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GRAY = (64, 64, 64)
COLOR_LIGHT_GRAY = (200, 200, 200)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_ORANGE = (255, 165, 0)
COLOR_BROWN = (139, 69, 19)

# Colores específicos del juego
COLOR_BG = COLOR_BLACK
COLOR_TEXT = COLOR_WHITE
COLOR_TEXT_DIM = COLOR_GRAY
COLOR_BORDER = COLOR_DARK_GRAY
COLOR_HIGHLIGHT = COLOR_YELLOW
COLOR_DANGER = COLOR_RED
COLOR_SUCCESS = COLOR_GREEN

# Barras
COLOR_HP_BAR = (255, 0, 0)
COLOR_HP_BAR_BG = (64, 0, 0)
COLOR_XP_BAR = (0, 0, 255)
COLOR_XP_BAR_BG = (0, 0, 64)
COLOR_MANA_BAR = (0, 0, 255)
COLOR_MANA_BAR_BG = (0, 0, 64)
