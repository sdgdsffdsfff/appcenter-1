from header import *


class OtherAdController(ControllerBase):
    def __init__(self, language='', ip=None, country=None):
        self._language = language
        if country is None: self._country = get_country_code(ip)
        else: self._country = country

    def get(self):
        try:
            res = mongo_db.other_ad.find({}, {"_id": 0})
            return res
        except Exception, ex: return {}
