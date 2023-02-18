class Interface:
    def greeting(self):
        print("Would you like to sign up or log in?")
        print("[sign up/log in]?")
        sign_up_or_log_in = input()
        return sign_up_or_log_in

    def check_opportunities(self, user):
        print("Your opportunities:")
        print("""
        1. delete account
        2. create post
        3. view your posts
        4. delete your post
        5. edit your post
        6. check user posts by login
        7. subscribe on user
        8. check subscribtions
        9. check subcsribers
        10. check mutual subscribtions 
        11. check all posts from subscribtions
        12. log out
        """)
        if self.check_rules(user, 13):
            print("""
            moderation opportunities:
            13. edit post by login
            14. delete account by login
            15. delete post by login
            """)
        if self.check_rules(user, 16):
            print("""
            administration opportunity:
            16. change role by login
            """)

    def check_rules(self, user, action):
        permissions = {
            "user" : list(range(1,13)),
            "moderator" : list(range(1,16)),
            "admin" : list(range(1,17))
        }
        return action in permissions[user.role]


    def do_action(self, user):
        print("Choose action:")
        action = input()
        if not action.isdigit():
            print("Invalid input")
            return self.do_action(user)
        action = int(action)
        if self.check_rules(user, action):
            match action:
                case 1:
                    user.delete_account()
                case 2:
                    user.create_post()
                case 3:
                    user.view_my_posts()
                case 4:
                    user.delete_post()
                case 5:
                    user.edit_post()
                case 6:
                    user.view_other_posts()
                case 7:
                    user.subscribe()
                case 8:
                    user.check_subscriptions()
                case 9:
                    user.check_subscribers()
                case 10:
                    user.mutual_sub()
                case 11:
                    user.check_sub_posts()
                case 12:
                    # log out
                    return True
                case 13:
                    user.edit_other_post()
                case 14:
                    user.delete_other_account()
                case 15:
                    user.delete_other_post()
                case 16:
                    user.change_rights()
        else:
            print("Permission denied")

