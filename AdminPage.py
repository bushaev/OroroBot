import logging
from DatabaseConnector import Database
class AdminPage:
    def __init__(self, bot):
        self.admins = [82755431]
        self.bot = bot

    def add_admin(self, id):
        self.admins.append(id)

    def notify_one(self, msg):
        self.bot.sendMessage(admin_list[0], msg)

    def notify_all(self, msg):
        for admin_id in self.admins:
            self.bot.sendMessage(admin_id, msg)

    def is_admin(self, id):
        return id in self.admins

    def get_admin(self):
        db = Database()
        return db.get_user(self.admins[0])

    def handle_api_error(self, error_code, flag=False):
        if flag:
            msg = "Connection refused 3 times in a row with code {0}".format(error_code)
            logging.critical(msg)
            self.notify_all(msg)
            return

        if  401 <= error_code <= 404:
            self.notify_all("connection to api refused with error {0}".format(error_code))
            logging.critical("Connection to API refused with error {0}".format(error_code))
        logging.error("Connection to API refused with error {0}".format(error_code))
