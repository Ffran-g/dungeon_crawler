# Dungeon Crawler - Roguelike RPG

## Resumen

Dungeon Crawler es un roguelike tradicional desarrollado en Python usando Pygame. El jugador desciende por 8 pisos de mazmorras generadas proceduralmente, battledo enemigos, encontrando tesoros y enfrentándose a bosses únicos. El objetivo es derrotar al boss del piso 8 para victoria.

---

## Cómo Hacer Funcionar el Juego

### 1. Instalar Python
Si no tienes Python, descárgalo desde https://www.python.org (versión 3.x)

### 2. Instalar dependencias
```bash
pip install pygame
```

### 3. Ejecutar el juego
```bash
python main.py
```

### 4. Para jugar
1. Ejecuta el juego con `python main.py`
2. Selecciona una clase (Guerrero, Mago, Pícaro o Brujo)
3. Ingresa tu nombre
4. Usa las flechas para moverte por la mazmorra
5. Derrota a los enemigos y elites para desbloquear las escaleras
6. Desciende hasta el piso 8 y derrota al boss
7. ¡Victoria!

---

## Características Principales

- **8 pisos de mazmorra** con dificultad progresiva
- **4 clases de personaje** con habilidades únicas y passivas
- **Sistema de combate por turnos** estratégico
- **Generación procedural** de salas, enemigos y objetos
- **Equipamiento** con rarezas (común, poco común, raro, épico, legendario)
- **Mercader** para comprar/vender objetos
- **Santuarios** para descansar y curar
- **Sistema de guardado/carga** con 3 ranuras

---

## Controles

| Tecla | Acción |
|-------|--------|
| **Flechas** | Moverse en la mazmorra |
| **Enter/Espacio** | Entrar en sala / Confirmar |
| **I** | Abrir inventario |
| **E** | Ver equipamiento |
| **Escape** | Menú de pausa |
| **B** | Comprar (mercader) |
| **V** | Vender (mercader) |
| **1-4** | Seleccionar habilidad en combate |
| **Q/E** | Cambiar objetivo (combate múltiple) |
| **D** | Defender |
| **R** | Huir |

---

## Estructura del Proyecto

```
dungeon_crawler/
├── main.py                    # Punto de entrada y loop principal
├── src/
│   ├── core/
│   │   ├── constants.py       # Constantes del juego
│   │   ├── config.py          # Configuración global
│   │   └── state_machine.py   # Máquina de estados del juego
│   ├── entities/
│   │   ├── player.py          # Jugador y clases (Warrior, Mage, Rogue, Warlock)
│   │   ├── enemy.py           # Enemigos (Basic, Elite, Boss)
│   │   └── item.py            # Items, equipamiento y generador
│   ├── systems/
│   │   ├── combat.py          # Sistema de combate por turnos
│   │   ├── dungeon.py         # Generación de mazmorras
│   │   └── save_system.py     # Guardado/carga
│   └── ui/
│       └── renderer.py        # Renderizado de UI
└── assets/saves/              # Archivos de guardado JSON
```

---

## Clases de Personaje

| Clase | HP | ATK | DEF | Descripción |
|-------|-----|-----|-----|-------------|
| **Guerrero** | 120 | 15 | 10 | Alto HP y defensa. Usa concentración para ataques dobles. |
| **Mago** | 80 | 20 | 5 | Alto daño mágico. Usa mana para habilidades. |
| **Pícaro** | 90 | 12 | 6 | Veloz, evasión alta. Golpes múltiples. |
| **Brujo** | 110 | 14 | 6 | Usa su vida para lanzar hechizos oscuros. |

---

## Sistema de Combate

- **Turnos alternados**: El jugador siempre ataca primero
- **Acciones**: Atacar, Defender, Objeto, Huir
- **Consumibles**: Tomar una pocion no consume tu turno
---

## Combate Rápido

Prueba las clases antes de embarcarte en una aventura.

**Importante**: El equipamiento y objetos para este modo son los básicos de la propia clase

1. Selecciona un tipo de enemgio al que enfrentar
2. Selecciona un Heroe
3. Enfrentate en un único combate para probar las capacidades de tu clase

**VS enemigo Básico**: El jugador sera de Lvl 1
**VS enemigo Élite**: El jugador sera Lvl 10
**VS enemigo Boss**: El jugador sera Lvl 20 

---

## Licencia

Proyecto de ejemplo educativo.
