-- Table definitions for the tournament project.

\c tournament;


-- This table stores the tournaments id's and acts as a key reference
-- and by using this there is no need to delete any data in other tables

CREATE TABLE tournaments (
    id          serial PRIMARY KEY,
    name        varchar(40) NOT NULL
);

-- This table stores the players and has a foreign key referencing to
-- the tournaments table

CREATE TABLE players (
    id          serial CONSTRAINT firstkey PRIMARY KEY,
    name        varchar(40) NOT NULL,
    tournamentID        integer references tournaments(id)
);


-- This table stores match occurrences between two players, it
-- also having a reference to players and tournaments tables

CREATE TABLE matches (
    id		serial PRIMARY KEY,
    pid1	integer NOT NULL references players(id),
    pid2        integer NOT NULL references players(id),
    draw	boolean DEFAULT FALSE,
    tournamentID	integer  references tournaments(id)
);


-- This table stores a score for a match played for each individual
-- player, it also stores a flag if the player have received a bye.  

CREATE TABLE scores (
    id          serial PRIMARY KEY,
    tournamentID  integer references tournaments(id),
    playerID	integer NOT NULL ,
    score	integer DEFAULT 0,
    bye		boolean DEFAULT FALSE 
);


-- This is a view created joining players and score tables summing up all the
-- wins to create the standings 

CREATE VIEW wins AS
    SELECT  p.id as ID, p.name as name, coalesce(SUM(s.score),0) as wins, COUNT(s.tournamentID) as matches
    FROM players as p
    FULL OUTER JOIN scores as s
    ON p.ID = s.playerID
    WHERE s.tournamentid IS NULL OR (s.tournamentid IN  (select MAX(id) FROM tournaments))
    AND p.tournamentid IS NULL OR (p.tournamentid IN  (select MAX(id) FROM tournaments))
    GROUP BY p.id;


-- This function sums up the wins from all the players a player had played against
-- to produce an OMW (Opponent Match Wins)
 
CREATE OR REPLACE FUNCTION getscores(int) RETURNS bigint
   AS 'select coalesce(sum(score),0) from scores where playerid in (select (case when pid1 = $1 then pid2 when pid2 = $1 then pid1 end) from matches);'
LANGUAGE SQL;


-- Create a view based on the previous function to show OMW
     
CREATE VIEW omw AS
    select id, getscores(id) as omw_score from (select * from wins) as m order by omw_score desc;


-- Initialize a first tournament so column ID is not null
 
INSERT INTO tournaments (name) values('London 1989');

\q

