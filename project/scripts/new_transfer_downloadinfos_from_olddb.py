from pymongo import MongoClient
from datetime import datetime

FROM_MONGO_SEVRER_URL = "mongodb://appdb:cdj6u58CtSa@54.72.191.195:27017/appdb?slaveok=true"
TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
from_client = MongoClient(FROM_MONGO_SEVRER_URL)
to_client = MongoClient(TO_MONGO_SEVRER_URL)
from_db = from_client["appdb"]
to_db = to_client["appcenter"]

def update_new_appbase(app_download):
    bundle_id = app_download["bundleid"]
    app_id = app_download["appid"]
    package_sign = abs(app_download["jb"]-1)
    hash_v = app_download["hash"]
    new_base_download = {
        "bundleId": bundle_id,
        "version" : app_download["bundleversion"],
        "minOsVersion": app_download.get("min_os_version", ""),
        "addTime": app_download.get("addTime", datetime.now()),
        "hash": hash_v, "appid": app_id, "sign": package_sign
    }
    old_app = from_db.app.find_one(
        {"appid": appid},
        {"bundleid": 1, "sign": 1, "icon": 1, "review": 1, "appid":1, "_id": 0}
    )
    if not old_app: return
    to_db.AppDownload.update({"hash": hash_v}, {"$set": new_base_download}, True)
    temp_info = {}
    temp_info["review"] = 1
    temp_info["appid"] = old_app.get("appid", 0)
    temp_info["icon"] = old_app.get("icon", "")
    if package_sign == 1: temp_info["sign"] = package_sign
    to_db.AppBase.update({"bundleId": bundle_id}, {"$set": temp_info})
    to_db.AppBase_CN.update({"bundleId": bundle_id}, {"$set": temp_info})

def worker(partial_list):
    for app_download in partial_list:
        try:
            update_new_appbase(app_download)
        except: continue

lists = []
where = {"soft_delete": {"$ne": 1}}
for index, app_download in enumerate(from_db.app_download.find(where)):
    if index == 100: break
    lists.append(app_download)

thread_num = 20
length = len(lists)
import math
num_per_thread = int(math.ceil(length / float(thread_num)))
threads = []
for i in range(thread_num):
    t = threading.Thread(target=worker, args=(lists[i*num_per_thread: (i+1)*num_per_thread], ))
    threads.append(t)
    t.start()
