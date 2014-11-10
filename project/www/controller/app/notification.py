#encoding=UTF8
from header import *
from bson.objectid import ObjectId
from bson.json_util import dumps


class NotificationController(ControllerBase):

    def __init__(self, language='EN', device="1", ip=None):

        self._language = language
        self._country = get_country_code(ip)
        self.device = device

    def get(self, object_id):
        pass

    def get_list(self):
        res = mongo_db.notification.find({"published": True})
        if not res.count():
            return []
        rs = []
        res = res[0]
        rs = res["noti"]
        return rs