from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Unicode
from sqlalchemy.orm import sessionmaker, relationship
import logging
import sqlalchemy

Base = declarative_base()

user_show_table = Table('association_us', Base.metadata,
                    Column('left_id', Integer, ForeignKey('Users.id')),
                    Column('right_id', Integer, ForeignKey('Shows_c.id'))
                  )
user_episode_table = Table('association_ue', Base.metadata,
                         Column('left_id', Integer, ForeignKey('Users.id')),
                         Column('right_id', Integer, ForeignKey('Episodes.id'))
                     )
 
    
class UserModel(Base):
    __tablename__ = 'Users'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer)
    first_name = Column(String(100, collation='utf8_bin'))
    last_name = Column(String(100, collation='utf8_bin'))
    username = Column(String(100))
    shows_subscribed = relationship("ShowModel", secondary=user_show_table, backref='subscribers')
    episodes_to_watch = relationship("EpisodeModel", secondary=user_episode_table, backref='subscribers')

    def __repr__(self):
        return 'User (id=%s first_name=%s last_name=%s username=%s)' % (
             self.id, self.first_name, self.last_name, self.username)

class ShowModel(Base):
    __tablename__ = 'Shows_c' #change
    id = Column(Integer, primary_key=True)
    name = Column(String(150))
    poster_url = Column(String(300))
    rating = Column(Integer)
    desc = Column(String(500))
    idbm_id = Column(Integer)
    slug = Column(String(500))
    newest_video = Column(Integer)

    def __repr__(self):
        return 'Show (name=%s)' % (self.name)

class EpisodeModel(Base):
    __tablename__ = 'Episodes'
    id = Column(Integer, primary_key=True)
    show_id = Column(Integer, ForeignKey('Shows_c.id'))
    show = relationship(ShowModel)
    name = Column(String(200))
    desc = Column(String(1000))
    season = Column(Integer)
    number = Column(Integer)

    def __repr__(self):
        return 'Episode %s (show=%s, s=%s e=%s)' % (
                self.name, self.show.name, self.season, self.number )

