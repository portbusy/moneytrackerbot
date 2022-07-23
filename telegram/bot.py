import logging
import sys
from datetime import datetime

from telebot import TeleBot
from telebot.types import Message

from db_manager import DatabaseManager
from models.replies import Replies
from . import configs

LOGGER = logging.getLogger(__name__)


def _retrieve_token(token_path: str = configs.DEFAULT_TOKEN_POSITION.get()) -> str:
    try:
        with open(token_path, "r") as token_file:
            _token = token_file.readline()
            if not _token:
                LOGGER.error(f'The provided file was empty, check the file again')
                sys.exit(0)
            return _token
    except FileNotFoundError:
        LOGGER.error(f'File {token_path} not found')
        sys.exit(0)


class MoneyTrackerBot:

    _bot = TeleBot(token=_retrieve_token())

    def __init__(self):
        self._replies = Replies()
        self._db = DatabaseManager()
        self._last_update_id = None

    @staticmethod
    def split_expense_message(message: str):
        """Split the message sent by the user with the format '+/-expense_value comment'"""
        value = message[1:message.index(" ")]
        comment = message[message.index(" ") + 1:len(message)]
        return value, comment

    @staticmethod
    def format_expense_row(row):
        row = f"{row}".replace("(", "").replace(")", "").replace("'", "")
        return f"{row}\n"

    @_bot.message_handler(commands=['start', 'help'])
    def welcome_message(self, message: Message):
        """Handles 'start' and 'help' commands"""
        self._bot.reply_to(message, self._replies.start)

    @_bot.message_handler(regexp="+\d{1,}\s\w{1,}")
    def add_income(self, message: Message):
        """Handles messages that are income-related"""
        income_value, income_comment = self.split_expense_message(message.text)
        self._db.add_income(message.date, income_value, income_comment)
        self._bot.reply_to(message, self._replies.add_income_success)

    @_bot.message_handler(regexp="-\d{1,}\s\w{1,}")
    def add_outcome(self, message: Message):
        """Handles messages that are outcome-related"""
        outcome_value, outcome_comment = self.split_expense_message(message.text)
        self._db.add_outcome(message.date, outcome_value, outcome_comment)
        self._bot.reply_to(message, self._replies.add_outcome_success)

    @_bot.message_handler(commands=['listincome'])
    def list_income(self, message: Message):
        """List all the income for the current month"""
        # TODO: add a method to list the income for a specific month
        current_month = datetime.now().strftime("%m")
        rows = self._db.get_income(current_month)
        LOGGER.debug(f'Fetched entries: {rows}')
        if rows:
            income_list: str = ""
            for row in rows:
                income_list += self.format_expense_row(row)
            month_total_income = self._db.get_total_income(current_month)
            LOGGER.debug(f'Month total: {month_total_income}, formatted income list: {income_list}')
            self._bot.reply_to(message, f'{self._replies.list_income}\n\n{income_list}\n\n'
                                        f'Total income: {month_total_income} €')
        else:
            self._bot.reply_to(message, self._replies.no_income_found)

    @_bot.message_handler(commands=['listoutcome'])
    def list_outcome(self, message: Message):
        """List all the outcome for the current month"""
        # TODO: add a method to list the outcome for a specific month
        current_month = datetime.now().strftime("%m")
        rows = self._db.get_outcome(current_month)
        LOGGER.debug(f'Fetched entries: {rows}')
        if rows:
            outcome_list: str = ""
            for row in rows:
                outcome_list += self.format_expense_row(row)
            month_total_outcome = self._db.get_total_outcome(current_month)
            LOGGER.debug(f'Month total: {month_total_outcome}, formatted income list: {outcome_list}')
            self._bot.reply_to(message, f'{self._replies.list_income}\n\n{outcome_list}\n\n'
                                        f'Total income: {month_total_outcome} €')
        else:
            self._bot.reply_to(message, self._replies.no_outcome_found)

    @_bot.message_handler(commands=['balance'])
    def balance(self, message: Message):
        current_month = datetime.now().strftime("%m")
        month_total_outcome = self._db.get_total_outcome(current_month)
        month_total_income = self._db.get_total_income(current_month)
        if month_total_income is None:
            month_total_income = 0.0
        elif month_total_outcome is None:
            month_total_outcome = 0.0

        LOGGER.debug(f'Total income: {month_total_income}, Total outcome: {month_total_outcome}')
        month_balance = month_total_income - month_total_outcome
        self._bot.reply_to(
            message,
            self._replies.balance.format(
                month_balance,
                month_total_income,
                month_total_outcome
            )
        )

    def start(self):
        LOGGER.info(f'Starting bot')
        self._bot.infinity_polling()
