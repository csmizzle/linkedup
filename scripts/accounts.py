import random


def get_account() -> list:
    """
    Randomly selects linkedin creds if the user has multiple account for educational purposes ... ;)
    :return: account selection from
    """
    account_list = [
        ['', ''],  # add accounts here for linkedin login
    ]
    account = random.choice(account_list)
    return account
