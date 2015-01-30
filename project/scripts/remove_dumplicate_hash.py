from pymongo import MongoClient
from datetime import datetime
import hashlib

TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"

to_client = MongoClient(TO_MONGO_SEVRER_URL)
to_db = to_client["appcenter"]

def remove(remove_file):
    for line in open("/Users/qijianbiao/Desktop/to_be_remoted.txt", "r"):
        hash_v = line.strip()
        print hash_v
        hash_entry = list(to_db.AppDownload.find({"hash": hash_v}))
        if hash_entry: remove_file.write(hash_v+"\n")
        #to_db.AppDownload.remove({"hash": hash_v})

if __name__ == "__main__":
    remove_file = open("/Users/qijianbiao/Desktop/to_be_remoted_new.txt", "w")
    remove(remove_file)
    remove_file.close()
