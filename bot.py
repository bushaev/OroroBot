import telepot as tp
import sys, time, json
from getopt import getopt
from DatabaseConnector import Database
from AdminPage import AdminPage
from MessageHandler import MessageHandler
from APIConnector import APIRequestSender
from Helper import Messages
import logging

login = None
password = None
token = None
force_update = False

def usage():
    print ('python bot.py -t <token> -c <ororo_credentials> [-f] [-h] [-v]')
    print ('    -t <token> bot token aquired through BotFather')
    print ('    -c <credentials> login:password from ororo.tv')
    print ('    -f/--force_update forces update on one the admin\'s shows')
    print ('    -v use debug level logging')

def get_latest_episode(episodes):
    curent_latest = None
    for episode in episodes:
        if curent_latest is None:
            curent_latest = episode
        elif curent_latest['season'] < episode['season']:
            curent_latest = episode
        elif curent_latest['season'] == episode['season'] and curent_latest['number'] < episode['number']:
            curent_latest = episode

    return curent_latest


def update_tv_shows(api, db, bot):
    logging.info('Updating TV Show')
    shows_json = api.show_list_json()
    if not shows_json:
        return
    for show in shows_json['shows']:
        id = show['id']
        show_db = db.get_show(id)
        if not show_db:
            logging.info('Found new TV show that wasn\'t in the list before %s',
                            show['name'])
            db.add_show(id, show['name'], show['poster'],
                        show['imdb_rating'], show['desc'],
                        show['imdb_id'], show['slug'],
                        show['newest_video'])
            continue
        if show_db.newest_video != show['newest_video']:
            db.update_show_newest_video(id, show['newest_video'])
            s = api.show_json(id)
            episode = get_latest_episode(s['episodes'])
            db.add_episode(
                episode['id'],
                episode['name'],
                episode['plot'],
                id,
                episode['season'],
                episode['number']
            )
            for user in show_db.subscribers:
                bot.sendMessage(user.id, Messages.new_episode(
                    show_db.name + "\n" + episode['name'] +
                        '\nSeason: ' + str(episode['season']) +
                        '\nEpisode' + str(episode['number'])
                    ,user.language
                ))



if __name__ == '__main__':
    log_level = logging.WARNING
    optlist, args = getopt(sys.argv[1:], 'hfc:t:v', ['force_update'])
    for arg, value in optlist:
        if arg == '-c':
            login, password = value.split(':')
        elif arg == '-t':
            token = value
        elif arg == '-h':
            usage()
            exit(0)
        elif arg == '-v':
            log_level = logging.INFO
        elif arg in ['-f', 'force_update']:
            force_update = True

    logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=log_level)

    if token is None:
        logging.critical('No token were provided. Abort')
        exit(0)
    else:
        bot = tp.Bot(token)

    if login is None or password is None:
        logging.critical('No credentials for ororo. Abort')
        exit

    db = Database()
    admin = AdminPage(bot)
    handle = MessageHandler(bot, admin)
    api = APIRequestSender((login, password), admin.handle_api_error)

    try:
        bot.message_loop({'chat': handle.on_chat_message
                         ,'callback_query' : handle.on_callback_query})
        if force_update:
            show = admin.get_admin().shows_subscribed[0]
            db.update_show_newest_video(show.id, 0)
        update_tv_shows(api, db, bot)
        while 1:
            time.sleep(1000)
    except:
        admin.notify_one("Critical. bot is down. Please check logs or contact Vitaly Bushaev @bushaev")
        raise
