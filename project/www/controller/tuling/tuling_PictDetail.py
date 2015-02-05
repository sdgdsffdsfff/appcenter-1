#encoding=UTF8
#code by LP
#2013-11-28
import time
import math
import cjson
import json
import traceback
import random
from bson.objectid import ObjectId
from www.controller.app.header import *
from www.controller.app.app_download import AppDownloadController
from header import *
import pymongo
import re
from bson import ObjectId

class AppTopicController(ControllerBase):

    def __init__(self, language='en', ip=None):

        self._language = language
        self._country = get_country_code(ip)

    def get_list(self, obj_id,page,type,sexi):
        try:
            limit_no = 20

            if type not in ['hot','new','recommend']:
                    return []

	    if  obj_id != '':
		#print 
		sexi_list=['1','3','4','5','6','7','8','9']
		res1 = tuling_mongo_db.wallpaper_category.find({"_id":ObjectId(obj_id)})
                if not res1:
                    return []
		category = res1[0]['category']
		if str(sexi) not in sexi_list:
                    total = tuling_mongo_db.wallpaper.find({'category':category,'download_url':re.compile('.jpg$')}).count()
                    res = tuling_mongo_db.wallpaper.find({'category':category,'download_url':re.compile('.jpg$')},{'_id':0,'download_url':1,"size":1}).sort([(type,pymongo.ASCENDING)]).skip((page-1)*limit_no).limit(limit_no)
		else:

		    total = tuling_mongo_db.wallpaper.find({'category':category,"sexi":sexi,'download_url':re.compile('.jpg$')}).count()	    		    
		    res = tuling_mongo_db.wallpaper.find({'sexi':sexi,'category':category,'download_url':re.compile('.jpg$')},{'_id':0,'download_url':1,'sexi':1,"size":1}).sort([(type,pymongo.DESCENDING)]).skip((page-1)*limit_no).limit(limit_no)
		    
		    
            elif obj_id == '':
                if type == 'new':		    		    
                    type = '_id'
		sexi_list =['1','3','4','5','6','7','8','9']
	        if str(sexi) not in sexi_list:
	            total = tuling_mongo_db.wallpaper.find({'download_url':re.compile('.jpg$')}).count()
                    res = tuling_mongo_db.wallpaper.find({'download_url':re.compile('.jpg$')},{'_id':0,'download_url':1,"size":1}).sort([(type,pymongo.DESCENDING)]).skip((page-1)*limit_no).limit(limit_no)
	        else:
		    total = tuling_mongo_db.wallpaper.find({'sexi':sexi,'download_url':re.compile('.jpg$')}).count()
		    res = tuling_mongo_db.wallpaper.find({'sexi':sexi,'download_url':re.compile('.jpg$')},{'_id':0,'download_url':1,'sexi':1,"size":1}).sort([(type,pymongo.DESCENDING)]).skip((page-1)*limit_no).limit(limit_no)
		   

	    else:
                return []
            if not res:
                return []
            download_list = []
	    [download_list.append(item) for item in res]
	    return_dict = {}
	    return_dict['list'] = download_list
	    return_dict['total'] = total
            return return_dict
	    
        except Exception, ex:
            print ex
            return []
			
			
			
			
			
			
			
			

