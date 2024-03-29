# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-3-22.

import pyes
import pymongo
from conf.settings import settings
from common.ng_mongo import NGMongoConnect
from common.ng_redis import NGRedis
from www.controller.app.search import AppSearch
from www.controller.app.app import AppController
from www.controller.app.header import artworkUrl512_to_114_icon, file_size_format
import threading, multiprocessing

mongo = NGMongoConnect(settings['mongodb']['host'], replica_set=settings["mongodb"].get("replica_set", None))
mongo_db = mongo.get_database('appcenter')


def index_apps(app_search, apps):
    for index, app in enumerate(apps):
        bundle_id = app.get("bundleId", None)
        if not bundle_id: continue
        support_iphone, support_ipad = 0, 0
        for d in app['supportedDevices']:
            if 'iPhone' in d: support_iphone = 1
            if 'iPad' in d: support_ipad = 1
        rating = app.get('averageUserRating', 0)

        try:
            icon = artworkUrl512_to_114_icon(app['artworkUrl512'])
            sign = app.get('sign', 0)
            app_version = appc.get_app_version_cache(app['bundleId'])

            if not app_version:
                ipa_version_jb = 'unknown'
                ipa_version_signed = 'unknown'
            else:
                ipa_version_jb = app_version['ipaVersion']['jb']
                ipa_version_signed = app_version['ipaVersion']['signed']

            app_cn = mongodb.AppBase_CN.find_one({'bundleId': bundle_id}, {"trackName": 1})
            if not app_cn: track_name_cn = app['trackName']
            else: track_name_cn = app_cn.get("trackName", app["trackName"])
            app_search.add_index(
                ID = str(app['_id']),
                track_name = app['trackName'],
                track_name_cn = track_name_cn,
                support_iphone = support_iphone,
                support_ipad = support_ipad, icon = icon,
                bundle_id = app['bundleId'], rating = rating,
                size = file_size_format(app.get('fileSizeBytes', 0)),
                sign = sign, ipa_version_jb = ipa_version_jb,
                ipa_version_signed = ipa_version_signed,
                download_count = app.get("downloadCount", 0)
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
        if app_len <= end: break
        start = end
        end += thread_num
        if end > app_len: end = app_len


def build_search_index_run():
    app_search = AppSearch()
    try: app_search.create_index()
    except: pass
    num_apps_per_process = 50000
    fields = {
        "trackName": 1, "bundleId": 1,
        "supportedDevices": 1, "artworkUrl512": 1,
        "averageUserRating": 1, "sign": 1,
        "fileSizeBytes": 1, "downloadVersion": 1,
        "downloadCount": 1
    }
    apps = []
    processes = []
    for index, app in enumerate(mongo_db.AppBase.find({'review': 1}, fields)):
        apps.append(app)
        if (index + 1) % num_apps_per_process == 0:
            p = multiprocessing.Process(target=index_process_worker, args=(app_search, apps))
            p.start()
            processes.append(p)
            apps = []
    p = multiprocessing.Process(target=index_process_worker, args=(app_search, apps))
    p.start()
    processes.append(p)
    for process in processes: process.join()
    app_search.refresh()
