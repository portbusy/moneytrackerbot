import requests
import json
import logging
from datetime import datetime
from urllib import parse
from sys import exit

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) -35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

f = open("token.txt", "r")
TOKEN = f.readline()
if not TOKEN:
    LOGGER.error("Error occurred, have you filled the token.txt file with your bot token?")
    exit()

URL = "https://api.telegram.org/bot{}/".format(TOKEN)

f = open("master.txt", "r")
master = int(f.readline())
if not master:
    LOGGER.error("Error occurred, have you filled the master.txt file with your master id?")
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
            LOGGER.info("Response message: {}".format(content))
        except requests.exceptions.ConnectionError:
            content = str({
                "ok": True,
                "result": []
            })
            LOGGER.info("Max retries exceed, passing composed content: {}".format(content))
        return content

    #
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

    #
    def get_updates(self, offset=None):
        url = URL + "getUpdates?timeout=240"
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
            LOGGER.error("No valid text provided!")
            text = "No valid text provided"
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
            LOGGER.debug("chat: {}, allowed: {}".format(chat, self.allowed))
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
            LOGGER.info("Connection from: {}".format(chat))
            return 1
        else:
            self.send_message("Unknown user, access denied. Contact system admin", chat)
            message = [name, " ", surname, "\nUsername: ", username, "\nID: ", chat, "\nAt: ", str(time),
                       "Concedere i privilegi all'utente?"]
            message = ''.join(map(str, message))
            keyboard = [[chat], ["Home"]]
            self.send_message(message, self.master, keyboard)
            return 0