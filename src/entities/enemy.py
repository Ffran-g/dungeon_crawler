"""
Módulo de Enemigos - Tipos y jerarquía
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import random

from src.core.constants import *


@dataclass
class EnemyType:
    """Define un tipo de enemigo"""
    name: str
    base_hp: int
    base_atk: int
    base_def: int
    xp_reward: int
    gold_reward: int
    enemy_type: str  # basic, elite, boss
    abilities: List[str] = None
    
    def __post_init__(self):
        if self.abilities is None:
            self.abilities = []


# Definición de tipos de enemigos
ENEMY_TEMPLATES: Dict[str, EnemyType] = {
    # Enemigos básicos piso 1-2
    "goblin": EnemyType("Goblin", 30, 8, 2, 10, 4, ENEMY_TYPE_BASIC),
    "rat_giant": EnemyType("Rata Gigante", 35, 10, 1, 12, 5, ENEMY_TYPE_BASIC),
    "skeleton": EnemyType("Esqueleto", 40, 12, 3, 15, 6, ENEMY_TYPE_BASIC),
    "orc": EnemyType("Orco", 45, 14, 4, 18, 8, ENEMY_TYPE_BASIC),
    "zombie": EnemyType("Zombi", 50, 10, 5, 20, 10, ENEMY_TYPE_BASIC),
    
    # Enemigos básicos piso 3-4 (versiones fuertes)
    "hobgoblin": EnemyType("Hobgoblin", 55, 16, 5, 25, 12, ENEMY_TYPE_BASIC),
    "rat_mutant": EnemyType("Rata Mutante", 50, 14, 3, 22, 10, ENEMY_TYPE_BASIC),
    
    # Enemigos básicos piso 5-6 (nuevos)
    "spider_giant": EnemyType("Araña Gigante", 45, 18, 2, 22, 12, ENEMY_TYPE_BASIC),
    "wraith": EnemyType("Espectro", 35, 20, 1, 25, 15, ENEMY_TYPE_BASIC),
    "ogre": EnemyType("Ogro", 70, 18, 6, 30, 15, ENEMY_TYPE_BASIC),
    "harpy": EnemyType("Arpía", 40, 22, 2, 28, 18, ENEMY_TYPE_BASIC),
    
    # Enemigos elite
    "orc_berserker": EnemyType("Orco Berserker", 80, 18, 6, 40, 15, ENEMY_TYPE_ELITE, ["rage"]),
    "troll": EnemyType("Trol", 100, 20, 8, 50, 18, ENEMY_TYPE_ELITE, ["regen"]),
    "necromancer": EnemyType("Nigromante", 70, 22, 4, 45, 20, ENEMY_TYPE_ELITE, ["life_drain", "summon"]),
    "vampire": EnemyType("Vampiro", 85, 24, 5, 55, 25, ENEMY_TYPE_ELITE, ["life_steal"]),
    
    # Bosses
    "dragon": EnemyType("Dragón Ancianos", 150, 25, 8, 150, 50, ENEMY_TYPE_BOSS, 
                        ["fire_breath", "fly", "enrage"]),
    "lich": EnemyType("Lich Señor", 120, 22, 6, 120, 40, ENEMY_TYPE_BOSS,
                      ["dark_magic", "summon_undead", "enrage"]),
    "demon": EnemyType("Demonio Infernal", 140, 28, 7, 140, 45, ENEMY_TYPE_BOSS,
                       ["hell_fire", "teleport", "enrage"]),
}


class Enemy:
    """
    Clase base para todos los enemigos
    """
    
    def __init__(self, enemy_template: EnemyType, floor: int = 1, 
                 difficulty_mult: float = 1.0):
        self.template = enemy_template
        self.name = enemy_template.name
        
        # Stats escalados por piso y dificultad
        self.floor = floor
        self.difficulty_mult = difficulty_mult
        
        self.max_hp = int(enemy_template.base_hp * self._get_hp_mult())
        self.current_hp = self.max_hp
        self._base_atk = int(enemy_template.base_atk * self._get_stat_mult())
        self._base_def = int(enemy_template.base_def * self._get_stat_mult())
        
        # Recompensas
        self.xp_reward = int(enemy_template.xp_reward * self._get_reward_mult())
        self.gold_reward = int(enemy_template.gold_reward * self._get_reward_mult())
        
        # Tipo
        self.enemy_type = enemy_template.enemy_type
        
        # Habilidades especiales
        self.abilities = enemy_template.abilities.copy() if enemy_template.abilities else []
        
        # Estado de combate
        self.is_defending = False
        self.defense_boost = 0
        self.status_effects: Dict[str, int] = {}
        
        # Contador de stack del Brujo
        self.warlock_stack = 0
        
        # Boss specific
        self.boss_phase = 1
        self.max_phases = 3 if self.enemy_type == ENEMY_TYPE_BOSS else 1
        self.original_name = enemy_template.name  # Guardar nombre original para sprite
    
    def _get_hp_mult(self) -> float:
        """Calcula multiplicador de HP basado en piso"""
        base = 1.0 + (self.floor - 1) * 0.15
        return base * self.difficulty_mult
    
    def _get_stat_mult(self) -> float:
        """Calcula multiplicador de stats basado en piso"""
        base = 1.0 + (self.floor - 1) * 0.1
        return base * self.difficulty_mult
    
    def _get_reward_mult(self) -> float:
        """Calcula multiplicador de recompensas"""
        return 1.0 + (self.floor - 1) * 0.2
    
    def take_damage(self, damage: int) -> int:
        """Aplica daño, retorna daño real"""
        actual = max(MIN_DAMAGE, damage)
        self.current_hp = max(0, self.current_hp - actual)
        
        # Check boss phase change
        if self.enemy_type == ENEMY_TYPE_BOSS:
            hp_percent = self.current_hp / self.max_hp
            if hp_percent <= 0.66 and self.boss_phase == 1:
                self.boss_phase = 2
            elif hp_percent <= 0.33 and self.boss_phase == 2:
                self.boss_phase = 3
                self._enrage()
        
        return actual
    
    def _enrage(self) -> None:
        """Boss entra en fase de enraged"""
        self._base_atk = int(self._base_atk * 1.3)
        self.name = f"{self.template.name} (Enfurecido)"
    
    def heal(self, amount: int) -> int:
        """Cura al enemigo"""
        old = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        return self.current_hp - old
    
    def is_alive(self) -> bool:
        return self.current_hp > 0
    
    def start_turn(self) -> List[str]:
        """Inicia turno, retorna mensajes de efectos"""
        messages = []
        self.is_defending = False
        self.defense_boost = 0
        
        # Aplicar efectos de estado (veneno)
        if "poison" in self.status_effects:
            poison_damage = 5  # Daño base por veneno
            self.current_hp = max(0, self.current_hp - poison_damage)
            messages.append(f"El {self.name} recibe {poison_damage} de daño por veneno.")
        
        # Reducir efectos de estado
        for effect in list(self.status_effects.keys()):
            self.status_effects[effect] -= 1
            if self.status_effects[effect] <= 0:
                del self.status_effects[effect]
        
        return messages
    
    @property
    def defense(self) -> int:
        defense = self._base_def + self.defense_boost
        if "def_down" in self.status_effects:
            defense -= 3
        return max(0, defense)
    
    @property
    def atk(self) -> int:
        attack = self._base_atk
        if "atk_down" in self.status_effects:
            attack -= 3
        return max(1, attack)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serializa a diccionario"""
        return {
            "template_id": self.template.name.lower().replace(" ", "_"),
            "floor": self.floor,
            "difficulty_mult": self.difficulty_mult,
            "current_hp": self.current_hp,
            "boss_phase": self.boss_phase,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Enemy':
        """Deserializa desde diccionario"""
        template_id = data["template_id"]
        template = ENEMY_TEMPLATES.get(template_id)
        if not template:
            template = ENEMY_TEMPLATES["goblin"]
        
        enemy = cls(template, data["floor"], data["difficulty_mult"])
        enemy.current_hp = data["current_hp"]
        enemy.boss_phase = data.get("boss_phase", 1)
        return enemy


class EnemyFactory:
    """
    Factory para crear enemigos con generación procedural
    """
    
    @staticmethod
    def create_basic_enemy(floor: int, difficulty: float = 1.0) -> List[Enemy]:
        """Crea un enemigo básico aleatorio según el piso"""
        
        # Seleccionar plantillas según el piso
        if floor <= 2:
            # Piso 1-2: enemigos básicos originales
            basic_templates = [
                t for t in ENEMY_TEMPLATES.values() 
                if t.enemy_type == ENEMY_TYPE_BASIC 
                and t.name in ["Goblin", "Rata Gigante", "Esqueleto", "Orco", "Zombi"]
            ]
        elif floor <= 4:
            # Piso 3-4: versiones fuertes
            basic_templates = [
                t for t in ENEMY_TEMPLATES.values() 
                if t.enemy_type == ENEMY_TYPE_BASIC 
                and t.name in ["Hobgoblin", "Rata Mutante", "Orco"]
            ]
        else:
            # Piso 5-6: nuevos enemigos
            basic_templates = [
                t for t in ENEMY_TEMPLATES.values() 
                if t.enemy_type == ENEMY_TYPE_BASIC 
                and t.name in ["Araña Gigante", "Espectro", "Ogro", "Arpía"]
            ]
        
        template = random.choice(basic_templates)
        
        # Goblin, Rata Gigante, Hobgoblin, Rata Mutante aparecen en grupos de 2
        if template.name in ["Goblin", "Rata Gigante", "Hobgoblin", "Rata Mutante"]:
            enemies = []
            for i in range(2):
                enemy = Enemy(template, floor, difficulty)
                enemy.name = f"{template.name} {i+1}"
                enemies.append(enemy)
            return enemies
        
        # Orco aparece en pareja en piso 3-4
        if floor >= 3 and floor <= 4 and template.name == "Orco":
            enemies = []
            for i in range(2):
                enemy = Enemy(template, floor, difficulty)
                enemy.name = f"Orco {i+1}"
                enemies.append(enemy)
            return enemies
        
        return [Enemy(template, floor, difficulty)]
    
    @staticmethod
    def create_elite_enemy(floor: int, difficulty: float = 1.0) -> List[Enemy]:
        """Crea un enemigo elite aleatorio"""
        elite_templates = [t for t in ENEMY_TEMPLATES.values() 
                         if t.enemy_type == ENEMY_TYPE_ELITE]
        template = random.choice(elite_templates)
        return [Enemy(template, floor, difficulty)]
    
    @staticmethod
    def create_boss(floor: int, difficulty: float = 1.0) -> List[Enemy]:
        """Crea un boss aleatorio"""
        boss_templates = [t for t in ENEMY_TEMPLATES.values() 
                         if t.enemy_type == ENEMY_TYPE_BOSS]
        template = random.choice(boss_templates)
        return [Enemy(template, floor, difficulty)]
    
    @staticmethod
    def create_enemy_by_type(enemy_type: str, floor: int, 
                            difficulty: float = 1.0) -> List[Enemy]:
        """Crea un enemigo del tipo especificado"""
        if enemy_type == ENEMY_TYPE_BASIC:
            return EnemyFactory.create_basic_enemy(floor, difficulty)
        elif enemy_type == ENEMY_TYPE_ELITE:
            return EnemyFactory.create_elite_enemy(floor, difficulty)
        elif enemy_type == ENEMY_TYPE_BOSS:
            return EnemyFactory.create_boss(floor, difficulty)
        else:
            return EnemyFactory.create_basic_enemy(floor, difficulty)
