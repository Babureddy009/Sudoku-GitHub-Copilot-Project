import os
import sys

# Ensure tests can import app.py and sudoku_logic.py when run from workspace root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
