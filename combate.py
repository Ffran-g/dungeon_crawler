"""
Archivo de prueba para el sistema de combate - Test automatico
"""

import sys
sys.path.insert(0, '.')

from src.entities.player import Player
from src.entities.enemy import EnemyFactory
from src.systems.combat import CombatSystem
from src.core.constants import *


def test_combat():
    """Prueba automatica del sistema de combate"""
    
    print("=" * 50)
    print("TEST: Sistema de Combate")
    print("=" * 50)
    
    # Crear jugador guerrero
    player = Player("Hero", "warrior")
    print(f"\n[JUGADOR] {player.name} - {player.player_class.name}")
    print(f"  HP: {player.current_hp}/{player.effective_max_hp}")
    print(f"  ATQ: {player.attack}, DEF: {player.defense}")
    
    # Crear enemigo
    enemy = EnemyFactory.create_basic_enemy(1, 1.0)
    print(f"\n[ENEMIGO] {enemy.name}")
    print(f"  HP: {enemy.current_hp}/{enemy.max_hp}")
    print(f"  ATQ: {enemy.atk}, DEF: {enemy.defense}")
    
    # Crear combate
    combat = CombatSystem(player, enemy)
    print(f"\n[COMBATE] Iniciado")
    print(f"  Turno: {combat.turn_count}")
    print(f"  Turno jugador: {combat.player_turn}")
    
    # ===== TEST 1: Jugador ataca =====
    print("\n" + "-" * 40)
    print("TEST 1: Jugador ataca")
    print("-" * 40)
    
    result = combat.player_attack(0)
    print(f"  Accion: player_attack(0)")
    print(f"  Mensajes: {result.messages}")
    print(f"  HP Enemigo despues de ataque: {enemy.current_hp}/{enemy.max_hp}")
    
    # Verificar que el enemigo perdio HP
    if enemy.current_hp < enemy.max_hp:
        print("  [OK] El enemigo perdio HP (CORRECTO)")
    else:
        print("  [ERROR] El enemigo NO perdio HP")
    
    # Siguiente turno
    combat.next_turn()
    print(f"\n  Turno despues de next_turn(): {combat.turn_count}")
    print(f"  Turno del jugador: {combat.player_turn}")
    
    # ===== TEST 2: Enemigo ataca =====
    print("\n" + "-" * 40)
    print("TEST 2: Enemigo ataca")
    print("-" * 40)
    
    player_hp_before = player.current_hp
    result = combat.enemy_turn()
    print(f"  Accion: enemy_turn()")
    print(f"  Mensajes: {result.messages}")
    print(f"  HP Jugador despues de ataque: {player.current_hp}/{player.effective_max_hp}")
    
    # Verificar que el jugador perdio HP
    if player.current_hp < player_hp_before:
        print("  [OK] El jugador perdio HP (CORRECTO)")
    else:
        print("  [ERROR] El jugador NO perdio HP")
    
    # Siguiente turno
    combat.next_turn()
    print(f"\n  Turno despues de next_turn(): {combat.turn_count}")
    print(f"  Turno del jugador: {combat.player_turn}")
    
    # ===== TEST 3: Jugador se defiende =====
    print("\n" + "-" * 40)
    print("TEST 3: Jugador se defiende")
    print("-" * 40)
    
    player_hp_before = player.current_hp
    
    result = combat.player_defend()
    print(f"  Accion: player_defend()")
    print(f"  Mensajes: {result.messages}")
    print(f"  is_defending: {player.is_defending}")
    print(f"  defense_boost: {player.defense_boost}")
    
    if player.is_defending:
        print("  [OK] Jugador esta defendiendo (CORRECTO)")
    else:
        print("  [ERROR] Jugador NO se esta defendiendo")
    
    # Siguiente turno
    combat.next_turn()
    print(f"\n  Turno despues de next_turn(): {combat.turn_count}")
    print(f"  Turno del jugador: {combat.player_turn}")
    
    # ===== TEST 4: Enemigo ataca mientras jugador se defiende =====
    print("\n" + "-" * 40)
    print("TEST 4: Enemigo ataca mientras jugador se defiende")
    print("-" * 40)
    
    player_hp_before = player.current_hp
    result = combat.enemy_turn()
    print(f"  Accion: enemy_turn()")
    print(f"  Mensajes: {result.messages}")
    print(f"  HP Jugador: {player.current_hp}")
    print(f"  Danio recibido: {player_hp_before - player.current_hp}")
    
    # Siguiente turno
    combat.next_turn()
    
    # ===== RESULTADOS FINALES =====
    print("\n" + "=" * 50)
    print("RESULTADOS FINALES")
    print("=" * 50)
    print(f"  Turnos jugados: {combat.turn_count}")
    print(f"  HP Jugador final: {player.current_hp}/{player.effective_max_hp}")
    print(f"  HP Enemigo final: {enemy.current_hp}/{enemy.max_hp}")
    print(f"  Combate terminado: {combat.combat_over}")
    print(f"  Victoria: {combat.victory}")
    
    print("\n[OK] Test completado!")


if __name__ == "__main__":
    test_combat()
