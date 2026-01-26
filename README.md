# Logastroids

Asteroid-style PyGame shooter with rotating thrust controls, shields, and leveling.

## Quick Start

From the project root:

```bash
./run-game
```

The `run-game` script will automatically:
- Create a virtual environment if needed
- Install/update dependencies from `requirements.txt` (only when changed)
- Launch the game

Assets live under `sprite-sheets/`. High scores are stored in `high_scores.json` in the project root.

---

## Detailed Setup (Manual Installation)

### Requirements
- Python 3.10+ (tested on 3.13)
- SDL dependencies for PyGame (installed by default on most systems)
- Project Python deps are listed in `requirements.txt`

### Manual Setup (macOS/Linux)
From the project root:

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Running the game manually
With the virtualenv active:

```bash
python spaceship_game.py
```
