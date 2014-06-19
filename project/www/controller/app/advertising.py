#encoding=UTF8
#code by LP
#2013-11-4

from header import *

class AdvertisingController(ControllerBase):

    def __init__(self, identifier, language='US', ip=None):
        self._identifier = identifier
        self._language = language
        self._country = get_country_code(ip)

    def get(self, num):
        '''
        Get advertising
        '''
        res = mongo_db.advertising.find_one({'identifier':self._identifier})
        if not res or 'items' not in res:
            return []

        filter_items = []
        for item in res['items']:
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

            if tmp_item == None:
                continue
            filter_items.append({'title':tmp_item['title'], 'link':tmp_item['link'], 'picURL':create_pic_url(tmp_item['store_path'])})

        return filter_items[0:num]



