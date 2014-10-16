from pymongo import MongoClient
from datetime import datetime
import hashlib

# TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@61.155.215.40:37017/appcenter?slaveok=true"

to_client = MongoClient(TO_MONGO_SEVRER_URL)
to_db = to_client["appcenter"]

def transfer(bundleids_file):
    print "begin transfer"
    downloads = to_db.AppDownload.find({"addTime": {"$gt": datetime(2014, 10, 16, 0, 0, 0)}, "sign": 1},
                                            {"bundleId": 1, "version": 1, "addTime": 1, "hash": 1})
    print downloads.count()
    results = {}
    for index, download in enumerate(downloads):
        bundleId = download.get("bundleId", "")
        version = download.get("version", "")
        addTime = download.get("addTime", "")
        hash_c = download.get("hash", "")
        key_hash = hashlib.md5(bundleId+version).hexdigest()
        if key_hash not in results:
            results[key_hash] = [addTime, hash_c]
        else:
            print hash_c
            if addTime > results[key_hash][0]:
                bundleids_file.write(results[key_hash][1] + "\n")
                results[key_hash] = [addTime, hash_c]
            else:
                bundleids_file.write(hash_c + "\n")

if __name__ == "__main__":
    with open("downloads_hash.txt", "w") as f:
        transfer(f)
