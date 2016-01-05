import db
import os
import operator


def win_percentage(wins, loses):
    total_games = wins + loses
    if total_games == 0:
        return None
    return wins / total_games


def generate_leaderboard(scores):
    print("Raw scores: %s" % scores)
    sorted_scores = sorted(scores.items(), key=operator.itemgetter(1))
    sorted_scores.reverse()
    print("Sorted scores: %s" % sorted_scores)

    # Assign Placings
    current_place = 0
    last_seen_score = -1.0
    leaderboard = []
    for score in sorted_scores:
        if score[1] != last_seen_score:
            current_place += 1
        last_seen_score = score[1]
        leaderboard.append({'name': score[0], 'rank': current_place})

    return leaderboard


def calculate_rpi(gameName):
    # Use the database directly, let PostgreSQL do the heavy lifting
    conn = db.database_connection()
    cur = conn.cursor()

    # Get the game ID
    cur.execute("SELECT id FROM game WHERE name = %s", [gameName])
    game_id = cur.fetchone()

    # Only players who have played this game enough count
    score_threashold = int(os.environ["LEADERBOARD_SCORE_THREASHOLD"])

    print("Using Score Threashold: %s" % score_threashold)
    cur.execute("SELECT player.id, player.name FROM player WHERE (SELECT count(*) FROM score WHERE score.game_id = %s AND (score.winner_id = player.id OR score.loser_id = player.id)) >= %s", [game_id, score_threashold])
    players = cur.fetchall()

    print("Valid Players: %s" % [players])
    win_percentages = {}
    for playerId, playerName in players:
        # Calculate win percentage for each player
        cur.execute("SELECT count(*) FROM score WHERE score.game_id = %s AND score.winner_id = %s", [game_id, playerId])
        wins = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM score WHERE score.game_id = %s AND score.loser_id = %s", [game_id, playerId])
        loses = cur.fetchone()[0]
        win_percentages[playerName] = win_percentage(wins, loses)
    print("Win Percentages %s" % [win_percentages])

    # Weight the Win Percentage and the Opp win Percentage
    opp_win_per_weight = float(os.environ["OPPONENTS_WIN_PERCENTAGE_WEIGHT"])
    win_per_weight = 1 - opp_win_per_weight

    scores = {}
    opp_win_percentages = {}
    for playerId, playerName in players:
        # Find the ids of this player's opponents
        cur.execute("SELECT player.name FROM player WHERE player.id IN ((SELECT winner_id FROM score WHERE score.game_id = %s AND score.loser_id = %s) UNION (SELECT loser_id FROM score WHERE score.game_id = %s AND score.winner_id = %s))", [game_id, playerId, game_id, playerId])
        opponents = cur.fetchall()

        opp_win_percentage = 0
        for opp_name in opponents:
            if opp_name in win_percentages:
                opp_win_percentage += win_percentages[oppName]
        opp_win_percentage /= len(opponents)

        # Calculate this player's score
        scores[playerName] = win_percentages[playerName] * win_per_weight
        + opp_win_percentage * opp_win_per_weight
    print("Scores: %s" % scores)

    return scores
