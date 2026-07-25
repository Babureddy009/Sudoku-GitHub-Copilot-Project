# Sudoku Flask Project

This project is a web-based Sudoku game built with Flask and modern JavaScript. It generates playable Sudoku puzzles, validates user moves, and provides a polished user interface with gameplay helpers and persistent local leaderboard tracking.

## Features

- Difficulty selector (Easy, Medium, Hard)
- Unique solution validation for generated puzzles
- Timer
- Hint button
- Check solution
- Live validation
- Top 10 leaderboard
- Dark/Light mode
- Responsive UI

## Tech Stack

- Python 3.11+
- Flask
- Vanilla JavaScript (ES6)
- HTML/CSS
- Pytest

## Installation and Setup

1. Clone the repository.
2. Open a terminal and move into the starter app directory:

```bash
cd starter
```

3. Create a virtual environment:

```bash
python -m venv .venv
```

4. Activate the virtual environment:

Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the Application

From the starter directory:

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:5000
```

## Run the Tests

From the starter directory:

```bash
python -m pytest -q
```

## Notes

- The leaderboard is stored in browser local storage.
- GitHub Copilot was used during development to help implement and refine features.
