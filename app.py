from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import sqlite3
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key-for-deployment"
DB_PATH = Path(__file__).with_name("game.db")


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS scores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_name TEXT NOT NULL,
                attempts INTEGER NOT NULL,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("player_name", "").strip()[:20]
        if not name:
            flash("Please enter your name to start.", "error")
            return redirect(url_for("index"))

        session.clear()
        session["player_name"] = name
        session["secret_number"] = random.randint(1, 100)
        session["attempts"] = 0
        session["game_over"] = False
        session["message"] = "I'm thinking of a number between 1 and 100. Good luck!"
        return redirect(url_for("game"))

    return render_template("index.html")


@app.route("/game", methods=["GET", "POST"])
def game():
    if "secret_number" not in session:
        return redirect(url_for("index"))

    if request.method == "POST" and not session.get("game_over"):
        raw_guess = request.form.get("guess", "").strip()

        try:
            guess = int(raw_guess)
            if not 1 <= guess <= 100:
                raise ValueError
        except ValueError:
            session["message"] = "Enter a whole number from 1 to 100."
            session["message_type"] = "error"
            return redirect(url_for("game"))

        session["attempts"] += 1
        secret = session["secret_number"]

        if guess < secret:
            session["message"] = "Too low! Try a higher number."
            session["message_type"] = "info"
        elif guess > secret:
            session["message"] = "Too high! Try a lower number."
            session["message_type"] = "info"
        else:
            session["message"] = f"Correct! You guessed it in {session['attempts']} attempts."
            session["message_type"] = "success"
            session["game_over"] = True

            with get_db() as db:
                db.execute(
                    "INSERT INTO scores (player_name, attempts) VALUES (?, ?)",
                    (session["player_name"], session["attempts"])
                )

    return render_template(
        "game.html",
        player_name=session["player_name"],
        attempts=session["attempts"],
        message=session.get("message", ""),
        message_type=session.get("message_type", "info"),
        game_over=session.get("game_over", False)
    )


@app.route("/new-game")
def new_game():
    name = session.get("player_name")
    if not name:
        return redirect(url_for("index"))
    session["secret_number"] = random.randint(1, 100)
    session["attempts"] = 0
    session["game_over"] = False
    session["message"] = "New number selected. Start guessing!"
    session["message_type"] = "info"
    return redirect(url_for("game"))


@app.route("/leaderboard")
def leaderboard():
    with get_db() as db:
        scores = db.execute("""
            SELECT player_name, attempts, played_at
            FROM scores
            ORDER BY attempts ASC, played_at DESC
            LIMIT 10
        """).fetchall()
    return render_template("leaderboard.html", scores=scores)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
