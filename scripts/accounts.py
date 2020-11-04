import random


def get_account() -> list:
    """
    Randomly selects linkedin creds if the user has multiple account for educational purposes ... ;)
    :return: account selection from
    """
    account_list = [
        ['chrissmith700@gmail.com', 'Hq4_7!lowbar'], # add accounts here for linkedin login
        # ['jmariegao@gmail.com', "c5@'F>LjMN`^(#<?"]
    ]
    account = random.choice(account_list)
    return account
