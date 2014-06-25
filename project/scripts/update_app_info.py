import json, requests, time

from conf.settings import settings
from common.ng_mongo import NGMongoConnect
mongo = NGMongoConnect(settings['mongodb']['host'])
mongo_db = mongo.get_database('appcenter')

host_url = "http://54.183.93.130/"
get_file_failed_url = host_url + "fail-getting-file/"
finish_handle_url = host_url + "finish-handling-file/"

def update_app_info(file_name, data):
    oid = data.get("data", {}).get("appid_file", {}).get("_id", {}).get("$oid", "")
    print "Begining update app info"
    for line in file(file_name, "r"):
        try:
            if line.strip() == "": continue
            app_info = json.loads(line)
            dicts = {}
            for name, value in app_info.items(): dicts[name] = value
            mongo_db.AppBase.update({"bundleId": app_info["bundleId"]}, {"$set": dicts}, True)
        except Exception, e: print "line error: %s" % e.message; continue
    try:
        requests.post(finish_handle_url + oid + "/")
    except Exception, e:
        print "post error: %s" % e.message
        requests.post(get_file_failed_url + oid + "/")

def request_4_appinfo_file():
    get_file_url = host_url + "get-file/appinfo/"
    res = requests.post(get_file_url)
    data = res.json()
    if data.get("code", "")  == 0 and data.get("data").get("appid_file") != None:
        file_name = data.get("data", {}).get("appid_file", {}).get("filename", "")
        oid = data.get("data", {}).get("appid_file", {}).get("_id", {}).get("$oid", "")
        try: raw_res = requests.get(file_name)
        except Exception: requests.post(get_file_failed_url + oid + "/")
        file_to_update = "/tmp/" + file_name.split("/")[-1]
        print "Begin to write remote file"
        with open(file_to_update, "w") as f: f.write(raw_res.content)
        print "Finish writing remote file"
        return file_to_update, data
    return None, None

def recursive_update_app_info():
    while True:
        file_name, data = request_4_appinfo_file()
        if not file_name:
            print("No job get, try in 5 minute later! waiting...")
            time.sleep(60 * 5)
            continue
        update_app_info(file_name, data)
