import sudoku_logic


def test_create_empty_board_shape_and_values():
    board = sudoku_logic.create_empty_board()
    assert len(board) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in board)
    assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)


def test_deep_copy_returns_independent_copy():
    board = sudoku_logic.create_empty_board()
    clone = sudoku_logic.deep_copy(board)
    clone[0][0] = 7
    assert board[0][0] == sudoku_logic.EMPTY
    assert clone[0][0] == 7


def test_is_safe_detects_row_column_and_box_conflicts():
    board = sudoku_logic.create_empty_board()
    board[0][1] = 5
    board[1][0] = 6
    board[1][1] = 7

    assert not sudoku_logic.is_safe(board, 0, 0, 5)  # row conflict
    assert not sudoku_logic.is_safe(board, 0, 0, 6)  # column conflict
    assert not sudoku_logic.is_safe(board, 0, 0, 7)  # 3x3 box conflict
    assert sudoku_logic.is_safe(board, 0, 0, 8)


def test_generate_puzzle_returns_valid_shapes_and_clue_count():
    clues = 35
    puzzle, solution = sudoku_logic.generate_puzzle(clues)

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(len(row) == sudoku_logic.SIZE for row in solution)

    non_empty = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
    assert non_empty == clues

    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if puzzle[i][j] != sudoku_logic.EMPTY:
                assert puzzle[i][j] == solution[i][j]


def test_generate_puzzle_has_unique_solution_for_difficulty_clues():
    for clues in (40, 32, 26):
        puzzle, _ = sudoku_logic.generate_puzzle(clues)
        solutions = sudoku_logic.count_solutions(sudoku_logic.deep_copy(puzzle), limit=2)
        assert solutions == 1


def test_remove_cells_checks_uniqueness_before_removal_commit(monkeypatch):
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)

    calls = {'count': 0}

    def fake_count_solutions(_board, limit=2):
        calls['count'] += 1
        return 1

    monkeypatch.setattr(sudoku_logic.random, 'shuffle', lambda seq: None)
    monkeypatch.setattr(sudoku_logic, 'count_solutions', fake_count_solutions)

    assert sudoku_logic.remove_cells_keeping_unique(board, clues=80)
    assert calls['count'] == 1


def test_remove_cells_restores_cell_when_uniqueness_breaks(monkeypatch):
    board = sudoku_logic.create_empty_board()
    assert sudoku_logic.fill_board(board)
    original = sudoku_logic.deep_copy(board)

    def fake_count_solutions(_board, limit=2):
        return 2

    monkeypatch.setattr(sudoku_logic.random, 'shuffle', lambda seq: None)
    monkeypatch.setattr(sudoku_logic, 'count_solutions', fake_count_solutions)

    assert not sudoku_logic.remove_cells_keeping_unique(board, clues=80)
    assert board == original
