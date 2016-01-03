CREATE TABLE IF NOT EXISTS player (
       id serial PRIMARY KEY,
       name varchar(40) UNIQUE NOT NULL,
       created timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE IF NOT EXISTS game (
       id serial PRIMARY KEY,
       name varchar(40) UNIQUE NOT NULL,
       created timestamp NOT NULL DEFAULT (now())
);

CREATE TABLE IF NOT EXISTS score (
       id serial PRIMARY KEY,
       winner_id integer REFERENCES player(id) NOT NULL,
       loser_id integer REFERENCES player(id) NOT NULL,
       game_id integer REFERENCES game(id) NOT NULL,
       happened timestamp NOT NULL DEFAULT (now()),
       CONSTRAINT must_be_different CHECK (winner_id <> loser_id)
);
