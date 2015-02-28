# pingpong
Ping Pong multiplayer Game API in Django with REST API

Requirements:
1. Python 2.7.6
2. Django 1.7
3. Django-rest framework
4. MySQL connected to Django
5. Username and password for each user is the name (small caps)


This is only the API, so you have to send GET and POST requests from some extension to the server using auth Token.
All requests from user to referee are authenticated by Authentication Token generated by Django-REST framework.

localhost/admin
for accessing the admin interface of Django

The API routes are: (Headers = Authentication : Token <token>)
Round 1:
1. localhost/join/
user sends request to join the game for level 1
2. localhost/join/status/
user sends request to know the status of how many players joined the game
3. localhost/game/details/1/
user sends request to know the detail of the opponent and his initial order and game id
4. localhost/round/1/
user sends the his turn using POST according to his playing order(integer if 1st, and list if 2nd)
5. localhost/status/1/
user sends request to know the status of the ongoing game, the number of points, new order

After round 1, referee shuts down the eliminated players and thus prevents accessing the game further.
The selected players wait till the 4 winners are selected and new games are allocated for round2.
Round 2:
1. localhost/game/details/2/
user sends request to know the detail of the opponent and his initial order and game id
2. localhost/round/2/
user sends the his turn using POST according to his playing order(integer if 1st, and list if 2nd)
3. localhost/status/2/
user sends request to know the status of the ongoing game, the number of points, new order

Similarly after second round.
Round 3:
1. localhost/game/details/3/
user sends request to know the detail of the opponent and his initial order and game id
2. localhost/round/3/
user sends the his turn using POST according to his playing order(integer if 1st, and list if 2nd)
3. localhost/status/3/
user sends request to know the status of the ongoing game, the number of points, new order

Finally after the tournament,
localhost/report/
The above request generates the full match report for every player.


All the above requests have been tested and stored in MySQL Database which is attached to this mail.
For running again empty the referee_game table and similarly referee_players so that new game can be calculated.
This can be achieved by adding a new function.