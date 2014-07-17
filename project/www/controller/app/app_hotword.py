#encoding=UTF8
#code by LP
#2013-11-28

import datetime
from header import *
from bson.objectid import ObjectId
from bson.json_util import dumps


class AppHotWordController(ControllerBase):

    def __init__(self, language='EN', device="1", ip=None):

        self._language = language
        self._country = get_country_code(ip)
        self.device = device

    def get(self, object_id):
        res = mongo_db.hot_word.find_one({'_id': ObjectId(object_id)})
        if not res:
            return {}
        return dumps(res)

    def get_list(self):
        res = mongo_db.hot_word.find({"language": self._language, "device": self.device})
        if not res:
            return []
        return dumps(res)