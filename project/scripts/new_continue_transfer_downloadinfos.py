from pymongo import MongoClient
from datetime import datetime, timedelta
import time

FROM_MONGO_SEVRER_URL = "mongodb://appdb:cdj6u58CtSa@54.72.191.195:27017/appdb?slaveok=true"
TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
from_client = MongoClient(FROM_MONGO_SEVRER_URL)
to_client = MongoClient(TO_MONGO_SEVRER_URL)
from_db = from_client["appdb"]
to_db = to_client["appcenter"]

def update_new_appbase(app_download, bundleids_file):
    bundle_id = app_download["bundleid"]
    app_id = app_download["appid"]
    package_sign = abs(app_download["jb"]-1)
    hash_v = app_download["hash"]
    new_base_download = {
        "bundleId": bundle_id,
        "version" : app_download["bundleversion"],
        "minOsVersion": app_download.get("min_os_version", ""),
        "addTime": app_download.get("addtime", datetime.now()),
        "hash": hash_v, "appid": app_id, "sign": package_sign
    }
    to_db.AppDownload.update({"hash": hash_v}, {"$set": new_base_download}, True)
    new_app_base = to_db.AppBase.find_one({"bundleId": bundle_id})
    if new_app_base:
        old_app = from_db.app.find_one(
            {"appid": app_id},
            {"bundleid": 1, "sign": 1, "icon": 1, "review": 1, "appid":1, "_id": 0}
        )
        temp_info = {}
        temp_info["review"] = 1
        temp_info["appid"] = old_app.get("appid", 0)
        temp_info["icon"] = old_app.get("icon", "")
        if package_sign == 1: temp_info["sign"] = package_sign
        to_db.AppBase.update({"bundleId": bundle_id}, {"$set": temp_info})
        to_db.AppBase_CN.update({"bundleId": bundle_id}, {"$set": temp_info})
    else:
        bundleids_file.write(bundle_id + "\n")

def find_new_downloads(begin_date):
    where = {"addtime": {"$gt": begin_date}, "soft_delete": {"$ne": 1}}
    new_downloads =  list(from_db.app_download.find(where))
    print len(new_downloads)
    return new_downloads

if __name__ == "__main__":
    begin_date = datetime(2014, 10, 3, 0, 0, 0)
    while True:
        old_downloads = find_new_downloads(begin_date)
        with open("/tmp/new_bundleids.txt", "w") as bundleids_file:
            for index, old_download in enumerate(old_downloads):
                try: update_new_appbase(old_download, bundleids_file)
                except Exception, e:
                    print e.message
                    continue
            begin_date = datetime.now() - timedelta(60 * 35)
        time.sleep(60*30)
