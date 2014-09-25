from pymongo import MongoClient
from datetime import datetime

FROM_MONGO_SEVRER_URL = "mongodb://appdb:cdj6u58CtSa@54.72.191.195:27017/appdb?slaveok=true"
TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
from_client = MongoClient(FROM_MONGO_SEVRER_URL)
to_client = MongoClient(TO_MONGO_SEVRER_URL)
from_db = from_client["appdb"]
to_db = to_client["appcenter"]

def transfer_app_download():
    now = datetime.now()
    where = {"addtime": {"$lt": now}, "soft_delete": {"$ne": 1}}
    app_downloads = from_db.app_download.find(where)
    app_downloads_list = []
    for app_download in app_downloads:
        try:
            app_downloads_list.append({
                "bundleId": app_download["bundleid"],
                "version" : app_download["bundleversion"],
                "minOsVersion": app_download.get("min_os_version", ""),
                "addTime": app_download.get("addTime", datetime.now()),
                "hash": app_download["hash"],
                "appid": app_download["appid"],
                "sign" : abs(app_download["jb"]-1)
            })
        except: continue
    print len(app_downloads_list)
    for app_download in app_downloads_list:
        app_id = app_download.get("appid", None)
        hash_v = app_download.get("hash", None)
        if not app_id or not hash_v: continue
        print hash_v
        to_db.AppDownload.update({"hash": hash_v}, {"$set": app_download}, True)


def update_appbase():
    app_list = from_db.app.find({}, {"bundleid": 1, "sign": 1, "icon": 1, "review": 1, "appid":1, "_id": 0})
    app_list = list(app_list)
    for app in app_list:
        bundle_id = app.get("bundleid", None)
        if not bundle_id: continue
        print bundle_id
        temp_info = {}
        temp_info["sign"] = app.get("sign", 0)
        temp_info["icon"] = app.get("icon", "")
        temp_info["review"] = app.get("review", 0)
        temp_info["appid"] = app.get("appid", 0)
        to_db.AppBase.update({"bundleId": bundle_id}, {"$set": temp_info})
        to_db.AppBase_CN.update({"bundleId": bundle_id}, {"$set": temp_info})

if __name__ == "__main__":
    update_appbase()
