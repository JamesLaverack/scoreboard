import db
import os
import operator


def win_percentage(wins, loses):
    totalGames = wins + loses
    if totalGames == 0:
        return None
    return wins / totalGames


def generate_leaderboard(scores):
    print("Raw scores: %s" % scores)
    sortedScores = sorted(scores.items(), key=operator.itemgetter(1))
    sortedScores.reverse()
    print("Sorted scores: %s" % sortedScores)

    # Assign Placings
    currentPlace = 0
    lastSeenScore = -1.0
    leaderboard = []
    for score in sortedScores:
        if score[1] != lastSeenScore:
            currentPlace += 1
        lastSeenScore = score[1]
        leaderboard.append({'name': score[0], 'rank': currentPlace})

    return leaderboard


def calculate_rpi(gameName):
    # Use the database directly, let PostgreSQL do the heavy lifting
    conn = db.database_connection()
    cur = conn.cursor()

    # Get the game ID
    cur.execute("SELECT id FROM game WHERE name = %s", [gameName])
    gameId = cur.fetchone()

    # Only players who have played this game enough count
    scoreThreashold = int(os.environ["LEADERBOARD_SCORE_THREASHOLD"])

    print("Using Score Threashold: %s" % scoreThreashold)
    cur.execute("SELECT player.id, player.name FROM player WHERE (SELECT count(*) FROM score WHERE score.game_id = %s AND (score.winner_id = player.id OR score.loser_id = player.id)) >= %s", [gameId, scoreThreashold])
    players = cur.fetchall()

    print("Valid Players: %s" % [players])
    winPercentages = {}
    for playerId, playerName in players:
        # Calculate win percentage for each player
        cur.execute("SELECT count(*) FROM score WHERE score.game_id = %s AND score.winner_id = %s", [gameId, playerId])
        numWins = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM score WHERE score.game_id = %s AND score.loser_id = %s", [gameId, playerId])
        numLoses = cur.fetchone()[0]
        winPercentages[playerName] = win_percentage(numWins, numLoses)
    print("Win Percentages %s" % [winPercentages])

    # Weight the Win Percentage and the Opp win Percentage
    oppWinPerWeight = float(os.environ["OPPONENTS_WIN_PERCENTAGE_WEIGHT"])
    winPerWeight = 1 - oppWinPerWeight

    scores = {}
    oppWinPercentages = {}
    for playerId, playerName in players:
        # Find the ids of this player's opponents
        cur.execute("SELECT player.name FROM player WHERE player.id IN ((SELECT winner_id FROM score WHERE score.game_id = %s AND score.loser_id = %s) UNION (SELECT loser_id FROM score WHERE score.game_id = %s AND score.winner_id = %s))", [gameId, playerId, gameId, playerId])
        opponents = cur.fetchall()

        oppWinPercentage = 0
        for oppName in opponents:
            if oppName in winPercentages:
                oppWinPercentage += winPercentages[oppName]
        oppWinPercentage /= len(opponents)

        # Calculate this player's score
        scores[playerName] = winPercentages[playerName] * winPerWeight
        + oppWinPercentage * oppWinPerWeight
    print("Scores: %s" % scores)

    return scores
