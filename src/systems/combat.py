"""
Sistema de Combate - Lógica de combate por turnos
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import random

from src.entities.player import Player
from src.entities.enemy import Enemy
from src.entities.item import ItemGenerator
from src.core.constants import *


class CombatAction:
    """Representa una acción en combate"""

    # Tipos de acción
    ATTACK = "attack"
    SKILL = "skill"
    DEFEND = "defend"
    ITEM = "item"
    RUN = "run"

    def __init__(self, action_type: str, source: Any, target: Any = None,
                 data: Optional[Dict[str, Any]] = None):
        self.action_type = action_type
        self.source = source
        self.target = target
        self.data = data or {}
        self.damage_dealt = 0
        self.heal_amount = 0
        self.messages: List[str] = []
        self.success = True


@dataclass
class CombatLog:
    """Registro de eventos del combate"""
    messages: List[str] = None

    def __post_init__(self):
        if self.messages is None:
            self.messages = []

    def add(self, message: str):
        """Añade un mensaje al log"""
        self.messages.append(message)
        # Mantener solo los últimos 50 mensajes
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]

    def get_recent(self, count: int = 10) -> List[str]:
        """Retorna los últimos n mensajes"""
        return self.messages[-count:]


class CombatSystem:
    """
    Sistema de combate por turnos
    """

    def __init__(self, player: Player, enemies: List[Enemy], can_flee: bool = True):
        self.player = player
        self.enemies = enemies if enemies else []
        self.target_index = 0  # Índice del enemigo objetivo actual
        self.log = CombatLog()
        self.turn_count = 1
        self.combat_over = False
        self.victory = False
        self.last_action: Optional[CombatAction] = None
        self.pending_actions: List[CombatAction] = []
        self.can_flee = can_flee  # Indica si se puede huir del combate
        
        # Contador de veces que se usa Golpe (para reducir stun chance)
        self.golpe_uses = 0
        
        # Flag para rastrear si el jugador esquivó el último ataque (para Asesinato)
        self.player_dodged_last_attack = False
        
        # Flag para diferir el turno del enemigo (para delay visual)
        self.enemy_turn_delayed = False
        
        # Determinar quién ataca primero basado en velocidad
        self.player_turn = self.get_turn_order()

        # Iniciar combate
        if len(self.enemies) == 1:
            self.log.add(f"¡Combate iniciado contra {self.enemies[0].name}!")
        else:
            enemy_names = ", ".join([e.name for e in self.enemies])
            self.log.add(f"¡Combate iniciado contra {enemy_names}!")

        # Si el enemigo ataca primero, ejecutar su turno
        if not self.player_turn and self.enemies:
            self._process_enemy_turn()

    @property
    def enemy(self) -> Optional[Enemy]:
        """Compatibilidad con código anterior - retorna el enemigo objetivo actual"""
        if 0 <= self.target_index < len(self.enemies):
            return self.enemies[self.target_index]
        return self.enemies[0] if self.enemies else None

    def get_alive_enemies(self) -> List[Enemy]:
        """Retorna lista de enemigos vivos"""
        return [e for e in self.enemies if e.is_alive()]
    
    def _update_target_if_dead(self):
        """Actualiza el objetivo si el enemigo actual está muerto"""
        if self.enemies:
            # Verificar si el enemigo objetivo está muerto o si es None
            current_enemy = self.enemy if self.target_index < len(self.enemies) else None
            if current_enemy is None or not current_enemy.is_alive():
                alive = self.get_alive_enemies()
                if alive:
                    for i, e in enumerate(self.enemies):
                        if e.is_alive():
                            self.target_index = i
                            break

    def get_turn_order(self) -> bool:
        """
        El jugador siempre ataca primero
        """
        return True

    def _process_enemy_turn(self):
        """Procesa el turno de cada enemigo vivo"""
        if not self.combat_over and not self.player_turn:
            alive_enemies = self.get_alive_enemies()
            
            # Procesar turno de cada enemigo vivo
            for enemy in alive_enemies:
                if self.combat_over or not enemy.is_alive():
                    continue
                    
                # Guardar objetivo actual
                original_target = self.target_index
                self.target_index = self.enemies.index(enemy)
                
                # Verificar si el enemigo está aturdido
                if hasattr(enemy, 'status_effects') and "stunned" in enemy.status_effects:
                    self.log.add(f"El {enemy.name} está aturdido y no puede actuar!")
                    enemy.status_effects["stunned"] -= 1
                    if enemy.status_effects["stunned"] <= 0:
                        del enemy.status_effects["stunned"]
                    continue
                
                # Aplicar efectos de estado (veneno) al inicio del turno
                messages = enemy.start_turn()
                for msg in messages:
                    self.log.add(msg)
                
                # Verificar si murió por veneno
                if not enemy.is_alive():
                    continue
                
                # Turno del enemigo
                enemy_action = self.enemy_turn()
                self.pending_actions.append(enemy_action)
                
                # Si el jugador murió, terminar
                if not self.player.is_alive():
                    self._handle_defeat(enemy_action)
                    return
            
            # Restaurar índice de objetivo
            self.target_index = 0
            
            # Solo pasar al turno del jugador si el combate no terminó
            if not self.combat_over:
                self.next_turn()

    def _end_player_action(self):
        """Finaliza la acción del jugador y procesa el turno del enemigo si corresponde"""
        if not self.combat_over:
            # Actualizar objetivo si el actual está muerto
            self._update_target_if_dead()
            
            # Cambiar al turno del enemigo (sin aumentar turn_count todavía)
            self.player_turn = False
            
            # Si el delay está activado, no ejecutar el turno del enemigo todavía
            if self.enemy_turn_delayed:
                return
            
            # Ejecutar turno del enemigo automáticamente
            self._process_enemy_turn()
    
    def execute_delayed_enemy_turn(self):
        """Ejecuta el turno del enemigo que fue diferido"""
        if self.enemy_turn_delayed and not self.combat_over:
            self.enemy_turn_delayed = False
            self._process_enemy_turn()

    def player_attack(self, skill_index: int = -1) -> CombatAction:
        """
        Jugador ataca al enemigo
        skill_index: -1 = ataque básico, 0-3 = habilidad
        """
        # Limpiar acciones pendientes al inicio del turno del jugador
        self.pending_actions = []
        
        # Aplicar passivas al inicio del turno
        self._apply_passives_start_turn()
        
        # Verificar y actualizar objetivo si es necesario
        alive = self.get_alive_enemies()
        if not alive:
            action = CombatAction(CombatAction.ATTACK, self.player, None)
            action.success = False
            action.messages.append("No hay enemigos vivos.")
            return action
        self._update_target_if_dead()

        action = CombatAction(CombatAction.ATTACK, self.player, self.enemy)

        if not self.player_turn:
            action.success = False
            action.messages.append("No es tu turno.")
            return action

        # Verificar si tiene concentración máxima (ejecutar acción 2 veces) - solo guerrero
        double_attack = False
        if (hasattr(self.player, 'class_id') and self.player.class_id == "warrior" and 
            hasattr(self.player, 'concentration_ready') and self.player.concentration_ready):
            double_attack = True
            self.player.consume_concentration()
            self.log.add("¡CONCENTRACIÓN! ¡ATAQUE DOBLE!")

        # Obtener información de la habilidad
        if skill_index == -1:
            # Ataque básico
            damage = self._calculate_damage(
                self.player.attack,
                self.enemy.defense,
                self.enemy.is_defending,
                getattr(self.enemy, 'defense_boost', 0)
            )
            is_crit = self._check_critical()

            if is_crit:
                damage = int(damage * CRITICAL_HIT_MULTIPLIER)
                action.messages.append("¡Golpe crítico!")

            actual_damage = self.enemy.take_damage(damage)
            action.damage_dealt = actual_damage
            action.messages.append(f"Atacas al {self.enemy.name} por {actual_damage} de daño.")
            
            # Aplicar passivas de robo de vida
            self._apply_passives_on_damage(actual_damage)
            
            # Si el enemigo murió, actualizar al siguiente objetivo vivo
            if not self.enemy.is_alive():
                self._handle_victory(action)
                # Si no todos los enemigos están muertos, actualizar objetivo
                if not self.combat_over:
                    self._update_target_if_dead()
                    alive = self.get_alive_enemies()
                    if alive:
                        action.messages.append(f"¡{self.enemy.name} derrotado! Quedan {len(alive)} enemigo(s).")
            
            # Añadir concentración si hace daño
            if actual_damage > 0:
                self._add_concentration()

        else:
            # Validar índice de habilidad
            if skill_index < 0 or skill_index >= len(self.player.player_class.skills):
                action.success = False
                action.messages.append("Habilidad inválida.")
                self._add_messages_to_log(action)
                return action

            # Usar habilidad
            result = self.player.use_skill(skill_index)

            # Verificar que el resultado sea válido
            if not isinstance(result, tuple) or len(result) != 3:
                action.success = False
                action.messages.append("Error al usar habilidad.")
                self._add_messages_to_log(action)
                return action

            success, skill_or_msg, effect = result

            if not success:
                action.success = False
                action.messages.append(skill_or_msg)
                self._add_messages_to_log(action)
                return action

            skill = skill_or_msg

            if effect == "damage":
                base_damage = int(self.player.attack * skill.damage_mult)
                
                # Aplicar bonus de Asesinato si el jugador esquivó el último ataque
                if skill.name == "Asesinato" and self.player_dodged_last_attack:
                    base_damage = int(base_damage * 1.5)
                    action.messages.append("¡Asesinato! Esquivaste su ataque, daño aumentado.")
                    self.player_dodged_last_attack = False  # Consumir el bonus
                
                # Aplicar defensa del enemigo a las habilidades también
                damage = self._calculate_damage(
                    base_damage,
                    self.enemy.defense,
                    self.enemy.is_defending,
                    getattr(self.enemy, 'defense_boost', 0)
                )
                actual_damage = self.enemy.take_damage(damage)
                action.damage_dealt = actual_damage
                action.messages.append(f"Usas {skill.name} contra {self.enemy.name} por {actual_damage} de daño.")
                
                # Añadir concentración si hace daño
                if actual_damage > 0:
                    self._add_concentration()
                
                # Aplicar aturdimiento si la habilidad lo tiene (con probabilidad que baja)
                if skill.stun_chance > 0:
                    # Golpe: probabilidad inicial 75%, baja 15% por cada uso
                    current_stun_chance = skill.stun_chance - (self.golpe_uses * 0.15)
                    current_stun_chance = max(0.15, current_stun_chance)  # Mínimo 15%
                    
                    if random.random() < current_stun_chance:
                        self.enemy.status_effects["stunned"] = 1
                        action.messages.append(f"¡{self.enemy.name} queda aturdido! ({int(current_stun_chance*100)}%)")
                    
                    self.golpe_uses += 1

            elif effect == "heal":
                heal = self.player.heal(skill.heal_amount)
                action.heal_amount = heal
                action.messages.append(f"Usas {skill.name} y te curas {heal} HP.")

            elif effect == "buff":
                # Aplicar buff con duración
                duration = skill.buff_duration + 1  # +1 porque dura este turno + los siguientes
                
                if skill.attack_boost > 0:
                    self.player.buffs["furia"] = duration
                    self.player.attack_boost = skill.attack_boost
                    turns_text = "este turno" if duration == 1 else f"{duration} turnos"
                    action.messages.append(f"Usas {skill.name}. Ataque aumentado +{skill.attack_boost} por {turns_text}.")
                
                if skill.defense_boost > 0:
                    self.player.buffs["escudo"] = duration
                    self.player.is_defending = True
                    self.player.defense_boost = skill.defense_boost
                    if skill.attack_boost == 0:
                        turns_text = "este turno" if duration == 1 else f"{duration} turnos"
                        action.messages.append(f"Usas {skill.name}. Escudo activo por {turns_text}.")

            elif effect == "debuff":
                # Aplicar veneno al enemigo
                poison_damage = int(self.player.attack * 0.3)
                if "poison" not in self.enemy.status_effects:
                    self.enemy.status_effects["poison"] = 3  # 3 turnos de veneno
                else:
                    self.enemy.status_effects["poison"] = 3  # Refrescar
                action.messages.append(f"Usas {skill.name}. {self.enemy.name} queda envenenado por {poison_damage} daño/turno.")

            elif effect == "stun":
                # Aturdimiento (para habilidades que solo stunnan sin daño)
                self.enemy.status_effects["stunned"] = skill.stun_turns
                action.messages.append(f"Usas {skill.name}. {self.enemy.name} queda aturdido por {skill.stun_turns} turno.")

            elif effect == "multihit":
                # Múltiples golpes (misiles arcanos o ráfaga)
                total_damage = 0
                hit_name = "Golpe"
                if hasattr(self.player, 'class_id') and self.player.class_id == "mage":
                    hit_name = "Misil"
                for i in range(skill.multihit_count):
                    hit_damage = random.randint(skill.min_damage, skill.max_damage)
                    actual_hit = self.enemy.take_damage(hit_damage)
                    total_damage += actual_hit
                    action.messages.append(f"{hit_name} {i+1}: {actual_hit} de daño")
                    # Verificar si murió después de cada golpe
                    if not self.enemy.is_alive():
                        break
                action.damage_dealt = total_damage
                action.messages.append(f"Usas {skill.name}. Total: {total_damage} de daño en {skill.multihit_count} impactos.")

            elif effect == "shield":
                # Escudo repelente - reduce daño y lo devuelve
                self.player.is_defending = True
                self.player.defense_boost = skill.defense_boost
                self.player.buffs["escudo_rep"] = 2  # Dura 2 turnos
                self.player.reflect_percent = skill.reflect_percent
                action.messages.append(f"Usas {skill.name}. Escudo activo: -{skill.defense_boost} DEF, {skill.reflect_percent}% daño reflejado.")

            elif effect == "channel":
                # Canalizar - recupera mana
                if hasattr(self.player, 'restore_mana'):
                    restored = self.player.restore_mana(skill.mana_restore)
                    action.messages.append(f"Usas {skill.name}. Recuperas {restored} de Mana.")
                else:
                    action.messages.append(f"Usas {skill.name}. (Tu clase no usa Mana)")

            elif effect == "evasion":
                # Evasión - 50% de esquivar el siguiente ataque
                self.player.evasion_chance = 50
                action.messages.append(f"Usas {skill.name}. 50% de probabilidad de esquivar el siguiente ataque.")

            elif effect == "curse":
                # Maldición - aplica una maldición aleatoria
                curse_type = random.choice(["poison", "atk_down", "def_down", "stunned", "confused"])
                if curse_type == "poison":
                    self.enemy.status_effects["poison"] = 3
                    action.messages.append(f"¡Maldición! {self.enemy.name} queda envenenado.")
                elif curse_type == "atk_down":
                    self.enemy.status_effects["atk_down"] = 3
                    action.messages.append(f"¡Maldición! {self.enemy.name} tiene -3 ATQ por 3 turnos.")
                elif curse_type == "def_down":
                    self.enemy.status_effects["def_down"] = 3
                    action.messages.append(f"¡Maldición! {self.enemy.name} tiene -3 DEF por 3 turnos.")
                elif curse_type == "stunned":
                    self.enemy.status_effects["stunned"] = 1
                    action.messages.append(f"¡Maldición! {self.enemy.name} queda aturdido.")
                elif curse_type == "confused":
                    self.enemy.status_effects["confused"] = 2
                    action.messages.append(f"¡Maldición! {self.enemy.name} está confuse (50% de dañarse a sí mismo).")

            elif effect == "cursed_explosion":
                # Explosión Maldita - daño basado en maldiciones del enemigo
                curse_count = len(self.enemy.status_effects)
                if curse_count == 0:
                    action.messages.append(f"Usas {skill.name}. ¡El enemigo no tiene maldiciones!")
                else:
                    base_damage = int(self.player.attack * skill.damage_mult * curse_count)
                    damage = self._calculate_damage(
                        base_damage,
                        self.enemy.defense,
                        self.enemy.is_defending,
                        getattr(self.enemy, 'defense_boost', 0)
                    )
                    actual_damage = self.enemy.take_damage(damage)
                    action.damage_dealt = actual_damage
                    action.messages.append(f"¡EXPLOSIÓN MALDITA! {curse_count} maldiciones detonan: {actual_damage} de daño.")

            elif effect == "consume_curses":
                # Consumir Maldiciones - beneficios basados en maldiciones del enemigo
                consumed = 0
                atk_debuff = self.enemy.status_effects.get("atk_down", 0)
                def_debuff = self.enemy.status_effects.get("def_down", 0)
                poison_turns = self.enemy.status_effects.get("poison", 0)
                
                # Consumir veneno - daño inmediato
                if poison_turns > 0:
                    poison_damage = poison_turns * 8
                    self.enemy.take_damage(poison_damage)
                    action.messages.append(f"Consumes el veneno: {poison_damage} de daño.")
                    consumed += 1
                
                # Consumir debuff de ATQ - buff de ATQ para el jugador
                if atk_debuff > 0:
                    self.player.buffs["maldicion_fuerza"] = 2
                    self.player.attack_boost = 5
                    action.messages.append(f"Consumes la maldición de ATQ: +5 ATQ para ti.")
                    consumed += 1
                
                # Consumir debuff de DEF - buff de DEF para el jugador
                if def_debuff > 0:
                    self.player.buffs["maldicion_proteccion"] = 2
                    self.player.is_defending = True
                    self.player.defense_boost = 5
                    action.messages.append(f"Consumes la maldición de DEF: +5 DEF para ti.")
                    consumed += 1
                
                # Limpiar las maldiciones consumidas (excepto stunned y confused)
                for key in ["poison", "atk_down", "def_down"]:
                    if key in self.enemy.status_effects:
                        del self.enemy.status_effects[key]
                
                if consumed == 0:
                    action.messages.append(f"Usas {skill.name}. No hay maldiciones para consumir.")

            elif effect == "life_steal":
                # Toque Vampírico - roba vida del enemigo
                base_damage = int(self.player.attack * skill.damage_mult)
                damage = self._calculate_damage(
                    base_damage,
                    self.enemy.defense,
                    self.enemy.is_defending,
                    getattr(self.enemy, 'defense_boost', 0)
                )
                actual_damage = self.enemy.take_damage(damage)
                action.damage_dealt = actual_damage
                
                # Curar al jugador
                heal_amount = int(actual_damage * 0.5)
                actual_heal = self.player.heal(heal_amount)
                action.heal_amount = actual_heal
                action.messages.append(f"Usas {skill.name}. Robas {actual_damage} de daño y te curas {actual_heal} HP.")

            elif effect == "escape":
                # Intentar huir
                return self.player_run()

        # Añadir mensajes al log
        self._add_messages_to_log(action)

        # Verificar si el enemigo murió
        if not self.enemy.is_alive():
            self._handle_victory(action)
            
            # Si no todos los enemigos están muertos, actualizar objetivo
            if not self.combat_over and not self._check_all_enemies_dead():
                self._update_target_if_dead()
                alive = self.get_alive_enemies()
                if alive:
                    action.messages.append(f"¡{self.enemy.name} derrotado! Quedan {len(alive)} enemigo(s).")

        # Si tiene concentración máxima, ejecutar ataque extra
        if double_attack and self.enemy.is_alive():
            # Ejecutar ataque extra
            extra_damage = self._calculate_damage(
                self.player.attack,
                self.enemy.defense,
                self.enemy.is_defending,
                getattr(self.enemy, 'defense_boost', 0)
            )
            extra_actual = self.enemy.take_damage(extra_damage)
            self.log.add(f"¡ATAQUE EXTRA! Atacas al {self.enemy.name} por {extra_actual} de daño.")
            action.damage_dealt += extra_actual
            
            # Verificar si murió por el ataque extra
            if not self.enemy.is_alive():
                alive = self.get_alive_enemies()
                if alive:
                    for i, e in enumerate(self.enemies):
                        if e.is_alive():
                            self.target_index = i
                            break

        self.last_action = action

        # Verificar victoria antes de finalizar el turno
        alive_count = sum(1 for e in self.enemies if e and e.is_alive())
        
        if alive_count == 0:
            # Todos los enemigos muertos - manejar victoria
            self.combat_over = True
            self.victory = True
            gold_gained = sum(e.gold_reward for e in self.enemies if e and not e.is_alive())
            xp_gained = sum(e.xp_reward for e in self.enemies if e and not e.is_alive())
            self.player.gold += gold_gained
            self.player.add_xp(xp_gained)
            enemy_names = [e.name for e in self.enemies if e]
            if len(enemy_names) == 1:
                action.messages.append(f"¡Derrotaste al {enemy_names[0]}!")
            else:
                action.messages.append(f"¡Derrotaste a los enemigos: {', '.join(enemy_names)}!")
            action.messages.append(f"Ganas {gold_gained} oro y {xp_gained} XP.")
            return action

        # Finalizar acción del jugador y procesar turno del enemigo
        self._end_player_action()

        return action

    def player_defend(self) -> CombatAction:
        """Jugador se defiende"""
        # Limpiar acciones pendientes al inicio del turno del jugador
        self.pending_actions = []

        action = CombatAction(CombatAction.DEFEND, self.player)

        if not self.player_turn:
            action.success = False
            action.messages.append("No es tu turno.")
            return action

        defense_skill = self.player.player_class.defense_skill
        self.player.is_defending = True
        self.player.defense_boost = defense_skill.defense_boost

        heal = 0
        if defense_skill.heal_amount:
            heal = self.player.heal(defense_skill.heal_amount)
            action.heal_amount = heal

        action.messages.append(f"Te defendes. {defense_skill.description}")
        if heal > 0:
            action.messages.append(f"Te curas {heal} HP.")

        # Añadir mensajes al log
        self._add_messages_to_log(action)

        self.last_action = action

        # Finalizar acción del jugador y procesar turno del enemigo
        self._end_player_action()

        return action

    def player_use_item(self, item_index: int) -> CombatAction:
        """Jugador usa un objeto"""
        # Limpiar acciones pendientes al inicio del turno del jugador
        self.pending_actions = []

        action = CombatAction(CombatAction.ITEM, self.player)

        if not self.player_turn:
            action.success = False
            action.messages.append("No es tu turno.")
            return action

        # Verificar que el inventario existe
        if not hasattr(self.player, 'inventory') or not self.player.inventory:
            action.success = False
            action.messages.append("No tienes objetos en el inventario.")
            self._add_messages_to_log(action)
            return action

        if item_index < 0 or item_index >= len(self.player.inventory):
            action.success = False
            action.messages.append("Objeto inválido.")
            self._add_messages_to_log(action)
            return action

        item = self.player.inventory[item_index]

        if item.item_type != ITEM_TYPE_CONSUMABLE:
            action.success = False
            action.messages.append("Este objeto no se puede usar en combate.")
            self._add_messages_to_log(action)
            return action

        # Usar el objeto
        used = False

        if "heal" in item.stats:
            heal = self.player.heal(item.stats["heal"])
            action.heal_amount = heal
            action.messages.append(f"Bebes {item.name} y te curas {heal} HP.")
            used = True

        if "mana" in item.stats:
            mana = self.player.restore_mana(item.stats["mana"])
            action.messages.append(f"Bebes {item.name} y restauras {mana} Mana.")
            used = True

        if "cure_poison" in item.stats and item.stats["cure_poison"]:
            if hasattr(self.player, 'status_effects') and "poison" in self.player.status_effects:
                del self.player.status_effects["poison"]
                action.messages.append(f"Usas {item.name} y curas el veneno.")
                used = True

        if used:
            self.player.remove_item(item)
        else:
            action.success = False
            action.messages.append(f"No puedes usar {item.name} aquí.")

        # Añadir mensajes al log
        self._add_messages_to_log(action)

        self.last_action = action

        # Finalizar acción del jugador y procesar turno del enemigo
        self._end_player_action()

        return action

    def player_run(self) -> CombatAction:
        """Jugador intenta huir"""
        # Limpiar acciones pendientes al inicio del turno del jugador
        self.pending_actions = []

        action = CombatAction(CombatAction.RUN, self.player)

        if not self.player_turn:
            action.success = False
            action.messages.append("No es tu turno.")
            return action
        
        # Verificar si se puede huir
        if not self.can_flee:
            action.success = False
            action.messages.append("¡No puedes huir de este combate!")
            self._end_player_action()
            self._add_messages_to_log(action)
            return action

        # 50% de probabilidad de huir
        if random.random() < 0.5:
            # Pérdida de oro por huir
            gold_loss = max(1, int(self.player.gold * 0.1))
            self.player.gold = max(0, self.player.gold - gold_loss)

            self.combat_over = True
            self.victory = False
            action.messages.append(f"¡Escapas! Pero pierdes {gold_loss} de oro.")
        else:
            action.messages.append("¡No puedes escapar!")
            # Si falla el escape, continuar con el turno del enemigo
            self._end_player_action()

        # Añadir mensajes al log
        self._add_messages_to_log(action)

        self.last_action = action
        return action

    def enemy_turn(self) -> CombatAction:
        """
        Turno del enemigo (IA)
        """
        action = CombatAction(CombatAction.ATTACK, self.enemy, self.player)

        # Verificar si el enemigo está aturdido
        if hasattr(self.enemy, 'status_effects') and "stunned" in self.enemy.status_effects:
            action.messages.append(f"El {self.enemy.name} está aturdido y no puede actuar!")
            return action

        # Verificar confusión - 50% de probabilidad de atacarse a sí mismo
        if hasattr(self.enemy, 'status_effects') and "confused" in self.enemy.status_effects:
            if random.random() < 0.5:
                self.log.add(f"¡{self.enemy.name} está confuse y se ataca a sí mismo!")
                confusion_damage = int(self.enemy.atk * 0.5)
                actual_confusion = self.enemy.take_damage(confusion_damage)
                action.messages.append(f"{self.enemy.name} se hace {actual_confusion} de daño a sí mismo.")
                self._add_messages_to_log(action)
                self.last_action = action
                return action

        # IA del enemigo - siempre realiza una acción
        ai_decision = self._get_enemy_ai_decision()

        if ai_decision == "attack":
            # Ataque básico
            damage = self._calculate_damage(
                self.enemy.atk,
                self.player.defense,
                self.player.is_defending,
                getattr(self.player, 'defense_boost', 0)
            )
            
            # Verificar evasión del jugador (Pícaro)
            if hasattr(self.player, 'evasion_chance') and self.player.evasion_chance > 0:
                if random.random() * 100 < self.player.evasion_chance:
                    action.messages.append(f"¡ESQUIVAS el ataque de {self.enemy.name}!")
                    self.player.evasion_chance = 0  # Consumir evasión
                    self.player_dodged_last_attack = True  # Flag para Asesinato
                    self._add_messages_to_log(action)
                    self.last_action = action
                    return action
            
            # Resetear flag de evasión si no esquivó
            self.player_dodged_last_attack = False
            
            is_crit = random.random() < 0.1

            if is_crit:
                damage = int(damage * CRITICAL_HIT_MULTIPLIER)
                action.messages.append("¡Golpe crítico del enemigo!")

            actual_damage = self.player.take_damage(damage)
            action.damage_dealt = actual_damage
            action.messages.append(f"El {self.enemy.name} te ataca: {actual_damage} de daño.")
            
            # Aplicar daño reflejado si tiene escudo repelente
            if actual_damage > 0 and hasattr(self.player, 'reflect_percent') and self.player.reflect_percent > 0:
                reflect_damage = int(actual_damage * self.player.reflect_percent / 100)
                reflect_actual = self.enemy.take_damage(reflect_damage)
                action.messages.append(f"¡Escudo repelente! {self.enemy.name} recibe {reflect_actual} de daño.")
            
            # Añadir concentración si recibe daño
            if actual_damage > 0:
                self._add_concentration()

        elif ai_decision == "defend":
            # El enemigo se defiende
            self.enemy.is_defending = True
            self.enemy.defense_boost = 5
            action.messages.append(f"El {self.enemy.name} se DEFIENDE.")

        elif ai_decision == "skill":
            # El enemigo usa una habilidad especial
            skill_name = random.choice(["Golpe Poderoso", "Ataque Furioso", "Embestida"])
            base_damage = int(self.enemy.atk * 1.5)
            damage = self._calculate_damage(
                base_damage,
                self.player.defense,
                self.player.is_defending,
                getattr(self.player, 'defense_boost', 0)
            )
            
            # Verificar evasión del jugador (Pícaro)
            if hasattr(self.player, 'evasion_chance') and self.player.evasion_chance > 0:
                if random.random() * 100 < self.player.evasion_chance:
                    action.messages.append(f"¡ESQUIVAS el ataque de {self.enemy.name}!")
                    self.player.evasion_chance = 0  # Consumir evasión
                    self.player_dodged_last_attack = True  # Flag para Asesinato
                    self._add_messages_to_log(action)
                    self.last_action = action
                    return action
            
            # Resetear flag de evasión si no esquivó
            self.player_dodged_last_attack = False
            
            actual_damage = self.player.take_damage(damage)
            action.damage_dealt = actual_damage
            action.messages.append(f"El {self.enemy.name} usa {skill_name}: {actual_damage} de daño!")
            
            # Aplicar daño reflejado si tiene escudo repelente
            if actual_damage > 0 and hasattr(self.player, 'reflect_percent') and self.player.reflect_percent > 0:
                reflect_damage = int(actual_damage * self.player.reflect_percent / 100)
                reflect_actual = self.enemy.take_damage(reflect_damage)
                action.messages.append(f"¡Escudo repelente! {self.enemy.name} recibe {reflect_actual} de daño.")

            # Añadir concentración si recibe daño
            if actual_damage > 0:
                self._add_concentration()

        # Añadir mensajes al log
        self._add_messages_to_log(action)

        # Verificar si el jugador murió
        if not self.player.is_alive():
            self._handle_defeat(action)

        self.last_action = action
        return action

    def get_pending_actions(self) -> List[CombatAction]:
        """Retorna y limpia las acciones pendientes (útil para la UI)"""
        actions = self.pending_actions.copy()
        self.pending_actions = []
        return actions

    def _get_enemy_ai_decision(self) -> str:
        """
        IA simple del enemigo - 3 opciones: Atacar, Defender, Habilidad
        """
        hp_percent = self.enemy.current_hp / max(1, self.enemy.max_hp)  # Evitar división por cero
        enemy_type = self.enemy.enemy_type

        # Enemigo básico - principalmente ataca
        if enemy_type == ENEMY_TYPE_BASIC:
            roll = random.random()
            if roll < 0.8:
                return "attack"
            elif roll < 0.9:
                return "defend"
            else:
                return "skill"

        # Enemigo élite - más uso de habilidades
        elif enemy_type == ENEMY_TYPE_ELITE:
            if hp_percent < 0.3:
                # Baja vida - más defensivo
                roll = random.random()
                if roll < 0.4:
                    return "attack"
                elif roll < 0.7:
                    return "defend"
                else:
                    return "skill"
            else:
                roll = random.random()
                if roll < 0.5:
                    return "attack"
                elif roll < 0.7:
                    return "skill"
                else:
                    return "defend"

        # Boss - más agresivo y usa habilidades
        elif enemy_type == ENEMY_TYPE_BOSS:
            if hp_percent < 0.33:
                # Fase enfurecida - muy agresivo
                roll = random.random()
                if roll < 0.6:
                    return "skill"
                elif roll < 0.8:
                    return "attack"
                else:
                    return "defend"
            elif hp_percent < 0.66:
                roll = random.random()
                if roll < 0.5:
                    return "skill"
                elif roll < 0.8:
                    return "attack"
                else:
                    return "defend"
            else:
                roll = random.random()
                if roll < 0.35:
                    return "skill"
                elif roll < 0.7:
                    return "attack"
                else:
                    return "defend"

        return "attack"

    def _calculate_damage(self, attacker_atk: int, defender_def: int,
                         is_defending: bool = False, defense_boost: int = 0) -> int:
        """
        Calcula daño con variación aleatoria

        Args:
            attacker_atk: Ataque del atacante
            defender_def: Defensa del defensor
            is_defending: Si el defensor está en posición defensiva
            defense_boost: Bonus adicional de defensa
        """
        # Validar que los stats no sean negativos
        attacker_atk = max(1, attacker_atk)
        defender_def = max(0, defender_def)
        defense_boost = max(0, defense_boost)

        # Calcular defensa total
        total_defense = defender_def + defense_boost

        # Si está defendiendo, duplicar la defensa efectiva
        if is_defending:
            total_defense = int(total_defense * 2)

        # Fórmula mejorada: daño = ataque * 0.6 - defensa * 0.3
        reduced_defense = int(total_defense * 0.3)
        base_damage = int(attacker_atk * 0.6) - reduced_defense

        # Asegurar daño mínimo del 30% del ataque
        min_damage = int(attacker_atk * 0.3)
        base_damage = max(min_damage, base_damage)

        # Variación ±20%
        variation = random.uniform(0.8, 1.2)

        damage = int(base_damage * variation)

        # Daño mínimo de 1
        return max(1, damage)

    def _check_critical(self) -> bool:
        """Verifica si es golpe crítico incluyendo passivas"""
        crit_chance = CRITICAL_HIT_CHANCE + self._get_passive_bonus("crit_bonus")
        return random.random() < crit_chance
    
    def _add_concentration(self):
        """Añade +1 de concentración al jugador (solo guerrero)"""
        if hasattr(self.player, 'class_id') and self.player.class_id == "warrior":
            if hasattr(self.player, 'add_concentration'):
                reached_max = self.player.add_concentration()
                if reached_max:
                    self.log.add("¡CONCENTRACIÓN MÁXIMA! Tu siguiente ataque se ejecutará 2 veces!")
    
    def _apply_passives_start_turn(self):
        """Aplica efectos de passivas al inicio del turno del jugador"""
        if not hasattr(self.player, 'player_class'):
            return
            
        passives = self.player.player_class.passives
        
        for passive in passives:
            if passive.passive_type == "regen_hp":
                hp_percent = (self.player.current_hp / self.player.effective_max_hp) * 100
                if hp_percent < 100:
                    heal = self.player.heal(passive.value)
                    if heal > 0:
                        self.log.add(f"[PASSIVA] {passive.name}: +{heal} HP")
            
            elif passive.passive_type == "regen_mana":
                if self.player.current_mana < self.player.max_mana:
                    mana_restore = min(passive.value, self.player.max_mana - self.player.current_mana)
                    self.player.current_mana += mana_restore
                    if mana_restore > 0:
                        self.log.add(f"[PASSIVA] {passive.name}: +{mana_restore} MANA")
    
    def _apply_passives_on_damage(self, damage_dealt: int):
        """Aplica efectos de passivas cuando hace daño"""
        if not hasattr(self.player, 'player_class'):
            return
            
        passives = self.player.player_class.passives
        
        for passive in passives:
            if passive.passive_type == "lifesteal_passive":
                heal = min(passive.value, self.player.effective_max_hp - self.player.current_hp)
                if heal > 0:
                    self.player.current_hp += heal
                    self.log.add(f"[PASSIVA] {passive.name}: +{heal} HP robado")
    
    def _apply_passives_on_hit_received(self, damage_received: int):
        """Aplica efectos de passivas cuando recibe daño"""
        if not hasattr(self.player, 'player_class'):
            return
            
        passives = self.player.player_class.passives
        
        for passive in passives:
            if passive.passive_type == "damage_reduction":
                hp_percent = (self.player.current_hp / self.player.effective_max_hp) * 100
                if hp_percent < passive.trigger_threshold:
                    reduction = passive.value
                    self.log.add(f"[PASSIVA] {passive.name}: -{reduction} daño recibido")
    
    def _get_passive_bonus(self, bonus_type: str) -> float:
        """Retorna bonus de passivas para el cálculo de daño/crítico/etc"""
        if not hasattr(self.player, 'player_class'):
            return 0.0
            
        passives = self.player.player_class.passives
        bonus = 0.0
        
        for passive in passives:
            if passive.passive_type == bonus_type:
                if passive.passive_type == "crit_bonus":
                    bonus += passive.value
                elif passive.passive_type == "skill_damage_bonus":
                    bonus += passive.value
                elif passive.passive_type == "evasion_bonus":
                    bonus += passive.value
        
        return bonus / 100.0 if bonus > 0 else 0.0

    def _add_messages_to_log(self, action: CombatAction):
        """Añade los mensajes de una acción al log de combate"""
        for msg in action.messages:
            self.log.add(msg)

    def _check_all_enemies_dead(self) -> bool:
        """Verifica si todos los enemigos están muertos"""
        if not self.enemies:
            return True
        alive_count = 0
        for e in self.enemies:
            if e and e.is_alive():
                alive_count += 1
        return alive_count == 0

    def _handle_victory(self, action: CombatAction):
        """Maneja victoria en combate"""
        # Contar enemigos vivos
        alive_count = 0
        for e in self.enemies:
            if e and e.is_alive():
                alive_count += 1
        
        if alive_count > 0:
            return  # Ainda hay enemigos vivos
        
        self.combat_over = True
        self.victory = True

        # Ya se añadieron las recompensas en player_attack() - solo añadir mensajes extra
        
        # Posibilidad de loot
        if random.random() < 0.3:
            floor = self.enemies[0].floor if self.enemies else 1
            loot = ItemGenerator.generate_random_equipment(floor)
            if self.player.add_item(loot):
                action.messages.append(f"¡Encontraste {loot.name}!")

        # Mostrar mensaje de nivel subido
        # El mensaje de XP ya se añadió en player_attack()

    def _handle_defeat(self, action: CombatAction):
        """Maneja derrota en combate"""
        self.combat_over = True
        self.victory = False
        action.messages.append("¡Has sido derrotado!")
        self.log.add("Derrota en combate.")

    def next_turn(self) -> None:
        """Avanza al siguiente turno"""
        if not self.combat_over:
            self.turn_count += 1

            # Preparar para el turno del siguiente
            self.player_turn = not self.player_turn

            if self.player_turn:
                self.player.start_turn()
                
                # Regeneración pasiva de mana para magos
                if hasattr(self.player, 'class_id') and self.player.class_id == "mage":
                    if hasattr(self.player, 'restore_mana'):
                        restored = self.player.restore_mana(2)
                        if restored > 0:
                            self.log.add(f"Regeneras {restored} de Mana.")

    def get_combat_status(self) -> Dict[str, Any]:
        """Retorna el estado actual del combate"""
        return {
            "turn": self.turn_count,
            "player_turn": self.player_turn,
            "combat_over": self.combat_over,
            "victory": self.victory,
            "player": {
                "name": self.player.name,
                "current_hp": self.player.current_hp,
                "max_hp": self.player.effective_max_hp,
                "current_mana": self.player.current_mana,
                "max_mana": self.player.max_mana,
                "is_defending": self.player.is_defending,
            },
            "enemy": {
                "name": self.enemy.name,
                "current_hp": self.enemy.current_hp,
                "max_hp": self.enemy.max_hp,
                "enemy_type": self.enemy.enemy_type,
            }
        }