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
from bson.objectid import ObjectId
from www.controller.app.header import *
from www.controller.app.app_download import AppDownloadController
from header import *
from bson import Binary, Code
from bson.json_util import dumps

class AppTopicController(ControllerBase):

    def __init__(self, language='en', ip=None):

        self._language = language
        self._country = get_country_code(ip)

    def get_list(self,category_language, jb=0):
        try:
	    res1 = tuling_mongo_db.ringtone_category_language.find()

	    if not res1:
		return []

	    dict_language = {}
	    for item in res1:
		list_temp = []

		list_temp.append(item['AB'])
		list_temp.append(item['CN'])
		list_temp.append(dumps(item['_id']))
		dict_language[item['EN']] = list_temp

            res = tuling_mongo_db.ringtone.aggregate([{"$group": {'_id': "$category",'count': {'$sum': 1}}}])
            if not res:
                return []

            output = []

            [output.append(item) for item in res['result']]

	    for item in output:
	        if dict_language.has_key(item["_id"]):
                    if  category_language == 'CN':
                        item["name"] =  dict_language[item["_id"]][1]
                    elif  category_language == 'AB':
                        item["name"] =  dict_language[item["_id"]][0]
                    else:
                        item["name"] =  item["_id"]

		    item['id'] = eval(dict_language[item['_id']][2])['$oid']
		    del item['_id']

            return output

        except Exception, ex:
            print ex
            return []

