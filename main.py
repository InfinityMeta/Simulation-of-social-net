import functionality as f
from interface import Interface


def main():
    conn = f.create_connection()
    conn.autocommit = True

    interface = Interface()
    sign_up_or_log_in = interface.greeting()

    if sign_up_or_log_in == "sign up":
        user = f.User(conn, True)

    elif sign_up_or_log_in == "log in":
        user = f.User(conn, False)
    else:
        print("Incorrect input")
        return 0

    interface.check_opportunities(user)

    while True:
        if interface.do_action(user):
            break
    return 1


if __name__ == '__main__':
    main()
