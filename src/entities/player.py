"""
Módulo de Jugador - Clases y personaje
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import random

from src.core.constants import *


@dataclass
class Skill:
    """Representa una habilidad del personaje"""
    name: str
    description: str
    damage_mult: float = 1.0
    heal_amount: int = 0
    defense_boost: int = 0
    attack_boost: int = 0
    stun_chance: float = 0.0  # Probabilidad de aturdimiento (0.0 - 1.0)
    stun_turns: int = 0
    mana_cost: int = 0
    hp_cost: int = 0  # Coste de vida (brujo)
    cooldown: int = 0
    buff_duration: int = 0  # Duración del buff en turnos (0 = 1 turno)
    effect: str = "damage"  # damage, heal, buff, debuff, stun, multihit, shield, channel
    multihit_count: int = 0  # Número de golpes para multihit
    min_damage: int = 0  # Daño mínimo para habilidades especiales
    max_damage: int = 0  # Daño máximo para habilidades especiales
    reflect_percent: int = 0  # Porcentaje de daño rechazado (shield)
    mana_restore: int = 0  # Mana recuperado (channel)


@dataclass
class Passive:
    """Representa una habilidad pasiva del personaje"""
    name: str
    description: str
    passive_type: str  # regen_hp, regen_mana, crit_bonus, evasion_bonus, lifesteal, damage_reduction, skill_discount
    value: int = 0  # Valor del bonus
    trigger_threshold: int = 0  # Umbral para activar (ej: HP% para activar regen)
    
    def get_description(self) -> str:
        """Retorna descripción formateada"""
        return f"{self.name}: {self.description}"


class CharacterClass:
    """Clase base para las clases de personaje"""
    
    def __init__(self, class_id: str, name: str, base_stats: Dict[str, int], 
                 skills: List[Skill], description: str, passives: List[Passive] = None,
                 defense_skill: Skill = None):
        self.id = class_id
        self.name = name
        self.base_stats = base_stats
        self.skills = skills
        self.description = description
        self.passives = passives or []
        
        # Habilidades de defensa únicas por clase
        self.defense_skill = self._get_defense_skill()
    
    def _get_defense_skill(self) -> Skill:
        """Define la habilidad de defensa única de cada clase"""
        return Skill(
            name="Defender",
            description="Reduce el daño recibido",
            defense_boost=5
        )


class Warrior(CharacterClass):
    def __init__(self):
        super().__init__(
            "warrior", "Guerrero",
            BASE_STATS["warrior"],
            [
                Skill("Corte", "Un ataque poderoso", damage_mult=1.5),
                Skill("Golpe", "Ataque con probabilidad de aturdir (baja con uso)", damage_mult=1.2, stun_chance=0.75),
                Skill("Furia", "Aumenta tu ataque temporalmente (+5 ATQ)", damage_mult=1.0, effect="buff", attack_boost=5, buff_duration=1),
                Skill("Escudo", "Gran defensa (+15 DEF) y reduce daño recibido", damage_mult=0.5, effect="buff", defense_boost=15, buff_duration=1),
            ],
            "Guerrero experto en combate cuerpo a cuerpo. Alto HP y defensa.",
            passives=[
                Passive("Regeneración", "Restaura 2 HP cada turno", "regen_hp", value=2),
                Passive("Piel de Acero", "+5 DEF cuando HP < 30%", "damage_reduction", value=5, trigger_threshold=30),
            ]
        )
        
    def _get_defense_skill(self) -> Skill:
        return Skill(
            name="Postura Defensiva",
            description="+10 DEF por un turno",
            defense_boost=10
        )


class Mage(CharacterClass):
    def __init__(self):
        super().__init__(
            "mage", "Mago",
            BASE_STATS["mage"],
            [
                Skill("Misiles Arcanos", "3 golpes de 1-4 de daño cada uno", effect="multihit", multihit_count=3, min_damage=1, max_damage=4, mana_cost=10),
                Skill("Escudo Repelente", "Reduce daño recibido y lo devuelve al atacante", effect="shield", defense_boost=10, reflect_percent=50, mana_cost=8),
                Skill("Canalizar", "Recupera 20 de Mana", effect="channel", mana_restore=20),
                Skill("Bola de Fuego", "Gran daño mágico", damage_mult=2.0, mana_cost=15),
            ],
            "Maestro de las artes arcanas. Alto daño pero frágil.",
            passives=[
                Passive("Regeneración Mágica", "Restaura 3 MANA cada turno", "regen_mana", value=3),
                Passive("Intelecto", "+10% de daño con habilidades", "skill_damage_bonus", value=10),
                Passive("Escudo Arcano", "+8 DEF cuando MANA > 50%", "damage_reduction", value=8, trigger_threshold=50),
            ]
        )
        
    def _get_defense_skill(self) -> Skill:
        return Skill(
            name="Escudo Mágico",
            description="+8 DEF y regenera 10 MANA",
            defense_boost=8
        )


class Rogue(CharacterClass):
    def __init__(self):
        super().__init__(
            "rogue", "Pícaro",
            BASE_STATS["rogue"],
            [
                Skill("Ráfaga", "4 golpes rápidos de poco daño cada uno", effect="multihit", multihit_count=4, min_damage=1, max_damage=3),
                Skill("Veneno", "Envenena al enemigo (daño por turnos)", damage_mult=0.8, effect="debuff"),
                Skill("Evasión", "50% de probabilidad de esquivar el siguiente ataque", effect="evasion"),
                Skill("Asesinato", "Gran daño si esquivaste el ataque anterior", damage_mult=2.5),
            ],
            "Asesino silencioso. Veloz y con ataques rápidos.",
            passives=[
                Passive("Golpe Crítico", "+5% chance de crítico", "crit_bonus", value=5),
                Passive("Evasión Natural", "+10% chance de evasión", "evasion_bonus", value=10),
                Passive("Instinto Asesino", "+20% daño cuando el enemigo tiene < 25% HP", "execute_bonus", value=20, trigger_threshold=25),
            ]
        )
        
    def _get_defense_skill(self) -> Skill:
        return Skill(
            name="Sombra",
            description="50% probabilidad de esquivar",
            defense_boost=5
        )


class Cleric(CharacterClass):
    def __init__(self):
        super().__init__(
            "warlock", "Brujo",
            BASE_STATS["warlock"],
            [
                Skill("Maldición", "Aplica una maldición aleatoria al enemigo", effect="curse", hp_cost=8),
                Skill("Explosión Maldita", "Daño basado en maldiciones del enemigo", damage_mult=1.0, effect="cursed_explosion", hp_cost=10),
                Skill("Consumir Maldiciones", "Consume maldiciones del enemigo para obtener beneficios", effect="consume_curses", hp_cost=5),
                Skill("Toque Vampírico", "Roba vida del enemigo", damage_mult=1.2, effect="life_steal"),
            ],
            "Maestro de las artes oscuras. Usa su vida para lanzar hechizos.",
            passives=[
                Passive("Toque Vampírico", "Restaura 2 HP al usar habilidad", "lifesteal_passive", value=2),
                Passive("Coste Reducido", "-15% costo de habilidades", "skill_discount", value=15),
                Passive("Resistencia Oscura", "+10% de reducción de daño cuando HP < 40%", "damage_reduction", value=10, trigger_threshold=40),
            ]
        )
        
    def _get_defense_skill(self) -> Skill:
        return Skill(
            name="Protección Divina",
            description="+7 DEF y cura 10 HP",
            defense_boost=7,
            heal_amount=10
        )


CLASSES: Dict[str, CharacterClass] = {
    "warrior": Warrior(),
    "mage": Mage(),
    "rogue": Rogue(),
    "warlock": Cleric(),
}


@dataclass
class Equipment:
    """Sistema de equipamiento del jugador"""
    weapon: Optional[Any] = None
    armor: Optional[Any] = None
    accessory_1: Optional[Any] = None
    accessory_2: Optional[Any] = None
    
    def get_total_bonus(self) -> Dict[str, int]:
        """Calcula el bonus total del equipamiento"""
        bonus = {"atk": 0, "def": 0, "hp": 0}
        
        for item in [self.weapon, self.armor, self.accessory_1, self.accessory_2]:
            if item:
                bonus["atk"] += item.stats.get("atk", 0)
                bonus["def"] += item.stats.get("def", 0)
                bonus["hp"] += item.stats.get("hp", 0)
        
        return bonus
    
    def equip_item(self, item: Any, slot: str) -> Optional[Any]:
        """Equipa un item, retorna el item anterior si existía"""
        if slot == "weapon":
            old = self.weapon
            self.weapon = item
        elif slot == "armor":
            old = self.armor
            self.armor = item
        elif slot == "accessory_1":
            old = self.accessory_1
            self.accessory_1 = item
        elif slot == "accessory_2":
            old = self.accessory_2
            self.accessory_2 = item
        else:
            return None
        
        return old
    
    def unequip_item(self, slot: str) -> Optional[Any]:
        """Desequipa un item"""
        return self.equip_item(None, slot)


class Player:
    """
    Clase principal del jugador
    """
    
    def __init__(self, name: str, class_id: str):
        self.name = name
        self.class_id = class_id
        self.player_class = CLASSES[class_id]
        
        # Stats base
        self.max_hp = self.player_class.base_stats["hp"]
        self.current_hp = self.max_hp
        self.base_atk = self.player_class.base_stats["atk"]
        self.base_def = self.player_class.base_stats["def"]
        
        # Stats derivados (se calculan con equipamiento)
        self._bonus_atk = 0
        self._bonus_def = 0
        self._bonus_hp = 0
        
        # Mana (para magos) / Concentración (para guerreros)
        self.max_mana = 50
        self.current_mana = self.max_mana
        
        # Concentración (guerrero) - máximo 10
        self.max_concentration = 10
        self.current_concentration = 0
        self.concentration_ready = False
        
        # Nivel y XP
        self.level = 1
        self.xp = 0
        self.xp_to_next_level = 100
        
        # Oro
        self.gold = 0
        
        # Inventario y equipamiento
        self.inventory: List[Any] = []
        self.equipment = Equipment()
        
        # Equipamiento inicial según la clase
        self._give_starting_equipment(class_id)
        
        # Estado de combate
        self.is_defending = False
        self.defense_boost = 0
        self.attack_boost = 0
        self.reflect_percent = 0  # Porcentaje de daño reflejado (escudo repelente)
        self.evasion_chance = 0  # Probabilidad de esquivar (pícaro)
        self.buffs: Dict[str, int] = {}  # buff_name: turns remaining
        self.status_effects: Dict[str, int] = {}  # effect: turns remaining
        
        # Cooldown de habilidades
        self.skill_cooldowns: Dict[str, int] = {}
    
    def _give_starting_equipment(self, class_id: str):
        """Da equipamiento inicial según la clase"""
        from src.entities.item import ItemGenerator
        
        # Generar items básicos aleatorios de nivel 1
        weapon = ItemGenerator.generate_random_equipment(1)
        armor = ItemGenerator.generate_random_equipment(1)
        
        # Equipar
        self.equipment.weapon = weapon
        self.equipment.armor = armor
        
        # Actualizar stats
        self.update_stats_from_equipment()
    
    @property
    def attack(self) -> int:
        return self.base_atk + self._bonus_atk + self.attack_boost
    
    @property
    def defense(self) -> int:
        return self.base_def + self._bonus_def + self.defense_boost
    
    @property
    def effective_max_hp(self) -> int:
        return self.max_hp + self._bonus_hp
    
    def update_stats_from_equipment(self) -> None:
        """Actualiza stats basado en equipamiento"""
        bonus = self.equipment.get_total_bonus()
        self._bonus_atk = bonus["atk"]
        self._bonus_def = bonus["def"]
        self._bonus_hp = bonus["hp"]
    
    def take_damage(self, damage: int) -> int:
        """Aplica daño al jugador, retorna daño real recibido"""
        actual_damage = max(MIN_DAMAGE, damage)
        self.current_hp = max(0, self.current_hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """Cura al jugador, retorna cantidad curada"""
        old_hp = self.current_hp
        self.current_hp = min(self.effective_max_hp, self.current_hp + amount)
        return self.current_hp - old_hp
    
    def use_mana(self, amount: int) -> bool:
        """Usa mana, retorna True si tiene suficiente"""
        if self.current_mana >= amount:
            self.current_mana -= amount
            return True
        return False
    
    def restore_mana(self, amount: int) -> int:
        """Restaura mana"""
        old_mana = self.current_mana
        self.current_mana = min(self.max_mana, self.current_mana + amount)
        return self.current_mana - old_mana
    
    def add_concentration(self) -> bool:
        """Añade +1 de concentración. Retorna True si alcanza el máximo"""
        if self.current_concentration < self.max_concentration:
            self.current_concentration += 1
            if self.current_concentration >= self.max_concentration:
                self.concentration_ready = True
                return True
        return False
    
    def consume_concentration(self) -> bool:
        """Consume la concentración acumulada. Retorna True si estaba lista"""
        if self.concentration_ready:
            self.current_concentration = 0
            self.concentration_ready = False
            return True
        return False
    
    def reset_concentration(self) -> None:
        """Reinicia la concentración"""
        self.current_concentration = 0
        self.concentration_ready = False
    
    def add_xp(self, amount: int) -> List[int]:
        """Añade XP y retorna lista de niveles gained"""
        levels_gained = []
        self.xp += amount
        
        while self.xp >= self.xp_to_next_level:
            self.xp -= self.xp_to_next_level
            self.level_up()
            levels_gained.append(self.level)
        
        return levels_gained
    
    def level_up(self) -> None:
        """Sube de nivel"""
        self.level += 1
        self.xp_to_next_level = int(self.xp_to_next_level * 1.5)
        
        # Mejora de stats por nivel
        self.max_hp += 10
        self.current_hp = self.effective_max_hp
        self.base_atk += 2
        self.base_def += 1
        self.max_mana += 5
        self.current_mana = self.max_mana
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def start_turn(self) -> None:
        """Inicia turno de combate"""
        # Resetear estados que duran un turno
        self.evasion_chance = 0
        
        # Reducir duración de buffs activos
        for buff in list(self.buffs.keys()):
            self.buffs[buff] -= 1
            if self.buffs[buff] <= 0:
                del self.buffs[buff]
        
        # Aplicar buffs activos - Guerrero
        if "furia" in self.buffs:
            self.attack_boost = 5
        else:
            self.attack_boost = 0
            
        if "escudo" in self.buffs:
            self.is_defending = True
            self.defense_boost = 15
            self.reflect_percent = 0
        elif "escudo_rep" in self.buffs:
            # Escudo repelente del mago
            self.is_defending = True
            self.defense_boost = 10
            self.reflect_percent = 50
        elif "maldicion_proteccion" in self.buffs:
            # Buff de consumir maldición DEF del brujo
            self.is_defending = True
            self.defense_boost = 5
        else:
            self.is_defending = False
            self.defense_boost = 0
            self.reflect_percent = 0
        
        # Aplicar buff de ataque del brujo
        if "maldicion_fuerza" in self.buffs:
            self.attack_boost = 5
        
        # Reducir cooldowns
        for skill in list(self.skill_cooldowns.keys()):
            self.skill_cooldowns[skill] -= 1
            if self.skill_cooldowns[skill] <= 0:
                del self.skill_cooldowns[skill]
        
        # Reducir efectos de estado
        for effect in list(self.status_effects.keys()):
            self.status_effects[effect] -= 1
            if self.status_effects[effect] <= 0:
                del self.status_effects[effect]
    
    def use_skill(self, skill_index: int) -> tuple:
        """Usa una habilidad, retorna (success, message, effect)"""
        if skill_index < 0 or skill_index >= len(self.player_class.skills):
            return False, "Habilidad inválida", None
        
        skill = self.player_class.skills[skill_index]
        
        # Verificar cooldown
        if skill.name in self.skill_cooldowns:
            return False, f"{skill.name} en cooldown ({self.skill_cooldowns[skill.name]} turnos)", None
        
        # Verificar mana
        if skill.mana_cost > 0 and not self.use_mana(skill.mana_cost):
            return False, "No tienes suficiente mana", None
        
        # Verificar hp_cost (brujo)
        if skill.hp_cost > 0 and self.current_hp <= skill.hp_cost:
            return False, "No tienes suficiente vida", None
        
        # Consumir HP si tiene coste
        if skill.hp_cost > 0:
            self.current_hp -= skill.hp_cost
        
        # Aplicar cooldown
        if skill.cooldown > 0:
            self.skill_cooldowns[skill.name] = skill.cooldown
        
        return True, skill, skill.effect
    
    def get_skills_info(self) -> List[Dict[str, Any]]:
        """Retorna información de todas las habilidades"""
        info = []
        for i, skill in enumerate(self.player_class.skills):
            cooldown = self.skill_cooldowns.get(skill.name, 0)
            info.append({
                "index": i,
                "name": skill.name,
                "description": skill.description,
                "damage_mult": skill.damage_mult,
                "mana_cost": skill.mana_cost,
                "cooldown": cooldown,
                "on_cooldown": cooldown > 0
            })
        return info
    
    def add_item(self, item: Any) -> bool:
        """Añade item al inventario"""
        if len(self.inventory) < INVENTORY_MAX_SLOTS:
            self.inventory.append(item)
            return True
        return False
    
    def remove_item(self, item: Any) -> bool:
        """Remueve item del inventario"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa el jugador a diccionario"""
        from src.entities.item import Item
        
        def serialize_item(item):
            if item is None:
                return None
            if hasattr(item, 'to_dict') and callable(item.to_dict):
                try:
                    return item.to_dict()
                except:
                    pass
            if hasattr(item, 'id') and hasattr(item, 'name') and hasattr(item, 'item_type'):
                return {
                    "id": str(getattr(item, 'id', '')),
                    "name": str(getattr(item, 'name', 'Unknown')),
                    "item_type": str(getattr(item, 'item_type', '')),
                    "rarity": str(getattr(item, 'rarity', 'common')),
                    "description": str(getattr(item, 'description', '')),
                    "stats": dict(getattr(item, 'stats', {})),
                    "value": int(getattr(item, 'value', 0)),
                    "stackable": bool(getattr(item, 'stackable', False)),
                    "max_stack": int(getattr(item, 'max_stack', 1)),
                }
            return {"name": "unknown_item"}
        
        return {
            "name": self.name,
            "class_id": self.class_id,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "max_mana": self.max_mana,
            "current_mana": self.current_mana,
            "base_atk": self.base_atk,
            "base_def": self.base_def,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next_level": self.xp_to_next_level,
            "gold": self.gold,
            "inventory": [serialize_item(item) for item in self.inventory],
            "equipment": {
                "weapon": serialize_item(self.equipment.weapon),
                "armor": serialize_item(self.equipment.armor),
                "accessory_1": serialize_item(self.equipment.accessory_1),
                "accessory_2": serialize_item(self.equipment.accessory_2),
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Player':
        """Deserializa el jugador desde diccionario"""
        player = cls(data["name"], data["class_id"])
        player.max_hp = data["max_hp"]
        player.current_hp = data["current_hp"]
        player.max_mana = data["max_mana"]
        player.current_mana = data["current_mana"]
        player.base_atk = data["base_atk"]
        player.base_def = data["base_def"]
        player.level = data["level"]
        player.xp = data["xp"]
        player.xp_to_next_level = data["xp_to_next_level"]
        player.gold = data["gold"]
        
        # Cargar items del inventario
        from src.entities.item import Item
        player.inventory = [Item.from_dict(item_data) for item_data in data.get("inventory", [])]
        
        # Cargar equipamiento
        equip_data = data.get("equipment", {})
        if equip_data.get("weapon"):
            player.equipment.weapon = Item.from_dict(equip_data["weapon"])
        if equip_data.get("armor"):
            player.equipment.armor = Item.from_dict(equip_data["armor"])
        if equip_data.get("accessory_1"):
            player.equipment.accessory_1 = Item.from_dict(equip_data["accessory_1"])
        if equip_data.get("accessory_2"):
            player.equipment.accessory_2 = Item.from_dict(equip_data["accessory_2"])
        
        player.update_stats_from_equipment()
        return player
