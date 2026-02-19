# Dungeon Crawler - Arquitectura del Proyecto

## Estructura de Carpetas

```
dungeon_crawler/
├── main.py                    # Punto de entrada, loop principal
├── src/
│   ├── core/
│   │   ├── game.py            # Controlador principal del juego
│   │   ├── state_machine.py   # Máquina de estados
│   │   ├── config.py          # Configuraciones globales
│   │   └── constants.py       # Constantes del juego
│   ├── entities/
│   │   ├── player.py          # Jugador y clases
│   │   ├── enemy.py           # Enemigos (básico, elite, boss)
│   │   ├── item.py            # Objetos y equipamiento
│   │   └── merchant.py        # Comerciante
│   ├── systems/
│   │   ├── combat.py          # Sistema de combate por turnos
│   │   ├── dungeon.py         # Generación procedural de mazmorras
│   │   ├── save_system.py     # Sistema de guardado/carga
│   │   ├── difficulty.py      # Sistema de dificultad
│   │   └── ai.py              # IA de enemigos
│   ├── ui/
│   │   ├── renderer.py        # Renderizado ASCII
│   │   ├── menu.py            # Menús del juego
│   │   └── components.py     # Componentes UI reutilizables
│   └── data/
│       ├── abilities.py       # Habilidades de cada clase
│       ├── loot_tables.py     # Tablas de loot
│       └── dungeon_layouts.py # Layouts predefinidos
├── assets/
│   ├── saves/                 # Archivos de guardado
│   └── fonts/                # Fuentes (monoespaciadas)
└── README.md
```

---

