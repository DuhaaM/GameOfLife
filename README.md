# Conway's Game of Life

This project contains two interactive versions of Conway's Game of Life:

1. **A web version**: [`Game/game_of_life_web.html`](Game/game_of_life_web.html).
   It runs in any modern browser, on computers as well as phones and tablets.
2. **A desktop version**: [`Python/jeu_de_la_vie.py`](Python/jeu_de_la_vie.py).
   It is a Python program built with the pygame library.

Both versions use the same rules and can import patterns from the
[conwaylife.com wiki](https://conwaylife.com/wiki/).

---

## 1. What is the Game of Life?

The Game of Life is a "zero-player game" invented by the mathematician
John Horton Conway in 1970. It takes place on a grid of square cells. Each
cell is either **alive** or **dead**. You draw a starting configuration, start
the simulation, and watch how it evolves on its own.

At every step (called a **generation**), each cell looks at its 8 neighbours
(horizontal, vertical and diagonal). The following rules are applied to all
cells at the same time:

| Rule         | Description                                                                    |
|--------------|--------------------------------------------------------------------------------|
| **Birth**    | A dead cell with exactly 3 living neighbours becomes alive.                    |
| **Survival** | A living cell with 2 or 3 living neighbours stays alive.                       |
| **Death**    | In every other case, the cell dies (loneliness or overcrowding) or stays dead. |

These rules are written **B3/S23** (Born with 3, Survives with 2 or 3).

These rules are very simple, but they produce surprisingly complex behaviours:

- **Still lifes**: patterns that never change.
- **Oscillators**: patterns that repeat after a few generations (Pulsar).
- **Spaceships**: patterns that move across the grid (Glider, LWSS).
- **Guns**: patterns that produce spaceships forever (Gosper glider gun).
- **Methuselahs**: tiny patterns that evolve for a very long time (R-pentomino, Acorn).

---

## 2. The web version (`Game/game_of_life_web.html`)

### 2.1 Launching

No installation is needed. Open `game_of_life_web.html` in a web browser
(Firefox, Chrome, Edge, Safari, etc.), for example by double-clicking it.
The game only uses the internet to load its fonts, so it works offline too.

When the game starts, a Gosper glider gun is already on the grid and the
simulation is running.

### 2.2 Screen layout

- **Top bar**: shows the title and the simulation engine in use (GPU or CPU).
  It also shows the current **generation** number and the **population**
  (the number of living cells).
- **Centre**: the grid.
- **Bottom bar**: the control buttons.

### 2.3 Buttons

| Button          | Action                                                                                                                                       |
|-----------------|----------------------------------------------------------------------------------------------------------------------------------------------|
| **Play / Pause**| Start or stop the simulation.                                                                                                                |
| **+1**          | Pause and advance by exactly one generation.                                                                                                 |
| **Move / Draw** | Choose the tool used on the grid. **Move**: drag to move around the grid. **Draw**: click or drag to draw cells (starting on a living cell erases instead). |
| **Patterns**    | Open the pattern library (see 2.5).                                                                                                          |
| **− / +**       | Zoom out / zoom in.                                                                                                                          |
| **Fit**         | Zoom and centre the view on all living cells.                                                                                                |
| **Random**      | Fill the visible area with random cells.                                                                                                     |
| **Clear**       | Erase every cell and reset the generation counter.                                                                                           |
| **Speed**       | Slider from 1 to 240 generations per second.                                                                                                 |

### 2.4 Mouse, touch and keyboard

| Input                      | Action                                              |
|----------------------------|-----------------------------------------------------|
| Mouse wheel                | Zoom in / out around the mouse pointer.             |
| Right or middle drag       | Move the view, whatever tool is selected.           |
| Pinch with two fingers     | Zoom and move the view (phones and tablets).        |
| `Space`                    | Play / pause.                                       |
| `N`                        | Advance by one generation.                          |
| Arrow keys                 | Move the view.                                      |
| `Escape`                   | Close the pattern library or cancel a placement.    |

### 2.5 Pattern library

The **Patterns** button opens a list of famous patterns, each shown with a
small preview: Glider, Lightweight spaceship (LWSS), Pulsar, R-pentomino,
Acorn, Diehard, Gosper glider gun and Copperhead.

- If *"Clear the grid before placing the pattern"* is ticked, the grid is
  emptied and the pattern is placed in the centre of the view.
- If it is not ticked, the library closes. Then click (or tap) the grid
  where you want the pattern.

You can also import **any** pattern from the conwaylife.com wiki:

1. Copy the RLE code from a pattern's page. For example, the code for a
   glider is `bob$2bo$3o!`.
2. Paste it in the text box at the bottom of the library.
3. Press **Place this pattern**.

The plaintext `.cells` format works too.

### 2.6 How it works

- **GPU engine (default)**: the universe is stored as an image of up to
  4096 × 4096 cells (2048 × 2048 on phones). The graphics card computes every
  generation with WebGL, updating all cells in parallel, so very large and
  very fast simulations are possible. The edges of the grid are connected,
  like a *torus*: a glider leaving on the right comes back on the left.
- **CPU engine (fallback)**: used only if WebGL is not available. It stores
  only the living cells, so the grid is practically unlimited. However, it is
  slower on big patterns.

The top bar shows which engine is in use.

---

## 3. The Python version (`Python/jeu_de_la_vie.py`)

> **Note:** the texts displayed in this version's window are in French.

### 3.1 Installation and launching

Requirements: Python 3 and the pygame library.

```bash
pip install pygame
python Python/jeu_de_la_vie.py
```

When the program starts, a Gosper glider gun is already on the grid and the
simulation is paused. Press `Space` to start it.

### 3.2 Screen layout

The information bar at the top shows:

- the state (`LECTURE` = running, `PAUSE` = paused);
- the generation number;
- the population;
- the speed in generations per second;
- the zoom level;
- help or messages.

### 3.3 Controls

**Drawing**

| Input               | Action               |
|---------------------|----------------------|
| Left click (hold)   | Draw living cells.   |
| Right click (hold)  | Erase cells.         |

**Moving and zooming**

| Input                | Action                                   |
|----------------------|------------------------------------------|
| Mouse wheel          | Zoom in / out around the mouse pointer.  |
| `I` / `O`            | Zoom in / out with the keyboard.         |
| Arrow keys           | Move the view.                           |
| Middle click (hold)  | Drag the view.                           |
| `H`                  | Go back to the starting view.            |

**Simulation**

| Key        | Action                                           |
|------------|--------------------------------------------------|
| `Space`    | Play / pause.                                    |
| `N`        | Advance by one generation (when paused).         |
| `A` / `D`  | Speed up / slow down (1 to 60 generations/s).    |
| `C`        | Clear the whole grid.                            |
| `R`        | Fill the visible area randomly.                  |
| `Escape`   | Quit.                                            |

**Built-in patterns** (placed at the mouse position)

| Key | Pattern                        |
|-----|--------------------------------|
| `1` | Glider                         |
| `2` | Lightweight spaceship (LWSS)   |
| `3` | Pulsar                         |
| `4` | R-pentomino                    |
| `5` | Gosper glider gun              |

The number keys work on QWERTY and AZERTY keyboards (no need to press
`Shift`) and on the numeric keypad.

### 3.4 Importing patterns from the conwaylife.com wiki

There are three ways to import a pattern. The pattern is always placed
centred on the mouse pointer.

| Input          | Action                                                                                                                                                                                                                                  |
|----------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `T`            | Type the name of a pattern, then press `Enter` to download it (internet connection required). The name is the `.rle` file name shown on the pattern's wiki page, e.g. `gosperglidergun`, `acorn` or `copperhead`. A full http(s) address also works. `Escape` cancels the typing. |
| `Ctrl+V`       | Paste a pattern copied from the wiki (RLE code or the content of a `.cells` file).                                                                                                                                                      |
| Drag & drop    | Drop a `.rle` or `.cells` file onto the window.                                                                                                                                                                                         |
| `0`            | Place the last imported pattern again.                                                                                                                                                                                                  |

Some patterns are designed for a rule other than B3/S23. When you import one,
the information bar shows a warning, because the pattern will not behave as
expected.

### 3.5 How it works

The grid is infinite: the program stores only the coordinates of the living
cells. To compute the next generation, it counts the living neighbours of
each cell that touches a living cell. Then it applies the B3/S23 rules. The
program draws only the cells inside the view, and it hides the grid lines when
the cells become too small.

---

## 4. Ideas to get started

- Place a single **Glider** and watch it travel diagonally.
- Place an **R-pentomino** (only 5 cells) and see how long it takes to settle
  (1103 generations).
- Draw a horizontal line of 3 cells: it becomes a **blinker**, the simplest
  oscillator.
- Use **Random** (or `R`) and watch the chaos slowly turn into still lifes,
  oscillators and gliders.
- Browse the [conwaylife.com wiki](https://conwaylife.com/wiki/) and import
  your favourite patterns.
