#encoding=UTF8
#code by LP
#2013-12-5

import sys
import argparse, multiprocessing
from www.controller.app.app import AppController
from common.ng_daemon import NGDaemon
from conf.settings import settings
from common.ng_mongo import NGMongoConnect


mongo = NGMongoConnect(settings['mongodb']['host'], replica_set=settings["mongodb"].get("replica_set", None))
mongo_db = mongo.get_database('appcenter')


def cache_app_list(genre_id):
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


def cache_app_list_run(genreID=None):
    if genreID != None:
        genre_id = int(genreID)
        cache_app_list(genre_id)
    else:
        pool = multiprocessing.Pool(processes=16)
        for index, genre in enumerate(mongo_db.app_genre.find()):
            print "Cache genre %s" % str(genre['genreId'])
            pool.apply_async(cache_app_list, (genre['genreId'], ))
        pool.close()
        pool.join()
