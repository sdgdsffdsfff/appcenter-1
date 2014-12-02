#encoding=UTF8
#code by LP
#2013-11-4

import time
import datetime
import os
import shutil
from header import *
from bson.objectid import ObjectId
from lib.ipa import get_info_from_ipa, check_sign_from_ipa
from collections import defaultdict

class AppDownloadController(ControllerBase):
    '''
    APP 下载
    '''
    def get_all_downloads_of_app(self, bundleid, vv_version="common"):
        cur_apple_account = ""
        if vv_version != "common":
            cur_vshare_version = mongo_db.vshare_version.find_one({"identity": vv_version})
            cur_apple_account = cur_vshare_version.get("apple_account", "common")
        where = {'bundleId': bundleid}
        res = list(mongo_db.AppDownload.find(where))
        res = list(sort_downloads(res))
        results_common = defaultdict(list)
        results_apple_account = defaultdict(list)
        for re in res:
            apple_account = re.get("apple_account", None)
            if apple_account == cur_apple_account:
                results_apple_account[re.get("sign", 0)].append(re)
            elif apple_account is None:
                results_common[re.get("sign", 0)].append(re)
        return (results_apple_account.get(1, []) + results_common.get(1, []),
                results_apple_account.get(0, []) + results_common.get(0, []))

    def get_by_bundleids(self, bundleids, sign=0, vv_version="common"):
        results_1 = defaultdict(list)
        results_2 = defaultdict(list)
        results = defaultdict(list)
        where = {'bundleId': {"$in": bundleids}, "sign": sign}
        res = mongo_db.AppDownload.find(where)
        cur_vshare_version = mongo_db.vshare_version.find_one({"identity": vv_version})
        if cur_vshare_version is not None:
            cur_apple_account = cur_vshare_version.get("apple_account", "")
        else: cur_apple_account = ""
        for down in res:
            apple_account = down.get("apple_account", None)
            if apple_account and apple_account == cur_apple_account:
                results_1[down["bundleId"]].append(down)
            elif apple_account is None:
                results_2[down["bundleId"]].append(down)
        for key, value in results_1.items():
            try: results[key] += list(sort_downloads(list(value)))
            except: results[key] += list(value)
        for key, value in results_2.items():
            try: results[key] += list(sort_downloads(list(value)))
            except: results[key] += list(value)
        return results

    def get_by_bundleid(self, bundleid, sign=0, vv_version="common"):
        """
        通过bundleid获取app
        """

        where = {'bundleId': bundleid, 'sign': int(sign)}

        res = mongo_db.AppDownload.find(where)
        if res:
            res = list(res)
            res = sort_downloads(res)
        #按版本排序
        return list(res)

    def get_by_bid(self, bundleid):
        """
        通过bundleid获取app的所有下载地址
        """

        where = {'bundleId': bundleid}
        res = mongo_db.AppDownload.find(where)
        if res:
            res = list(res)
            res = sort_downloads(res)
        #按版本排序
        return list(res)

    def delete_by_hash(self, hash_str):
        """
        通过hash值删除
        """
        mongo_db.AppDownload.remove({'hash': hash_str})

    def delete_by_objectid(self, _id):
        """
        通过hash值删除
        """
        mongo_db.AppDownload.remove({'_id': ObjectId(_id)})

    def get_download_url(self, ha):
        """get download link of an ipa hash"""
        return create_ipa_url(ha)

    def add(self, file_path, sign=0, bundle_id=None):
        """
        ipa文件入库
        """
        sha1 = sha1_of_file(file_path)
        dest_file_path = os.path.join(settings['ipa_dir'], hash_to_path(sha1)+'.ipa')

        dir_name = os.path.dirname(dest_file_path)
        if not os.path.isdir(dir_name):
            os.makedirs(dir_name)
        shutil.move(file_path, dest_file_path)

        info = get_info_from_ipa(dest_file_path)
        sign = check_sign_from_ipa(dest_file_path)
        version = info['version']
        if bundle_id is None:
            bundle_id = info['bundleid']

        data = {
            'bundleId': bundle_id,
            'hash': sha1,
            'sign': sign,
            'minOsVersion': '',
            'version': version,
            'addTime': datetime.datetime.now()
        }
        mongo_db.AppDownload.update({'hash': sha1}, data, upsert=True)
