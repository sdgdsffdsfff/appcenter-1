#encoding=UTF8
#code by LP
#2013-12-5

import sys
import argparse
from www.controller.app.app import AppController
from common.ng_daemon import NGDaemon
from conf.settings import settings
from common.ng_mongo import NGMongoConnect


mongo = NGMongoConnect(settings['mongodb']['host'])
mongo_db = mongo.get_database('appcenter')


def cache_app_list(genre_id):
    try:
        print "Start cache genre: %s app list" % genre_id

        #更新推荐缓存前100页
        app = AppController()
        print 'Cache sort by sort'
        app.set_apps_cache(genre_id, ('sort', -1)) #推荐
        print 'Cache sort by downloadCount'
        app.set_apps_cache(genre_id, ('downloadCount', -1)) #最热
        print 'Cache sort by _id'
        app.set_apps_cache(genre_id, ('_id', -1)) #最新

        print "Cache %s OK" % genre_id
    except Exception, ex:
        import traceback
        traceback.print_exc()
        print "Cache %s ERROR: %s" % (genre_id, ex)


def cache_app_list_run(genreID=0):
    if genreID != 0:
        genre_id = int(genreID)
        cache_app_list(genre_id)
    else:
        for genre in mongo_db.app_genre.find():
            cache_genre_list(genre['genreId'])
