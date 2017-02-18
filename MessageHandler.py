from telepot.namedtuple import ReplyKeyboardRemove
from DatabaseConnector import Database
from AdminPage import AdminPage
from Helper import Keyboards, Messages
import telepot as tp
import logging


class MessageHandler:

    def __init__(self, bot, admin):
        self.bot = bot
        self.admin = admin
        self.db = Database()
        self.user_step = {}

    def on_callback_query(self, msg):
        query_id, from_id, query_data = tp.glance(msg, flavor='callback_query')
        logging.info('Callback Query: %s %s %s', query_id, from_id, query_data)

        data = query_data.split()
        type = int(data[0])

        user = self.db.get_user(from_id)
        if not user:
            self.bot.sendMessage(from_id, 'Please start with /start')
            return

        if type is 1:
            self.db.delete_episode_from_user_list(from_id, data[1])
            self.bot.answerCallbackQuery(
                query_id, Messages.mark_watched[
                    user.language])
        elif type is 2:
            show = self.db.get_show(data[1])
            self.db.subscribe_user(from_id, data[1])
            self.bot.sendMessage(
                from_id, Messages.subscribe_success(
                    show.name, user.language), reply_markup=Keyboards.main(
                    user.id, self.admin.is_admin(
                        user.id)))
            self.bot.answerCallbackQuery(
                query_id, Messages.success[
                    user.language])
            self.user_step[from_id] = 0
        elif type is 3:
            show = self.db.get_show(data[1])
            self.db.unsubscribe_user(from_id, data[1])
            self.bot.sendMessage(
                from_id, Messages.unsubscribe_success(
                    show.name, user.language), reply_markup=Keyboards.main(
                    user.id, self.admin.is_admin(
                        user.id)))
            self.bot.answerCallbackQuery(
                query_id, Messages.success[
                    user.language])
            self.user_step[from_id] = 0
        elif type is 4:
            user = self.db.get_user(data[1])
            for index, show in enumerate(user.shows_subscribed):
                self.bot.sendMessage(
                    from_id, '{0}. {1}'.format(
                        index + 1, show.name))
            self.bot.answerCallbackQuery(query_id, Messages.success[1])
        else:
            pass

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = tp.glance(msg)
        logging.info('Got a message for chat: %s %s %s',
                     content_type, chat_type, chat_id)
        user = msg['from']
        id = user['id']
        logging.info('%s', user)
        us = self.db.get_user(id)

        if not us:
            name = user['first_name']
            last_name = ''
            username = ''
            if 'last_name' in user:
                last_name = user['last_name']
            if 'username' in user:
                username = user['username']
            self.db.add_user(id, chat_id, name, last_name, username)
            self.admin.notify_all('New user id : {0}\n name={1}\n '
                                  'last_name = {2}\n username=@{3}'.format(
                                      id, name, last_name, username
                                  ))
            self.user_step[id] = 0
            us = self.db.get_user(id)
        else:
            lan = us.language

        try:
            command = msg['text']
            logging.info('%s', command)
            if command == '/start':
                self.bot.sendMessage(chat_id, 'Choose language',
                                     reply_markup=Keyboards.languages)
                self.user_step[id] = 0
            elif command in Messages.choose_language:
                l = command[0]
                lan = int(l) - 1
                self.db.set_user_language(id, lan)
                self.bot.sendMessage(
                    id,
                    Messages.language_chosen[lan],
                    reply_markup=Keyboards.main(
                        id,
                        self.admin.is_admin(id)))
                self.user_step[id] = 1
            elif lan is None:
                self.bot.sendMessage(
                    id,
                    'Choose language',
                    reply_markup=Keyboards.languages)
            elif command in Messages.subscribe:
                self.bot.sendMessage(id, Messages.enter_tv_show[lan],
                                     reply_markup=Keyboards.cancel(lan))
                self.user_step[id] = 2
            elif command in Messages.unsubscribe:
                self.bot.sendMessage(id, Messages.enter_tv_show[lan],
                                     reply_markup=Keyboards.cancel(lan))
                self.user_step[id] = 3
            elif command in Messages.show_non_watched:
                if len(us.episodes_to_watch) is 0:
                    self.bot.sendMessage(id, Messages.no_new_episodes[lan])
                for episode in us.episodes_to_watch:
                    self.bot.sendMessage(
                        id,
                        '{3}\nseason {1} - episode{2}\n{0}'.format(
                            episode.name,
                            episode.season,
                            episode.number,
                            episode.show.name),
                        reply_markup=Keyboards.episode(
                            episode.id,
                            lan))
            elif command in Messages.my_shows:
                if len(us.shows_subscribed) == 0:
                    self.bot.sendMessage(id, Messages.not_subscribed[lan])
                for i, show in enumerate(us.shows_subscribed):
                    self.bot.sendMessage(id, str(i + 1) + '. ' + show.name)
            elif command in Messages.cancel:
                step = self.user_step.get(id, 0)
                if step in [4, 5]:
                    self.user_step[id] = 0
                    self.bot.sendMessage(id, Messages.choose_action[lan],
                                         reply_markup=Keyboards.admin)
                    return
                self.bot.sendMessage(
                    id, Messages.choose_action[lan], reply_markup=Keyboards.main(
                        id, self.admin.is_admin(id)))
            else:
                is_admin = self.admin.is_admin(id)
                step = self.user_step.get(id, 0)
                if is_admin:
                    if self.admin.handle_admin_request(command, id,
                                                       self.user_step):
                        return


                if step in [2, 3]:
                        self.bot.sendMessage(id, Messages.possible_shows[lan],
                                             reply_markup=Keyboards.similar_shows(
                                             command, lan, self.user_step[id]))
                        self.user_step[id] = 0
                else:
                    self.bot.sendMessage(id, Messages.dont_understand[lan],
                                             reply_markup=Keyboards.main(id,
                                             is_admin))
                    self.user_step[id] = 0


        except Exception as e:
            if lan is None:
                lan = 0
            self.bot.sendMessage(id, Messages.exception[lan])
            self.admin.notify_one(str(e))
            raise
