import logging
from DatabaseConnector import Database
from Helper import Keyboards


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
            msg = "Connection refused 3 times in a row with code {0}".format(
                error_code)
            logging.critical(msg)
            self.notify_all(msg)
            return

        if 401 <= error_code <= 404:
            msg = "Connection to API refused with error {0}".format(error_code)
            self.notify_all(msg)
            logging.critical(msg)
        else:
            logging.error(
                "Connection to API refused with error {0}".format(error_code))

    def notify_all_users(self, msg):
        logging.debug('Send message to all users {0}'.format(msg))
        for user in self.db.get_all_users():
            self.bot.sendMessage(user.chat_id, str(msg))

    def handle_admin_request(self, msg, id, steps):
        step = steps.get(id, 0)
        if msg == 'Admin Page':
            self.bot.sendMessage(id, 'Welcome to Admin Page',
                                 reply_markup=Keyboards.admin)
        elif msg == 'See user list':
            for user in self.db.get_all_users():
                self.bot.sendMessage(id, '{0}\nname = {1} username = @{2}'.format(
                    user.id, user.first_name, user.username
                ), reply_markup=Keyboards.user_subscribtions(user.id))
        elif msg == 'Send to all':
            steps[id] = 4
            try:
                self.bot.sendMessage(id, 'Enter your message',
                                    reply_markup=Keyboards.cancel(0))
            except Exception as e:
                logging.error("couldnt send message %s", e)
        elif msg == 'Send to user':
            steps[id] = 5
            self.bot.sendMessage(id,
                                 'Please enter user_id and your message',
                                 reply_markup=Keyboards.cancel(0))
        elif step in [4, 5]:
            if step == 4:
                for user in self.db.get_all_users():
                    logging.info('Trying to send a message to user %s', id)
                    try:
                        self.bot.sendMessage(user.id, msg)
                    except Exception as e:
                        logging.error('Looks like bot has been blocked %s', e)
            elif step == 5:
                uid, *_ = msg.split()
                message = msg[len(uid) + 1:]
                self.bot.sendMessage(uid, message)

            steps[id] = 0
            self.bot.sendMessage(id, 'Success', reply_markup=Keyboards.admin)
        else:
            return False

        return True
