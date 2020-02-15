import requests
import os
import json
import logging
from datetime import datetime
from urllib import parse
from sys import exit

#------------------- LOGGER SETUP -------------------#
LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)


#------------------- TELEGRAM URL SETUP -------------------#
#------------------- CREATE TOKEN FILE
if not os.path.exists("token.txt"):
    LOGGER.info("Creating token.txt file")
    f = open("token.txt", "w+")
    f.close()
    LOGGER.error("token.txt file created, fill it with your token to get started")

#------------------- CHECK TOKEN
f = open("token.txt", "r")
TOKEN = f.readline()
if not TOKEN:
    LOGGER.error("Error occurred, have you filled the token.txt file with your bot token?")
    exit()
#------------------- URL COMPOSITION
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


#------------------- CLASS DEFIINITION -------------------#
class MessageHandler:
    # ------------------- INIT
    def __init__(self):
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

        self.master = 000000
        self.allowed = []
        self.get_files()

    # ------------------- GET FILES
    def get_files(self):
        f = open("master.txt", "r")
        self.master = int(f.readline())
        if not self.master:
            LOGGER.error("Error occurred, have you filled the master.txt file with your master id?")
            exit()

        f1 = open("valid_users.txt", "r")
        self.allowed = f1.readlines()
        if not self.allowed:
            f1.close()
            LOGGER.error("Allowed file empty, filling with masted id")
            f1 = open("valid_users.txt", "a")
            f1.write(str(self.master))
            f1.close()
            self.allowed.append(self.master)

    # ------------------- GET URL
    def get_url(self, url):
        try:
            response = requests.get(url)
            content = response.content.decode("utf8")
            LOGGER.info("Response message: {}".format(content))
        except requests.exceptions.ConnectionError:
            content = str({
                "ok": True,
                "result": []
            })
            LOGGER.info("Max retries exceed, passing composed content: {}".format(content))
        return content

    # ------------------- GET JSON FROM URL
    def get_json_from_url(self, url):
        content = self.get_url(url)
        try:
            js = json.loads(content)
            LOGGER.info("Got json from url: {}".format(js))
        except AttributeError:
            LOGGER.error("Attribute error, content was {}".format(content))
            js = json.loads(self.get_url(url))
        except json.decoder.JSONDecodeError:
            LOGGER.error("Json decode error, content was {}\n".format(content))
            js = json.loads(self.get_url(url))
        return js

    # ------------------- GET UPDATES
    def get_updates(self, offset=None):
        url = URL + "getUpdates?timeout=240"
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    # ------------------- GET LAST UPDATE ID
    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    # ------------------- SEND MESSAGE
    def send_message(self, text, chat_id: int, reply_markup=None):
        text = parse.quote_plus(text)
        url = URL + "SendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
        if reply_markup:
            url += "&reply_markup={}".format(reply_markup)
        self.get_url(url)

    # ------------------- GET TEXT AND CHAT ID
    def get_text_and_chat(self, updates):
        len_updates = len(updates["result"])
        last_update = len_updates - 1
        try:
            text = updates["result"][last_update]["message"]["text"]
        except:
            LOGGER.error("No valid text provided!")
            text = "No valid text provided"
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return text, chat_id

    # ------------------- GET NAME
    def get_name(self, updates):
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
            try:
                name = update["message"]["chat"]["first_name"]
            except KeyError:
                # write_log2("no_name", time)
                name = "n/a"
            try:
                surname = update["message"]["chat"]["last_name"]
            except KeyError:
                # write_log2("no_surname", time)
                surname = "n/a"
        return name

    # ------------------- ID CHECK
    def id_check(self, updates):
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
            LOGGER.debug("chat: {}, allowed: {}".format(chat, self.allowed))
            date = update["message"]["date"]
            time = datetime.fromtimestamp(date)
            time = time.strftime('%Y-%m-%d at %H:%M:%S')
            try:
                name = update["message"]["chat"]["first_name"]
            except KeyError:
                name = "n/a"
            try:
                surname = update["message"]["chat"]["last_name"]
            except KeyError:
                surname = "n/a"
            try:
                username = update["message"]["chat"]["username"]
            except KeyError:
                username = "n/a"

        if str(chat) in self.allowed:
            LOGGER.info("Connection from: {}".format(chat))
            return 1
        else:
            self.send_message("Unknown user, access denied. Contact system admin", chat)
            message = [name, " ", surname, "\nUsername: ", username, "\nID: ", chat, "\nAt: ", str(time),
                       "Per aggiungere l'utente usare il comando /adduser #chatid"]

            self.send_message(message, self.master)
            return 0

    # ------------------- ADD USER
    def add_user(self, user):
        f = open("valid_users.txt", "a")
        f.write(user+"\n")
        f.close()
        self.send_message("You are now allowed to use ths bot, congratulations! type /start to begin :)", user)
        LOGGER.info("User {} added to valid users".format(user))
        self.get_files()