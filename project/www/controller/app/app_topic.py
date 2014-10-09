#encoding=UTF8
#code by LP
#2013-11-28
import time
import math
import cjson
import json
import traceback
import random
import datetime
from header import *
from bson.objectid import ObjectId
from www.controller.app.header import *
from www.controller.app.app_download import AppDownloadController


class AppTopicController(ControllerBase):

    def __init__(self, language='en', ip=None):

        self._language = language
        self._country = get_country_code(ip)

    def get(self, object_id, jb, front=False):

        res = mongo_db.app_topic.find_one({'_id': ObjectId(object_id), 'prisonbreak': int(jb)})
        if not res:
            return {}
        del res['_id']
        res['icon'] = create_pic_url(res['icon_store_path'])
        try:
            del res['icon_store_path']
            del res['icon_hash']
            res['update_time'] = datetime_format(res['update_time'])
        except:
            return {}

        if front:
            tmp = []
            for item in res['items']:
                if item.get("bundleId", "") != "":
                    downloads = self.get_downloads(item["bundleId"], jb)
                    ipa = create_ipa_url(downloads['ipaHash'])
                else:
                    ipa = ""
                    downloads = {}
                tmp.append({'trackName': item['trackName'],
                    'averageUserRating': item['averageUserRating'],
                    'icon': item['icon'], 'ipaVersion': downloads.get('ipaVersion', ''),
                    "ipaDownloadUrl": ipa, 'size': item['size'], 'ID': item['ID']}
                )
                res['items'] = tmp
            try:
                del res['country']
            except: pass
            try:
                del res['language']
            except: pass
            try:
                del res['status']
            except: pass
        return res

    def get_list(self, jb=0):
        try:
            res = mongo_db.app_topic.find({'status': 1, 'prisonbreak': jb}).sort({"order": 1})
            if not res:
                return []
            output = []

            for item in res:
                tmp_item = None

                if 'language' in item and self._language in item['language']:
                    tmp_item = item
                if 'country' in item and self._country in item['country']:
                    tmp_item = item
                if ('language' in item and len(item['language']) == 0) and \
                        ('country' in item and len(item['country']) == 0):
                    tmp_item = item
                if 'language' not in item and 'country' not in item:
                    tmp_item = item
                if tmp_item is None:
                    continue

                try:
                    count = len(item['items'])
                except:
                    count = 0
                try:
                    update_time = datetime_format(item['updateTime'])
                except:
                    update_time = datetime_format(datetime.datetime.now())

                output.append({'description': tmp_item['description'], 'topicID': str(tmp_item['_id']), 'name': tmp_item['name'], 'appCount': count, 'update_time': update_time,'icon': create_pic_url(tmp_item['icon_store_path'])})

            return output
        except Exception, ex:
            print ex
            return []

    def get_downloads(self, bundle_id, sign):

        ipaHash = "" #最新版
        ipaVersion = "" #最新版本号
        ipaHistoryDownloads = "" #历史版本

        #直接下载数据
        download = AppDownloadController()
        res = download.get_by_bundleid(bundle_id, sign)
        tmp_download_list = {}
        if res:
            for down in res:
                try:
                    tmp = {'ipaHash': down['hash'], 'version': down['version'],
                           'addTime': str(down['addTime'])}
                    if down['version'] not in tmp_download_list:
                        tmp_download_list[down['version']] = []
                    tmp_download_list[down['version']].append(tmp)
                except Exception, ex:
                    print ex
                    pass
            try:
                ipaHistoryDownloads = sort_dict_keys(tmp_download_list)
            except Exception, ex:
                print ex
            try:
                key = ipaHistoryDownloads.keys()[0]
                ipaHash = ipaHistoryDownloads[key][0]['ipaHash']
                ipaVersion = ipaHistoryDownloads[key][0]['version']
            except Exception, ex:
                traceback.print_exc()
                pass

        return {'ipaHash': ipaHash, 'ipaVersion': ipaVersion, 'ipaHistoryDownloads': ipaHistoryDownloads}
