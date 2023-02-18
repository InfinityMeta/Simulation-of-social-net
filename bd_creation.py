import functionality as f
import psycopg2
from psycopg2 import sql

class Database:
    def __init__(self, conn, db_name):

        self.cursor = conn.cursor()
        self.db_name = db_name

        self.cursor.execute(sql.SQL("CREATE DATABASE {db_name};").format(
            db_name=sql.Identifier(db_name))
        )

        print("Database created successfully")

    @staticmethod
    def print_success_create(table_name):
        print(f"Table {table_name} created successfully")

    def create_table_users(self):

        self.cursor.execute("""
        CREATE TABLE Users (
        id serial PRIMARY KEY,
        login varchar NOT NULL,
        password varchar NOT NULL,
        role varchar NOT NULL);
        """)
        Database.print_success_create("Users")

    def create_table_posts(self):

        self.cursor.execute("""
        CREATE TABLE Posts (
        post_id serial PRIMARY KEY,
        user_id int NOT NULL,
        post text NOT NULL,
        time timestamp DEFAULT NOW());
        """)
        Database.print_success_create("Posts")

    def create_table_hashtags(self):
        self.cursor.execute("""
                CREATE TABLE Hashtags (
                ht_id serial PRIMARY KEY,
                post_id int NOT NULL,
                hashtag text NOT NULL );
                """)
        Database.print_success_create("Hashtags")

    def create_table_subscriptions(self):
        self.cursor.execute("""
                CREATE TABLE Subscriptions (
                id_from serial PRIMARY KEY,
                id_to int NOT NULL );
                """)
        Database.print_success_create("Subscriptions")

    def create_admin(self, login, password):
        self.cursor.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")
        self.cursor.execute("""INSERT INTO Users (login,password,role) 
                    VALUES (%(login)s, crypt(%(password)s, gen_salt('md5')), %(role)s);""",
                            {'login' : login, 'password' : password, 'role' : 'admin'})
        print("Account of administrator is created")

def create_database(conn, db_name, admin_login, admin_password):
    db = Database(conn, db_name)
    new_conn = f.create_connection(dbname=db.db_name)
    new_conn.autocommit = True
    db.cursor = new_conn.cursor()

    db.create_table_users()
    db.create_table_posts()
    db.create_table_hashtags()
    db.create_table_subscriptions()
    db.create_admin(admin_login, admin_password)
    return new_conn

conn = f.create_connection()
conn.autocommit = True

create_database(conn, "Network", "Maxim", "qwerty")