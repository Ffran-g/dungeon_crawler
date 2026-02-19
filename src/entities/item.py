"""
Módulo de Items - Equipamiento y objetos consumibles
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random

from src.core.constants import *


# ============================================================================
# DEFINICIONES DE ITEMS
# ============================================================================

WEAPON_PREFIXES = {
    RARITY_COMMON: ["Rota", "Simple", "Vieja"],
    RARITY_UNCOMMON: ["Buena", "Afilada", "Sólida"],
    RARITY_RARE: ["Mágica", "Encantada", "Superior"],
    RARITY_EPIC: ["Legendaria", "Épica", "Ancestral"],
    RARITY_LEGENDARY: ["Divina", "Mythica", "Legendaria"],
}

ARMOR_PREFIXES = {
    RARITY_COMMON: ["Rota", "Simple", "Usada"],
    RARITY_UNCOMMON: ["Buena", "Sólida", "Resistente"],
    RARITY_RARE: ["Mágica", "Encantada", "Superior"],
    RARITY_EPIC: ["Legendaria", "Épica", "Ancestral"],
    RARITY_LEGENDARY: ["Divina", "Mythica", "Legendaria"],
}

ACCESSORY_PREFIXES = {
    RARITY_COMMON: ["Simple", "Básica"],
    RARITY_UNCOMMON: ["Buena", "Útil"],
    RARITY_RARE: ["Mágica", "Especial"],
    RARITY_EPIC: ["Legendaria", "Épica"],
    RARITY_LEGENDARY: ["Divina", "Mythica"],
}

WEAPON_NAMES = ["Espada", "Hacha", "Maza", "Daga", "Lanza", "Bastón"]
ARMOR_NAMES = ["Armadura", "Pechera", "Cota", "Túnica", "Escudo"]
ACCESSORY_NAMES = ["Anillo", "Amuleto", "Cinturón", "Collar"]


# ============================================================================
# CLASE ITEM
# ============================================================================

@dataclass
class Item:
    """Clase base para todos los items"""
    id: str
    name: str
    item_type: str
    rarity: str
    description: str
    stats: Dict[str, int]
    value: int  # Valor en oro
    stackable: bool = False
    max_stack: int = 1
    
    def __post_init__(self):
        if not self.stats:
            self.stats = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el item"""
        return {
            "id": self.id,
            "name": self.name,
            "item_type": self.item_type,
            "rarity": self.rarity,
            "description": self.description,
            "stats": self.stats,
            "value": self.value,
            "stackable": self.stackable,
            "max_stack": self.max_stack,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Item':
        """Deserializa el item"""
        item = cls(
            id=data["id"],
            name=data["name"],
            item_type=data["item_type"],
            rarity=data["rarity"],
            description=data["description"],
            stats=data.get("stats", {}),
            value=data["value"],
            stackable=data.get("stackable", False),
            max_stack=data.get("max_stack", 1),
        )
        return item
    
    def get_display_name(self) -> str:
        """Retorna nombre con color según rareza"""
        return f"[{self.rarity.upper()}] {self.name}"
    
    def get_slot_type(self) -> str:
        """Retorna el tipo de slot para equipar"""
        if self.item_type == ITEM_TYPE_WEAPON:
            return "weapon"
        elif self.item_type == ITEM_TYPE_ARMOR:
            return "armor"
        elif self.item_type == ITEM_TYPE_ACCESSORY:
            return "accessory_1"  # Se asigna dinámicamente
        return None


# ============================================================================
# ITEMS PREDEFINIDOS
# ============================================================================

# Armas predefinidas
WEAPONS = {
    "rusty_sword": Item(
        "rusty_sword", "Espada Oxidada", ITEM_TYPE_WEAPON, RARITY_COMMON,
        "Una espada vieja y oxidada", {"atk": 3}, 10
    ),
    "iron_sword": Item(
        "iron_sword", "Espada de Hierro", ITEM_TYPE_WEAPON, RARITY_UNCOMMON,
        "Una espada de hierro bien forjada", {"atk": 7}, 50
    ),
    "steel_sword": Item(
        "steel_sword", "Espada de Acero", ITEM_TYPE_WEAPON, RARITY_RARE,
        "Una espada de acero de calidad", {"atk": 12}, 150
    ),
    "flame_sword": Item(
        "flame_sword", "Espada de Fuego", ITEM_TYPE_WEAPON, RARITY_EPIC,
        "Una espada encantada con fuego", {"atk": 18}, 400
    ),
    "dragon_slayer": Item(
        "dragon_slayer", "Matadragones", ITEM_TYPE_WEAPON, RARITY_LEGENDARY,
        "La legendaria espada matadragones", {"atk": 30}, 1000
    ),
    "poison_dagger": Item(
        "poison_dagger", "Daga Venenosa", ITEM_TYPE_WEAPON, RARITY_UNCOMMON,
        "Una daga coated con veneno", {"atk": 5, "poison_on_hit": 2}, 80
    ),
}

# Armaduras predefinidas
ARMORS = {
    "leather_armor": Item(
        "leather_armor", "Armadura de Cuero", ITEM_TYPE_ARMOR, RARITY_COMMON,
        "Armadura básica de cuero", {"def": 2}, 15
    ),
    "iron_armor": Item(
        "iron_armor", "Armadura de Hierro", ITEM_TYPE_ARMOR, RARITY_UNCOMMON,
        "Armadura sólida de hierro", {"def": 5}, 75
    ),
    "steel_armor": Item(
        "steel_armor", "Armadura de Acero", ITEM_TYPE_ARMOR, RARITY_RARE,
        "Armadura de acero reforzada", {"def": 10}, 200
    ),
    "magic_armor": Item(
        "magic_armor", "Armadura Mágica", ITEM_TYPE_ARMOR, RARITY_EPIC,
        "Armadura con protección mágica", {"def": 15, "hp": 20}, 500
    ),
    "divine_armor": Item(
        "divine_armor", "Armadura Divina", ITEM_TYPE_ARMOR, RARITY_LEGENDARY,
        "Armadura bendecida por los dioses", {"def": 25, "hp": 50}, 1500
    ),
    "thorns_armor": Item(
        "thorns_armor", "Armadura de Espinas", ITEM_TYPE_ARMOR, RARITY_RARE,
        "Devuelve daño al atacante", {"def": 5, "reflect_damage": 5}, 250
    ),
}

# Accesorios predefinidos
ACCESSORIES = {
    "ring_strength": Item(
        "ring_strength", "Anillo de Fuerza", ITEM_TYPE_ACCESSORY, RARITY_UNCOMMON,
        "Aumenta la fuerza", {"atk": 3}, 60
    ),
    "ring_agility": Item(
        "ring_agility", "Anillo de Agilidad", ITEM_TYPE_ACCESSORY, RARITY_UNCOMMON,
        "Aumenta el ataque", {"atk": 3}, 60
    ),
    "amulet_health": Item(
        "amulet_health", "Amuleto de Salud", ITEM_TYPE_ACCESSORY, RARITY_RARE,
        "Aumenta la vida máxima", {"hp": 25}, 180
    ),
    "belt_defense": Item(
        "belt_defense", "Cinturón de Defensa", ITEM_TYPE_ACCESSORY, RARITY_RARE,
        "Aumenta la defensa", {"def": 5}, 180
    ),
    "vampiric_amulet": Item(
        "vampiric_amulet", "Amuleto Vampirico", ITEM_TYPE_ACCESSORY, RARITY_RARE,
        "Regenera vida cada turno", {"hp": 3, "regen_per_turn": 3}, 300
    ),
    "lucky_charm": Item(
        "lucky_charm", "Amuleto de la Suerte", ITEM_TYPE_ACCESSORY, RARITY_RARE,
        "Aumenta el crítico", {"crit_chance": 10}, 250
    ),
}

# Consumibles predefinidos
CONSUMABLES = {
    "health_potion": Item(
        "health_potion", "Poción de Vida", ITEM_TYPE_CONSUMABLE, RARITY_COMMON,
        "Restaura 30 HP", {"heal": 30}, 20, stackable=True, max_stack=10
    ),
    "health_potion_large": Item(
        "health_potion_large", "Poción de Vida Grande", ITEM_TYPE_CONSUMABLE, RARITY_UNCOMMON,
        "Restaura 75 HP", {"heal": 75}, 50, stackable=True, max_stack=5
    ),
    "mana_potion": Item(
        "mana_potion", "Poción de Mana", ITEM_TYPE_CONSUMABLE, RARITY_COMMON,
        "Restaura 25 Mana", {"mana": 25}, 25, stackable=True, max_stack=10
    ),
    "antidote": Item(
        "antidote", "Antídoto", ITEM_TYPE_CONSUMABLE, RARITY_COMMON,
        "Cura veneno", {"cure_poison": True}, 15, stackable=True, max_stack=10
    ),
    "strength_potion": Item(
        "strength_potion", "Poción de Fuerza", ITEM_TYPE_CONSUMABLE, RARITY_UNCOMMON,
        "+10 ATQ por 3 turnos", {"temp_atk": 10, "temp_atk_turns": 3}, 40, stackable=True, max_stack=5
    ),
    "poison_dart": Item(
        "poison_dart", "Dardo Envenenado", ITEM_TYPE_CONSUMABLE, RARITY_COMMON,
        "Hace 1 daño + aplica veneno (3 turnos)", {"fixed_damage": 1, "apply_poison": 3}, 15, stackable=True, max_stack=10
    ),
}


# ============================================================================
# GENERADOR DE ITEMS
# ============================================================================

class ItemGenerator:
    """
    Genera items aleatorios based en piso y dificultad
    """
    
    @staticmethod
    def generate_weapon(floor: int, rarity: str = None) -> Item:
        """Genera un arma aleatoria"""
        if rarity is None:
            rarity = ItemGenerator._get_random_rarity(floor)
        
        prefix = random.choice(WEAPON_PREFIXES.get(rarity, [""]))
        base_name = random.choice(WEAPON_NAMES)
        
        # Calcular stats based en rareza y piso
        base_stats = int(3 * RARITY_MULTIPLIERS[rarity] * (1 + floor * 0.1))
        
        item = Item(
            id=f"generated_{random.randint(10000, 99999)}",
            name=f"{prefix} {base_name}",
            item_type=ITEM_TYPE_WEAPON,
            rarity=rarity,
            description=f"Un {base_name.lower()} {rarity}",
            stats={"atk": base_stats},
            value=int(base_stats * 5 * RARITY_MULTIPLIERS[rarity]),
        )
        return item
    
    @staticmethod
    def generate_armor(floor: int, rarity: str = None) -> Item:
        """Genera una armadura aleatoria"""
        if rarity is None:
            rarity = ItemGenerator._get_random_rarity(floor)
        
        prefix = random.choice(ARMOR_PREFIXES.get(rarity, [""]))
        base_name = random.choice(ARMOR_NAMES)
        
        base_stats = int(2 * RARITY_MULTIPLIERS[rarity] * (1 + floor * 0.1))
        
        item = Item(
            id=f"generated_{random.randint(10000, 99999)}",
            name=f"{prefix} {base_name}",
            item_type=ITEM_TYPE_ARMOR,
            rarity=rarity,
            description=f"Un {base_name.lower()} {rarity}",
            stats={"def": base_stats},
            value=int(base_stats * 5 * RARITY_MULTIPLIERS[rarity]),
        )
        return item
    
    @staticmethod
    def generate_accessory(floor: int, rarity: str = None) -> Item:
        """Genera un accesorio aleatorio"""
        if rarity is None:
            rarity = ItemGenerator._get_random_rarity(floor)
        
        prefix = random.choice(ACCESSORY_PREFIXES.get(rarity, [""]))
        base_name = random.choice(ACCESSORY_NAMES)
        
        # Stats aleatorios
        stat_type = random.choice(["atk", "def", "hp"])
        base_value = int(2 * RARITY_MULTIPLIERS[rarity] * (1 + floor * 0.1))
        
        item = Item(
            id=f"generated_{random.randint(10000, 99999)}",
            name=f"{prefix} {base_name}",
            item_type=ITEM_TYPE_ACCESSORY,
            rarity=rarity,
            description=f"Un {base_name.lower()} {rarity}",
            stats={stat_type: base_value},
            value=int(base_value * 4 * RARITY_MULTIPLIERS[rarity]),
        )
        return item
    
    @staticmethod
    def _get_random_rarity(floor: int) -> str:
        """Determina rareza aleatoria basada en piso"""
        weights = {
            RARITY_COMMON: 60,
            RARITY_UNCOMMON: 25,
            RARITY_RARE: 10,
            RARITY_EPIC: 4,
            RARITY_LEGENDARY: 1,
        }
        
        # Aumentar rareza con el piso
        if floor > 3:
            weights[RARITY_COMMON] = 45
            weights[RARITY_UNCOMMON] = 30
        if floor > 5:
            weights[RARITY_COMMON] = 35
            weights[RARITY_UNCOMMON] = 30
            weights[RARITY_RARE] = 20
        
        total = sum(weights.values())
        roll = random.randint(1, total)
        
        cumulative = 0
        for rarity, weight in weights.items():
            cumulative += weight
            if roll <= cumulative:
                return rarity
        
        return RARITY_COMMON
    
    @staticmethod
    def generate_random_equipment(floor: int) -> Item:
        """Genera equipo aleatorio"""
        choice = random.choice(["weapon", "armor", "accessory"])
        
        if choice == "weapon":
            return ItemGenerator.generate_weapon(floor)
        elif choice == "armor":
            return ItemGenerator.generate_armor(floor)
        else:
            return ItemGenerator.generate_accessory(floor)


# ============================================================================
# INVENTARIO
# ============================================================================

class Inventory:
    """Sistema de inventario"""
    
    def __init__(self, max_slots: int = INVENTORY_MAX_SLOTS):
        self.max_slots = max_slots
        self.items: List[Item] = []
    
    def add_item(self, item: Item) -> bool:
        """Añade item al inventario"""
        # Verificar si es apilable y ya existe
        if item.stackable:
            for existing in self.items:
                if existing.id == item.id and len(self.items) < self.max_slots:
                    return True
        
        if len(self.items) < self.max_slots:
            self.items.append(item)
            return True
        return False
    
    def remove_item(self, item: Item) -> bool:
        """Remueve item"""
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def get_item(self, index: int) -> Optional[Item]:
        """Obtiene item por índice"""
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def is_full(self) -> bool:
        return len(self.items) >= self.max_slots
    
    def to_dict(self) -> List[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]
    
    @classmethod
    def from_dict(cls, data: List[Dict[str, Any]]) -> 'Inventory':
        inv = cls()
        inv.items = [Item.from_dict(d) for d in data]
        return inv
