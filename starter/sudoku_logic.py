import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def find_empty_cell(board):
    """Return the first empty cell coordinates, or None when board is full."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                return row, col
    return None

def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, limit=2):
    """Count Sudoku solutions up to limit, returning early once reached."""
    empty_cell = find_empty_cell(board)
    if empty_cell is None:
        return 1

    row, col = empty_cell
    solutions = 0
    for candidate in range(1, SIZE + 1):
        if is_safe(board, row, col, candidate):
            board[row][col] = candidate
            solutions += count_solutions(board, limit=limit)
            board[row][col] = EMPTY
            if solutions >= limit:
                return solutions
    return solutions


def remove_cells_keeping_unique(board, clues):
    """Remove cells while preserving a single-solution puzzle."""
    cells_to_remove = SIZE * SIZE - clues
    removed = 0

    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    for row, col in positions:
        if removed >= cells_to_remove:
            break
        if board[row][col] == EMPTY:
            continue

        original = board[row][col]
        board[row][col] = EMPTY

        board_for_count = deep_copy(board)
        if count_solutions(board_for_count, limit=2) == 1:
            removed += 1
        else:
            board[row][col] = original

    return removed == cells_to_remove

def generate_puzzle(clues=35):
    if clues < 0 or clues > SIZE * SIZE:
        raise ValueError(f"clues must be between 0 and {SIZE * SIZE}")

    max_generation_attempts = 200
    for _ in range(max_generation_attempts):
        board = create_empty_board()
        fill_board(board)
        solution = deep_copy(board)
        puzzle = deep_copy(board)

        if remove_cells_keeping_unique(puzzle, clues):
            return puzzle, solution

    raise RuntimeError("Unable to generate a unique puzzle for the requested clue count")
