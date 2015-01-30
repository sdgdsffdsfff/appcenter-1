from pymongo import MongoClient
from datetime import datetime

TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
to_client = MongoClient(TO_MONGO_SEVRER_URL)
to_db = to_client["appcenter"]


def get_apps_info(genre_id, track_ids):
    app_list_redis_key = "APPLIST_%s_SIGN_%s_LANG_%s_GENRE_%s_LIMIT_%s_SORT_%s_DESC"
    where = {"trackId": {"$in": track_ids}}
    lang = "ar"
    apps = mongo_db.AppBase.find(where, {
        "trackId":1, "trackName": 1, "bundleId": 1, "artworkUrl512": 1,
        "averageUserRating": 1, "screenshotUrls": 1, "ipadScreenshotUrls": 1,
        "fileSizeBytes": 1, "version": 1, 'cnname': 1, 'arname':1
    })
    keys['iphone_jb_key'] = app_list_redis_key % ('iphone', 0, lang, genre_id, 600, 'sort')
    keys['iphone_signed_key'] = app_list_redis_key % ('iphone', 1, lang,genre_id, 600, 'sort')
    keys['ipad_jb_key'] = app_list_redis_key % ('ipad', 0, lang, genre_id, 600, 'sort')
    keys['ipad_signed_key'] = app_list_redis_key % ('ipad', 1, lang, genre_id, 600, 'sort')
    sign = {'signed': 1, 'jb': 0}
    for s in sign.keys():
        print 'Push to redis, lang:%s, genre: %s, sign: %s' % (lang, genre_id, s)
        #查询签名的
        if sign[s] == 1: where['sign'] = 1
        apps = self.get_apps(where, lang, sort, self.limit)
        for app in apps:
            data = cjson.encode(app)
            if app['supportIpad'] == 1 or app['supportIphone'] == 1:
                redis_master_pipeline.lpush(keys['ipad_'+ s +'_key'], data)
            if app['supportIphone'] == 1:
                redis_master_pipeline.lpush(keys['iphone_'+ s +'_key'], data)
