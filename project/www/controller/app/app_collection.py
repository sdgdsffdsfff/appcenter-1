#encoding=UTF8
#code by LP
#2013-11-27

from header import *


class AppCollectionController(ControllerBase):
    def __init__(self, identifier, language='US', ip=None, country=None):
        self._identifier = identifier
        self._language = language

        if country is None:
            self._country = get_country_code(ip)
        else:
            self._country = country

    def get(self, num=None, front=False):
        '''
        Get app collection
        num 获取数量  front是否前端显示
        '''
        try:
            res = mongo_db.app_collection.find_one({'identifier': self._identifier})
            if not res or 'items' not in res:
                return {}
            try:
                title = res['title']['EN']
            except:
                title = res['title']['ZH']
            try:
                title = res['title'][self._language]
            except:
                pass

            filter_items = []
            for item in res['items']:
                tmp_item = None

                if 'language' in item and self._language in item['language']:
                    tmp_item = item
                elif 'country' in item and self._country in item['country']:
                    tmp_item = item
                elif ('language' in item and len(item['language']) == 0) and \
                        ('country' in item and len(item['country']) == 0):
                    tmp_item = item
                elif 'language' not in item and 'country' not in item:
                    tmp_item = item

                if tmp_item is None:
                    continue
                try:
                    rating = item['averageUserRating']
                except:
                    rating = 0
                if front:
                    filter_items.append(
                        {'trackName': tmp_item['trackName'], 'ID': tmp_item['ID'], 'averageUserRating': rating,
                        'icon': tmp_item['icon'], 'version': tmp_item['version'], 'size': tmp_item['size'], 'sort': tmp_item['sort']})
                else:
                    filter_items.append(
                        {'trackName': tmp_item['trackName'], 'ID': tmp_item['ID'], 'averageUserRating': rating,
                        'icon': tmp_item['icon'], 'sort': tmp_item['sort'], 'country': tmp_item['country'],
                        'id': tmp_item['id'], 'language': tmp_item['language'], 'version': tmp_item['version'], 
                        'size': tmp_item['size']})
            data = sort_items(filter_items)
            return {'title': title, 'identifier': res['identifier'], 'data': data if num is None else data[0:num]}
        except Exception, ex:
            print ex
            return {}



