import typing
from typing import Dict


class Replies:
    def __init__(self):
        self.emojis = None
        self.balance = None
        self.no_outcome_found = None
        self.no_income_found = None
        self.add_outcome_success = None
        self.list_income = None
        self.add_income_success = None
        self.delete = None
        self.start = None

    def init(self):
        self.start: str = "Hi! I will help you keep track of your expenses :) \nYou can simply add an income just " \
                          "typing '+value comment' or an outcome typing '-value comment'"
        self.delete: str = "With this command you can delete a wrong entry, \nSimply type /delete +/-value comment." \
                           "\nIf you do not remember the comment just type /listincome or /listoutcome"

        self.add_income_success: str = f'Income successfully registered {self.get_emoji_unicode("moneybag")}'
        self.add_outcome_success: str = f'Outcome successfully registered {self.get_emoji_unicode("moneywings")}'
        self.list_income: str = f'Current month income list:\n\n'
        self.no_income_found: str = f'No income to be displayed here {self.get_emoji_unicode("openhands")}'
        self.no_outcome_found: str = f'No outcome to be displayed here {self.get_emoji_unicode("openhands")}'
        self.balance: str = "Current month balance: {0} €\n\n\nTotal income: {1} €\n\nTotal outcome: {2} €"
        self.emojis: Dict = {
            "moneybag": u'\U0001F4B0',
            "moneywings": u'\U0001F4B8',
            "openhands": u'\U0001F450'
        }

    @property
    def emoji(self):
        return self.emojis

    def get_emoji_unicode(self, emoji_name: str) -> typing.Union[str, None]:
        return self.emoji.get(emoji_name, None)
