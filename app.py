from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
    return "Hello, world!"

@app.route("/user/<username>")
def show_user(username):
    return "User page for user " + username

@app.route("/game/<gamename>")
def show_game(gamename):
    return "Game page for game " + gamename

@app.route("/game/<gamename>/submit")
def show_submit_score(gamename):
    return "Submit a score for game " + gamename

@app.route("/game/<gamename>/leaderboard")
def show_leaderboard(gamename):
    return "Show the leaderboard for game " + gamename

if __name__ == "__main__":
    app.run();
