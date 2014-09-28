from pymongo import MongoClient
from datetime import datetime

FROM_MONGO_SEVRER_URL = "mongodb://appdb:cdj6u58CtSa@54.72.191.195:27017/appdb?slaveok=true"
TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
from_client = MongoClient(FROM_MONGO_SEVRER_URL)
to_client = MongoClient(TO_MONGO_SEVRER_URL)
from_db = from_client["appdb"]
to_db = to_client["appcenter"]


def update_app_download_netdisk():
    temp_docs = []
    for index, app_d_n in enumerate(from_db.app_download_netdisk.find({"uploader": "cloudl4files"})):
        app_id = app_d_n["appid"]
        f_app = from_db.app.find_one({"appid": app_id})
        if not f_app: continue
        print index
        bundle_id = f_app["bundleid"]
        temp_docs.append({
            "downloadUrl": app_d_n["download_url"],
            "sign": int(app_d_n["sign"]),
            "uploader": "cloud4files",
            "version": app_d_n["version"],
            "addTime": app_d_n.get("add_time", datetime.now()),
            "bundleId": bundle_id
        })
        if len(temp_docs) % 300 == 0:
            to_db.AppDownloadNetDisk.insert(temp_docs)
            temp_docs = []
    to_db.AppDownloadNetDisk.insert(temp_docs)

if __name__ == "__main__": update_app_download_netdisk()
