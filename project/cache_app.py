#encoding=UTF8
#code by LP
#2013-12-5

import sys
from www.controller.app.app import AppController
from conf.settings import settings
from common.ng_mongo import NGMongoConnect
import multiprocessing

mongo = NGMongoConnect(settings['mongodb']['host'])
mongo_db = mongo.get_database('appcenter')

def worker(_id):
    print _id
    appc = AppController()
    appc.set_app_cache(_id)
    

if __name__ == "__main__":
    
    try:
        appc = AppController()
        appc.set_app_cache(sys.argv[1])
    except:
        apps = mongo_db.AppBase.find({'review': 1})
        count = apps.count()
                
        pool = multiprocessing.Pool(processes=5)
        for app in apps:
            #worker(app['_id'])
            pool.apply_async(worker, (app['_id'], ))
        
        pool.close()
        pool.join()
