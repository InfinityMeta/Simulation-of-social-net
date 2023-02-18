# Simulation_of_social_net

Simulation of social network via connector to Postgresql written on Python by means of psycopg2.

3 types of users: Admin, moderators and normal users.

Normal user`s opportunities:

* delete account
* create posts
* view his posts
* delete his posts
* edit his posts
* view posts of other users
* subscribe to other users
* check his subscriptions
* check his subscribers
* check mutual subscriptions
* check posts of subscribers

Moderator`s opportunities:

* edit posts of other users
* delete accounts of other users
* delete posts of other users
* normal user`s opportunities

Admin`s opportunities:

* change rights of users
* moderator`s opportunities
