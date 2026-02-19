"""
Módulo de Generación de Mazmorras - Grid 9x9
"""

from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field
import random
from collections import deque

from src.core.constants import *


GRID_SIZE = 9
CENTER = GRID_SIZE // 2  # 4


@dataclass
class Room:
    """Representa una sala en la mazmorra"""
    x: int
    y: int
    floor: int
    room_type: str
    cleared: bool = False
    visited: bool = False
    visible: bool = False
    entered: bool = False  # El jugador ha entrado en la sala
    discovered: bool = False  # El jugador ha visto esta sala (revela el icono)
    has_stairs: bool = False  # Tiene escaleras al siguiente piso
    enemy: Any = None  # Enemigo individual (compatibilidad)
    enemies: List[Any] = field(default_factory=list)  # Lista de enemigos
    event_data: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.enemies is None:
            self.enemies = []

    @property
    def room_id(self) -> str:
        return f"floor{self.floor}_{self.x}_{self.y}"

    def is_combat_room(self) -> bool:
        return self.room_type.startswith("combat")

    def is_boss_room(self) -> bool:
        return self.room_type == ROOM_TYPE_COMBAT_BOSS

    def is_empty(self) -> bool:
        return self.room_type == "empty"

    def is_trap(self) -> bool:
        """Verifica si la sala es una trampa"""
        return self.room_type == ROOM_TYPE_TRAP

    def has_enemies(self) -> bool:
        """Verifica si hay enemigos en la sala"""
        if self.enemies:
            return any(e and e.is_alive() for e in self.enemies)
        return self.enemy is not None and self.enemy.is_alive()

    def get_enemies_list(self) -> List[Any]:
        """Retorna lista de enemigos"""
        if self.enemies:
            return [e for e in self.enemies if e]
        elif self.enemy:
            return [self.enemy]
        return []


