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

CREATE TABLE IF NOT EXISTS win (
       id serial PRIMARY KEY,
       winner integer REFERENCES player(id) NOT NULL,
       loser integer REFERENCES player(id) NOT NULL,
       game integer REFERENCES game(id) NOT NULL,
       happened timestamp NOT NULL DEFAULT (now()),
       CONSTRAINT must_be_different CHECK (winner <> loser)
);
