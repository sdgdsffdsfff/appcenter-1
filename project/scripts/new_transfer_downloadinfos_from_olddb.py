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
    temp_docs = []
    where = {"addtime": {"$lt": now}, "soft_delete": {"$ne": 1}}
    for app_download in from_db.app_download.find(where):
        app_id = app_download.get("appid", None)
        print app_id
        if not app_id: continue
        app = from_db.app.find_one({"appid": app_id})
        if not app: continue
        temp_docs.append({
            "bundleId": app_download["bundleid"], "version" : app_download["bundleversion"],
            "minOsVersion": app_download.get("min_os_version", ""),
            "addTime": app_download.get("addTime", datetime.now()),
            "hash": app_download["hash"], "appid": app_download["appid"], "sign" : abs(app_download["jb"]-1)
        })
        if len(temp_docs) % 1 == 0:
            to_db.AppDownload.insert(temp_docs)
            temp_docs = []
    to_db.AppDownload.insert(temp_docs)

def update_appbase():
    app_list = from_db.app.find({"review": 1}, {"bundleid": 1, "sign": 1, "icon": 1, "review": 1, "appid":1, "_id": 0})
    app_list = list(app_list)
    print len(app_list)
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
