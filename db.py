import pymongo
import json
from bson import json_util


class AuthError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class MongoBase(object):

    ''' Create cursor for database.
    '''

    def __init__(self, host='127.0.0.1', port=27017,
                 database=None, collection=None, login=None,
                 password=None):
        ''' Make object with information for connect to database.
        '''
        self.host = host
        self.port = port
        self.database = database
        self.collection = collection
        self.login = login
        self.password = password
        self.conn = None
        self.auth = False

    def make_connection(self, database=None):
        ''' Make connection to database.
        '''
        if database is None:
            self.conn = pymongo.Connection(self.host, self.port)[self.database]
            return self
        else:
            self.conn = pymongo.Cosnnection(self.host, self.port)[database]
            return self

    def get_collection(self, collection=None):
        ''' Make connection to collection.
        '''
        if collection is None:
            self.authenticate(self.login, self.password)
            return self.conn[self.collection]
        else:
            self.authenticate(self.login, self.password)
            return self.conn[collection]

    def authenticate(self, login=None, password=None):
        ''' Authentication in database
        '''
        if self.conn.authenticate(self.login, self.password) == True:
            self.auth is True
            return self.conn
        else:
            raise AuthError('AuthError: Login or password are wrong.')


def convert_to_json(string=object):
    if type(string) == pymongo.cursor.Cursor:
        s = []
        for x in range(string.count()):
            s.append(string.__next__())
        return "posts:" + json.dumps(s, default=json_util.default)
    else:
        return json.dumps(string, default=json_util.default)
