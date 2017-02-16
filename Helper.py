from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from DatabaseConnector import Database
import logging


class Messages:
    exception = [
        "Something happend, while processing your request. Developers are notified of the problem, we'll try to fix it as soon as possible",
        u'Что-то произошло во время обработки вашего запроса. Разработчки уведомлены о проблеме, мы попытаемся починить это как можно быстрее.']
    not_subscribed = [
        "Unfortunetaly, you've not yet subscribed to any tv shows to follow.",
        u'К сожалению, Вы еще не подписались ни на один сериал.'
    ]
    my_shows = [
        'My TV Shows',
        u'Мои Сериалы',
    ]
    mark_watched = [
        'Episode marked as watched',
        u'Эпизод помечен как просмотренный',
    ]
    success = [
        'Success',
        u'Успешно',
    ]
    watched = [
        'Watched',
        u'Просмотрено',
    ]
    subscribe = [
        'Subscribe',
        u'Подписаться',
    ]
    unsubscribe = [
        'Unsubscribe',
        u'Отписаться',
    ]
    latest = [
        'Show latest episodes',
        u'Показать последние эпизоды',
    ]
    not_watched = [
        'Show not yet watched episodes',
        u'Показать непросмотренные эпизоды',
    ]
    language_chosen = [
        'Great! Now you can subscribe to TV shows and get notifications as soon as new episode comes out!',
        u'Отлично! Теперь Вы можете подписываться на сериалы и получать уведомления как только новые эпизоды выйдут!',
    ]
    choose_language = [
        '1. English',
        u'2. Русский',
    ]
    enter_tv_show = [
        "All right! Enter the name of the TV show that you want to subscribe to",
        u'Введите название сериала, на которыйы Вы хотите подписаться',
    ]
    possible_shows = [
        'What show did you mean ?',
        u'Какой сериал Вы имели в виду ?',
    ]
    show_not_found = [
        "I'm sorry, but it looks like we couldn't find tv show that you want",
        u'Извините, похоже, мы не можем найти сериал, который вы хотите',
    ]
    show_non_watched = [
        'Show new episodes',
        u'Показать новые эпизоды',
    ]
    cancel = [
        'Cancel',
        u'Отменить'
    ]
    no_new_episodes = [
        'Unfortunetaly, you don\'t have any new episodes',
        u'К сожалению, нету новых серий :(',
    ]

    dont_understand = [
        'I don\'t understand what you mean, please start over',
        u'Я Вас не понимаю, пожалуйста, начните сначала'
    ]

    choose_action = [
        'Choose what you want to do',
        u'Выберите действие'
    ]

    @staticmethod
    def subscribe_success(show, language):
        message = [
            "You've subscribed successfuly to ",
            u'Вы успешно подписались на '
        ]
        return message[language] + show

    @staticmethod
    def unsubscribe_success(show, language):
        message = [
            "You've unsubscribed successfuly from ",
            u'Вы успешно отписались от '
        ]
        return message[language] + show

    @staticmethod
    def new_episode(name, language):
        message = [
            'Congradulations! The new episode came out\n',
            u'Ура! Вышел новый эпизод сериала\n',
        ]
        return message[language] + name


def distance(a, b):
    "Calculates the Levenshtein distance between a and b."
    n, m = len(a), len(b)
    if n > m:
        # Make sure n <= m, to use O(min(n,m)) space
        a, b = b, a
        n, m = m, n

    # Keep current and previous row, not entire matrix
    current_row = range(n + 1)
    for i in range(1, m + 1):
        previous_row, current_row = current_row, [i] + [0] * n
        for j in range(1, n + 1):
            add, delete, change = previous_row[
                j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
            if a[j - 1] != b[i - 1]:
                change += 1
            current_row[j] = min(add, delete, change)

    return current_row[n]


class Keyboards:

    languages = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=Messages.choose_language[0])],
        [KeyboardButton(text=Messages.choose_language[1])],
    ], resize_keyboard=True)

    admin = ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text='Send to all')],
        [KeyboardButton(text='See user list')],
        [KeyboardButton(text='Main keyboard')],
    ])

    @staticmethod
    def main(user_id, is_admin):
        logging.debug('Getting main keyboard for user id %s', str(user_id))
        user = Database().get_user(user_id)
        language = user.language
        buttons = [
            [KeyboardButton(text=Messages.subscribe[language]),
             KeyboardButton(text=Messages.unsubscribe[language])],
            [KeyboardButton(text=Messages.my_shows[language])],
            [KeyboardButton(text=Messages.show_non_watched[language])],
        ]
        if is_admin:
            buttons.append(
                [KeyboardButton(text="Admin Page")]
            )
        return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

    @staticmethod
    def user_subscribtions(user_id):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Subscribtions',
                                    callback_data='{0} {1}'.format(4, user_id))]
        ])

    @staticmethod
    def episode(episode_id, lan):
        logging.debug('Getting episode keyboard for episode id %s', episode_id)
        first_raw = [InlineKeyboardButton(text=Messages.watched[lan],
                                          callback_data='{0} {1}'.format(
            1, episode_id))]
        return InlineKeyboardMarkup(inline_keyboard=[first_raw])

    @staticmethod
    def cancel(lan):
        return ReplyKeyboardMarkup(keyboard=[
            [KeyboardButton(text=Messages.cancel[lan])]
        ], resize_keyboard=True)

    @staticmethod
    def similar_shows(msg, lan, type):
        possible_shows = []
        for show in Database().get_all_shows():
            if distance(
                    msg.lower(),
                    show.name.lower()) < len(
                    show.name) / 2 - 1:
                possible_shows.append(show)

        if (len(possible_shows) == 0):
            return

        inline_keyboard = []
        for show in possible_shows:
            logging.debug('Found similar show %s', show.name)
            inline_keyboard.append([InlineKeyboardButton(
                text=show.name, callback_data='{0} {1}'.format(type, show.id))])
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
