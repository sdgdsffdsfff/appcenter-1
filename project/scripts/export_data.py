from pymongo import MongoClient
from datetime import datetime

FROM_MONGO_SEVRER_URL = "mongodb://localhost:27017/"
TO_MONGO_SEVRER_URL = "mongodb://192.168.16.71:27017/"

from_client = MongoClient(FROM_MONGO_SEVRER_URL)
to_client = MongoClient(TO_MONGO_SEVRER_URL)

from_db = from_client["appdb"]
to_db = to_client["appcenter"]

def update_app_base():
    temp_docs = []
    for app in to_db.AppBaseTemp.find():
        bundle_id = app["bundleId"]
        f_app = from_db.app.find_one({"bundleid": bundle_id})
        if f_app:
            app["sign"] = f_app["sign"]
            app["icon"] = f_app["icon"]
            app["review"] = f_app.get("review", 0)
        temp_docs.append(app)
        if len(temp_docs) % 500 == 0:
            to_db.AppBase.insert(temp_docs)
            temp_docs = []
    to_db.AppBase.insert(temp_docs)


def update_app_download():
    temp_docs = []
    for app in from_db.app_download.find():
        temp_docs.append(
            {
                "bundleId": app["bundleid"],
                "sign" : abs(app["jb"]-1),
                "version" : app["version"],
                "minOsVersion": app.get("min_os_version", ""),
                "addTime": app.get("addTime", datetime.now()),
                "hash": app["hash"]
            }
        )
        if len(temp_docs) % 500 == 0:
            to_db.AppDownload.insert(temp_docs)
            temp_docs = []
    to_db.AppDownload.insert(temp_docs)

def update_app_download_netdisk():
    temp_docs = []
    for app_d_n in from_db.app_download_netdisk.find({"uploader": "cloudl4files"}):
        app_id = app_d_n["appid"]
        f_app = from_db.app.find_one({"appid": app_id})
        if not f_app: continue
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

if __name__ == "__main__":
    update_app_base()
    # update_app_download()
    # update_app_download_netdisk()
