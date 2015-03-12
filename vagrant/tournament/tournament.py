#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """This will set a new tournament and preserve old records
       with the previous tournament ID's.
       All the other queries are referenced to the latest
       tournament ID , so there is no need to delete any
       matches just set a new one.
    """
    setNewTournament("London Calling")   # set a new tournament

def deletePlayers():
    """This will set a new tournament and preserve the players
       records on the previous tournaments
       All the other queries are referenced to the latest
       tournament ID , so there is no need to delete any
       players just set a new one.
    """
    setNewTournament("Nashville")        # set a new tournament


def countPlayers():
    """Returns the number of players registered in the current
       tournament.
    """
    tournamentID = getTournament()       # get the last tournament
    conn = connect()
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM players WHERE tournamentID = %s;"
    cursor.execute(sql, [tournamentID])
    players_count = cursor.fetchone()[0]  # return 0 if count none
    conn.close()
    return players_count


def registerPlayer(name):
    """Adds a player to the tournament database.
       it will also add the current tournament ID this will remove
       the necessity of deleting the players table records.
  
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
    """Returns a list of the players and their wining records, sorted by wins.

    The first entry in the list is the player in first place, or a player
    tied for first place if there is currently a tie OMW - (Opponent Match Wins) is used

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
       Select first a count of how many times player had been awarded a 'bye'
       in this tournament.

       If not than insert into scores table a win, than set the flag to 'true' in column 'bye'

    Args:
      playerid:  the id number of the player who is awarded a win
    """
    tournamentID = getTournament()                  # get the latest tournament ID
    conn = connect()
    cursor = conn.cursor()
    sql = "SELECT COALESCE(sum(CASE WHEN bye THEN 1 ELSE 0 END),0) FROM scores where playerid=%s AND tournamentid=%s;"
    cursor.execute(sql, [playerid, tournamentID])
    bye_count = cursor.fetchone()[0]                # get a count
    if bye_count >= 1:                              # check if awarded more than one time
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

       DRAW EXCEPTION : If function is called with same ID for winner and loser it
       will trigger a function setByeScore() to award a win. 

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
      draw ( default false ) True to set the match as  draw
    """
    tournamentID = getTournament()
    conn = connect()
    cursor = conn.cursor()
    if winner == loser:                                            # check if same ID and give a 'bye'
        setByeScore(winner)
    else:
        sql = "INSERT INTO scores(tournamentid,playerid,score) values(%s,%s,%s);"
        cursor.execute(sql, [tournamentID, winner, 1])
        if draw:                                                    # if draw TRUE give loser a win
            cursor.execute(sql, [tournamentID, loser, 1])
        else:
            cursor.execute(sql, [tournamentID, loser, 0])
            sql = "INSERT INTO matches(pid1,pid2,draw,tournamentID) values(%s,%s,%s,%s);"
            cursor.execute(sql, [winner, loser, draw, tournamentID])
    conn.commit()
    conn.close()


def swissPairings():
    """ Returns a list of pairs of players for the next round of a match.

        First using the function getPlayersRank() get an ordered list by
        wins and 'OMW' , the object here is to match a pair which never played
        before in the tournament. Traverse the list starting with the first
        player and than check with adjacent one until you satisfy the conditions:
        1 - never played before, 2 - ID not equal to itself.
        Append the pair in an array 'seen' so you do not have to check again.
        Append the pair also in an array but with added names, for later return.

    Returns:
        A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    seen = set()                                                                # array to store checked pairs
    swisspairings = []                                                          # array to store final resulted pairs
    playersrank = getPlayersRank()                                              # get the ranked list
    for p1 in playersrank:                                                      # traverse list for each ...
        for p2 in playersrank:                                                  # ... start checking each adjacent
            if p1[0] != p2[0]:                                                  # continue if not itself
                if p2[0] not in getPlayersPlayed(p1[0]):                        # check if not played before
                    if p2[0] not in seen and p1[0] not in seen:                 # also if not paired already
                        seen.update([p1[0], p2[0]])                             # append results
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
    """Initialize a new tournament entering a name but also adding
       an incremental ID
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
    """Return a list of played players for a target 'playerid' .
       Select query will look for any rows in the table 'matches'
       that have the target player ID at any position, than extract
       the adjacent ID's as played and return them.
    """
    returnedPlayers = []                           # array to store players ID's
    conn = connect()
    cursor = conn.cursor()
    sql = "select pid1, pid2 from matches where pid1=%s or pid2=%s;"
    cursor.execute(sql, (playerid, playerid,))
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    for row in rows:                               # traverse rows
        if row[0] == playerid:                     # if 'playerid' found at [0]
            returnedPlayers.extend([row[1]])       # append [1] as played ID to array
        else:
            returnedPlayers.extend([row[0]])       # else it must be at [1] therefore append [0] as played ID
    return returnedPlayers


def printTableResults():
    """This is for DEBUG only it will print an output to screen from the
       players standings table so you can easily asses the results after
       a tournament.
    """
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
    
