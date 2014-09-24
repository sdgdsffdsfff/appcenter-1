from pymongo import MongoClient
from datetime import datetime

FROM_MONGO_SEVRER_URL = "mongodb://appdb:cdj6u58CtSa@54.72.191.195:27017/appdb"
TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.76.98.58:37017,61.155.215.40:37017,61.155.215.45:37017/appcenter"
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
        if not app_id: continue
        app = from_db.app.find_one({"app_id": app_id})
        temp_docs.append({
            "bundleId": app["bundleid"], "version" : app["bundle_version"],
            "minOsVersion": app.get("min_os_version", ""),
            "addTime": app.get("addTime", datetime.now()),
            "hash": app["hash"], "appid": app["appid"], "sign" : abs(app["jb"]-1)
        })
        if len(temp_docs) % 500 == 0:
            to_db.AppDownload.insert(temp_docs)
            temp_docs = []
    to_db.AppDownload.insert(temp_docs)

if __name__ == "__main__":
    transfer_app_download()