## Diagrama Conceptual de Clases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              STATE MACHINE                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│  │  MENU    │──▶│ SELECT   │──▶│ DUNGEON  │──▶│ COMBAT   │──▶│ VICTORY/ │  │
│  │  STATE   │   │  CLASS   │   │  STATE   │   │  STATE   │   │  DEATH   │  │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘   └──────────┘  │
│       │                                                    ▲                │
│       └────────────────────────────────────────────────────┘                │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           ENTITY (Abstract Base)                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  - name: str                                                          │    │
│  │  - max_hp: int                                                        │    │
│  │  - current_hp: int                                                    │    │
│  │  - attack: int                                                        │    │
│  │  - defense: int                                                       │    │
│  │  - speed: int                                                         │    │
│  │  + take_damage(amount): int                                          │    │
│  │  + is_alive(): bool                                                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│           ▲                         ▲                       ▲               │
│           │                         │                       │               │
│    ┌──────┴──────┐          ┌───────┴───────┐       ┌───────┴───────┐        │
│    │   PLAYER    │          │    ENEMY      │       │   MERCHANT    │        │
│    │             │          │               │       │               │        │
│    │ - class_obj │          │ - enemy_type   │       │ - inventory   │        │
│    │ - gold      │          │ - xp_reward   │       │ - gold        │        │
│    │ - inventory │          │ - loot_table  │       │ + trade()     │        │
│    │ - equipment │          │ + ai_action() │       └───────────────┘        │
│    │ + use_skill()│         └───────────────┘                                │
│    │ + equip()   │                                                               │
│    └─────────────┘                                                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              PLAYER CLASSES                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  WARRIOR    │  │    MAGE     │  │    ROGUE    │  │   CLERIC    │          │
│  │             │  │             │  │             │  │             │          │
│  │ HP: 120     │  │ HP: 80      │  │ HP: 90      │  │ HP: 100     │          │
│  │ ATK: 15     │  │ ATK: 20     │  │ ATK: 12     │  │ ATK: 10     │          │
│  │ DEF: 10     │  │ DEF: 5      │  │ DEF: 6      │  │ DEF: 8      │          │
│  │ SPD: 5      │  │ SPD: 6      │  │ SPD: 10     │  │ SPD: 5      │          │
│  │             │  │             │  │             │  │             │          │
│  │ Skills:     │  │ Skills:     │  │ Skills:     │  │ Skills:     │          │
│  │ - Slash     │  │ - Fireball  │  │ - Backstab  │  │ - Heal      │          │
│  │ - Bash      │  │ - Frost     │  │ - Poison    │  │ - Smite     │          │
│  │ - Rage      │  │ - Teleport  │  │ - Evade     │  │ - Buff      │          │
│  │ - Shield    │  │ - Mana      │  │ - Stealth   │  │ - Curse     │          │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                            ENEMY HIERARCHY                                   │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                          │
│  │   BASIC     │  │   ELITE    │  │    BOSS     │                          │
│  │             │  │             │  │             │                          │
│  │ HP: 30-50   │  │ HP: 80-120 │  │ HP: 200-500 │                          │
│  │ ATK: 5-10   │  │ ATK: 12-18 │  │ ATK: 20-35  │                          │
│  │ XP: 10-20   │  │ XP: 40-60  │  │ XP: 200-500 │                          │
│  │ Gold: 5-15  │  │ Gold: 30-50│  │ Gold: 100+ │                          │
│  │             │  │ + Special  │  │ + Phases    │                          │
│  │ Examples:   │  │   Abilities│  │ + Minions   │                          │
│  │ - Goblin    │  │ Examples:  │  │ Examples:   │                          │
│  │ - Rat       │  │ - Orc      │  │ - Dragon    │                          │
│  │ - Skeleton  │  │ - Troll    │  │ - Lich      │                          │
│  └─────────────┘  └─────────────┘  └─────────────┘                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                          EQUIPMENT SYSTEM                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         PLAYER                                       │    │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────┐  ┌────────────┐        │    │
│  │  │  WEAPON │  │ ARMOR    │  │ ACCESSORY 1│  │ACCESSORY 2 │        │    │
│  │  │         │  │          │  │            │  │            │        │    │
│  │  │ +ATK    │  │ +DEF     │  │ +STAT      │  │ +STAT      │        │    │
│  │  └─────────┘  └──────────┘  └────────────┘  └────────────┘        │    │
│  │                                                                     │    │
│  │  INVENTORY (max 20 slots)                                           │    │
│  │  ┌────┬────┬────┬────┬────┬────┬────┬────┐                         │    │
│  │  │ P1 │ P2 │ W1 │ A1 │ AC1│ AC2│ K1 │ ..│                         │    │
│  │  └────┴────┴────┴────┴────┴────┴────┴────┘                         │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Item Types: WEAPON, ARMOR, ACCESSORY, CONSUMABLE, MATERIAL                │
│  Rarities: COMMON, UNCOMMON, RARE, EPIC, LEGENDARY                          │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         DUNGEON GENERATION                                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         DUNGEON                                       │    │
│  │                                                                     │    │
│  │  Floor 1 ────── Floor 2 ────── Floor 3 ────── ... ────── Floor N   │    │
│  │    │              │              │                     │            │    │
│  │  ┌─┴─┐          ┌─┴─┐          ┌─┴─┐                 ┌─┴─┐          │    │
│  │  │R  │          │E  │          │B  │                 │Boss│          │    │
│  │  │C  │          │R  │          │   │                 │   │          │    │
│  │  │M  │          │T  │          │   │                 │   │          │    │
│  │  │   │          │   │          │   │                 │   │          │    │
│  │  └───┘          └───┘          └───┘                 └───┘          │    │
│  │  R=Room, C=Combat, M=Merchant, E=Elite, T=Trap, B=Boss              │    │
│  │                                                                     │    │
│  │  Room Types: COMBAT, EVENT, MERCHANT, TREASURE, SANCTUARY, BOSS    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Generation Algorithm: Binary Space Partitioning (BSP)                    │
│  + Room connections via corridors                                         │
│  + Difficulty scaling based on floor number                               │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                         COMBAT SYSTEM                                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                        TURN STRUCTURE                               │    │
│  │                                                                     │    │
│  │  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐         │    │
│  │  │ PLAYER  │───▶│ ENEMY   │───▶│ PLAYER  │───▶│ ENEMY   │───...   │    │
│  │  │ TURN    │    │ TURN    │    │ TURN    │    │ TURN    │         │    │
│  │  └─────────┘    └─────────┘    └─────────┘    └─────────┘         │    │
│  │       │               │               │               │            │    │
│  │       ▼               ▼               ▼               ▼            │    │
│  │  ┌─────────────────────────────────────────────────────────┐       │    │
│  │  │                  PLAYER ACTIONS                          │       │    │
│  │  │  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  │       │    │
│  │  │  │  FIGHT  │  │  DEFEND  │  │   RUN   │  │  ITEM    │  │       │    │
│  │  │  │ (Skill) │  │ (+DEF)   │  │(-Gold)  │  │(Potions) │  │       │    │
│  │  │  └─────────┘  └──────────┘  └─────────┘  └──────────┘  │       │    │
│  │  └─────────────────────────────────────────────────────────┘       │    │
│  │                                                                     │    │
│  │  Order determined by SPEED stat + some randomness                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Explicación de Cada Módulo

