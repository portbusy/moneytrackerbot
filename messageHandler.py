import requests
import json
import logging
from datetime import datetime
from urllib import parse
from sys import exit

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

f = open("token.txt", "r")
TOKEN = f.readline()
if not TOKEN:
    logging.error("Error occurred, have you filled the token.txt file with your bot token?")
    exit()

URL = "https://api.telegram.org/bot{}/".format(TOKEN)

f = open("master.txt", "r")
master = int(f.readline())
if not master:
    logging.error("Error occurred, have you filled the master.txt file with your master id?")
    exit()


class MessageHandler:

    def __init__(self):
        self.master = master
        self.allowed = [self.master]

    #
    def get_url(self, url):
        try:
            response = requests.get(url)
            content = response.content.decode("utf8")
        except requests.exceptions.ConnectionError:
            logging.info("Max retries exceed")
            content = ""
        return content

    #
    def get_json_from_url(self, url):
        try:
            content = self.get_url(url)
            js = json.loads(content)
        except AttributeError:
            event_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.error("\nFailed to load json content at {}, content was {}\n".format(event_time, self.get_url(url)))
            js = []
        return js

    #
    def get_updates(self, offset=None):
        url = URL + "getUpdates?timeout=1"
        if offset:
            url += "&offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    #
    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    #
    def send_message(self, text, chat_id, reply_markup=None):
        text = parse.quote_plus(text)
        url = URL + "SendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
        if reply_markup:
            url += "&reply_markup={}".format(reply_markup)
        self.get_url(url)

    #
    def get_text_and_chat(self, updates):
        len_updates = len(updates["result"])
        last_update = len_updates - 1
        try:
            text = updates["result"][last_update]["message"]["text"]
        except:
            text = "no valid text"
            logging.error("no valid text")
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return text, chat_id

    #
    def get_name(self, updates):
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
            try:
                name = update["message"]["chat"]["first_name"]
            except:
                # write_log2("no_name", time)
                name = "n/a"
            try:
                surname = update["message"]["chat"]["last_name"]
            except:
                # write_log2("no_surname", time)
                surname = "n/a"
        return name

    #
    def id_check(self, updates):
        for update in updates["result"]:
            chat = update["message"]["chat"]["id"]
            logging.info("chat: {}, allowed: {}".format(chat, self.allowed))
            date = update["message"]["date"]
            time = datetime.fromtimestamp(date)
            time = time.strftime('%Y-%m-%d at %H:%M:%S')
            try:
                name = update["message"]["chat"]["first_name"]
            except:
                name = "n/a"
            try:
                surname = update["message"]["chat"]["last_name"]
            except:
                surname = "n/a"
            try:
                username = update["message"]["chat"]["username"]
            except:
                username = "n/a"

        if chat in self.allowed:
            #logging.info("\nconnection from: {} ... \nconnection successful".format(chat))
            return 1
        else:
            self.send_message("Unknown user, access denied. Contact system admin", chat)
            message = [name, " ", surname, "\nUsername: ", username, "\nID: ", chat, "\nAt: ", str(time),
                       "Concedere i privilegi all'utente?"]
            message = ''.join(map(str, message))
            keyboard = [[chat], ["Home"]]
            self.send_message(message, self.master, keyboard)
            return 0