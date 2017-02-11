import telepot as tp
import sys, time, json
from getopt import getopt
from DatabaseConnector import Database
from AdminPage import AdminPage
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
            log_level = logging.DEBUG
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
