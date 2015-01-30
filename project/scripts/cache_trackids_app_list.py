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


def cache_apps(genre_id, track_ids):
    app = AppController()
    print "Begin Caching Genre: %s App List" % genre_id
    app.set_trackids_apps_cache(genre_id, track_ids)
    print "Finish Caching Genre: %s App List" % genre_id
