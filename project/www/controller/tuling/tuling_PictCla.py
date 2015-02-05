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

    def get_list(self, jb=0):
        try:
            res1 = tuling_mongo_db.wallpaper_category.find({},{'_id':1,'category':1,'download_url':1})
	    if not res1:
                return []
		
	    CateUrl_dict={}
	    for item in res1:
		list_temp = []

		list_temp.append(item['download_url'])
		list_temp.append(dumps(item['_id']))
		CateUrl_dict[item['category']] = list_temp

	    res = tuling_mongo_db.wallpaper.aggregate([{"$match":{'download_url':re.compile('.jpg$')}},{"$group": {'_id': "$category",'count': {'$sum': 1}}}])
            if not res:
                return []

            output = []

            [output.append(item) for item in res['result']]

	    for item in output:
		if CateUrl_dict.has_key(item['_id']):
			item['name'] = item['_id'] 
			item['url'] = CateUrl_dict[item['_id']][0]
			item['id'] = eval(CateUrl_dict[item['_id']][1])['$oid']
			del item['_id']

            return output
        except Exception, ex:
            print ex
            return []
			
			
			
			
			
			

