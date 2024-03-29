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
    app = AppController()
    print "Begin Caching Genre: %s App List" % genre_id
    #app.set_apps_cache(genre_id, ('sort', -1))
    #app.set_apps_cache(genre_id, ('downloadCount', -1))
    #app.set_apps_cache(genre_id, ('_id', -1))
    app.set_apps_cache_new(genre_id, ('sort', -1))
    app.set_apps_cache_new(genre_id, ('hot', -1))
    app.set_apps_cache_new(genre_id, ('new', -1))
    print "Finish Caching Genre: %s App List" % genre_id

def asynchronous_cache_genres():
    processes = []
    for index, genre in enumerate(mongo_db.app_genre.find()):
        cur_process = multiprocessing.Process(target=cache_app_list, args=(genre, ))
        cur_process.start()
        processes.append(cur_process)
    for pro in processes: pro.join()

def synchronous_cache_genres():
    pass

def cache_app_list_run(genreID=None):
    if genreID == "-1":
        synchronous_cache_genres()
    elif genreID != None:
        genre_id = int(genreID)
        cache_app_list(genre_id)
    else: asynchronous_cache_genres()
