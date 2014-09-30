import random, time, requests
from pymongo import MongoClient
from datetime import datetime
from www.controller.app.app_download import AppDownloadController
from conf.settings import settings
from www.controller.app.header import (mongo_db, redis_master, sha1_of_file,
                                       hash_to_path, create_pic_url_by_path, file_size_format)

FROM_MONGO_SEVRER_URL = "mongodb://appdb:cdj6u58CtSa@54.72.191.195:27017/appdb?slaveok=true"
TO_MONGO_SEVRER_URL = "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter"
from_client = MongoClient(FROM_MONGO_SEVRER_URL)
to_client = MongoClient(TO_MONGO_SEVRER_URL)
from_db = from_client["appdb"]
to_db = to_client["appcenter"]

app_download_c = AppDownloadController()

class MyFile(file):
    def __init__(self, qfile, mode, name):
        super(MyFile, self).__init__(self, qfile, mode)
        self.filename = name

def upload_hash_file(content, filename, target_dir, allow_ext=['png', 'jpg', 'jpeg']):
    '''
    上传文件
    '''
    if file:
        filename = filename.lower()
        filename = str(uuid.uuid1()) + "." + filename.rsplit('.', 1)[1]
        tmpfile = os.path.join(settings['tmp_dir'], filename)
        with open(tempfile, "w") as tt: tt.write(content)
        hash_str = sha1_of_file(tmpfile)
        save_file = '%s.%s' % (hash_to_path(hash_str), filename.rsplit('.', 1)[1])
        abs_save_file = os.path.join(target_dir, save_file)
        save_file_dir = os.path.dirname(abs_save_file)
        if not os.path.exists(save_file_dir): os.makedirs(save_file_dir)
        shutil.move(tmpfile, abs_save_file)
    else:
        raise Exception('上传失败')
    return hash_str, abs_save_file, save_file

def save_icon_and_return_hash(app_topic):
    icon_hash = app_topic.get("icon", None)
    if not icon_hash: return
    image_url = "http://pic.appvv.com/%s/114.jpg" % icon_hash
    content = requests.get(image_url).content
    hash_str, abs_save_file, save_file = upload_hash_file(
        content, "%s.jpg" % icon_hash, settings['pic_upload_dir'], ['png', 'jpg'])
    return hash_str

def update_app_topic():
    old_app_topics = from_db.app_topic.find({})
    old_app_topics = list(old_app_topics)
    print len(old_app_topics)
    print "load finish"
    for index, app_topic in enumerate(old_app_topics):
        print index
        try:
            topic_data = {"status":1}
            topic_data["update_time"] = app_topic.get("update_time", datetime.now())
            topic_data["name"] = app_topic["caption"]
            topic_data["description"] = app_topic.get("description", "")
            exists_topic = to_db.app_topic.find_one({"name": topic_data["name"], "description": topic_data["description"]})
            if exists_topic:
                print "exists"
                continue
            topic_data["prisonbreak"] = app_topic.get("jb", 1)
            old_language = app_topic.get("language", "cn")
            if old_language == "cn": language = ["zh-Hans"]
            elif old_language == "tw": language = ["zh-Hant"]
            elif old_language == "ar": language = ["ar"]
            else:
                language = ['en', 'it', 'vi', 'es', 'pt', 'fr', 'sv', 'nl', 'de', 'el', 'ca', 'cs', 'id', 'en-GB', 'ru', 'nb', 'tr', 'th', 'ro', 'pl', 'uk', 'hr', 'da', 'fa', 'pt-BR', 'pt-PT', 'fi', 'hu', 'ja', 'he', 'ko', 'km', 'sk', 'ms']
            topic_data["language"] = language
            items = []
            for app in from_db.app_topic_app.find({"topicid": app_topic["topicid"]}):
                temp_item = {}
                temp_item["sort"] = app.get("sort", 0)
                appid = app.get("appid", None)
                if not appid: continue
                app_instance = from_db.app.find_one({"appid": appid})
                if not app_instance: continue
                bundleId = app_instance.get("bundleid", None)
                trackId = app_instance.get("trackid", "")
                if not bundleId: continue
                with open("trackids.txt", "w") as fb: fb.write("%s\n" % str(trackId))
                temp_item["bundleId"] = bundleId
                downloads = app_download_c.get_by_bundleid(bundleId, topic_data["prisonbreak"])
                if downloads:
                    temp_item["version"] = downloads[-1]["version"]
                else:
                    temp_item["version"] = ""
                new_app_instance = to_db.AppBase.find_one({"bundleId": bundleId})
                new_app_instance_cn = to_db.AppBase_CN.find_one({"bundleId": bundleId})
                if not new_app_instance_cn or (not new_app_instance): continue
                if not new_app_instance and new_app_instance_cn:
                    temp = copy.copy(new_app_instance_cn)
                    temp.pop("_id")
                    to_db.AppBase.update({"bundleId": bundleId}, {"$set": temp}, True)
                    new_app_instance = to_db.AppBase.find_one({"bundleId": bundleId})
                temp_item["ID"] = str(new_app_instance["_id"])
                if app_topic.get("language", "cn") == "cn":
                    temp_item["trackName"] = new_app_instance_cn["trackName"]
                else:
                    temp_item["trackName"] = new_app_instance["trackName"]
                temp_item["icon"] = new_app_instance.get("artworkUrl512", "")
                temp_item["size"] = '%.2fMB' % (int(new_app_instance.get("fileSizeBytes", 0)) / 1024 / 1024)
                temp_item["averageUserRating"] = new_app_instance.get("averageUserRating", 0)
                temp_item["id"] = '%s%s' % (int(time.time()), random.randint(1000, 9999))
                items.append(temp_item)
            topic_data["items"] = items
            topic_data["country"] = []
            icon_hash = save_icon_and_return_hash(app_topic)
            topic_data["icon_store_path"] = "%s/%s/%s/%s/%s.jpg" % (
                icon_hash[0:2], icon_hash[2:4], icon_hash[4:6], icon_hash[6:8], icon_hash[8:40])
            topic_data["icon_hash"] = icon_hash
            to_db.app_topic.insert(topic_data)
        except Exception, e: raise e
