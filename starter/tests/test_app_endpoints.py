from app import app, CURRENT


def count_non_empty_cells(board):
    return sum(1 for row in board for cell in row if cell != 0)


def test_new_endpoint_returns_puzzle_and_sets_current_solution():
    client = app.test_client()

    response = client.get('/new?clues=35')
    assert response.status_code == 200

    payload = response.get_json()
    assert 'puzzle' in payload
    puzzle = payload['puzzle']
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)

    assert CURRENT['puzzle'] is not None
    assert CURRENT['solution'] is not None


def test_check_endpoint_returns_error_when_no_game_started():
    client = app.test_client()

    CURRENT['puzzle'] = None
    CURRENT['solution'] = None

    response = client.post('/check', json={'board': [[0] * 9 for _ in range(9)]})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_check_endpoint_returns_incorrect_cells_for_mismatches():
    client = app.test_client()

    client.get('/new?clues=35')
    solution = CURRENT['solution']

    board = [row[:] for row in solution]
    board[0][0] = (board[0][0] % 9) + 1
    if board[0][0] == solution[0][0]:
        board[0][0] = ((board[0][0] + 1) % 9) + 1

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200

    payload = response.get_json()
    assert 'incorrect' in payload
    assert 'correct' in payload
    assert 'incorrect_count' in payload
    assert 'empty_count' in payload
    assert 'is_complete_correct' in payload
    assert [0, 0] in payload['incorrect']
    assert payload['incorrect_count'] >= 1
    assert payload['empty_count'] == 0
    assert payload['is_complete_correct'] is False


def test_check_endpoint_reports_complete_when_board_is_correct():
    client = app.test_client()

    client.get('/new?clues=35')
    solution = CURRENT['solution']
    board = [row[:] for row in solution]

    response = client.post('/check', json={'board': board})
    assert response.status_code == 200

    payload = response.get_json()
    assert payload['incorrect'] == []
    assert payload['incorrect_count'] == 0
    assert payload['empty_count'] == 0
    assert payload['is_complete_correct'] is True


def test_hint_endpoint_returns_error_when_no_game_started():
    client = app.test_client()

    CURRENT['puzzle'] = None
    CURRENT['solution'] = None

    response = client.post('/hint', json={'board': [[0] * 9 for _ in range(9)]})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_hint_endpoint_returns_complete_message_for_full_board():
    client = app.test_client()

    client.get('/new?clues=35')
    full_board = [row[:] for row in CURRENT['solution']]

    response = client.post('/hint', json={'board': full_board})
    assert response.status_code == 200
    assert response.get_json() == {'message': 'Puzzle is already complete.'}


def test_hint_endpoint_returns_correct_value_for_empty_cell(monkeypatch):
    client = app.test_client()

    client.get('/new?clues=35')
    solution = CURRENT['solution']
    board = [row[:] for row in solution]
    board[0][0] = 0
    board[1][1] = 0

    monkeypatch.setattr('sudoku_service.random.choice', lambda seq: (0, 0))

    response = client.post('/hint', json={'board': board})
    assert response.status_code == 200

    payload = response.get_json()
    assert 'hint' in payload
    assert payload['hint'] == {'row': 0, 'col': 0, 'value': solution[0][0]}


def test_new_endpoint_uses_medium_difficulty_when_provided():
    client = app.test_client()

    response = client.get('/new?difficulty=medium')
    assert response.status_code == 200

    puzzle = response.get_json()['puzzle']
    assert count_non_empty_cells(puzzle) == 32


def test_new_endpoint_difficulty_clue_counts():
    client = app.test_client()

    easy = client.get('/new?difficulty=easy').get_json()['puzzle']
    medium = client.get('/new?difficulty=medium').get_json()['puzzle']
    hard = client.get('/new?difficulty=hard').get_json()['puzzle']

    assert count_non_empty_cells(easy) == 40
    assert count_non_empty_cells(medium) == 32
    assert count_non_empty_cells(hard) == 26


def test_new_endpoint_invalid_difficulty_falls_back_to_medium():
    client = app.test_client()

    response = client.get('/new?difficulty=expert')
    assert response.status_code == 200

    puzzle = response.get_json()['puzzle']
    assert count_non_empty_cells(puzzle) == 32


def test_validate_cell_endpoint_returns_error_when_no_game_started():
    client = app.test_client()

    CURRENT['puzzle'] = None
    CURRENT['solution'] = None

    response = client.post('/validate-cell', json={'row': 0, 'col': 0, 'value': 1})
    assert response.status_code == 400
    assert response.get_json() == {'error': 'No game in progress'}


def test_validate_cell_endpoint_identifies_fixed_clues():
    client = app.test_client()

    client.get('/new?difficulty=easy')
    puzzle = CURRENT['puzzle']

    fixed_row = None
    fixed_col = None
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] != 0:
                fixed_row = row
                fixed_col = col
                break
        if fixed_row is not None:
            break

    assert fixed_row is not None and fixed_col is not None

    response = client.post(
        '/validate-cell',
        json={'row': fixed_row, 'col': fixed_col, 'value': 1}
    )
    assert response.status_code == 200
    assert response.get_json() == {'is_fixed_clue': True, 'is_correct': True}


def test_validate_cell_endpoint_marks_correct_and_incorrect_values():
    client = app.test_client()

    client.get('/new?difficulty=easy')
    puzzle = CURRENT['puzzle']
    solution = CURRENT['solution']

    editable_row = None
    editable_col = None
    for row in range(9):
        for col in range(9):
            if puzzle[row][col] == 0:
                editable_row = row
                editable_col = col
                break
        if editable_row is not None:
            break

    assert editable_row is not None and editable_col is not None

    correct_value = solution[editable_row][editable_col]

    incorrect_value = (correct_value % 9) + 1
    if incorrect_value == correct_value:
        incorrect_value = ((incorrect_value + 1) % 9) + 1

    incorrect_response = client.post(
        '/validate-cell',
        json={'row': editable_row, 'col': editable_col, 'value': incorrect_value}
    )
    assert incorrect_response.status_code == 200
    assert incorrect_response.get_json() == {'is_fixed_clue': False, 'is_correct': False}

    correct_response = client.post(
        '/validate-cell',
        json={'row': editable_row, 'col': editable_col, 'value': correct_value}
    )
    assert correct_response.status_code == 200
    assert correct_response.get_json() == {'is_fixed_clue': False, 'is_correct': True}
