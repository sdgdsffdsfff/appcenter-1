#encoding=UTF-8
#code by LP
#2014-5-14

import datetime
import pygeoip
from distutils.version import LooseVersion
from conf.settings import settings
from conf.vshare import vshare_settings
from common.ng_mongo import NGMongoConnect
from common.ng_redis import NGRedis
from collections import OrderedDict

mongo = NGMongoConnect(settings['mongodb']['host'])
mongo_db = mongo.get_database('appcenter')

old_mongo = NGMongoConnect('mongodb://10.0.0.250:27017')
old_mongo_db = old_mongo.get_database('appdb')


def import_genre():
    for genre in old_mongo_db.app_genre.find():
        print 'import icon: %s' % genre['icon']
        genre_id = int(genre['genreid']])
        if genre_id == 99999997:
            genre_id = 1000

        mongo_db.app_genre.update({'genreId': genre_id}, {'$set':{'icon': genre['icon']}})

