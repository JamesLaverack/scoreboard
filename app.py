from flask import Flask, render_template, request, url_for, redirect, abort
from flask_bootstrap import Bootstrap
import db

app = Flask(__name__)
Bootstrap(app)

@app.route("/")
def hello():
    return render_template('index.html')

@app.route("/user/<name>")
def show_user(name):

    return render_template('user.html', name=name)

@app.route("/game/<gamename>")
def show_game(gamename):
    cur = db.database_connection().cursor()
    cur.execute("SELECT id FROM game WHERE name = %s", [gamename])
    id = cur.fetchone()

    cur.execute("SELECT winner.name, loser.name FROM win JOIN player winner ON winner.id = win.winner JOIN player loser ON loser.id = win.loser WHERE win.game = %s ORDER BY win.happened DESC LIMIT 3", [id])
    wins = cur.fetchall()

    if id is None:
        abort(404)

    return render_template('game.html', gamename=gamename, wins=wins)

@app.route("/game/")
def show_games():
    cur = db.database_connection().cursor()
    cur.execute("SELECT name FROM game")

    return render_template('games.html', games=cur.fetchall())

@app.route("/game/", methods=['POST'])
def add_game():
    conn = db.database_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO game (name) VALUES (%s)", [request.form['gameName']])
    conn.commit()

    return redirect(url_for('show_game', gamename=request.form['gameName']))

@app.route("/game/<gamename>/submit")
def show_submit_score(gamename):
    return render_template('submit.html', gamename=gamename)

def get_or_create_id_for_player(playerName):
    conn = db.database_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM player WHERE name = %s", [playerName])
    playerId = cur.fetchone();

    # If it doesn't exist, make it
    if playerId is None:
        cur.execute("INSERT INTO player (name) VALUES (%s)", [playerName])
        conn.commit()
        cur.execute("SELECT id FROM player WHERE name = %s", [playerName])
        playerId = cur.fetchone()

    return playerId

@app.route("/game/<gamename>/submit", methods=['POST'])
def submit_score(gamename):
    winnerId = get_or_create_id_for_player(request.form['winnerName'])
    loserId = get_or_create_id_for_player(request.form['loserName'])

    conn = db.database_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO win (winner, loser, game) VALUES (%s, %s, (SELECT id FROM game WHERE name = %s))", (winnerId, loserId, gamename))
    conn.commit()

    return redirect(url_for('show_game', gamename=gamename))

@app.route("/game/<gamename>/leaderboard")
def show_leaderboard(gamename):
    return render_template('leaderboard.html', gamename=gamename)

if __name__ == "__main__":
    app.run(debug=True)
