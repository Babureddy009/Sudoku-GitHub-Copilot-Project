from flask import Flask

from game_state import CURRENT
from routes import sudoku_bp

app = Flask(__name__)
app.register_blueprint(sudoku_bp)

if __name__ == '__main__':
    app.run(debug=True)