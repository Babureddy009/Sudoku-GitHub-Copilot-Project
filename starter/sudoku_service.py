"""Reusable service functions for Sudoku game flow."""

import random

import sudoku_logic

DIFFICULTY_TO_CLUES = {
    'easy': 40,
    'medium': 32,
    'hard': 26,
}


def get_clues_from_request(clues_value, default=35):
    """Parse clue count from request args and fall back to default."""
    if clues_value is None:
        return default
    return int(clues_value)


def get_clues_from_difficulty(difficulty_value, default='medium'):
    """Resolve puzzle clues from difficulty name with default fallback."""
    difficulty = (difficulty_value or default).lower()
    return DIFFICULTY_TO_CLUES.get(difficulty, DIFFICULTY_TO_CLUES[default])


def create_new_game(clues):
    """Generate and return a new puzzle and solution pair."""
    return sudoku_logic.generate_puzzle(clues)


def analyze_board(board, solution):
    """Compare board against solution and return cell-level check details."""
    incorrect = []
    correct = []
    empty_count = 0

    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            value = board[row][col]
            if value == sudoku_logic.EMPTY:
                empty_count += 1
            elif value == solution[row][col]:
                correct.append([row, col])
            else:
                incorrect.append([row, col])

    return {
        'incorrect': incorrect,
        'correct': correct,
        'incorrect_count': len(incorrect),
        'empty_count': empty_count,
        'is_complete_correct': len(incorrect) == 0 and empty_count == 0,
    }


def get_incorrect_cells(board, solution):
    """Return [row, col] cells where board does not match solution."""
    return analyze_board(board, solution)['incorrect']


def get_random_hint(board, solution):
    """Return a random empty cell and its correct value from the solution."""
    empty_cells = []
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] == sudoku_logic.EMPTY:
                empty_cells.append((row, col))

    if not empty_cells:
        return None

    row, col = random.choice(empty_cells)
    return {
        'row': row,
        'col': col,
        'value': solution[row][col],
    }