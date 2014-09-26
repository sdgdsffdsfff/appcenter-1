#encoding=UTF8
#code by LP
#2013-11-4

import time
import datetime
import os
import shutil
from header import *
from bson.objectid import ObjectId
from lib.ipa import get_info_from_ipa
from collections import defaultdict

class AppDownloadNetDiskController(ControllerBase):
    '''
    APP 下载
    '''
    def get_by_bundleids(self, bundleids, sign=0):
        results = defaultdict(list)
        results2 = dict()
        where = {'bundleId': {"$in": bundleids}, "sign": sign}
        res = mongo_db.AppDownloadNetDisk.find(where)
        for down in res:
            results[down["bundleId"]].append(down)
        for key, value in results.items():
            results2[key] = list(sort_downloads(list(value)))
        return results2

    def get_by_bundleid(self, bundleid, sign=0):
        """
        通过bundleid获取app
        """
        where = {'bundleId': bundleid, 'sign': sign}
        res = mongo_db.AppDownloadNetDisk.find(where)
        if res:
            res = list(res)
            res = sort_downloads(res)
        #按版本排序
        return list(res)
