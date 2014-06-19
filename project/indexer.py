# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-3-22.

import pyes
from conf.settings import settings
from common.ng_mongo import NGMongoConnect
from www.controller.app.search import AppSearch
from www.controller.app.header import artworkUrl512_to_114_icon, file_size_format
import threading, multiprocessing

mongo = NGMongoConnect(settings['mongodb']['host'])
mongo_db = mongo.get_database('appcenter')

def index_apps(app_search, apps):
    for index, app in enumerate(apps):
        support_iphone, support_ipad = 0, 0
        for d in app['supportedDevices']:
            if 'iPhone' in d: support_iphone = 1
            if 'iPad' in d: support_ipad = 1
        rating = app.get('averageUserRating', 0)
        try:
            icon = artworkUrl512_to_114_icon(app['artworkUrl512'])
            app_search.add_index(
                ID = str(app['_id']),
                track_name = app['trackName'],
                support_iphone = support_iphone,
                support_ipad = support_ipad, icon = icon,
                bundle_id = app['bundleId'], rating = rating,
                size = file_size_format(app.get('fileSizeBytes', 0)),
                sign = app.get('sign', 0), download_version = app.get('downloadVersion', "")
            )
        except Exception, ex: print ex

def index_process_worker(app_search, apps):
    print "%s-app的个数%d" % (multiprocessing.current_process().name, len(apps))
    app_len, thread_num = len(apps), 20
    start, end = 0, app_len > thread_num and thread_num or app_len
    while True:
        print "%s - %d-%d" % (multiprocessing.current_process().name, start, end)
        cur_thread = threading.Thread(target=index_apps, args=(app_search, apps[start:end]))
        cur_thread.start()
        cur_thread.join()
        if app_len <= end: break
        start = end
        end += thread_num
        if end > app_len: end = app_len


def index_app():
    app_search = AppSearch()
    try: app_search.delete_index()
    except: pass
    app_search.create_index()
    num_apps_per_process = 50000
    fields = {
        "trackName": 1, "bundleId": 1,
        "supportedDevices": 1, "artworkUrl512": 1,
        "averageUserRating": 1, "sign": 1, "size": 1,
        "fileSizeBytes": 1, "downloadVersion": 1
    }
    apps = []
    for index, app in enumerate(mongo_db.AppBase.find({}, fields)):
        apps.append(app)
        if (index + 1) % num_apps_per_process == 0:
            p = multiprocessing.Process(target=index_process_worker, args=(app_search, apps))
            p.start()
            apps = []
    p = multiprocessing.Process(target=index_process_worker, args=(app_search, apps))
    p.start()
    p.join()
    app_search.refresh()
