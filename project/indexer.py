# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-3-22.

import pyes
from conf.settings import settings
from common.ng_mongo import NGMongoConnect
from www.controller.app.search import AppSearch
from www.controller.app.header import artworkUrl512_to_114_icon

mongo = NGMongoConnect(settings['mongodb']['host'])
mongo_db = mongo.get_database('appcenter')

def index_app():
    s = AppSearch()
    try: s.delete_index()
    except: pass
    s.create_index()
    i = 0
    for app in mongo_db.AppBase.find(timeout=False):
        i += 1
        try:

        #if 'ipadScreenshotUrls' in app and len(app['ipadScreenshotUrls']) > 0:
        #    device = 'ipad'
        #if 'screenshotUrls' in app and len(app['screenshotUrls']) > 0:
        #    device = 'iphone'
        #if ('screenshotUrls' in app and len(app['screenshotUrls']) > 0) and ('ipadScreenshotUrls' in app and len(app['ipadScreenshotUrls']) > 0):
        #    device = 'all'

            support_iphone = 0
            support_ipad = 0

            for d in app['supportedDevices']:
                if 'iPhone' in d:
                    support_iphone = 1
                if 'iPad' in d:
                    support_ipad = 1

            icon = artworkUrl512_to_114_icon(app['artworkUrl512'])

            try:
                rating = app['averageUserRating']
            except:
                rating = 0
            s.add_index(track_name=app['trackName'], support_iphone=support_iphone, support_ipad=support_ipad, icon=icon,
                        bundle_id=app['bundleId'], rating=rating)
            print i
        except Exception, ex:
            print ex

    s.refresh()
