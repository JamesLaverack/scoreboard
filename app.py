from flask import Flask, render_template, request, url_for, redirect, abort
import flask_bootstrap
import db
import os
import rpi
import psycopg2.extras
import json

app = Flask(__name__)
flask_bootstrap.Bootstrap(app)


# This method is used by typeahead.js
@app.route("/api/v1/player")
def api_list_players():
    conn = db.database_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT name FROM player")
    names = [rec['name'] for rec in cur.fetchall()]

    return json.dumps(names)

@app.route("/")
def show_index():
    conn = db.database_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT name FROM (SELECT game.name, count(score.id) AS num_games FROM game LEFT JOIN score ON score.game_id = game.id GROUP BY game.name) AS games WHERE num_games > 3 ORDER BY num_games")
    popularGames = [x['name'] for x in cur.fetchall()]

    cur.execute("SELECT game.name AS game_name, winner.name AS winner_name, loser.name AS loser_name FROM score JOIN game ON score.game_id = game.id  JOIN player winner ON winner.id = score.winner_id JOIN player loser ON loser.id = score.loser_id ORDER BY score.happened DESC LIMIT 5")
    recentScores = cur.fetchall()

    return render_template('index.html',
                           popularGames=popularGames,
                           recentScores=recentScores)


@app.route("/player/")
def show_players():
    cur = db.database_connection().cursor()
    cur.execute("SELECT name FROM player")
    players = [x[0] for x in cur.fetchall()]

    return render_template('players.html', players=players)


@app.route("/player/<name>")
def show_player(name):
    if not player_exists(name):
        abort(404)

    conn = db.database_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("SELECT game.name AS game_name, winner.name AS winner_name, loser.name AS loser_name FROM score JOIN game ON score.game_id = game.id  JOIN player winner ON winner.id = score.winner_id JOIN player loser ON loser.id = score.loser_id WHERE winner.name = %s OR loser.name = %s ORDER BY score.happened DESC LIMIT 5", [name, name])
    recentScores = cur.fetchall()

    return render_template('player.html',
                           name=name,
                           recentScores=recentScores)


@app.route("/game/<gamename>")
def show_game(gamename):
    conn = db.database_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id FROM game WHERE name = %s", [gamename])
    id = cur.fetchone()

    if id is None:
        abort(404)

    id = id['id']

    cur.execute("SELECT winner.name AS winner_name, loser.name AS loser_name FROM score JOIN player winner ON winner.id = score.winner_id JOIN player loser ON loser.id = score.loser_id WHERE score.game_id = %s ORDER BY score.happened DESC LIMIT 3", [id])
    scores = cur.fetchall()

    rankings = rpi.calculate_rpi(gamename)
    leaderboard = rpi.generate_leaderboard(rankings)

    return render_template('game.html',
                           gamename=gamename,
                           scores=scores,
                           leaderboard=leaderboard)


@app.route("/game/")
def show_games():
    cur = db.database_connection().cursor()
    cur.execute("SELECT name FROM game")

    return render_template('games.html', games=cur.fetchall())


@app.route("/game/", methods=['POST'])
def add_game():
    conn = db.database_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO game (name) VALUES (%s)",
                [request.form['gameName']])
    conn.commit()

    return redirect(url_for('show_game', gamename=request.form['gameName']))


@app.route("/game/<gamename>/submit")
def show_submit_score(gamename):
    if not game_exists(gamename):
        abort(404)

    return render_template('submit.html', gamename=gamename)


def get_or_create_id_for_player(playerName):
    conn = db.database_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM player WHERE name = %s",
                [playerName])
    playerId = cur.fetchone()

    # If it doesn't exist, make it
    if playerId is None:
        cur.execute("INSERT INTO player (name) VALUES (%s)",
                    [playerName])
        conn.commit()
        cur.execute("SELECT id FROM player WHERE name = %s", [playerName])
        playerId = cur.fetchone()

    return playerId


@app.route("/game/<gamename>/submit", methods=['POST'])
def submit_score(gamename):
    if not game_exists(gamename):
        abort(404)

    winnerId = get_or_create_id_for_player(request.form['winnerName'])
    loserId = get_or_create_id_for_player(request.form['loserName'])

    conn = db.database_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO score (winner_id, loser_id, game_id)
    VALUES (%s, %s, (SELECT id FROM game WHERE name = %s))""",
                (winnerId, loserId, gamename))
    conn.commit()

    return redirect(url_for('show_game', gamename=gamename))


def game_exists(gamename):
    cur = db.database_connection().cursor()
    cur.execute("SELECT id FROM game WHERE name = %s", [gamename])
    return cur.fetchone() is not None


def player_exists(name):
    cur = db.database_connection().cursor()
    cur.execute("SELECT id FROM player WHERE name = %s", [name])
    return cur.fetchone() is not None


@app.route("/game/<gamename>/leaderboard")
def show_leaderboard(gamename):
    if not game_exists(gamename):
        abort(404)

    scoreThreashold = int(os.environ["LEADERBOARD_SCORE_THREASHOLD"])

    leaderboard = rpi.generate_leaderboard(rpi.calculate_rpi(gamename))
    print("Final leaderboard: %s" % leaderboard)
    return render_template('leaderboard.html',
                           gamename=gamename,
                           leaderboard=leaderboard,
                           scoreThreashold=scoreThreashold)


if __name__ == "__main__":
    app.run(debug=True)
