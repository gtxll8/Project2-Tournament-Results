# Project2-Tournament-Results
Tournament Results

Project Description:

This is a project that uses a PostgeSQL database, supported by python modules demonstrating a viable game tournament using the Swiss system. This project has two parts one is defining the schema and the relations between the tables and second is the code that will use it to support it.

What does this project achieve:

It passes all the requirements/tests asked for the final project in "Project2 Tournament Results" which are :

1. Old matches can be deleted.
2. Player records can be deleted.
3. After deleting, countPlayers() returns zero.
4. After registering a player, countPlayers() returns 1.
5. Players can be registered and deleted.
6. Newly registered players appear in the standings with no matches.
7. After a match, players have updated standings.
8. After one match, players with one win are paired.

Plus :

9. It can run an even or odd number of players , for the odd number the last player is awarded a "bye" only once per tournament. ( See : setByeScore(playerid) )
10. It has support for game draws. For that the function :  reportMatch(winner, loser, draw = False) has an optional argument - True will award score 1 to both players ( this can be of course be modified to award just 1/2 a point )
11. It implements OMW (Oppenent Match Wins) for example this is how the standings order look after using OMW :

 ```   
 id |        name        | wins | matches | omw
----+--------------------+------+---------+-----
 60 | Lassy Kline        |    3 |       3 |   4
 59 | Pinkie Pie         |    3 |       3 |   3
 57 | Fluttershy         |    2 |       3 |   5
 64 | Napoleon Bonaparte |    2 |       3 |   4
 61 | Gordon Blunt       |    2 |       3 |   3
 63 | Baine Vrent        |    2 |       3 |   3
 58 | Applejack          |    1 |       3 |   5
 56 | John Flynt         |    1 |       3 |   2
 62 | Minty Sutton       |    0 |       3 |   5
 ```

12. It supports more than one tournament, there is no need to delete players or matches after a tournament, only one function used: setNewTournament(), this will initialize a new id and a time stamp.


Requirements to test this project:

Steps (assuming you have Windows, it can be easily installed in a Linux based OS too ):
 1. Install vagrant in order to test it easily, if you don't have vagrant installed already check out the following link from UDACITY for instructions: https://www.udacity.com/wiki/ud197/install-vagrant
 2. Clone my (this) repositary ( https://github.com/gtxll8/Project2-Tournament-Results/ ) , it contains the neccessary files including vagrant setup file and the pg_config.sh modified to create the tournament DB and the create tables, viewsand functions neccessary for the project.
 3. Go to the cloned repositary, this will look in windows like this :
 "C:\<your home directoy>\GitHub\Project2-Tournament-Results\vagrant>" it will contain teh following files and directory:
 ```   
11/03/2015  08:59    <DIR>          .
11/03/2015  08:59    <DIR>          ..
11/03/2015  08:58    <DIR>          .vagrant
11/03/2015  09:39               354 pg_config.sh
11/03/2015  10:11    <DIR>          tournament
11/03/2015  09:24               461 Vagrantfile
               2 File(s)            815 bytes
               4 Dir(s)  196,121,255,936 bytes free
 ``` 
  4. Issue 'vagrant up' this will start the vagrant environment locally, at the end you should see the database tournament created and tables:
 ```   
==> default: You are now connected to database "tournament" as user "vagrant".
==> default: CREATE TABLE
==> default: CREATE TABLE
==> default: CREATE TABLE
==> default: CREATE TABLE
==> default: CREATE VIEW
==> default: CREATE FUNCTION
==> default: CREATE VIEW
==> default: INSERT 0 1 
 ```   
  5. SSH to the box using your favorite terminal , credentials are as follow:
 ``` 
Host: 127.0.0.1
Port: 2222
Username: vagrant
 ``` 
  6. Transfer the tournament directory from the cloned directory , for your convenience you can scp it from my DigitalOcean project box with the following command ( user name and password as above ):
  ``` 
  vagrant@vagrant-ubuntu-trusty-32:~$ scp -r vagrant@162.243.67.78:./vagrant/tournament .
 ``` 
 this will copy the entire directory with the neccessary files:
  ``` 
tournament_test_extended.py                                                                                           
tournament.pyc                                                                                                        
tournament_test.py                                                                                                    
tournament.sql                                                                                                        
tournament.py  
  ``` 
 
 Note: if the tables and views were not created on 'vagrant up' command, the schema creation can be done using psql command :
 ``` 
vagrant=>\i tournament.sql
 ```
7. In order to test the system run 'tournament_test.py' to test default functionality and 'tournament_test_extended.py' to test all the functionalities for extra credits.


Notes and considerations :
  
  