### core/
- **game.py**: Controlador principal que coordina todos los sistemas
- **state_machine.py**: Implementa el patrón State Machine para управление flujos del juego
- **config.py**: Configuraciones globales (ventana, colores, rutas)
- **constants.py**: Constantes del juego (tamaños, límites)

### entities/
- **player.py**: Clase base Player + 4 clases especializadas (Warrior, Mage, Rogue, Cleric)
- **enemy.py**: Enemigos con tipos (básico, elite, boss) y jerarquía
- **item.py**: Sistema de items, equipamiento y consumo
- **merchant.py**: Comerciante con inventario propio

### systems/
- **combat.py**: Lógica de combate por turnos
- **dungeon.py**: Generación procedural de salas
- **save_system.py**: Serialización JSON para guardar/cargar
- **difficulty.py**: Escalado de dificultad por nivel
- **ai.py**: IA simple para enemigos

### ui/
- **renderer.py**: Renderizado ASCII en Pygame
- **menu.py**: Menús (principal, selección clase, pausa)
- **components.py**: Botones, barras, ventanas reutilizables

### data/
- **abilities.py**: Definición de habilidades por clase
- **loot_tables.py**: Probabilidades de loot
- **dungeon_layouts.py**: Layouts predefinidos opcionales

---

## Manejo de Eventos Aleatorios

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         EVENT SYSTEM                                        │
│                                                                             │
│  Room Event Weights (pueden ajustarse por dificultad):                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  BASIC FLOOR (1-3):                                                 │    │
│  │  - Combat (Basic):     50%                                          │    │
│  │  - Treasure:           15%                                          │    │
│  │  - Trap:               15%                                          │    │
│  │  - Merchant:           10%                                          │    │
│  │  - Sanctuary:          10%                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  MID FLOOR (4-7):                                                   │    │
│  │  - Combat (Elite):    40%                                          │    │
│  │  - Combat (Basic):    15%                                          │    │
│  │  - Treasure:          15%                                          │    │
│  │  - Trap:              15%                                          │    │
│  │  - Merchant:          10%                                          │    │
│  │  - Sanctuary:          5%                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  BOSS FLOOR (8):                                                    │    │
│  │  - Boss:             100%                                          │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Implementación: random.choices() con weights en dungeon.py                │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Escalado de Dificultad

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      DIFFICULTY SCALING                                     │
│                                                                             │
│  Base Stats × Difficulty Multiplier:                                       │
│  ┌────────────┬──────────┬──────────┬──────────┬──────────┐               │
│  │   Floor    │   EASY   │  NORMAL  │   HARD   │ NIGHTMARE│               │
│  ├────────────┼──────────┼──────────┼──────────┼──────────┤               │
│  │     1      │   0.7x   │   1.0x   │   1.3x   │   1.5x   │               │
│  │     2      │   0.8x   │   1.1x   │   1.4x   │   1.7x   │               │
│  │     3      │   0.9x   │   1.2x   │   1.5x   │   1.9x   │               │
│  │     ...    │   ...    │   ...    │   ...    │   ...    │               │
│  │     N      │  0.7+N*0.1│ 1.0+N*0.1│ 1.3+N*0.1│ 1.5+N*0.2│               │
│  └────────────┴──────────┴──────────┴──────────┴──────────┘               │
│                                                                             │
│  Enemy Stats Formula:                                                       │
│  - HP = base_hp × floor_multiplier × difficulty_multiplier                  │
│  - ATK = base_atk × floor_multiplier × difficulty_multiplier                │
│  - DEF = base_def × floor_multiplier × difficulty_multiplier                │
│                                                                             │
│  Loot Scaling:                                                              │
│  - Gold reward = base_gold × floor_multiplier × difficulty_multiplier      │
│  - XP reward = base_xp × floor_multiplier × difficulty_multiplier          │
│  - Item rarity chance increases with floor                                 │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## IA de Enemigos

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENEMY AI                                            │
│                                                                             │
│  Basic Enemy AI:                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  1. If HP < 30%:                                                    │    │
│  │     - 50% chance: Use defensive ability / heal                     │    │
│  │     - 50% chance: Continue attacking                                │    │
│  │                                                                     │    │
│  │  2. If player.defending:                                           │    │
│  │     - Reduce attack power by 30%                                    │    │
│  │                                                                     │    │
│  │  3. Normal turn:                                                    │    │
│  │     - 80% chance: Normal attack                                      │    │
│  │     - 20% chance: Special ability (if available)                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Elite Enemy AI:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  - Uses special abilities more frequently (35% chance)             │    │
│  │  - Can use debuffs (poison, stun)                                   │    │
│  │  - May prioritize healing when low HP                              │    │
│  │  - Strategic ability usage based on battle state                   │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Boss AI:                                                                   │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  Phase 1 (100%-66% HP):                                             │    │
│  │  - Standard attacks + occasional special moves                     │    │
│  │                                                                     │    │
│  │  Phase 2 (66%-33% HP):                                              │    │
│  │  - Enters "enraged" mode, +30% ATK                                  │    │
│  │  - Uses abilities more frequently                                  │    │
│  │                                                                     │    │
│  │  Phase 3 (<33% HP):                                                 │    │
│  │  - Ultimate ability available                                       │    │
│  │  - May summon minions (if applicable)                               │    │
│  │  - Aggressive playstyle                                             │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Sistema de Guardado

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         SAVE SYSTEM                                         │
│                                                                             │
│  Save File Structure (JSON):                                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │  {                                                                  │    │
│  │    "player": {                                                      │    │
│  │      "name": "Hero",                                                │    │
│  │      "class": "warrior",                                           │    │
│  │      "level": 5,                                                    │    │
│  │      "xp": 1200,                                                    │    │
│  │      "current_hp": 80,                                              │    │
│  │      "max_hp": 100,                                                 │    │
│  │      "stats": { "str": 15, "int": 8, "dex": 10, "fai": 8 },         │    │
│  │      "gold": 250,                                                   │    │
│  │      "equipment": {                                                 │    │
│  │        "weapon": {"id": "sword_1", ...},                           │    │
│  │        "armor": {"id": "armor_1", ...},                             │    │
│  │        "accessory1": null,                                          │    │
│  │        "accessory2": null                                           │    │
│  │      },                                                             │    │
│  │      "inventory": [...items...]                                     │    │
│  │    },                                                               │    │
│  │    "dungeon": {                                                    │    │
│  │      "current_floor": 3,                                           │    │
│  │      "max_floors": 8,                                               │    │
│  │      "rooms_cleared": [...],                                        │    │
│  │      "visited_rooms": [...]                                        │    │
│  │    },                                                               │    │
│  │    "game_stats": {                                                  │    │
│  │      "total_kills": 45,                                             │    │
│  │      "total_damage_dealt": 2500,                                    │    │
│  │      "total_damage_taken": 800,                                     │    │
│  │      "floors_cleared": 2,                                           │    │
│  │      "playtime_seconds": 3600                                       │    │
│  │    },                                                               │    │
│  │    "settings": {                                                   │    │
│  │      "difficulty": "normal",                                       │    │
│  │      "sound_volume": 0.8                                           │    │
│  │    },                                                               │    │
│  │    "timestamp": "2024-01-15T10:30:00"                              │    │
│  │  }                                                                  │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                             │
│  Save Slots: 3 slots disponibles                                            │
│  Auto-save: Al final de cada piso de la mazmorra                          │
└─────────────────────────────────────────────────────────────────────────────┘
```
