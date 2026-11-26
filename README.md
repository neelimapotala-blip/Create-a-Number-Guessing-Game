# Number Quest — Number Guessing Game

A responsive Python Flask game with a SQLite leaderboard.

## Features
- Random number from 1 to 100
- High/low hints and attempt counter
- Input validation
- New game option
- SQLite database stores completed scores
- Responsive HTML/CSS interface

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Create and activate a virtual environment (recommended).
4. Install dependencies:

   `pip install -r requirements.txt`

5. Start the app:

   `python app.py`

6. Open `http://127.0.0.1:5000` in your browser.

The SQLite database (`game.db`) is created automatically the first time the app runs.

For deployment, set a strong secret key using an environment variable and turn off Flask debug mode.
