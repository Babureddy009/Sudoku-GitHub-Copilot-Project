// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_STORAGE_KEY = 'sudokuLeaderboardV1';
const THEME_STORAGE_KEY = 'sudokuThemePreferenceV1';
const LEADERBOARD_LIMIT = 10;
let puzzle = [];
let elapsedSeconds = 0;
let timerIntervalId = null;
let validationRequestCounter = 0;
let hasRecordedWinForCurrentGame = false;
let currentGameDifficulty = 'Medium';
let currentGameHintsUsed = 0;

function normalizeDifficulty(value) {
  const normalizedValue = String(value || '').trim().toLowerCase();
  if (normalizedValue === 'easy') {
    return 'Easy';
  }
  if (normalizedValue === 'hard') {
    return 'Hard';
  }
  return 'Medium';
}

function normalizeHintsUsed(value) {
  const parsedValue = Number.parseInt(String(value), 10);
  return Number.isInteger(parsedValue) && parsedValue >= 0 ? parsedValue : 0;
}

function getStoredTheme() {
  const storedTheme = localStorage.getItem(THEME_STORAGE_KEY);
  return storedTheme === 'dark' ? 'dark' : 'light';
}

function updateThemeToggleButton(theme) {
  const toggleButton = document.getElementById('theme-toggle');
  if (!toggleButton) {
    return;
  }

  const isDarkTheme = theme === 'dark';
  toggleButton.innerText = isDarkTheme ? 'Light Mode' : 'Dark Mode';
  toggleButton.setAttribute('aria-pressed', String(isDarkTheme));
}

function applyTheme(theme) {
  document.body.setAttribute('data-theme', theme);
  updateThemeToggleButton(theme);
}

function toggleTheme() {
  const nextTheme = document.body.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
  localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  applyTheme(nextTheme);
}

function formatElapsedTime(totalSeconds) {
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  const timerElement = document.getElementById('timer');
  if (timerElement) {
    timerElement.innerText = `Time: ${formatElapsedTime(elapsedSeconds)}`;
  }
}

function sanitizePlayerName(name) {
  const normalizedName = String(name || '').trim();
  return normalizedName.slice(0, 24);
}

function setStatusMessage(text, variant = 'info') {
  const messageElement = document.getElementById('message');
  if (!messageElement) {
    return;
  }

  const normalizedText = String(text || '').trim();
  if (!normalizedText) {
    messageElement.innerText = '';
    messageElement.removeAttribute('data-variant');
    return;
  }

  const iconByVariant = {
    success: '✅',
    warning: '⚠️',
    error: '❌',
    completion: '🎉'
  };

  const allowedVariant = (
    variant === 'success'
    || variant === 'warning'
    || variant === 'error'
    || variant === 'completion'
  ) ? variant : 'warning';

  const prefix = iconByVariant[allowedVariant] || iconByVariant.warning;
  messageElement.innerText = `${prefix} ${normalizedText}`;
  messageElement.setAttribute('data-variant', allowedVariant);
}

function loadLeaderboardEntries() {
  try {
    const raw = localStorage.getItem(LEADERBOARD_STORAGE_KEY);
    if (!raw) {
      return [];
    }

    const parsed = JSON.parse(raw);
    if (!Array.isArray(parsed)) {
      return [];
    }

    return parsed
      .filter((entry) => Number.isInteger(entry.seconds) && entry.seconds >= 0)
      .map((entry) => ({
        name: sanitizePlayerName(entry.name),
        seconds: entry.seconds,
        difficulty: normalizeDifficulty(entry.difficulty),
        hintsUsed: normalizeHintsUsed(entry.hintsUsed),
        completedAt: Number.isInteger(entry.completedAt) ? entry.completedAt : 0
      }));
  } catch (error) {
    return [];
  }
}

function saveLeaderboardEntries(entries) {
  localStorage.setItem(LEADERBOARD_STORAGE_KEY, JSON.stringify(entries));
}

function sortAndTrimLeaderboard(entries) {
  return [...entries]
    .sort((a, b) => {
      if (a.seconds !== b.seconds) {
        return a.seconds - b.seconds;
      }
      return a.completedAt - b.completedAt;
    })
    .slice(0, LEADERBOARD_LIMIT);
}

function renderLeaderboard() {
  const leaderboardBody = document.getElementById('leaderboard-body');
  if (!leaderboardBody) {
    return;
  }

  const entries = sortAndTrimLeaderboard(loadLeaderboardEntries());
  leaderboardBody.innerHTML = '';

  if (entries.length === 0) {
    const emptyRow = document.createElement('tr');
    const emptyCell = document.createElement('td');
    emptyCell.className = 'leaderboard-empty';
    emptyCell.colSpan = 5;
    emptyCell.innerText = 'No completed games yet.';
    emptyRow.appendChild(emptyCell);
    leaderboardBody.appendChild(emptyRow);
    return;
  }

  entries.forEach((entry, index) => {
    const row = document.createElement('tr');
    const displayName = entry.name || 'Anonymous';

    const rankCell = document.createElement('td');
    rankCell.innerText = String(index + 1);
    row.appendChild(rankCell);

    const nameCell = document.createElement('td');
    nameCell.innerText = displayName;
    row.appendChild(nameCell);

    const timeCell = document.createElement('td');
    timeCell.innerText = formatElapsedTime(entry.seconds);
    row.appendChild(timeCell);

    const difficultyCell = document.createElement('td');
    difficultyCell.innerText = entry.difficulty;
    row.appendChild(difficultyCell);

    const hintsUsedCell = document.createElement('td');
    hintsUsedCell.innerText = String(entry.hintsUsed);
    row.appendChild(hintsUsedCell);

    leaderboardBody.appendChild(row);
  });
}

