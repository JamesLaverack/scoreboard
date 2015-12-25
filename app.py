from flask import Flask, render_template
from flask_bootstrap import Bootstrap

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

@app.route("/game/<gamename>/submit")
def show_submit_score(gamename):
    return render_template('submit.html', gamename=gamename)

@app.route("/game/<gamename>/leaderboard")
def show_leaderboard(gamename):
    return render_template('leaderboard.html', gamename=gamename)

if __name__ == "__main__":
    app.run(debug=True)
