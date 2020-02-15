from datetime import datetime
import logging
from dbHelper import DBHelper
from messageHandler import MessageHandler

#------------------- LOGGER SETUP -------------------#
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funName) -35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


#------------------- MESSAGE VARIABLES -------------------#
handler = MessageHandler() #message handler

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
    "moneywings": u'\U0001F4B8',
    "openhands": u'\U0001F450'
}


#------------------- DB VARIABLES -------------------#
users_db = dict()


#------------------- MESSAGES FUNCTIONS -------------------#
#------------------- ADD INCOME
def add_income(value, comment, chat_id):
    date = datetime.now().strftime("%Y-%m-%d")
    users_db[str(chat_id)].add_income(date, value, comment, dbname=str(chat_id)+".sqlite")

#------------------- DELETE ENTRY
def delete_entry(text, chat_id):
    value = text[1:text.index(" ")]
    comment = text[text.index(" ") + 1:len(text)]
    if text.startswith("+"):
        users_db[str(chat_id)].delete_income(value, comment, dbname=str(chat_id)+".sqlite")
    elif text.startswith("-"):
        users_db[str(chat_id)].delete_outcome(value, comment, dbname=str(chat_id)+".sqlite")

#------------------- ADD OUTCOME
def add_outcome(value, comment, chat_id):
    date = datetime.now().strftime("%Y-%m-%d")
    users_db[str(chat_id)].add_outcome(date, value, comment, dbname=str(chat_id)+".sqlite")

#------------------- HANDLE TEXT
def text_handler(text, chat_id):
    message = ""  # to avoid reference before assignment error
    if text in messages:
        handler.send_message(reply[text], chat_id)
    elif text.startswith("+"):
        add_income(text[1:text.index(" ")], text[text.index(" ")+1:len(text)], chat_id)
        message = "Income successfully registered "+emoji["moneybag"]
    elif text.startswith("-"):
        add_outcome(text[1:text.index(" ")], text[text.index(" ")+1:len(text)], chat_id)
        message = "Outcome successfully registered " + emoji["moneywings"]
    elif text.startswith("/delete"):
        text = text.replace('/delete ', '')
        delete_entry(text, chat_id)
        message = "Entry removed successfully"
    elif text == "/listincome":
        month = datetime.now().strftime("%m")
        rows = users_db[str(chat_id)].get_income(month, dbname=str(chat_id)+".sqlite")
        LOGGER.info(rows)
        if rows:
            message = "Current month income list:\n\n"
            for r in rows:
                message = message + str(r).replace("(", "").replace(")", "").replace("'", "") + "\n"
            total_income = users_db[str(chat_id)].get_total_income(month, dbname=str(chat_id)+".sqlite")
            message = message+"\n\nTotal income: "+str(total_income)+" €"
        else:
            message = "No income to be displayed here " + emoji["openhands"]
    elif text == "/listoutcome":
        month = datetime.now().strftime("%m")
        rows = users_db[str(chat_id)].get_outcome(month, dbname=str(chat_id)+".sqlite")
        LOGGER.info("Rows obtained: {}".format(rows))
        if rows:
            message = "Current month outcome list:\n\n"
            for r in rows:
                message = message+str(r).replace("(", "").replace(")", "").replace("'", "")+"\n"
            total_outcome = users_db[str(chat_id)].get_total_outcome(month, dbname=str(chat_id)+".sqlite")
            message = message+"\n\nTotal income: "+str(total_outcome)+" €"
        else:
            message = "No income to be displayed here " + emoji["openhands"]
    elif text == "/balance":
        month = datetime.now().strftime("%m")
        total_income = users_db[str(chat_id)].get_total_income(month, dbname=str(chat_id)+".sqlite")
        if total_income is None:
            total_income = 0.0
        total_outcome = users_db[str(chat_id)].get_total_outcome(month, dbname=str(chat_id)+".sqlite")
        if total_outcome is None:
            total_outcome = 0.0
        LOGGER.info(total_outcome)
        balance = total_income - total_outcome
        message = "Current month balance: "+str(balance)+" €\n\n\nTotal income: "+str(total_income)+\
                  " €\n\nTotal outcome: "+str(total_outcome)+" €"
    elif text == "/adduser" and chat_id in handler.allowed:
        user = text[9:len(text)]
        handler.add_user(user=user)
        message="User "+user+" added successfully!"
        users_dbs_handler()
    else:
        message = "Sorry, I cannot process your message :( plese use /start to get started"
    handler.send_message(message, chat_id)


#------------------- DB FUNCTIONS -------------------#
#------------------- CREATE  DBS
def users_dbs_handler(): #create a db for each user
    for i in handler.allowed:
        users_db[str(i)] = handler.allowed.index(i)

    for i in handler.allowed:
        users_db[str(i)] = DBHelper(dbname=str(i) + ".sqlite")
        users_db[str(i)].setup()


#-------------------------------------- MAIN FUNCION --------------------------------------#
def main():
    users_dbs_handler()
    last_update_id = None
    while True:
        LOGGER.info("Getting updates")
        updates = handler.get_updates(last_update_id)
        if not updates:
            LOGGER.info("No updates found")
        elif updates != []:
            if len(updates["result"]) > 0:
                last_update_id = handler.get_last_update_id(updates) + 1
                LOGGER.debug(last_update_id)
                if handler.id_check(updates):
                    text, chat_id = handler.get_text_and_chat(updates)
                    name = handler.get_name(updates)
                    LOGGER.debug("Message: {} From: {}".format(text, chat_id))
                    text_handler(text, chat_id)

        else:
            LOGGER.error("Updates error, update was{} ".format(updates))


if __name__ == '__main__':
    main()
