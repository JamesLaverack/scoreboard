Scoreboard tracks score and ranks players who compete in two-player games. Scoreboard assumes no information about the relative score is available, meerly that two players competed and one of them was the winner and one of them was the loser. Draws are simiaraly ignored.

Scoring is calculated as a simple win percentage, weighted by the opponents win percentage.

# Requirements

* Python 3.4+
* PostgreSQL 9.3+

# Environment Variables

* `DATABASE_URL` specifies the database. e.g. "postgres://username:password@host/database"
* `LEADERBOARD_SCORE_THREASHOLD` specifies the number of times a player must have played to be ranked. Unranked players do not contribute to opponent's win percentage calcualtions. This must be an integer value.
* `OPPONENTS_WIN_PERCENTAGE_WEIGHT` specifies the weighting of the opponent's win percentage along with that players. This must be a floating point value between 0.0 and 1.0 inclusive.