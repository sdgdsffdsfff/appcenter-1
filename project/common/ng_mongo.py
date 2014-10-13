#encoding=UTF8
#code by LP
#2013-8-17

import random
import types

from pymongo import Connection, MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
from pymongo.errors import AutoReconnect

class NGMongoConnect(object): 
    '''
    mongodb连接
    '''
    conn = None

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.connect()

    def connect(self):
        replica_set = self.kwargs.get("replica_set", None)
        if replica_set:
            self.conn = MongoClient(replica_set["connection_str"], replicaSet=replica_set['replica_set_name'])
        else:
            self.conn = MongoClient(self.args[0])

    def disconnect(self):
        return self.conn.disconnect()

    def __getattr__(self, db_name):
        return self.get_database(db_name)

    def get_database(self, db_name):
        '''
        选择数据库
        '''
        return NGMongoDatabase(self.conn, db_name)

class NGMongosConnect(NGMongoConnect):
    '''
    多个mongo随机连接
    '''
    def __init__(self, confs):
        conf = random.choice(confs)
        if type(conf) is types.StringType:
            super(NGMongosConnect, self).__init__(conf)
        elif type(conf) is types.ListType:
            super(NGMongosConnect, self).__init__(*conf)
        elif type(conf) is types.DictType:
            super(NGMongosConnect, self).__init__(**conf)

def connect_retry(func, retries=3):
    '''
    断线重连,需要加断线重连，只需要加装饰器@connect_retry即可
    '''
    def wapper(self, *args, **kwargs):
        tries = 0
        while tries < retries:
            #print 'retry %s times' % tries
            try:
                return func(self, *args, **kwargs)
            except AutoReconnect, ex:
                #print 'retry %s times' % tries
                tries += 1
                try:
                    self.connection.connect()
                except:
                    pass
        raise AutoReconnect('Can not connect to the mongo server')   
    return wapper

class NGMongoDatabase(Database):
    '''
    database对象
    '''

    connection = None

    def __init__(self, connection, db_name):
        self.connection = connection
        super(NGMongoDatabase, self).__init__(connection, db_name)

    def __getattr__(self, collection_name):
        return self.get_collection(collection_name)

    def get_collection(self, collection_name):
        return NGMongoCollection(self.connection, self, collection_name)

class NGMongoCollection(Collection):
    '''
    collection对象
    '''

    connection = None

    def __init__(self, connection, db, collection_name):
        self.connection = connection
        self.parentObject = super(NGMongoCollection, self)
        self.parentObject.__init__(db, collection_name)

    @connect_retry
    def insert(self, *args, **kwargs):
        return self.parentObject.insert(*args, **kwargs)

    @connect_retry
    def update(self, *args, **kwargs):
        return self.parentObject.update(*args, **kwargs)

    @connect_retry
    def remove(self, *args, **kwargs):
        return self.parentObject.remove(*args, **kwargs)

    @connect_retry
    def find(self, *args, **kwargs):
        return self.parentObject.find(*args, **kwargs)

    @connect_retry
    def find_one(self, *args, **kwargs):
        return self.parentObject.find_one(*args, **kwargs)
