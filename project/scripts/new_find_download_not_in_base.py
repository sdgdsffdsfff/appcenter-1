from pymongo import MongoClient
from datetime import datetime
import threading
import math

FROM_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@61.155.215.40:37017/appcenter?slaveok=true"
from_client = MongoClient(FROM_MONGO_SEVRER_URL)
from_db = from_client["appcenter"]

app_downloads = list(from_db.AppDownload.find({}, {"_id":0, "bundleId": 1}))

def worker(lists, thread_index):
    print "thread %s start..., lenth: %d" % (str(thread_index), len(lists))
    with open("/Users/qijianbiao/bundle_ids/to_crawl_bundleids_%s.txt" % (str(thread_index)), "a") as bf:
        for index, app_download in enumerate(lists):
            try:
                app_b = from_db.AppBase.find_one({"bundleId": app_download["bundleId"]})
                if not app_b: bf.write(app_download["bundleId"]+"\n")
            except: continue

thread_num = 100
length = len(app_downloads)
num_per_thread = math.ceil(length / float(thread_num))

threads = []
for i in range(thread_num):
    begin = int(i*num_per_thread)
    end = int((i+1)*num_per_thread)
    t = threading.Thread(target=worker, args=(app_downloads[begin: end], i))
    threads.append(t)
    t.start()
