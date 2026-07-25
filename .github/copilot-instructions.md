# GitHub Copilot Instructions

You are assisting with a Python Flask Sudoku project.

## General Rules

- Use Python 3.11+
- Write clean, modular code.
- Keep functions small and reusable.
- Use descriptive variable names.
- Avoid duplicate code.
- Add docstrings to public functions.
- Follow PEP8.

## Flask

- Keep routes simple.
- Move business logic into separate modules.
- Handle exceptions gracefully.
- Return JSON from API endpoints where appropriate.

## Sudoku

- Every generated puzzle must have exactly one solution.
- Support Easy, Medium and Hard difficulties.
- Validate rows, columns and 3×3 grids.
- Lock prefilled cells.

## Frontend

- Responsive layout
- Light and Dark mode
- Highlight invalid cells
- Highlight hint-filled cells
- Use modern JavaScript (ES6)

## Testing

- Use pytest.
- Keep tests readable.
- Don't break existing functionality.