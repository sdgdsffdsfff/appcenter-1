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

class AppDownloadNetDiskController(ControllerBase):
    '''
    APP 下载
    '''

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