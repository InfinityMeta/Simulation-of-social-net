import sys
import re
import psycopg2
from more_itertools import one


def create_connection(dbname='Network', user='postgres', password='postgres', host='localhost', port='5432'):
    try:
        conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
    except psycopg2.OperationalError as e:
        print("connection is failed")
        sys.exit(1)
    else:
        print("Connection is successful")
        return conn


class User:

    def __init__(self, connection, sign_up):
        """
        регистрация (логин, пароль)
        """
        self.cursor = connection.cursor()
        if sign_up:
            print("Enter your login :")
            self.login = input()
            self.cursor.execute('SELECT login FROM users')
            logins = [name for (name,) in self.cursor.fetchall()]
            if self.login in logins:
                print("such login exists")
                return

            print("Enter your password :")
            password = input()

            self.role = 'user'

            self.cursor.execute(
                """ INSERT INTO users (login,password,role) 
                VALUES (%(login)s, crypt(%(password)s, gen_salt('md5')), %(role)s);
                """, {'login': self.login, 'password' : password, 'role' : self.role})

            print("Sign up is successful")

        else:
            User.log_in(self)

    def log_in(self):
        """
        вход (логин, пароль)
        """
        print("Enter your login :")
        login = input()

        self.cursor.execute(
            """
            SELECT * FROM users WHERE login=%(login)s 
            """, {'login': login})
        if len(self.cursor.fetchall()) == 0:
            print('Such login does not exist')
            return 0
        self.login = login
        print("Enter your password :")
        password = input()
        self.cursor.execute(
            """
            SELECT * FROM users WHERE login=%(login)s 
            and password=crypt(%(password)s, password)
            """, {'login': login, 'password': password})
        if len(set(self.cursor)) == 0:
            print('Wrong password')
        else:
            self.cursor.execute(
                """
                SELECT role FROM users WHERE login=%(login)s 
                """, {'login': login})
            self.role, = one(self.cursor.fetchall())
            print('Log in is successful')

    def delete_account(self):
        """
        удаление аккаунта (с постами или без)
        """
        print("Do you want to delete your posts too?")
        print("[yes/no]?")
        answer = input()
        if answer == "yes":
            self.cursor.execute(
                """
                SELECT id FROM users WHERE login=%(login)s;
                """, {'login': self.login})

            user_id, = one(self.cursor.fetchall())

            self.cursor.execute(
                """
                select post_id from posts where user_id=%(user_id)s
                """, {'user_id': user_id})

            post_ids = self.cursor.fetchall()

            for post_id in post_ids:
                self.cursor.execute(
                    """
                    DELETE FROM posts WHERE post_id=%(post_id)s;
                    """, {'post_id': post_id})
            print("Posts are deleted")

        self.cursor.execute(
            """
            DELETE FROM users WHERE login=%(login)s 
            """, {'login': self.login})
        print(f"{self.login} is deleted")

    # ВЗАИМОДЕЙСТВИЕ С ПОСТАМИ

    def create_post(self):
        """
        создание поста (если в тексте есть хеш-тег, должен автоматически регистрироваться данный тег)
        """
        print("Enter text of your post:")
        text = input()
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            insert into posts (user_id, post) values(%(id)s, %(post)s);
            """, {'id': user_id, 'post': text})

        print('Post is added')

        self.cursor.execute(
            """
            select post_id from posts where user_id=%(user_id)s
            """, {'user_id': user_id})

        post_id, = self.cursor.fetchall()[-1]

        hashtags = re.findall(r'(#+[a-zA-Z0-9(_)]+)', text)

        for hashtag in hashtags:
            self.cursor.execute(
                """
                insert into hashtags (post_id, hashtag) values(%(post_id)s, %(hashtag)s);
                """, {'post_id': post_id, 'hashtag': hashtag})

    def view_my_posts(self):
        """
        просмотр своих постов (постраничный)
        """
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        print("Do you want to view firstly new or old posts?")
        print("[new/old]?")

        order = input()
        order = "DESC" if order == "new" else "ASC"

        self.cursor.execute(
            """
            SELECT post_id, time, post FROM posts WHERE user_id=%(user_id)s ORDER BY time """ + order
            , {'user_id': user_id})
        id_date_and_post = self.cursor.fetchall()

        for post in id_date_and_post:
            print(f'post id : {post[0]}')
            print(post[1].strftime("%Y-%m-%d %H:%M:%S"))
            print(post[2])
            print("\n")

    def delete_post(self):
        """
        удаление своего поста
        """
        print("Enter id of your post:")
        post_id = input()

        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            SELECT * FROM posts WHERE post_id=%(post_id)s and user_id=%(user_id)s;
            """, {'post_id': post_id, 'user_id': user_id})

        if len(self.cursor.fetchall()) == 0:
            print("It is not your post")
        else:
            self.cursor.execute(
                """
                DELETE FROM posts WHERE post_id=%(post_id)s;
                """, {'post_id': post_id})
            print("Post is deleted")

    def edit_post(self):
        """
        редактирование своего поста
        """
        print("Enter id of your post:")
        post_id = input()
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            SELECT * FROM posts WHERE post_id=%(post_id)s and user_id=%(user_id)s;
            """, {'post_id': post_id, 'user_id': user_id})

        if len(self.cursor.fetchall()) == 0:
            print("It is not your post")
        else:
            print("Enter new text of your post:")
            new_text = input()
            self.cursor.execute(
                """
                UPDATE posts set post = %(new_text)s WHERE post_id=%(post_id)s;
                """, {'post_id': post_id, 'new_text': new_text})
            print("Post is changed")

    def view_other_posts(self):
        """
        просмотр постов пользователя по логину (постраничный, упорядочивание по дате - от новых, от старых)
        """
        print("Enter login of user whose posts you would like to view:")
        login = input()

        self.cursor.execute("""
                            SELECT * FROM users WHERE login=%(login)s 
                            """, {'login': login})
        if len(self.cursor.fetchall()) == 0:
            print('Such login does not exist')
            return

        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': login})

        user_id, = one(self.cursor.fetchall())

        print("Do you want to view firstly new or old posts?")
        print("[new/old]?")

        order = input()
        order = "DESC" if order == "new" else "ASC"

        self.cursor.execute(
            """
            SELECT post_id, time, post FROM posts WHERE user_id=%(user_id)s ORDER BY time """ + order
            , {'user_id': user_id})
        id_date_and_post = self.cursor.fetchall()

        for post in id_date_and_post:
            print(f'post id : {post[0]}')
            print(post[1].strftime("%Y-%m-%d %H:%M:%S"))
            print(post[2])
            print("\n")

    # ВЗАИМОДЕЙСТВИЕ С ПОДПИСКАМИ

    def subscribe(self):
        """
        подписка на пользователя
        """
        print("Enter the login of user you would like to subscribe to:")
        login_to = input()
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': login_to})

        user_id_to, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id_from, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            INSERT INTO subscriptions (id_from, id_to) VALUES(%(id_from)s, %(id_to)s);
            """, {'id_from': user_id_from, 'id_to': user_id_to})
        print(f"You have been subscribed to user {login_to}")

    def check_subscriptions(self):
        """
        посмотреть подписки
        """
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            SELECT id_to FROM subscriptions WHERE id_from=%(user_id)s;
            """, {'user_id': user_id})

        subscriptions_id = [name for name, in self.cursor.fetchall()]

        print("Your subscriptions:")
        for sub_id in subscriptions_id:
            self.cursor.execute("""
                                SELECT login FROM users WHERE id=%(id)s 
                                """, {'id': sub_id})

            print(one(self.cursor.fetchall())[0])

    def check_subscribers(self):
        """
        посмотреть подписчиков
        """
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            SELECT id_from FROM subscriptions WHERE id_to=%(user_id)s;
            """, {'user_id': user_id})

        subscribers_id = [name for name, in self.cursor.fetchall()]

        print("Your subscribers:")
        for sub_id in subscribers_id:
            self.cursor.execute("""
                                SELECT login FROM users WHERE id=%(id)s 
                                """, {'id': sub_id})

            print(one(self.cursor.fetchall())[0])

    def mutual_sub(self):
        """
        посмотреть взаимные подписки
        """
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            SELECT id_to FROM subscriptions WHERE id_from=%(user_id)s;
            """, {'user_id': user_id})

        subscriptions_id = [name for name, in self.cursor.fetchall()]

        print("Your mutual subscriptions:")

        mutual_id = []
        for sub_id in subscriptions_id:

            self.cursor.execute("""
                                SELECT id_to FROM subscriptions WHERE id_from=%(sub_id)s 
                                """, {'sub_id': sub_id})
            if user_id in [name for name, in self.cursor.fetchall()]:
                mutual_id.append(sub_id)

        for mut_id in mutual_id:
            self.cursor.execute("""
                                SELECT login FROM users WHERE id=%(id)s 
                                """, {'id': mut_id})

            print(one(self.cursor.fetchall())[0])

    def check_sub_posts(self):
        """
        просмотр всех постов подписок (постраничный, упорядочивание по дате - от новых, от старых)
        """
        self.cursor.execute(
            """
            SELECT id FROM users WHERE login=%(login)s;
            """, {'login': self.login})

        user_id, = one(self.cursor.fetchall())

        self.cursor.execute(
            """
            SELECT id_to FROM subscriptions WHERE id_from=%(user_id)s;
            """, {'user_id': user_id})

        subscriptions_id = [name for name, in self.cursor.fetchall()]

        for name in subscriptions_id:
            self.cursor.execute(
                """
                SELECT time, post FROM posts WHERE user_id=%(user_id)s""", {'user_id': name})
            date_and_post = self.cursor.fetchall()

            self.cursor.execute(
                """
                SELECT login FROM users WHERE id=%(id)s;
                """, {'id': name})

            sub_name, = one(self.cursor.fetchall())

            print(f"posts from {sub_name}:")

            for post in date_and_post:
                print(post[0].strftime("%Y-%m-%d %H:%M:%S"))
                print(post[1])
                print("\n")

    # МОДЕРАЦИЯ

    def edit_other_post(self):
        """
        редактирование постов пользователей
        """
        print("Enter id of user`s post:")
        post_id = input()
        print("Enter new text of user`s post:")
        new_text = input()
        self.cursor.execute(
            """
            UPDATE posts set post = %(new_text)s WHERE post_id=%(post_id)s;
            """, {'post_id': post_id, 'new_text': new_text})
        print("Post is changed")

    def delete_other_account(self):
        """
        удаление аккаунта пользователя (с постами или без)
        """
        if self.role == "moderator" or "admin":
            print("Enter login of user you would like to delete")
            login = input()
            print("Do you want to delete posts of user too?")
            print("[yes/no]?")
            answer = input()
            if answer == "yes":
                self.cursor.execute(
                    """
                    SELECT id FROM users WHERE login=%(login)s;
                    """, {'login': login})

                user_id, = one(self.cursor.fetchall())

                self.cursor.execute(
                    """
                    select post_id from posts where user_id=%(user_id)s
                    """, {'user_id': user_id})

                post_ids = self.cursor.fetchall()

                for post_id in post_ids:
                    self.cursor.execute(
                        """
                        DELETE FROM posts WHERE post_id=%(post_id)s;
                        """, {'post_id': post_id})
                print("Posts are deleted")
                self.cursor.execute("""
                                      DELETE FROM users WHERE login=%(login)s 
                                      """, {'login': login})
                print(f"{login} is deleted")
            else:
                print("Permission denied")

    def delete_other_post(self):
        """
        удаление поста пользователя
        """
        if self.role == "moderator" or "admin":
            print("Enter id of user`s post you would like to delete:")
            post_id = input()

            self.cursor.execute(
                """
                DELETE FROM posts WHERE post_id=%(post_id)s;
                """, {'post_id': post_id})
            print("Post is deleted")
        else:
            print("Permission denied")

    # АДМИНИСТРИРОВАНИЕ

    def change_rights(self):
        """
        изменение прав доступа
        """
        if self.role == "admin":
            print("Enter login of user whose rights you would like to update:")
            login = input()
            print("Would you like to upgrade to moderator or downgrade to user?:")
            print("[upgrade/downgrade]?")
            role = input()
            if role == "upgrade":
                role = "moderator"
            elif role == "downgrade":
                role = "user"
            else:
                print("incorrect input")
                self.change_rights()
            self.cursor.execute(
                """
                SELECT id FROM users WHERE login=%(login)s;
                """, {'login': login})

            user_id, = one(self.cursor.fetchall())

            self.cursor.execute(
                """
                UPDATE users set role = %(new_role)s WHERE id=%(user_id)s;
                """, {'user_id': user_id, 'new_role': role})
            print("Role is changed")
        else:
            print("Permission denied")
