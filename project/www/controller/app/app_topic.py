#encoding=UTF8
#code by LP
#2013-11-28

import datetime
from header import *
from bson.objectid import ObjectId


class AppTopicController(ControllerBase):

    def __init__(self, language='EN', ip=None):

        self._language = language
        self._country = get_country_code(ip)

    def get(self, object_id, front=False):

        res = mongo_db.app_topic.find_one({'_id': ObjectId(object_id)})
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
                tmp.append({'trackName': item['trackName'],
                    'averageUserRating': item['averageUserRating'],
                    'icon': item['icon'], 'version': item['version'], 
                    'size': item['size'], 'ID': item['ID']})
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

    def get_list(self):
        try:
            res = mongo_db.app_topic.find({'status': 1})
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

                output.append({'topicID': str(tmp_item['_id']), 'name': tmp_item['name'], 'appCount': count,
                               'update_time': update_time,'icon': create_pic_url(tmp_item['icon_store_path'])})
            return output
        except Exception, ex:
            print ex
            return []
