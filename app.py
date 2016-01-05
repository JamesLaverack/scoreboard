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


@app.route("/about/")
def show_about():
    github_link = "https://github.com/JamesLaverack/scoreboard"

    return render_template('about.html', github_link=github_link)


@app.route("/")
def show_index():
    conn = db.database_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT name FROM (SELECT game.name, count(score.id) AS num_games FROM game LEFT JOIN score ON score.game_id = game.id GROUP BY game.name) AS games WHERE num_games > 3 ORDER BY num_games")
    popular_games = [x['name'] for x in cur.fetchall()]

    cur.execute("SELECT game.name AS game_name, winner.name AS winner_name, loser.name AS loser_name FROM score JOIN game ON score.game_id = game.id  JOIN player winner ON winner.id = score.winner_id JOIN player loser ON loser.id = score.loser_id ORDER BY score.happened DESC LIMIT 5")
    recent_scores = cur.fetchall()

    return render_template('index.html',
                           popular_games=popular_games,
                           recent_scores=recent_scores)


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
    recent_scores = cur.fetchall()

    return render_template('player.html',
                           name=name,
                           recent_scores=recent_scores)


@app.route("/game/<game_name>/")
def show_game(game_name):
    conn = db.database_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT id FROM game WHERE name = %s", [game_name])
    id = cur.fetchone()

    if id is None:
        abort(404)

    id = id['id']

    cur.execute("SELECT winner.name AS winner_name, loser.name AS loser_name FROM score JOIN player winner ON winner.id = score.winner_id JOIN player loser ON loser.id = score.loser_id WHERE score.game_id = %s ORDER BY score.happened DESC LIMIT 3", [id])
    scores = cur.fetchall()

    rankings = rpi.calculate_rpi(game_name)
    leaderboard = rpi.generate_leaderboard(rankings)

    return render_template('game.html',
                           game_name=game_name,
                           scores=scores,
                           leaderboard=leaderboard)


@app.route("/game/")
def show_games():
    cur = db.database_connection().cursor()
    cur.execute("SELECT name FROM game")

    games = [x[0] for x in cur.fetchall()]

    return render_template('games.html', games=games)


@app.route("/game/", methods=['POST'])
def add_game():
    conn = db.database_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO game (name) VALUES (%s)",
                [request.form['game_name']])
    conn.commit()

    return redirect(url_for('show_game', game_name=request.form['game_name']))


@app.route("/game/<game_name>/submit/")
def show_submit_score(game_name):
    if not game_exists(game_name):
        abort(404)

    return render_template('submit.html', game_name=game_name)


def get_or_create_id_for_player(player_name):
    conn = db.database_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM player WHERE name = %s",
                [player_name])
    player_id = cur.fetchone()

    # If it doesn't exist, make it
    if player_id is None:
        cur.execute("INSERT INTO player (name) VALUES (%s)",
                    [player_name])
        conn.commit()
        cur.execute("SELECT id FROM player WHERE name = %s", [player_name])
        player_id = cur.fetchone()

    return player_id


@app.route("/game/<game_name>/submit/", methods=['POST'])
def submit_score(game_name):
    if not game_exists(game_name):
        abort(404)

    winner_id = get_or_create_id_for_player(request.form['winner_name'])
    loser_id = get_or_create_id_for_player(request.form['loser_name'])

    conn = db.database_connection()
    cur = conn.cursor()
    cur.execute("""INSERT INTO score (winner_id, loser_id, game_id)
    VALUES (%s, %s, (SELECT id FROM game WHERE name = %s))""",
                (winner_id, loser_id, game_name))
    conn.commit()

    return redirect(url_for('show_game', game_name=game_name))


def game_exists(game_name):
    cur = db.database_connection().cursor()
    cur.execute("SELECT id FROM game WHERE name = %s", [game_name])
    return cur.fetchone() is not None


def player_exists(name):
    cur = db.database_connection().cursor()
    cur.execute("SELECT id FROM player WHERE name = %s", [name])
    return cur.fetchone() is not None


@app.route("/game/<game_name>/leaderboard/")
def show_leaderboard(game_name):
    if not game_exists(game_name):
        abort(404)

    score_threashold = int(os.environ["LEADERBOARD_SCORE_THREASHOLD"])

    leaderboard = rpi.generate_leaderboard(rpi.calculate_rpi(game_name))
    print("Final leaderboard: %s" % leaderboard)
    return render_template('leaderboard.html',
                           game_name=game_name,
                           leaderboard=leaderboard,
                           score_threashold=score_threashold)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


if __name__ == "__main__":
    app.run(debug=True)
