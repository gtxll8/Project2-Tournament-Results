#!/usr/bin/env python
#
# Test cases for tournament.py

from tournament import *


def testPairings_8():
    print "Testing a 9 players tournament:"
    setNewTournament("Las Vegas")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    registerPlayer("Lassy Kline")
    registerPlayer("Gordon Blunt")
    registerPlayer("Minty Sutton")
    registerPlayer("Baine Vrent")
    registerPlayer("Napoleon Bonaparte")
    print "first round:"
    pairings = swissPairings()
    print pairings
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4, True)
    print "players: ", id3, " and ", id4, " draw!"
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    print "second round:"
    pairings = swissPairings()
    print pairings
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    reportMatch(id1, id2, True)
    print "players: ", id1, " and ", id2, " draw!"
    reportMatch(id3, id4)
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    print "third round:"
    pairings = swissPairings()
    print pairings
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    printTableResults()


def testPairings_9():
    print "Testing a 9 players tournament:"
    setNewTournament("Las Vegas")
    registerPlayer("John Flynt")
    registerPlayer("Fluttershy")
    registerPlayer("Applejack")
    registerPlayer("Pinkie Pie")
    registerPlayer("Lassy Kline")
    registerPlayer("Gordon Blunt")
    registerPlayer("Minty Sutton")
    registerPlayer("Baine Vrent")
    registerPlayer("Napoleon Bonaparte")
    print "first round:"
    pairings = swissPairings()
    print pairings
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8, id9] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    reportMatch(id9, id9)
    print "player: ", id9, " is given a bye!"
    print "second round:"
    pairings = swissPairings()
    print pairings
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8, id9] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4, True)
    print "players: ", id3, " and ", id4, " draw!"
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    reportMatch(id9, id9)
    print "player: ", id9, " is givn a bye!"
    print "third round:"
    pairings = swissPairings()
    print pairings
    standings = playerStandings()
    [id1, id2, id3, id4, id5, id6, id7, id8, id9] = [row[0] for row in standings]
    reportMatch(id1, id2)
    reportMatch(id3, id4)
    reportMatch(id5, id6)
    reportMatch(id7, id8)
    reportMatch(id9, id9)
    print "player: ", id9, " is given a bye!"
    printTableResults()


if __name__ == '__main__':
    
    testPairings_8()
    testPairings_9()
    print "Success!  All tests pass!"


