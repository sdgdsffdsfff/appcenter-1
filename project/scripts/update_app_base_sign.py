from pymongo import MongoClient
from datetime import datetime

TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
to_client = MongoClient(TO_MONGO_SEVRER_URL)
to_db = to_client["appcenter"]

def transfer():
    downloads = to_db.AppDownload.find({})
    for index, download in enumerate(downloads):
        bundle_id = download.get("bundleId", None)
        if not bundle_id: continue
        sign = download.get("sign", 0)
        data = {"review": 1}
        if sign == 1: data["sign"] = sign
        print index
        to_db.AppBase.update({"bundleId": bundle_id}, {"$set": data})

if __name__ == "__main__":
    transfer()
