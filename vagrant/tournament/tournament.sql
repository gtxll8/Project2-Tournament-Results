-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players (
    id          serial CONSTRAINT firstkey PRIMARY KEY,
    name        varchar(40) NOT NULL,
    tournamentID        integer
);

CREATE TABLE tournaments (
    id          serial PRIMARY KEY,
    set_timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);


CREATE TABLE matches (
    id		serial PRIMARY KEY,
    pid1	integer NOT NULL,
    pid2        integer NOT NULL,
    draw	boolean DEFAULT FALSE,
    tournamentID	integer
);

CREATE TABLE scores (
    id          serial PRIMARY KEY,
    tournamentID  integer,
    playerID	integer NOT NULL,
    score	integer DEFAULT 0,
    bye		boolean DEFAULT FALSE 
);

CREATE VIEW wins AS
    SELECT  p.id as ID, p.name as name, coalesce(SUM(s.score),0) as wins, COUNT(s.tournamentID) as matches
    FROM players as p
    FULL OUTER JOIN scores as s
    ON p.ID = s.playerID
    WHERE s.tournamentid IS NULL OR (s.tournamentid IN  (select MAX(id) FROM tournaments))
    AND p.tournamentid IS NULL OR (p.tournamentid IN  (select MAX(id) FROM tournaments))
    GROUP BY p.id;

CREATE OR REPLACE FUNCTION getscores(int) RETURNS bigint
   AS 'select coalesce(sum(score),0) from scores where playerid in (select (case when pid1 = $1 then pid2 when pid2 = $1 then pid1 end) from matches);'
LANGUAGE SQL;

     
CREATE VIEW omw AS
    select id, getscores(id) as omw_score from (select * from wins) as m order by omw_score desc;


INSERT INTO tournaments (set_timestamp) values(DEFAULT);

\q

