#encoding=utf-8
import json
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId

from conf.settings import settings

client = MongoClient(settings["mongodb"]["host"])

apple_url = "https://itunes.apple.com/cn/lookup?id="
db = client.appcenter

collection = db["AppBase"]
collection_cn = db["AppBase_CN"]

size = 100

def fetch_appbase():
	ids = []
	for app in collection.find().skip(470089):
		if "trackId" in app:
			ids.append(str(app["trackId"]))
			if len(ids) == size:
				rs = requests.get(apple_url + ",".join(ids))
				try:
					rs_json = rs.json()
				except ValueError:
					try:
						rs_json = json.loads(rs.text)
					except Exception:
						continue
				if "results" in rs_json and len(rs_json["results"]) != 0:
					for result in rs_json["results"]:
						print result
						app = collection_cn.find({"trackId": int(result["trackId"])})
						if app:
							collection_cn.update({"trackId": int(result["trackId"])}, {"$set": result}, upsert=True)
						else:
							collection_cn.insert(result)
						del ids[:]
						continue

if __name__ == '__main__':
	fetch_appbase()
