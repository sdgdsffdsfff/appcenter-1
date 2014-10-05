#encoding=UTF8
#code by LP
#2013-12-5

import sys
import argparse, multiprocessing
from www.controller.app.app import AppController
from common.ng_daemon import NGDaemon
from conf.settings import settings
from common.ng_mongo import NGMongoConnect

import gevent.monkey
gevent.monkey.patch_socket()
import gevent

mongo = NGMongoConnect(settings['mongodb']['host'], replica_set=settings["mongodb"].get("replica_set", None))
mongo_db = mongo.get_database('appcenter')


def cache_app_list(genre_id):
    app = AppController()
    print "Begin Caching Genre: %s App List" % genre_id
    app.set_apps_cache(genre_id, ('sort', -1)) #推荐
    app.set_apps_cache(genre_id, ('downloadCount', -1)) #最热
    app.set_apps_cache(genre_id, ('_id', -1)) #最新
    print "Finish Caching Genre: %s App List" % genre_id


def asynchronous_cache_genres():
    threads = []
    for index, genre in enumerate(mongo_db.app_genre.find()):
        threads.append(gevent.spawn(cache_app_list, str(genre['genreId'])))
    gevent.joinall(threads)

def synchronous_cache_genres():
    for index, genre in enumerate(mongo_db.app_genre.find()):
        print index
        cache_app_list(str(genre['genreId']))

def cache_app_list_run(genreID=None):
    if genreID == -1:
        synchronous_cache_genres()
    elif genreID != None:
        genre_id = int(genreID)
        cache_app_list(genre_id)
    else: asynchronous_cache_genres()