class Database:
    class __Database:
        def __init__(self):
            logging.info('Initializing database...')
            self.engine = create_engine('mysql+pymysql://root:chrome12@localhost:3306/test2?charset=utf8', convert_unicode=True)
            Base.metadata.bind = self.engine
            Base.metadata.create_all()
            self.sessions = sessionmaker(bind=self.engine)
            self.ses = self.sessions()

        def get_episode(self, id):
            logging.info('Get episode with id {0}'.format(id))
            return self.ses.query(EpisodeModel).filter(EpisodeModel.id == id).first()

        def update_users_episodes(self, show_id, episode):
            show = self.get_show(show_id)
            for user in show.subscribers:
                user.episodes_to_watch.append(episode)
            self.ses.commit()
        
        def delete_episode_from_user_list(self, user_id, episode_id):
            user = self.get_user(user_id)
            episode = self.get_episode(episode_id)
            if user and episode:
                try:
                    user.episodes_to_watch.remove(episode)
                    logging.info('Deleting episode {0} from user {1} list'.format(user, episode))
                except:
                    pass

        def add_episode(self, id, name, desc, show_id, season, number):
            logging.info('Adding new episode for {0} show {1} {2}', self.get_show(show_id), season, number)
            episode = EpisodeModel(id=id, name=name, desc=desc, show_id=show_id, season=season, number=number)
            try:
                self.ses.add(episode)
                self.ses.commit()
                logging.info('Added new episode with id {0}'.format(id))
                self.update_users_episodes(show_id, episode)
            except sqlalchemy.exc.IntegrityError:
                self.ses.rollback()
                logging.warning('tried to add episode with already existing id {0}'.format(id))


        def get_all_users(self):
            logging.info('Get all users query')
            return self.ses.query(UserModel).all()

        def add_user(self, id, chat_id, first_name, last_name, username):
            user = UserModel(id=id, chat_id=chat_id, first_name=first_name, last_name=last_name, username=username)
            try:
                self.ses.add(user)
                self.ses.commit()
                logging.info('Added new user with id {0}'.format(id))
            except sqlalchemy.exc.IntegrityError:
                self.ses.rollback()
                logging.warning('tried to add user with already existing id {0}'.format(user))

        def get_user(self, user_id):
            logging.info('Getting user with id {0}'.format(user_id))
            return self.ses.query(UserModel).filter(UserModel.id == user_id).first()

        def delete_all_users(self):
            logging.warning('Deleting all users')
            for user in self.get_all_users():
                self.ses.delete(user)
            self.ses.commit()
        
        def delete_all_episodes(self):
            logging.warning('Deleting all episodes')
            self.ses.query(EpisodeModel).delete()

        def add_show(self, id, name, poster_url, rating, desc, idbm_id, slug, newest_video):
            show = ShowModel(id=id, name=name, poster_url=poster_url, rating=rating, desc=desc, idbm_id=idbm_id, slug=slug, newest_video=newest_video)
            try:
                self.ses.add(show)
                self.ses.commit()
                logging.info('Added new show {0}'.format(show))
            except sqlalchemy.exc.IntegrityError:
                self.ses.rollback()
                logging.warning('Tried to add show with id that is already taken {0}'.format(show))

        def get_all_shows(self):
            logging.info('Get all shows entry')
            return self.ses.query(ShowModel).all()

        def get_show(self, show_id):
            logging.info('Getting show with id {0}'.format(show_id));
            return self.ses.query(ShowModel).filter(ShowModel.id == show_id).first()
        
        def subscribe_user(self, user_id, show_id):
            user = self.get_user(user_id)
            show = self.get_show(show_id)
            if (user and show):
                logging.info('Subscribing user {0} to show {1}'.format(user, show))
                user.shows_subscribed.append(show)
                self.ses.commit()
                return True
            else:
                logging.warning('Couldn\' find user or show for subscription')
                return False

        def unsubscribe_user(self, user_id, show_id):
            user = self.get_user(user_id)
            show = self.get_show(show_id)
            if user and show:
                logging.info('Unsubscribing user {0} from show {1}'.format(user, show))
                try:
                    user.shows_subscribed.remove(show)
                    self.ses.commit()
                except ValueError:
                    logging.warning('Tried to unsibscribe user {0} from show {1} that user never been subscribed to'.format(user, show))
                return True
            else:
                logging.warning('Couldn\' find user or show for unsubscription')
                return False




    instance = None

    def __init__(self):
        if not Database.instance:
            Database.instance = Database.__Database()

    
    def get_all_users(self):
        return Database.instance.get_all_users()

    def add_user(self, id, chat_id=id, first_name="", last_name="", username=""):
        Database.instance.add_user(id, chat_id, first_name, last_name, username)

    def get_user(self, user_id):
        return Database.instance.get_user(user_id)

    def delete_all_users(self):
        return Database.instance.delete_all_users()
    
    def add_show(self, id, name, poster_url="", rating=0, desc="", idbm_id=0, slug="", newest_video=0):
        Database.instance.add_show(id, name, poster_url, rating, desc, idbm_id, slug, newest_video)

    def get_all_shows(self):
        return Database.instance.get_all_shows()

    def get_show(self, show_id):
        return Database.instance.get_show(show_id)

    def add_episode(self, id, name="", desc="", show=1, season=1, episode=1):
        Database.instance.add_episode(id, name, desc, show, season, episode)

    def get_episode(self, id):
        return Database.instance.get_episode(id)

    def delete_all_episodes(self):
        Database.instance.delete_all_episodes()

    def subscribe_user(self, user_id, show_id):
        return Database.instance.subscribe_user(user_id, show_id)

    def unsubscribe_user(self, user_id, show_id):
        return Database.instance.unsubscribe_user(user_id, show_id)

    def delete_episode_from_user_list(self, user_id, episode_id):
        Database.instance.delete_episode_from_user_list(user_id, episode_id)


for user in Database().get_all_users():
    print (user)
