from pymongo import MongoClient
from datetime import datetime

TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
to_client = MongoClient(TO_MONGO_SEVRER_URL)
to_db = to_client["appcenter"]

def transfer():
    bases_cn = to_db.AppBase_CN.find({}, {"_id": 0})
    for index, app_cn in enumerate(bases_cn):
        track_id = app_cn["trackId"]
        print index
        app_base = to_db.AppBase.find_one({"trackId": track_id}, {"_id": 0})
        if not app_base:
            print track_id
            app_cn["from_db"] = "cn"
            to_db.AppBase.update({"trackId": track_id}, {"$set": app_cn}, True)

if __name__ == "__main__":
    transfer()
