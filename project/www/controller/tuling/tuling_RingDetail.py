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
import pymongo
import re
from bson import ObjectId
from bson import Binary, Code
from bson.json_util import dumps

class AppTopicController(ControllerBase):

    def __init__(self, language='en', ip=None):

        self._language = language
        self._country = get_country_code(ip)

    def get_list(self,type,obj_id,page=1):
        try:
            limit_no = 20
            if obj_id != '':
		res1 = tuling_mongo_db.ringtone_category_language.find({"_id":ObjectId(obj_id)})
                if not res1:
                    return []
		
		category = res1[0]['EN']

      		total = tuling_mongo_db.ringtone.find({'category':category}).count()		
                res = tuling_mongo_db.ringtone.find({'category':category},{'_id':0,'file_id':1,'filename':1,'filesize':1}).sort([('_id',pymongo.ASCENDING)]).skip((page-1)*limit_no).limit(limit_no)
	
            elif obj_id == '':
                if type not in ['hot','new','recommend']:
                    return []

                if type == 'new':
                    type = '_id'

		total = tuling_mongo_db.ringtone.find({}).count()
                res = tuling_mongo_db.ringtone.find({},{'_id':0,'file_id':1,'filename':1,'filesize':1}).sort([(type,pymongo.DESCENDING)]).skip((page-1)*limit_no).limit(limit_no)
            else:
                return []

            if not res:
                return []

            download_list = []

	    for item in res:
                item['download_url'] = 'http://iosmediacenter.s3.amazonaws.com/' + str(item['file_id'])
	        del item['file_id']
                download_list.append(item)
	    
            output ={}
            output['total'] = total
            output['data'] = download_list

            return output
        except Exception, ex:
            print ex
            return []

