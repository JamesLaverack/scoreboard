from flask import Flask, render_template, request, url_for, redirect
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
    return render_template('game.html', gamename=gamename)

@app.route("/game/")
def show_games():
    cur = db.database_connection().cursor()
    cur.execute("SELECT name FROM game");

    return render_template('games.html', games=cur.fetchall());

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

@app.route("/game/<gamename>/submit", methods=['POST'])
def submit_score(gamename):
    conn = db.database_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO win (winner, loser, game) VALUES ((SELECT id FROM player WHERE name = %s), (SELECT id FROM player WHERE name = %s), (SELECT id FROM game WHERE gamename = %s)", (request.form['winnerName'], request.form['loserName'], gamename ))
    conn.commit()

    return redirect(url_for('show_leaderboard', gamename=gamename))

@app.route("/game/<gamename>/leaderboard")
def show_leaderboard(gamename):
    return render_template('leaderboard.html', gamename=gamename)

if __name__ == "__main__":
    app.run(debug=True)
