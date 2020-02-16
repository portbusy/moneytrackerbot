from datetime import datetime
import logging
from dbHelper import DBHelper
import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, PrefixHandler
import re


#------------------- LOGGER SETUP -------------------#
LOG_FORMAT = ('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)




#------------------- CHECK TOKEN, MASTER & VALID USERS -------------------#
f = open("token.txt", "r")
TOKEN = f.readline()
if not TOKEN:
    LOGGER.error("Error occurred, have you filled the token.txt file with your bot token?")
    exit()

if not os.path.exists("master.txt"):
    LOGGER.info("Creating master.txt file...")
    f = open("master.txt", "w+")
    f.close()
    LOGGER.info("master.txt file created, fill it to get started")
    exit()

if not os.path.exists("valid_users.txt"):
    LOGGER.info("Creating valid_users.txt file...")
    f = open("valid_users.txt", "w+")
    f.close()
    LOGGER.info("valid_users.txt file created")



#------------------- MESSAGE VARIABLES -------------------#
global del_user_flag
global del_user_name

del_user_flag= False
del_user_name = None
# i found those code here https://apps.timwhitlock.info/emoji/tables/unicode :)
emoji = {
    "moneybag": u'\U0001F4B0',
    "moneywings": u'\U0001F4B8',
    "openhands": u'\U0001F450',
    "wink": u'\U0001F609',
    "flag": u'\U0001F6A8'
}


#------------------- DB VARIABLES -------------------#
users_db = dict()


#------------------- MESSAGES FUNCTIONS -------------------#
#------------------- START CALLBACK
def start_callback(update, context):
    chat_id = update.effective_chat.id
    message = "Hi! I will help you keep track of your expenses :) \nYou can simply add an income just typing " \
              "'+value comment' or an outcome typing '-value comment'.\nFor more details use /help command"
    context.bot.send_message(text=message, chat_id=chat_id)



#------------------- ADD INCOME
def add_income(update, context):
    text = update.message.text.strip("/income ")
    chat_id = update.effective_chat.id
    try:
        value = text[0:text.index(" ")]
        comment = text[text.index(" ")+1:len(text)]
        date = datetime.now().strftime("%Y-%m-%d")
        users_db[str(chat_id)].add_income(date, value, comment, dbname=str(chat_id)+".sqlite")
        message = "Income successfully registered "+emoji["moneybag"]
    except ValueError:
        message = "Incomplete message, the usage is /income amount comment :)"

    context.bot.send_message(text=message, chat_id=chat_id)
#------------------- LIST INCOME
def list_income(update, context):
    chat_id = update.effective_chat.id
    month = datetime.now().strftime("%m")
    rows = users_db[str(chat_id)].get_income(month, dbname=str(chat_id) + ".sqlite")
    LOGGER.info(rows)
    if rows:
        message = "Current month income list:\n\n"
        for r in rows:
            message = message + str(r).replace("(", "").replace(")", "").replace("'", "") + "\n"
        total_income = users_db[str(chat_id)].get_total_income(month, dbname=str(chat_id) + ".sqlite")
        message = message + "\n\nTotal income: " + str(total_income) + " €"
    else:
        message = "No income to be displayed here " + emoji["openhands"]

    context.bot.send_message(text=message, chat_id=chat_id)



#------------------- ADD OUTCOME
def add_outcome(update, context):
    text = update.message.text.strip("/outcome ")
    chat_id = update.effective_chat.id
    try:
        value = text[0:text.index(" ")]
        comment = text[text.index(" ")+1:len(text)]
        date = datetime.now().strftime("%Y-%m-%d")
        users_db[str(chat_id)].add_outcome(date, value, comment, dbname=str(chat_id) + ".sqlite")
        message = "Outcome successfully registered " + emoji["moneywings"]
    except ValueError:
        message = "Incomplete message, the usage is /income amount comment :)"

    context.bot.send_message(text=message, chat_id=chat_id)
#------------------- LIST OUTCOME
def list_outcome(update, context):
    chat_id = update.effective_chat.id
    month = datetime.now().strftime("%m")
    rows = users_db[str(chat_id)].get_outcome(month, dbname=str(chat_id) + ".sqlite")
    LOGGER.info("Rows obtained: {}".format(rows))
    if rows:
        message = "Current month outcome list:\n\n"
        for r in rows:
            message = message + str(r).replace("(", "").replace(")", "").replace("'", "") + "\n"
        total_outcome = users_db[str(chat_id)].get_total_outcome(month, dbname=str(chat_id) + ".sqlite")
        message = message + "\n\nTotal income: " + str(total_outcome) + " €"
    else:
        message = "No income to be displayed here " + emoji["openhands"]

    context.bot.send_message(text=message, chat_id=chat_id)



#------------------- DELETE ENTRY
def delete_entry(update, context):
    text = update.message.text.strip("/delete ")
    chat_id = update.effective_chat.id
    try:
        value = text[1:text.index(" ")]
        comment = text[text.index(" ") + 1:len(text)]
        if text.startswith("+"):
            users_db[str(chat_id)].delete_income(value, comment, dbname=str(chat_id)+".sqlite")
        elif text.startswith("-"):
            users_db[str(chat_id)].delete_outcome(value, comment, dbname=str(chat_id)+".sqlite")
        message = "Entry removed successfully"
    except ValueError:
        message = "Incomplete message, the usage is /delete +/-amount comment :)"

    context.bot.send_message(text=message, chat_id=chat_id)



#------------------- BALANCE
def balance(update, context):
    chat_id = update.effective_chat.id
    month = datetime.now().strftime("%m")
    total_income = users_db[str(chat_id)].get_total_income(month, dbname=str(chat_id) + ".sqlite")
    if total_income is None:
        total_income = 0.0
    total_outcome = users_db[str(chat_id)].get_total_outcome(month, dbname=str(chat_id) + ".sqlite")
    if total_outcome is None:
        total_outcome = 0.0
    LOGGER.info(total_outcome)
    balance = total_income - total_outcome
    message = "Current month balance: " + str(balance) + " €\n\n\nTotal income: " + str(total_income) + \
              " €\n\nTotal outcome: " + str(total_outcome) + " €"

    context.bot.send_message(text=message, chat_id=chat_id)


#------------------- USER MANAGEMENT
#------------------- ADD USER
def add_user(update, context):
    text = update.message.text.strip("/adduser ")
    chat_id = update.effective_chat.id
    user = text[0:len(text)]
    if id_check(update, chat_id):
        f = open("valid_users.txt", "a+")
        f.write("\n"+user)
        f.close()
        try:
            context.bot.send_message(text="You are now allowed to use ths bot, congratulations! type /start to begin :)", chat_id=user)
        except Exception:
            LOGGER.info(Exception)
        LOGGER.info("User {} added to valid users".format(user))
        _,allowed = get_files()
        message = "User " + user + " added successfully!"
        users_dbs_handler(allowed)
    else:
        message = "You are not allowed to use this function!"

    context.bot.send_message(text=message, chat_id=chat_id)
#------------------- LIST USERS
def list_user(update, context):
    chat_id = update.effective_chat.id
    if id_check(update, chat_id):
        with open("valid_users.txt", "r") as f:
            users = f.readlines()
        f.close()
        message = "Allowed users:\n\n"
        for user in users:
            message += user+"\n"
        message += "\nTo delete one use the /deluser command"
    else:
        message = "You are not allowed to use this function!"

    context.bot.send_message(text=message, chat_id=chat_id)
#------------------- REMOVE USER
def del_user(update, context, confirm_del=False):
    global del_user_flag
    global del_user_name
    text = update.message.text.strip("/deluser ")
    chat_id = update.effective_chat.id
    user = text[0:len(text)]
    if id_check(update, chat_id):
        master, allowed = get_files()
        if user != "" and confirm_del and user != master and del_user_name in allowed:
            user = del_user_name
            with open("valid_users.txt", "r") as f:
                lines = f.readlines()
            with open("valid_users.txt", "w") as f:
                for line in lines:
                    if line.strip("\n") != user and not re.match(r'^\n*$', line) and line != "":
                        f.write(line)
            f.close()
            LOGGER.info("User {} removed from valid users".format(user))
            _,allowed = get_files()
            message = "User " + user + " removed successfully!"
            os.remove(user+".sqlite")
            users_dbs_handler(allowed)
            del_user_flag = False
            del_user_name = None
        elif user != "" and not confirm_del and user in allowed:
            message = emoji["flag"]+"Are you sure you want to delete user "+user+" ? This action is irreversible"+emoji["flag"]
            del_user_flag = True
            del_user_name = user
        elif user != "" and user not in allowed:
            message = "This username is not stored, type /listuser for the complete user list"

        else:
            message = "You must insert a valid user to delete, type /listuser for the complete user list"
    else:
        message = "You are not allowed to use this function!"

    context.bot.send_message(text=message, chat_id=chat_id)



#------------------- TEXT HANDLER
def text_handler(update, context):
    text = update.message.text
    if (text == "yes" or text == "Yes") and del_user_flag == True:
        confirm_del = True
        LOGGER.info("Sending delete request")
        del_user(update, context, confirm_del)
    else:
        message = "No valid text provided, try with /start "+emoji["wink"]
        context.bot.send_message(text=message, chat_id=update.effective_chat.id)


#------------------- ERROR HANDLER
def error(update, context):
    """Log Errors caused by Updates."""
    LOGGER.warning('Update "%s" caused error "%s"', update, context.error)



#------------------- AUXILIARY FUNCTIONS -------------------#
#------------------- GET FILES
def get_files():
    f = open("master.txt", "r")
    master = int(f.readline().replace('\n', ''))
    if not master:
        LOGGER.error("Error occurred, have you filled the master.txt file with your master id?")
        exit()
    f.close()
    f1 = open("valid_users.txt", "r")
    allowed = f1.read().splitlines()
    if not allowed:
        f1.close()
        LOGGER.error("Allowed file empty, filling with masted id")
        f1 = open("valid_users.txt", "a")
        f1.write(str(master))
        f1.close()
        allowed.append(master)
    f1.close()
    allowed = list(filter(lambda a: a != "", allowed))
    LOGGER.info("Done getting files, results {} {}".format(master, allowed))
    return master, allowed



#------------------- ID CHECK
def id_check(update, chat):
    text = update.message.text.strip("/deluser ")
    f = open("master.txt", "r")
    master = f.readline()
    if chat == int(master) and text != master:
        #LOGGER.info("Connection from: {}".format(chat))
        return 1
    else:
        return 0



#------------------- DB FUNCTIONS -------------------#
#------------------- CREATE  DBS
def users_dbs_handler(allowed): #create a db for each user
    for i in allowed:
        if i != "\n" and i != "" and len(str(i))>0:
            users_db[str(i)] = allowed.index(i)
    for i in allowed:
        if i != "\n" and i != "" and len(str(i)) > 0:
            users_db[str(i)] = DBHelper(dbname=str(i) + ".sqlite")
            users_db[str(i)].setup()
    LOGGER.info("Create user_dbs list {}".format(allowed))


#------------------- MAIN -------------------#
def main():
    master, allowed = get_files()
    users_dbs_handler(allowed)

    updater = Updater(TOKEN, use_context=True)

    #used for handlers registration
    dispatcher = updater.dispatcher

    #start function
    dispatcher.add_handler(CommandHandler("start", start_callback))

    #income handler
    dispatcher.add_handler(CommandHandler("income", add_income))
    dispatcher.add_handler(CommandHandler("listincome", list_income))

    #outcome handler
    dispatcher.add_handler(CommandHandler("outcome", add_outcome))
    dispatcher.add_handler(CommandHandler("listoutcome", list_outcome))

    #delete entry handler
    dispatcher.add_handler(CommandHandler("delete", delete_entry))

    #get balance handler
    dispatcher.add_handler(CommandHandler("balance", balance))

    #add user handler
    dispatcher.add_handler(CommandHandler("adduser", add_user))

    dispatcher.add_handler(CommandHandler("listuser", list_user))

    dispatcher.add_handler(CommandHandler("deluser", del_user))

    dispatcher.add_handler(MessageHandler(Filters.text, text_handler))
    dispatcher.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
