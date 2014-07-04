import json, requests, time, urllib2, urllib, zipfile, os, sys, pexpect

from conf.settings import settings
from common.ng_mongo import NGMongoConnect
mongo = NGMongoConnect(settings['mongodb']['host'])
mongo_db = mongo.get_database('appcenter')

host_url = "http://54.183.93.130/"
get_file_failed_url = host_url + "fail-getting-file/"
finish_handle_url = host_url + "finish-handling-file/"

FILE_TO_SAVE_DIR =  "/data1/tmp_jsons/"


def request_appinfo_file_info():
    get_file_url = host_url + "get-file/appinfo/"
    print "Begin to get appinfo file info"
    res = requests.post(get_file_url, timeout=60)
    return res.json()

def request_appinfo_file(data):
    if data.get("code", "")  == 0 and data.get("data").get("appid_file") != None:
        file_name = data.get("data", {}).get("appid_file", {}).get("filename", "")
        oid = data.get("data", {}).get("appid_file", {}).get("_id", {}).get("$oid", "")
        try:
            print "Begin to get file: %s..." % file_name
            remote_file_dir = "/mnt/spiders/upload/app_info_files/" + file_name.split("/")[-1]
            file_to_update = FILE_TO_SAVE_DIR + file_name.split("/")[-1]
            cmd = 'scp root@54.183.93.130:%s %s' % (remote_file_dir, file_to_update)
            child = pexpect.spawn(cmd)
            child.timeout = 300
            child.expect('password:')
            child.sendline('aPp6vv_c7om')
            child.interact()
            # file_to_update = FILE_TO_SAVE_DIR + file_name.split("/")[-1]
            # write_to_file = open(file_to_update, "wb")
            # print "Begin to connect remote file server"
            # u = urllib2.urlopen(file_name, timeout=60)
            # print "Finish connecting remote file server"
            # file_size_dl = 0
            # block_size = 1028 * 16
            # print "Begin to read file from remote file server"
            # while True:
            #     buffer = u.read(block_size)
            #     if not buffer: break
            #     write_to_file.write(buffer)
            #     file_size_dl += len(buffer)
            #     print "Have readed %d size from file server" % file_size_dl

            print "Finish getting remote file"
            return file_to_update, data
        except Exception, e:
            print "<Request Appinfo File> Error %s occurs and mongo id is : %s" % (e.message, oid)
            i = 5
            while i > 0:
                try:
                    requests.post(get_file_failed_url + oid + "/", timeout=60)
                    break
                except:
                    time.sleep(3)
                    i -= 1
            return None, None
    print "No file has founded"
    return None, None

def update_app_info(file_name, data):
    oid = data.get("data", {}).get("appid_file", {}).get("_id", {}).get("$oid", "")
    try:
        file_to_zip = zipfile.ZipFile(file_name)
        file_to_zip.extractall(FILE_TO_SAVE_DIR)
        json_file_name = file_to_zip.namelist()[0]
        print "Begin to update app info"
        for line in file(os.path.join(FILE_TO_SAVE_DIR, json_file_name), "r"):
            try:
                if line.strip() == "": continue
                app_info = json.loads(line)
                dicts = {}
                for name, value in app_info.items(): dicts[name] = value
                mongo_db.AppBase.update({"bundleId": app_info["bundleId"]}, {"$set": dicts}, True)
            except Exception, e: print "line error: %s" % e.message
        requests.post(finish_handle_url + oid + "/", timeout=30)
        print "Finish updating app info"
    except Exception, e:
        print "<Update App Info>post error: %s and mongo id is %s" % (e.message, oid)
        i = 5
        while i > 0:
            try:
                requests.post(get_file_failed_url + oid + "/", timeout=30)
                break
            except:
                time.sleep(3)
                i -= 1

def get_appinfo_and_file():
    try:
        data = request_appinfo_file_info()
    except Exception, e:
        print "Getting App info json Error: %s" % e.message
        return None, None
    return request_appinfo_file(data)

def recursive_update_app_info():
    while True:
        file_name, data = get_appinfo_and_file()
        if not file_name:
            print("No job get Or Fuck its networking, try in 1 minute later! waiting...")
            time.sleep(60 * 1)
            continue
        update_app_info(file_name, data)
