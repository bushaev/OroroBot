import logging
from DatabaseConnector import Database
class AdminPage:
    def __init__(self, bot):
        self.admins = [82755431, 89917125, 157322980]
        self.bot = bot
        self.db = Database()

    def add_admin(self, id):
        self.admins.append(id)

    def notify_one(self, msg, reply_markup=None):
        self.bot.sendMessage(self.admins[0], msg, reply_markup=reply_markup)

    def notify_all(self, msg, reply_markup=None):
        for admin_id in self.admins:
            self.bot.sendMessage(admin_id, msg, reply_markup=reply_markup)

    def is_admin(self, id):
        return id in self.admins

    def get_admin(self):
        return self.db.get_user(self.admins[0])

    def get_admin_id(self):
        return self.admins[0]

    def handle_api_error(self, error_code, flag=False):
        if flag:
            msg = "Connection refused 3 times in a row with code {0}".format(error_code)
            logging.critical(msg)
            self.notify_all(msg)
            return

        if  401 <= error_code <= 404:
            msg = "Connection to API refused with error {0}".format(error_code)
            self.notify_all(msg)
            logging.critical(msg)
        else:
            logging.error("Connection to API refused with error {0}".format(error_code))

    def notify_all_users(msg):
        logging.debug('Send message to all users {0}'.format(msg))
        for user in self.db.get_all_users():
            self.bot.sendMessage(user.chat_id, str(msg))
