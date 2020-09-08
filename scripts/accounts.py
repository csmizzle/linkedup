import random


def get_account():
    """
    TODO: Clean up and eventually remove this
    :return:
    """
    account_list = [
        ['', ''],  # add accounts here for linkedin login
    ]
    account = random.choice(account_list)
    return account
