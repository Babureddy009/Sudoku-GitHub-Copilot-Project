"""Flask routes for Sudoku pages and API endpoints."""

from flask import Blueprint, jsonify, render_template, request

from game_state import CURRENT
from sudoku_service import (
    analyze_board,
    create_new_game,
    get_clues_from_difficulty,
    get_clues_from_request,
    get_random_hint,
)

sudoku_bp = Blueprint('sudoku', __name__)


@sudoku_bp.route('/')
def index():
    return render_template('index.html')


@sudoku_bp.route('/new')
def new_game():
    clues_value = request.args.get('clues')
    if clues_value is not None:
        clues = get_clues_from_request(clues_value)
    else:
        clues = get_clues_from_difficulty(request.args.get('difficulty'))
    puzzle, solution = create_new_game(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})


@sudoku_bp.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    analysis = analyze_board(board, solution)
    return jsonify(analysis)


@sudoku_bp.route('/hint', methods=['POST'])
def get_hint():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    hint = get_random_hint(board, solution)
    if hint is None:
        return jsonify({'message': 'Puzzle is already complete.'})

    return jsonify({'hint': hint})


@sudoku_bp.route('/validate-cell', methods=['POST'])
def validate_cell():
    data = request.json or {}
    row = data.get('row')
    col = data.get('col')
    value = data.get('value')

    solution = CURRENT.get('solution')
    puzzle = CURRENT.get('puzzle')
    if solution is None or puzzle is None:
        return jsonify({'error': 'No game in progress'}), 400

    if not all(isinstance(idx, int) for idx in (row, col)):
        return jsonify({'error': 'row and col must be integers'}), 400

    if not (0 <= row < 9 and 0 <= col < 9):
        return jsonify({'error': 'row and col out of range'}), 400

    if puzzle[row][col] != 0:
        return jsonify({'is_fixed_clue': True, 'is_correct': True})

    if not isinstance(value, int) or not (1 <= value <= 9):
        return jsonify({'error': 'value must be an integer from 1 to 9'}), 400

    return jsonify({
        'is_fixed_clue': False,
        'is_correct': value == solution[row][col],
    })