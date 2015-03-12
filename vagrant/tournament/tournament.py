#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """This will set a new tournamnet and preserve old recrds
       with the previous tournamnt ID's.
       All the other queries are referenced to the latest
       tournament ID , so there is no need to delete any
       matches just set a new tournamnent ID;
    """
    setNewTournament("London Calling")   # create a new tournament

def deletePlayers():
    """This will set a new tournament and preserve the players
       records on the previous tournaments
       All the other queries are referenced to the latest
       tournament ID , so there is no need to delete any
       players just set a new tournamnent ID
    """
    setNewTournament("Nashville")   # create a new tournament


def countPlayers():
    """Returns the number of players registered in the current
       tournament.
    """
    tournamentID = getTournament()       # get the last tournament
    conn = connect()
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM players WHERE tournamentID = %s;"
    cursor.execute(sql,[tournamentID])
    players_count = cursor.fetchone()[0]  # return 0 if count none
    conn.close()
    return players_count


def registerPlayer(name):
    """Adds a player to the tournament database.
       it will also add the current tournament this will remove
       the necessity of deleting the players.
  
    Args:
      name: the player's full name (need not be unique).
    """
    tournamentID = getTournament()  # get the last tournament
    conn = connect()
    cursor = conn.cursor()
    sql = "INSERT INTO players (name,tournamentID) values(%s,%s);"
    cursor.execute(sql, [name, tournamentID])
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list is the player in first place, or a player
    tied for first place if there is currently a tie OMW OMW - (Opponent Match Wins) is used

    OMW is achieved using a join with 'omw' view.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cursor = conn.cursor()
    sql = "select w.id, w.name, w.wins, w.matches from wins as w JOIN omw as o ON w.id = o.id order by w.wins desc, o.omw_score desc;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows


def setByeScore(playerid):
    """Gives one player a bye (skipped round), only once per tournament

    Args:
      playerid:  the id number of the player who is awarded a win
    """
    tournamentID = getTournament()
    conn = connect()
    cursor = conn.cursor()
    sql = "SELECT COALESCE(sum(CASE WHEN bye THEN 1 ELSE 0 END),0) FROM scores where playerid=%s AND tournamentid=%s;"
    cursor.execute(sql, [playerid, tournamentID])
    bye_count = cursor.fetchone()[0]
    if bye_count >= 1:
        score = 0
        bye = False
    else:
        score = 1
        bye = True
    sql = "INSERT INTO scores(tournamentid,playerid,score,bye) values(%s,%s,%s,%s);"
    cursor.execute(sql, [tournamentID, playerid, score, bye])
    conn.commit()
    conn.close()


def reportMatch(winner, loser, draw=False):
    """Records the outcome of a single match between two players.
       EXCEPTION : If function is called with same ID for winner and loser it
       will trigger a function setByeScore() to award a win. 

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw ( default false ) True to set the match as  draw
    """
    tournamentID = getTournament()
    conn = connect()
    cursor = conn.cursor()
    if winner == loser:
        setByeScore(winner)
    else:
        sql = "INSERT INTO scores(tournamentid,playerid,score) values(%s,%s,%s);"
        cursor.execute(sql, [tournamentID, winner, 1])
        if draw:
            cursor.execute(sql, [tournamentID, loser, 1])
        else:
            cursor.execute(sql, [tournamentID, loser, 0])
            sql = "INSERT INTO matches(pid1,pid2,draw,tournamentID) values(%s,%s,%s,%s);"
            cursor.execute(sql, [winner, loser, draw, tournamentID])
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    seen = set()
    swisspairings = []
    playersrank = getPlayersRank()
    for p1 in playersrank:
        for p2 in playersrank:
            if p1[0] != p2[0]:
                if p2[0] not in getPlayersPlayed(p1[0]):
                    if p2[0] not in seen and p1[0] not in seen:
                        seen.update([p1[0], p2[0]])
                        swisspairings.append((p1[0], p1[1], p2[0], p2[1]))

    return swisspairings


def getTournament():
    """Returns the current tournament ID
    Returns:
     A single value, the last tournament ID.    
     """
    conn = connect()
    cursor = conn.cursor()
    sql = "SELECT MAX(ID) FROM tournaments;"
    cursor.execute(sql)
    tournamentID = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return tournamentID


def setNewTournament(name):
    """Initialize a new tournament by generating a time stamp 
       and an incremental ID
    """
    conn = connect()
    cursor = conn.cursor()
    sql = "INSERT INTO tournaments (name) values(%s);"
    cursor.execute(sql, [name])
    conn.commit()
    conn.close()


def getPlayersRank():
    """Return a list of players IDs ordered by their rank desc
       Using a join on 'omw' view to implement OMW - (Opponent Match Wins)
       total numbers of wins by players they have played against.
       
       Example of the wins view which orders players with the same score
       by omw_score desc:
 
  playerid |        name        | wins | omw_score
----------+--------------------+------+-----------
       84 | Gordon Blunt       |    2 |         2
       81 | Applejack          |    2 |         1
       85 | Minty Sutton       |    1 |         3
       79 | Twilight Sparkle   |    1 |         2
       86 | Baine Vrent        |    1 |         2
       82 | Pinkie Pie         |    1 |         1
       87 | Napoleon Bonaparte |    1 |         0
       83 | Lassy Kline        |    0 |         3
       80 | Fluttershy         |    0 |         2


    """
    conn = connect()
    cursor = conn.cursor()
    sql = "select w.id as playerid, name from wins as w JOIN omw as o ON w.id = o.id order by w.wins desc, o.omw_score desc;"
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows


def getPlayersPlayed(playerid):
    """Return a list of already played players ID
    """
    returnedPlayers = []
    conn = connect()
    cursor = conn.cursor()
    sql = "select pid1, pid2 from matches where pid1=%s or pid2=%s;"
    cursor.execute(sql, (playerid, playerid,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        if row[0] == playerid:
            returnedPlayers.extend([row[1]])
        else:
            returnedPlayers.extend([row[0]])
    return returnedPlayers


def printTableResults():
    conn = connect()
    sql = "select w.id, w.name, w.wins, w.matches, o.omw_score as omw from wins as w JOIN omw as o ON w.id = o.id order by w.wins desc, o.omw_score desc;"
    cursor = conn.cursor()
    cursor.execute(sql)
    columns = [column[0] for column in cursor.description]
    print " ------- STANDINGS RESULTS ------- "
    print columns
    for row in cursor.fetchall():
        print "   ", row[0], "   ", row[1], "   ", row[2], "   ", row[3], "   ", row[4]

    print " ------- END PRINT ---------------"
    conn.close()
    
