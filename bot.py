from datetime import datetime
import logging
from dbHelper import DBHelper
from messageHandler import MessageHandler


logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

db = DBHelper()
f = open("master.txt", "r")
master = int(f.readline())
if not master:
    logging.error("Error occurred, have you filled the master.txt file with your master id?")
    exit()


handler = MessageHandler()
messages = [
    "/start",
    "/delete"
]
reply = {
    "/start": "Hi! I will help you keep track of your expenses :) \nYou can simply add an income just typing "
              "'+value comment' or an outcome typing '-value comment'",
    "/delete": "With this command you can delete a wrong entry, \nSimply type /delete +/-value comment."
               "\nIf you do not remember the comment just type /listincome or /listoutcome"
}

# i found those code here https://apps.timwhitlock.info/emoji/tables/unicode :)
emoji = {
    "moneybag": u'\U0001F4B0',
    "moneywings": u'\U0001F4B8'
}


def add_income(value, comment):
    date = datetime.now().strftime("%Y-%m-%d")
    db.add_income(date, value, comment)


def delete_entry(text):
    value = text[1:text.index(" ")]
    comment = text[text.index(" ") + 1:len(text)]
    if text.startswith("+"):
        db.delete_income(value, comment)
    elif text.startswith("-"):
        db.delete_outcome(value, comment)


def add_outcome(value, comment):
    date = datetime.now().strftime("%Y-%m-%d")
    db.add_outcome(date, value, comment)


def text_handler(text, chat_id):
    message = ""  # to avoid reference before assignment error
    if text in messages:
        handler.send_message(reply[text], chat_id)
    elif text.startswith("+"):
        add_income(text[1:text.index(" ")], text[text.index(" ")+1:len(text)])
        message = "Income successfully registered "+emoji["moneybag"]
    elif text.startswith("-"):
        add_outcome(text[1:text.index(" ")], text[text.index(" ")+1:len(text)])
        message = "Outcome successfully registered " + emoji["moneywings"]
    elif text.startswith("/delete"):
        text = text.replace('/delete ', '')
        delete_entry(text)
        message = "Entry removed successfully"
    elif text == "/listincome":
        month = datetime.now().strftime("%m")
        rows = db.get_income(month)
        logging.info(rows)
        message = "Current month income list:\n\n"
        for r in rows:
            message = message + str(r).replace("(", "").replace(")", "").replace("'", "") + "\n"
    elif text == "/listoutcome":
        month = datetime.now().strftime("%m")
        rows = db.get_outcome(month)
        logging.info(rows)
        message = "Current month outcome list:\n\n"
        for r in rows:
            message = message+str(r).replace("(", "").replace(")", "").replace("'", "")+"\n"
    handler.send_message(message, chat_id)


def main():
    db.setup()
    last_update_id = None
    while True:
        updates = handler.get_updates(last_update_id)
        if not updates:
            logging.info("no updates found")
        else:
            if len(updates["result"]) > 0:
                last_update_id = handler.get_last_update_id(updates) + 1
                logging.debug(last_update_id)
                if handler.id_check(updates):
                    text, chat_id = handler.get_text_and_chat(updates)
                    name = handler.get_name(updates)
                    logging.debug("Message: {} From: {}".format(text, chat_id))
                    text_handler(text, chat_id)


if __name__ == '__main__':
    main()

