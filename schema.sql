CREATE TABLE player (
       id serial PRIMARY KEY,
       name varchar(40) UNIQUE NOT NULL
);

CREATE TABLE game (
       id serial PRIMARY KEY,
       name varchar(40) UNIQUE NOT NULL
);

CREATE TABLE win (
       id serial PRIMARY KEY,
       winner integer REFERENCES player(id) NOT NULL,
       loser integer REFERENCES player(id) NOT NULL,
       happened timestamp NOT NULL
);