function recordSolvedGame() {
  if (hasRecordedWinForCurrentGame) {
    return;
  }

  const playerNameInput = document.getElementById('player-name');
  const playerName = playerNameInput ? sanitizePlayerName(playerNameInput.value) : '';

  const nextEntries = sortAndTrimLeaderboard([
    ...loadLeaderboardEntries(),
    {
      name: playerName,
      seconds: elapsedSeconds,
      difficulty: currentGameDifficulty,
      hintsUsed: currentGameHintsUsed,
      completedAt: Date.now()
    }
  ]);

  saveLeaderboardEntries(nextEntries);
  hasRecordedWinForCurrentGame = true;
  renderLeaderboard();
}

function stopTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
}

function startTimer() {
  stopTimer();
  timerIntervalId = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function resetAndStartTimer() {
  elapsedSeconds = 0;
  updateTimerDisplay();
  startTimer();
}

function applyLiveValidationStyle(inputElement, isIncorrect) {
  if (inputElement.disabled) {
    return;
  }
  inputElement.className = isIncorrect ? 'sudoku-cell incorrect' : 'sudoku-cell';
}

async function validateCellLive(inputElement, row, col, value) {
  if (inputElement.disabled || puzzle[row][col] !== 0) {
    return;
  }

  if (!value) {
    applyLiveValidationStyle(inputElement, false);
    return;
  }

  const requestId = ++validationRequestCounter;
  inputElement.dataset.validationRequestId = String(requestId);

  try {
    const response = await fetch('/validate-cell', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        row,
        col,
        value: parseInt(value, 10)
      })
    });

    const data = await response.json();
    if (inputElement.dataset.validationRequestId !== String(requestId)) {
      return;
    }

    if (!response.ok || data.error || data.is_fixed_clue) {
      return;
    }

    applyLiveValidationStyle(inputElement, !data.is_correct);
  } catch (error) {
    // Keep gameplay uninterrupted if live-validation network requests fail.
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const target = e.target;
        const val = e.target.value.replace(/[^1-9]/g, '');
        target.value = val;
        const row = parseInt(target.dataset.row, 10);
        const col = parseInt(target.dataset.col, 10);
        validateCellLive(target, row, col, val);
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

function readBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

async function newGame() {
  const difficultySelect = document.getElementById('difficulty');
  const difficulty = difficultySelect ? difficultySelect.value : 'medium';
  currentGameDifficulty = normalizeDifficulty(difficulty);
  currentGameHintsUsed = 0;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  hasRecordedWinForCurrentGame = false;
  resetAndStartTimer();
  setStatusMessage('');
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = readBoardFromInputs();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  if (data.error) {
    setStatusMessage(data.error, 'error');
    return;
  }

  const incorrect = new Set((data.incorrect || []).map(x => x[0] * SIZE + x[1]));
  const correct = new Set((data.correct || []).map(x => x[0] * SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    } else if (correct.has(idx)) {
      inp.className = 'sudoku-cell correct';
    }
  }

  if (data.is_complete_correct) {
    stopTimer();
    recordSolvedGame();
    setStatusMessage('Congratulations! You solved the puzzle.', 'completion');
  } else {
    const incorrectCount = Number.isInteger(data.incorrect_count) ? data.incorrect_count : incorrect.size;
    const emptyCount = Number.isInteger(data.empty_count)
      ? data.empty_count
      : board.flat().filter(cell => cell === 0).length;

    if (incorrectCount > 0) {
      const incorrectMessage = incorrectCount === 1
        ? 'There is 1 incorrect entry.'
        : `There are ${incorrectCount} incorrect entries.`;

      if (emptyCount > 0) {
        setStatusMessage(`${incorrectMessage} Fill the remaining ${emptyCount} empty cell(s).`, 'warning');
      } else {
        setStatusMessage(incorrectMessage, 'warning');
      }
    } else {
      setStatusMessage(`No mistakes so far. Fill the remaining ${emptyCount} empty cell(s).`, 'success');
    }
  }
}

async function useHint() {
  currentGameHintsUsed += 1;
  const board = readBoardFromInputs();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });

  const data = await res.json();
  if (data.error) {
    setStatusMessage(data.error, 'error');
    return;
  }

  if (data.message) {
    setStatusMessage(data.message, 'warning');
    return;
  }

  const hint = data.hint;
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const idx = hint.row * SIZE + hint.col;
  const targetInput = inputs[idx];

  targetInput.value = hint.value;
  targetInput.disabled = true;
  targetInput.className = 'sudoku-cell hint-filled';

  setStatusMessage(`Hint used: filled row ${hint.row + 1}, column ${hint.col + 1}.`, 'warning');
}

// Wire buttons
window.addEventListener('load', () => {
  applyTheme(getStoredTheme());
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('use-hint').addEventListener('click', useHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  updateTimerDisplay();
  renderLeaderboard();
  // initialize
  newGame();
});