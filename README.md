# Dungeon Crawler - Roguelike RPG

Un juego de rol tipo dungeon crawler con generación procedural de mazmorras, desarrollado en Python usando Pygame.

## Temática

**Dungeon Crawler** es un roguelike tradicional donde el jugador desciende por 8 pisos de una mazmorra procedimental, battling enemigos, encontrando tesoros, evitando trampas y enfrentándose a bosses únicos. El objetivo es derrotar al boss del piso 8 para obtener la victoria.

### Características Principales
- **8 pisos de mazmorra** con dificultad progresiva
- **4 clases de personaje** con habilidades únicas y passivas
- **Sistema de combate por turnos** estratégico
- **Generación procedural** de salas, enemigos y objetos
- **Equipamiento** con rarezas (común, poco común, raro, épico, legendario)
- **Mercader** para comprar/vender objetos
- **Santuarios** para descansar y curar
- **Sistema de guardado/carga** con 3 ranuras

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

## Tecnología

- **Lenguaje**: Python 3.x
- **Librería Gráfica**: Pygame
- **Formato de guardado**: JSON
- **Arquitectura**: Orientada a objetos con patrón State Machine

### Requisitos
```
pip install pygame
```

---

## Clases de Personaje

| Clase | HP | ATK | DEF | Descripción |
|-------|-----|-----|-----|-------------|
| **Guerrero** | 120 | 15 | 10 | Alto HP y defensa. Usa concentración para ataques dobles. |
| **Mago** | 80 | 20 | 5 | Alto daño mágico. Usa mana para habilidades. |
| **Pícaro** | 90 | 12 | 6 | Veloz, evasión alta. Golpes múltiples. |
| **Brujo** | 110 | 14 | 6 | Usa su vida para lanzar hechizos oscuros. |

### Habilidades por Clase

**Guerrero:**
- Corte (daño 1.5x)
- Golpe (aturdir)
- Furia (buff de ataque)
- Escudo (gran defensa)

**Mago:**
- Misiles Arcanos (3 golpes)
- Escudo Repelente (refleja daño)
- Canalizar (recupera mana)
- Bola de Fuego (alto daño)

**Pícaro:**
- Ráfaga (4 golpes rápidos)
- Veneno (daño por turnos)
- Evasión (50% esquivar)
- Asesinato (alto daño tras evasión)

**Brujo:**
- Maldición (efectos aleatorios)
- Explosión Maldita (detona maldiciones)
- Consumir Maldiciones (beneficios)
- Toque Vampírico (roba vida)

---

## Sistema de Combate

- **Turnos alternados**: El jugador siempre ataca primero
- **Acciones**: Atacar, Defender, Objeto, Huir
- **Daño**: Fórmula basada en ataque y defensa con variación ±20%
- **Golpe crítico**: 10% de probabilidad (1.5x daño)
- **Evasión**: Habilidades y passivas del Pícaro
- **Concentración** (Guerrero): Acumula al atacar, permite ataque doble

### Enemigos

| Tipo | Características |
|------|-----------------|
| **Básico** | Goblin, Rata Gigante, Esqueleto, Orco, Zombi... |
| **Élite** | Orco Berserker, Trol, Nigromante, Vampiro |
| **Boss** | Dragón Ancianos, Lich Señor, Demonio Infernal |

Los bosses tienen **3 fases** (100%, 66%, 33% HP) y se enfurecen en la última.

---

## Sistema de Mazmorras

- **Grid 9x9** por piso
- **8 pisos** totales (pisos 7 y 8 son lineales)
- **Generación procedural** con BFS para garantizar conectividad
- **Tipos de sala**:
  - Combate Básico
  - Combate Élite
  - Combate Boss
  - Tesoro
  - Trampa
  - Mercader
  - Santuario
  - Escaleras

### Desbloqueo de Escaleras
Para acceder al siguiente piso, debes derrotar a todos los enemigos Élite o al Boss del piso actual.

---

## Sistema de Items

### Tipos
- **Armas**: Proporcionan ataque
- **Armaduras**: Proporcionan defensa
- **Accesorios**: bonificaciones diversas
- **Consumibles**: Poción de Vida, Poción de Mana, Antídoto...

### Rarezas
| Rareza | Color | Multiplicador |
|--------|-------|----------------|
| Común | Gris | 1.0x |
| Poco Común | Verde | 1.5x |
| Raro | Azul | 2.0x |
| Épico | Púrpura | 3.0x |
| Legendario | Naranja | 5.0x |

### Equipamiento
El jugador tiene 4 slots: weapon, armor, accessory_1, accessory_2, más un inventario de 20 espacios.

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

## Guardado y Carga

- **3 ranuras** de guardado
- **Persistencia**: Player, inventario, equipamiento, posición en mazmorra, progreso por piso
- **Ubicación**: `src/assets/saves/save_slot_X.json`

---

## Dificultad

| Nivel | Multiplicador |
|-------|---------------|
| Easy | 0.7x |
| Normal | 1.0x |
| Hard | 1.3x |
| Nightmare | 1.5x |

La dificultad afecta stats de enemigos y recompensas.

---

## Cómo Ejecutar

```bash
# Instalar dependencias
pip install pygame

# Ejecutar el juego
python main.py
```

---

## Objetivo del Juego

1. Seleccionar una clase
2. Ingresar tu nombre
3. Explorar la mazmorra piso por piso
4. Derrotar elites para desbloquear escaleras
5. Derrotar al Boss del piso 8
6. ¡Victoria!

---

## Estado del Proyecto

El juego está **completo y funcional** con todas las características implementadas:
- Menú principal
- Selección de clase
- Exploración de mazmorra
- Combate por turnos
- Sistema de equipamiento
- Mercader y santuario
- Guardado y carga
- Pantallas de victoria/derrota

---

## Licencia

Proyecto de ejemplo educativo.