class Dungeon:
    """
    Generación y gestión de la mazmorra - Grid 9x9
    """

    def __init__(self, max_floors: int = MAX_DUNGEON_FLOORS, difficulty: str = DIFFICULTY_NORMAL, player_class: str = "warrior"):
        self.max_floors = max_floors
        self.difficulty = difficulty
        self.difficulty_mult = DIFFICULTY_MULTIPLIERS.get(difficulty, 1.0)
        self.player_class = player_class  # Clase del jugador para generar items del mercader

        self.current_floor = 1
        self.grid: Dict[int, Dict[Tuple[int, int], Room]] = {}
        self.player_x = CENTER
        self.player_y = CENTER

        # Control de elites y escaleras por piso
        self.elites_defeated_this_floor = 0
        self.total_elites_this_floor = 0
        self.stairs_unlocked = False
        self.boss_defeated_this_floor = False

        # Generar la mazmorra completa
        self._generate_dungeon()

        # Contar elites del primer piso
        self._count_elites_and_boss()

        # La sala inicial está visitada y visible
        start_room = self.get_room(CENTER, CENTER)
        if start_room:
            start_room.visited = True
            start_room.entered = True
            start_room.discovered = True
            start_room.room_type = "start"
            self._update_visibility()

    def _generate_dungeon(self) -> None:
        """Genera la mazmorra completa"""
        for floor in range(1, self.max_floors + 1):
            self.grid[floor] = self._generate_floor(floor)

    def _count_elites_and_boss(self):
        """Cuenta cuántos elites y bosses hay en el piso actual"""
        elite_count = 0
        has_boss = False

        floor_grid = self.grid.get(self.current_floor, {})
        for room in floor_grid.values():
            # Verificar si es elite o boss (puede ser lista o objeto único)
            enemy = room.enemy
            if enemy:
                # Si es lista, tomar el primer elemento
                if isinstance(enemy, list):
                    if enemy:
                        enemy = enemy[0]
                    else:
                        continue
                if enemy.enemy_type == ENEMY_TYPE_ELITE:
                    elite_count += 1
                elif enemy.enemy_type == ENEMY_TYPE_BOSS:
                    has_boss = True

        self.total_elites_this_floor = elite_count
        self.boss_defeated_this_floor = has_boss and self._is_boss_defeated()

    def _is_boss_defeated(self) -> bool:
        """Verifica si el boss del piso actual está derrotado"""
        floor_grid = self.grid.get(self.current_floor, {})
        for room in floor_grid.values():
            enemy = room.enemy
            if enemy:
                # Si es lista, tomar el primer elemento
                if isinstance(enemy, list):
                    if enemy:
                        enemy = enemy[0]
                    else:
                        continue
                if enemy.enemy_type == ENEMY_TYPE_BOSS:
                    return room.cleared
        return False

    def _generate_floor(self, floor: int) -> Dict[Tuple[int, int], Room]:
        """Genera un piso de la mazmorra como grid 9x9 con conectividad garantizada"""
        
        # PISO 7: Mapa lineal de 5 casillas
        if floor == 7:
            return self._generate_floor_7()
        
        # PISO 8: Mapa lineal de 4 casillas (boss final)
        if floor == 8:
            return self._generate_floor_8()
        
        grid = {}

        # Crear todas las salas como empty inicialmente
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                grid[(x, y)] = Room(x, y, floor, "empty")

        # PASO 1: Generar salas conectadas usando BFS garantizado
        connected_rooms = self._generate_connected_maze()

        # PASO 2: Marcar salas conectadas
        for x, y in connected_rooms:
            grid[(x, y)].room_type = "placeholder"  # Temporal

        # PASO 3: La sala central es el inicio
        grid[(CENTER, CENTER)].room_type = "start"
        grid[(CENTER, CENTER)].visited = True
        grid[(CENTER, CENTER)].discovered = True

        # PASO 4: Convertir a lista y shuffle para asignación aleatoria
        available_rooms = list(connected_rooms - {(CENTER, CENTER)})
        total_available = len(available_rooms)
        random.shuffle(available_rooms)

        # PASO 5: Calcular cantidades basadas en PORCENTAJES
        has_boss = (floor == 4 or floor == self.max_floors)

        # Porcentajes configurables (suman ~100%):
        PCT_EMPTY_ROOMS = 0.27      # 27% - Salas vacías (sin nada)
        PCT_COMBAT_BASIC = 0.37     # 37% - Combate básico
        PCT_TREASURES = 0.09        # 9% - Tesoros
        PCT_TRAPS = 0.07            # 7% - Trampas
        PCT_SANCTUARIES = 0.05      # 5% - Santuarios
        PCT_MERCHANTS = 0.05        # 5% - Comerciantes
        # Elites: 1-2 FIJOS (no porcentual)
        # Boss: 1 sala fija (2%)
        # Escaleras: 1 sala fija (2%)
        # Start: 1 sala fija (2%)

        num_empty = max(1, int(total_available * PCT_EMPTY_ROOMS))
        num_combat_basic = max(1, int(total_available * PCT_COMBAT_BASIC))
        num_elites = random.randint(1, 2) if not has_boss else 0  # MÍNIMO 1, MÁXIMO 2
        num_treasures = max(1, int(total_available * PCT_TREASURES))
        num_traps = max(1, int(total_available * PCT_TRAPS))
        num_sanctuaries = max(1, int(total_available * PCT_SANCTUARIES))
        num_merchants = max(1, int(total_available * PCT_MERCHANTS))

        # PASO 6: Asignar escaleras (siempre última sala lejana)
        stairs_pos = None
        if available_rooms:
            stairs_pos = max(available_rooms, key=lambda p: abs(p[0] - CENTER) + abs(p[1] - CENTER))
            grid[stairs_pos].has_stairs = True
            grid[stairs_pos].room_type = ROOM_TYPE_STAIRS  # Las escaleras son un tipo específico
            available_rooms.remove(stairs_pos)
            num_sanctuaries = max(0, num_sanctuaries - 1)  # Ya usamos un santuario

        # PASO 7: Asignar boss (segunda sala más lejana)
        if has_boss and available_rooms:
            boss_pos = max(available_rooms, key=lambda p: abs(p[0] - CENTER) + abs(p[1] - CENTER))
            grid[boss_pos].room_type = ROOM_TYPE_COMBAT_BOSS
            from src.entities.enemy import EnemyFactory
            boss_list = EnemyFactory.create_boss(floor, self.difficulty_mult)
            grid[boss_pos].enemy = boss_list[0] if boss_list else None
            grid[boss_pos].enemies = boss_list
            available_rooms.remove(boss_pos)

        # PASO 8: Asignar elites (GARANTIZADO: 1-2 elites)
        elites_assigned = 0
        for _ in range(num_elites):
            if not available_rooms:
                break
            pos = available_rooms.pop()
            grid[pos].room_type = ROOM_TYPE_COMBAT_ELITE
            from src.entities.enemy import EnemyFactory
            elite_list = EnemyFactory.create_elite_enemy(floor, self.difficulty_mult)
            grid[pos].enemy = elite_list[0] if elite_list else None
            grid[pos].enemies = elite_list
            elites_assigned += 1

        # Verificación de seguridad: si no hay elites y no hay boss, forzar al menos 1 elite
        if elites_assigned == 0 and not has_boss and available_rooms:
            pos = available_rooms.pop()
            grid[pos].room_type = ROOM_TYPE_COMBAT_ELITE
            from src.entities.enemy import EnemyFactory
            elite_list = EnemyFactory.create_elite_enemy(floor, self.difficulty_mult)
            grid[pos].enemy = elite_list[0] if elite_list else None
            grid[pos].enemies = elite_list

        # PASO 9: Asignar tesoros
        for _ in range(min(num_treasures, len(available_rooms))):
            if not available_rooms:
                break
            pos = available_rooms.pop()
            grid[pos].room_type = ROOM_TYPE_TREASURE
            grid[pos].event_data = self._generate_treasure(floor)

        # PASO 10: Asignar trampas
        for _ in range(min(num_traps, len(available_rooms))):
            if not available_rooms:
                break
            pos = available_rooms.pop()
            grid[pos].room_type = ROOM_TYPE_TRAP
            grid[pos].event_data = self._generate_trap()

        # PASO 11: Asignar santuarios
        for _ in range(min(num_sanctuaries, len(available_rooms))):
            if not available_rooms:
                break
            pos = available_rooms.pop()
            grid[pos].room_type = ROOM_TYPE_SANCTUARY

        # PASO 12: Asignar comerciantes
        for _ in range(min(num_merchants, len(available_rooms))):
            if not available_rooms:
                break
            pos = available_rooms.pop()
            grid[pos].room_type = ROOM_TYPE_MERCHANT
            # Generar items para vender
            from src.entities.item import ItemGenerator, CONSUMABLES
            items_for_sale = []
            
            # Siempre añadir una poción de vida pequeña (o grande con 50% chance)
            if random.random() < 0.5:
                items_for_sale.append(CONSUMABLES["health_potion_large"])
            else:
                items_for_sale.append(CONSUMABLES["health_potion"])
            
            # Si el jugador usa mana (Mago), añadir poción de mana
            if self.player_class == "mage":
                items_for_sale.append(CONSUMABLES["mana_potion"])
            
            # Añadir 2-3 items de equipamiento
            num_equipment = random.randint(2, 3)
            for _ in range(num_equipment):
                item = ItemGenerator.generate_random_equipment(floor)
                if item:
                    items_for_sale.append(item)
            
            grid[pos].event_data = {"items": items_for_sale}

        # PASO 13: Asignar combates básicos
        for _ in range(min(num_combat_basic, len(available_rooms))):
            if not available_rooms:
                break
            pos = available_rooms.pop()
            grid[pos].room_type = ROOM_TYPE_COMBAT_BASIC
            from src.entities.enemy import EnemyFactory
            enemies = EnemyFactory.create_basic_enemy(floor, self.difficulty_mult)
            grid[pos].enemies = enemies
            grid[pos].enemy = enemies[0] if enemies else None  # Compatibilidad

        # PASO 14: Asignar salas vacías (las que quedan)
        for pos in available_rooms:
            grid[pos].room_type = "empty_room"  # Sala vacía pero accesible

        return grid

    def _generate_connected_maze(self) -> Set[Tuple[int, int]]:
        """
        Genera un conjunto de salas GARANTIZADAMENTE CONECTADAS usando BFS
        Retorna un Set de posiciones (x, y) que están todas conectadas entre sí
        """
        # Comenzar desde el centro
        connected: Set[Tuple[int, int]] = {(CENTER, CENTER)}
        frontier: deque = deque([(CENTER, CENTER)])

        # Objetivo: 50-70% del mapa (40-57 salas de 81)
        target_rooms = random.randint(40, 57)

        # Direcciones: arriba, abajo, izquierda, derecha
        directions = [(0, -1), (0, 1), (-1, 0), (1, 0)]

        while len(connected) < target_rooms and frontier:
            # Tomar una sala del frontier (FIFO para BFS)
            current_x, current_y = frontier.popleft()

            # Barajar direcciones para variabilidad
            random.shuffle(directions)

            # Intentar conectar 1-2 vecinos
            connections_made = 0
            max_connections = random.randint(1, 2)

            for dx, dy in directions:
                if connections_made >= max_connections:
                    break

                nx, ny = current_x + dx, current_y + dy

                # Verificar límites y que no esté visitada
                if (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and
                    (nx, ny) not in connected):

                    # 80% de probabilidad de conectar
                    if random.random() < 0.8:
                        connected.add((nx, ny))
                        frontier.append((nx, ny))
                        connections_made += 1

            # Con 30% de probabilidad, re-añadir al frontier para más ramificaciones
            if random.random() < 0.3:
                # Verificar que tenga vecinos no conectados
                has_unconnected = any(
                    (current_x + dx, current_y + dy) not in connected and
                    0 <= current_x + dx < GRID_SIZE and
                    0 <= current_y + dy < GRID_SIZE
                    for dx, dy in directions
                )
                if has_unconnected:
                    frontier.append((current_x, current_y))

        # VALIDACIÓN: Verificar conectividad usando BFS
        if not self._verify_connectivity(connected):
            # Si hay desconexión, regenerar
            return self._generate_connected_maze()

        return connected

    def _verify_connectivity(self, rooms: Set[Tuple[int, int]]) -> bool:
        """
        Verifica que todas las salas en el set estén conectadas entre sí
        Usa BFS desde el centro para verificar que se puede llegar a todas
        """
        if not rooms or (CENTER, CENTER) not in rooms:
            return False

        visited = {(CENTER, CENTER)}
        queue = deque([(CENTER, CENTER)])

        while queue:
            x, y = queue.popleft()

            for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
                nx, ny = x + dx, y + dy
                if (nx, ny) in rooms and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny))

        # Todas las salas deben ser alcanzables
        return len(visited) == len(rooms)

    def _generate_merchant_items(self, floor: int) -> List:
        """Genera items para el mercader"""
        from src.entities.item import ItemGenerator, CONSUMABLES
        items_for_sale = []
        
        # Siempre añadir una poción de vida
        if random.random() < 0.5:
            items_for_sale.append(CONSUMABLES["health_potion_large"])
        else:
            items_for_sale.append(CONSUMABLES["health_potion"])
        
        # Si el jugador usa mana (Mago), añadir poción de mana
        if self.player_class == "mage":
            items_for_sale.append(CONSUMABLES["mana_potion"])
        
        # Añadir 2-3 items de equipamiento
        num_equipment = random.randint(2, 3)
        for _ in range(num_equipment):
            item = ItemGenerator.generate_random_equipment(floor)
            if item:
                items_for_sale.append(item)
        
        return items_for_sale

    def _generate_floor_7(self) -> Dict[Tuple[int, int], Room]:
        """Genera el piso 7 como línea recta de 5 casillas"""
        grid = {}
        
        # Crear grid vacío
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                grid[(x, y)] = Room(x, y, 7, "empty")
        
        # Línea horizontal en el centro: posiciones 0,1,2,3,4 desde la izquierda
        positions = [(i, CENTER) for i in range(5)]
        
        # Casilla 1: Inicio
        grid[(0, CENTER)].room_type = "start"
        grid[(0, CENTER)].visited = True
        grid[(0, CENTER)].discovered = True
        
        # Casilla 2: Santuario
        grid[(1, CENTER)].room_type = ROOM_TYPE_SANCTUARY
        
        # Casilla 3: Tienda
        grid[(2, CENTER)].room_type = ROOM_TYPE_MERCHANT
        items_for_sale = self._generate_merchant_items(7)
        grid[(2, CENTER)].event_data = {"items": items_for_sale}
        
        # Casilla 4: 2 Elites aleatorios
        grid[(3, CENTER)].room_type = ROOM_TYPE_COMBAT_ELITE
        from src.entities.enemy import EnemyFactory
        elite1 = EnemyFactory.create_elite_enemy(7, self.difficulty_mult)
        elite2 = EnemyFactory.create_elite_enemy(7, self.difficulty_mult)
        all_elites = elite1 + elite2  # Combinar las dos listas
        grid[(3, CENTER)].enemies = all_elites
        grid[(3, CENTER)].enemy = all_elites[0] if all_elites else None  # Compatibilidad
        
        # Casilla 5: Escaleras al piso 8
        grid[(4, CENTER)].room_type = ROOM_TYPE_STAIRS
        grid[(4, CENTER)].has_stairs = True
        
        return grid

    def _generate_floor_8(self) -> Dict[Tuple[int, int], Room]:
        """Genera el piso 8 como línea recta de 3 casillas (BOSS FINAL)"""
        grid = {}
        
        # Crear grid vacío
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                grid[(x, y)] = Room(x, y, 8, "empty")
        
        # Línea horizontal en el centro: posiciones 0,1,2
        # Casilla 1: Inicio
        grid[(0, CENTER)].room_type = "start"
        grid[(0, CENTER)].visited = True
        grid[(0, CENTER)].discovered = True
        
        # Casilla 2: Boss Final
        grid[(1, CENTER)].room_type = ROOM_TYPE_COMBAT_BOSS
        from src.entities.enemy import EnemyFactory
        boss_list = EnemyFactory.create_boss(8, self.difficulty_mult)
        grid[(1, CENTER)].enemies = boss_list
        grid[(1, CENTER)].enemy = boss_list[0] if boss_list else None  # Compatibilidad
        
        # Casilla 3: Victoria (escaleras que levam al final)
        grid[(2, CENTER)].room_type = ROOM_TYPE_STAIRS
        grid[(2, CENTER)].has_stairs = True
        grid[(2, CENTER)].event_data = {"is_victory": True}
        
        return grid

    def _generate_trap(self) -> Dict[str, Any]:
        """Genera una trampa"""
        trap_types = [
            {"name": "Trampa de Flechas", "damage": int(15 * self.difficulty_mult), "description": "Flechas disparan desde las paredes"},
            {"name": "Pozo de Espinas", "damage": int(20 * self.difficulty_mult), "description": "El suelo se abre bajo tus pies"},
            {"name": "Gas Venenoso", "damage": int(10 * self.difficulty_mult), "description": "Gas nocivo llena la sala"},
        ]
        return random.choice(trap_types)

    def _generate_treasure(self, floor: int) -> Dict[str, Any]:
        """Genera tesoro"""
        from src.entities.item import ItemGenerator
        
        # Oro siempre
        gold = random.randint(15, 35) * floor
        
        # Pequeña posibilidad de item (15% base, +2% por piso)
        item_chance = 0.15 + (floor * 0.02)
        item = None
        if random.random() < item_chance:
            # Cuanto más alto el piso, mayor rareza
            if floor >= 6 and random.random() < 0.1:
                loot_rarity = "epic"
            elif floor >= 4 and random.random() < 0.2:
                loot_rarity = "rare"
            else:
                loot_rarity = "uncommon"
            
            item = ItemGenerator.generate_random_equipment(floor)
        
        return {
            "item": item,
            "gold": gold,
        }

    def get_room(self, x: int, y: int) -> Optional[Room]:
        """Obtiene una sala por coordenadas"""
        if 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE:
            return self.grid.get(self.current_floor, {}).get((x, y))
        return None

    def get_current_room(self) -> Optional[Room]:
        """Obtiene la sala actual del jugador"""
        return self.get_room(self.player_x, self.player_y)

    def move_player(self, dx: int, dy: int) -> bool:
        """Mueve al jugador. Retorna True si fue posible"""
        new_x = self.player_x + dx
        new_y = self.player_y + dy

        # Verificar límites
        if not (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE):
            return False

        # Verificar que hay sala (las salas "empty_room" son navegables)
        room = self.get_room(new_x, new_y)
        if not room or room.room_type == "empty":  # "empty" son obstáculos, "empty_room" son navegables
            return False

        # Mover
        self.player_x = new_x
        self.player_y = new_y
        room.visited = True
        room.entered = True
        room.discovered = True  # Al entrar, SIEMPRE se descubre

        # Actualizar visibilidad
        self._update_visibility()

        # Retornar info de la sala para manejar eventos automáticos
        return room.room_type

    def _update_visibility(self):
        """
        Actualiza qué salas son visibles y descubiertas
        - visible: salas que el jugador puede VER (adyacentes)
        - discovered: salas que revelan su icono/tipo de forma permanente

        REGLA:
        - Enemigos, tesoros, santuarios y comerciantes se revelan cuando el jugador
          está adyacente, y permanecen visibles de forma permanente.
        - Las trampas permanecen ocultas hasta que el jugador entra en ellas.
        """
        cx, cy = self.player_x, self.player_y

        # La sala actual siempre visible y descubierta
        current = self.get_room(cx, cy)
        if current and current.room_type != "empty":
            current.visible = True
            current.visited = True
            current.discovered = True

        # Las 4 direcciones (no diagonales) son visibles
        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            room = self.get_room(cx + dx, cy + dy)
            if room and room.room_type != "empty":
                room.visible = True

                # REGLAS DE DISCOVERY:
                # - Si la sala ya fue descubierta, mantenerla descubierta
                # - Si no ha sido descubierta:
                #   - Si es trampa: NO descubrir hasta que entre (handled in move_player)
                #   - Si tiene enemigo/tesoro/mercader/santuario: descubrir al estar adyacente
                if not room.discovered:
                    if room.is_trap():
                        pass  # Las trampas no se descubren hasta entrar
                    else:
                        room.discovered = True

    def get_visible_rooms(self) -> List[Tuple[int, int, Room]]:
        """Retorna lista de salas visibles con coordenadas"""
        rooms = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                room = self.get_room(x, y)
                if room and room.visible:
                    rooms.append((x, y, room))
        return rooms

    def get_discovered_rooms(self) -> List[Tuple[int, int, Room]]:
        """Retorna lista de salas descubiertas (que muestran su icono) con coordenadas"""
        rooms = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                room = self.get_room(x, y)
                if room and room.discovered:
                    rooms.append((x, y, room))
        return rooms

    def clear_current_room(self) -> None:
        """Marca la sala actual como cleared"""
        room = self.get_current_room()
        if room:
            room.cleared = True

            # Verificar tipo de sala y desbloquear escaleras
            self._check_and_unlock_stairs()

    def _check_and_unlock_stairs(self):
        """Verifica si se deben desbloquear las escaleras"""
        room = self.get_current_room()
        if not room:
            return

        # Verificar tipo de sala y desbloquear escaleras
        enemy = room.enemy[0] if isinstance(room.enemy, list) else room.enemy
        is_elite = room.room_type == ROOM_TYPE_COMBAT_ELITE or (enemy and enemy.enemy_type == ENEMY_TYPE_ELITE)
        is_boss = room.room_type == ROOM_TYPE_COMBAT_BOSS or (enemy and enemy.enemy_type == ENEMY_TYPE_BOSS)

        if is_elite:
            self.elites_defeated_this_floor += 1
            if self.elites_defeated_this_floor >= self.total_elites_this_floor:
                self._unlock_stairs()

        elif is_boss:
            self.boss_defeated_this_floor = True
            self._unlock_stairs()

    def _unlock_stairs(self):
        """Desbloquea las escaleras (las hace visibles)"""
        if self.stairs_unlocked:
            return

        self.stairs_unlocked = True

        # Hacer visibles las escaleras
        floor_grid = self.grid.get(self.current_floor, {})
        for pos, room in floor_grid.items():
            if room.has_stairs:
                room.visible = True
                room.discovered = True

    def can_use_stairs(self) -> bool:
        """Verifica si el jugador está en una sala con escaleras"""
        room = self.get_current_room()
        return room and room.has_stairs and self.stairs_unlocked

    def is_dungeon_complete(self) -> bool:
        """Verifica si se completó la mazmorra"""
        return self.current_floor == self.max_floors and self.boss_defeated_this_floor

    def next_floor(self) -> bool:
        """Avanza al siguiente piso. Retorna False si es el último"""
        if self.current_floor < self.max_floors:
            self.current_floor += 1
            
            # Para pisos 7 y 8, el inicio está en el borde izquierdo (0, CENTER)
            if self.current_floor >= 7:
                self.player_x = 0
                self.player_y = CENTER
            else:
                self.player_x = CENTER
                self.player_y = CENTER

            # Reiniciar contadores del nuevo piso
            self.elites_defeated_this_floor = 0
            self.stairs_unlocked = False
            self.boss_defeated_this_floor = False

            # La sala inicial del nuevo piso
            start_room = self.get_room(self.player_x, self.player_y)
            if start_room:
                start_room.visited = True
                start_room.entered = True
                start_room.discovered = True

            # Contar elites del nuevo piso
            self._count_elites_and_boss()

            self._update_visibility()
            return True
        return False

    def get_dungeon_status(self) -> Dict[str, Any]:
        """Retorna estado de la mazmorra"""
        floor_grid = self.grid.get(self.current_floor, {})

        # Contar tipos de salas
        total_rooms = 0
        room_counts = {
            "empty_rooms": 0,
            "combat_basic": 0,
            "combat_elite": 0,
            "combat_boss": 0,
            "treasures": 0,
            "traps": 0,
            "sanctuaries": 0,
            "merchants": 0,
            "start": 0,
            "stairs": 0,
        }

        cleared_rooms = 0
        discovered_rooms = 0

        for room in floor_grid.values():
            if room.room_type == "empty":
                continue  # Obstáculos no cuentan

            total_rooms += 1

            if room.cleared:
                cleared_rooms += 1
            if room.discovered:
                discovered_rooms += 1

            # Contar por tipo
            if room.room_type == "empty_room":
                room_counts["empty_rooms"] += 1
            elif room.room_type == ROOM_TYPE_COMBAT_BASIC:
                room_counts["combat_basic"] += 1
            elif room.room_type == ROOM_TYPE_COMBAT_ELITE:
                room_counts["combat_elite"] += 1
            elif room.room_type == ROOM_TYPE_COMBAT_BOSS:
                room_counts["combat_boss"] += 1
            elif room.room_type == ROOM_TYPE_TREASURE:
                room_counts["treasures"] += 1
            elif room.room_type == ROOM_TYPE_TRAP:
                room_counts["traps"] += 1
            elif room.room_type == ROOM_TYPE_SANCTUARY:
                room_counts["sanctuaries"] += 1
            elif room.room_type == ROOM_TYPE_MERCHANT:
                room_counts["merchants"] += 1
            elif room.room_type == "start":
                room_counts["start"] += 1

            if room.has_stairs:
                room_counts["stairs"] += 1

        # Calcular porcentajes
        room_percentages = {}
        if total_rooms > 0:
            for room_type, count in room_counts.items():
                room_percentages[room_type] = round((count / total_rooms) * 100, 1)

        return {
            "current_floor": self.current_floor,
            "max_floors": self.max_floors,
            "total_rooms": total_rooms,
            "cleared_rooms": cleared_rooms,
            "discovered_rooms": discovered_rooms,
            "room_counts": room_counts,
            "room_percentages": room_percentages,
            "elites_defeated": self.elites_defeated_this_floor,
            "total_elites": self.total_elites_this_floor,
            "stairs_unlocked": self.stairs_unlocked,
            "player_x": self.player_x,
            "player_y": self.player_y,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializa la mazmorra"""
        floors_data = {}
        for floor_num, grid_data in self.grid.items():
            grid_serialized = {}
            for (x, y), room in grid_data.items():
                # Serializar enemigo solo si existe y tiene el método to_dict
                enemy_data = None
                if room.enemy and hasattr(room.enemy, 'to_dict'):
                    enemy_data = room.enemy.to_dict()

                grid_serialized[f"{x}_{y}"] = {
                    "x": room.x,
                    "y": room.y,
                    "floor": room.floor,
                    "room_type": room.room_type,
                    "cleared": room.cleared,
                    "visited": room.visited,
                    "visible": room.visible,
                    "entered": room.entered,
                    "discovered": room.discovered,
                    "has_stairs": room.has_stairs,
                    "enemy": enemy_data,
                    "event_data": room.event_data,
                }
            floors_data[floor_num] = grid_serialized

        return {
            "max_floors": self.max_floors,
            "difficulty": self.difficulty,
            "player_class": self.player_class,
            "current_floor": self.current_floor,
            "player_x": self.player_x,
            "player_y": self.player_y,
            "elites_defeated_this_floor": self.elites_defeated_this_floor,
            "total_elites_this_floor": self.total_elites_this_floor,
            "stairs_unlocked": self.stairs_unlocked,
            "boss_defeated_this_floor": self.boss_defeated_this_floor,
            "floors": floors_data,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Dungeon':
        """Deserializa la mazmorra"""
        dungeon = cls.__new__(cls)  # Crear sin llamar __init__

        dungeon.max_floors = data["max_floors"]
        dungeon.difficulty = data["difficulty"]
        dungeon.difficulty_mult = DIFFICULTY_MULTIPLIERS.get(dungeon.difficulty, 1.0)
        dungeon.player_class = data.get("player_class", "warrior")
        dungeon.current_floor = data["current_floor"]
        dungeon.player_x = data["player_x"]
        dungeon.player_y = data["player_y"]
        dungeon.grid = {}

        # Atributos de control de elites y escaleras
        dungeon.elites_defeated_this_floor = data.get("elites_defeated_this_floor", 0)
        dungeon.total_elites_this_floor = data.get("total_elites_this_floor", 0)
        dungeon.stairs_unlocked = data.get("stairs_unlocked", False)
        dungeon.boss_defeated_this_floor = data.get("boss_defeated_this_floor", False)

        from src.entities.enemy import Enemy

        for floor_num, grid_data in data["floors"].items():
            dungeon.grid[int(floor_num)] = {}
            for key, rd in grid_data.items():
                x, y = map(int, key.split('_'))
                room = Room(rd["x"], rd["y"], rd["floor"], rd["room_type"])
                room.cleared = rd["cleared"]
                room.visited = rd["visited"]
                room.visible = rd["visible"]
                room.entered = rd.get("entered", False)
                room.discovered = rd.get("discovered", False)
                room.has_stairs = rd.get("has_stairs", False)
                room.event_data = rd.get("event_data")

                if rd.get("enemy"):
                    room.enemy = Enemy.from_dict(rd["enemy"])

                dungeon.grid[int(floor_num)][(x, y)] = room

        return dungeon