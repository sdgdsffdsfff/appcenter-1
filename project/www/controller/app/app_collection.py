#encoding=UTF8
#code by LP
#2013-11-27

from header import *
from app import AppController

class AppCollectionController(ControllerBase):
    def __init__(self, identifier, language='', ip=None, country=None):
        self._identifier = identifier
        self._language = language

        if country is None:
            self._country = get_country_code(ip)
        else:
            self._country = country

    def get(self, num=None, front=False, sign=0, vv_version="common"):
        '''
        Get app collection
        num 获取数量  front是否前端显示
        '''
        #create a dict to map the language and collection,
        # need to find a better way to avoid hard code the language and  database name
        lang_collection = {"zh-Hans": "AppBase_CN", "en": "AppBase"}
        try:
            res = mongo_db.app_collection.find_one({'identifier': self._identifier})
            if not res or 'items' not in res: return {}
            try: title = res['title']['en']
            except: title = res['title']['zh-Hans']
            try: title = res['title'][self._language]
            except: pass
            filter_items = []
            app_controller = AppController()
            bundleids = [itemq.get('bundleId', '') for itemq in res['items']]
            download_infos = app_controller.get_downloads_of_allbundleids(bundleids, sign, vv_version)
            for item in res['items']:
                tmp_item = None
                if self._language == "":
                    tmp_item = item
                else:
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
                download_info = download_infos[tmp_item.get('bundleId', '')]
                d_version = download_info.get("ipaVersion", "")
                try:
                    download_info.pop("ipaHistoryDownloads")
                except Exception, e: pass

                download_info["ipaDownloadUrl"] = create_ipa_url(download_info["ipaHash"], sign)

                superurl = item.get("superurl", "").strip()
                superurl_sign = item.get("superurl_sign", "").strip()
                if superurl != "" and sign != 1:
                    download_info["ipaDownloadUrl"] = superurl.strip().replace(' ', '%20')
                    download_info["issuperurl"] = 1
                if superurl_sign != "" and sign != 0:
                    download_info["ipaDownloadUrl"] = superurl_sign.strip().replace(' ', '%20')
                    download_info["issuperurl_sign"] = 1

                app_trackName = tmp_item['trackName']
                if self._language in lang_collection:
                    t_item = mongo_db[lang_collection[self._language]].find_one({"bundleId": tmp_item["bundleId"]})
                    if t_item:
                        app_trackName = t_item.get("trackName", app_trackName)

                if self._language == "ar":
                    app_trackName = app_trackName if tmp_item.get("arname", "") == "" else tmp_item["arname"]
                if self._language == "zh-Hans":
                    app_trackName = app_trackName if tmp_item.get("cnname", "") == "" else tmp_item["cnname"]
                if front:
                    temp_d1 = {
                        'trackName': app_trackName,
                        'ID': tmp_item['ID'], 'averageUserRating': rating,
                        'bundleId': tmp_item.get('bundleId',''),
                        'icon': tmp_item['icon'], 'version': d_version,
                        'size': tmp_item.get('size', ''), 'sort': tmp_item['sort']
                    }
                    temp_d1.update(download_info)
                    filter_items.append(temp_d1)
                else:
                    temp_d2 = {
                        'trackName': app_trackName,
                        'ID': tmp_item['ID'], 'averageUserRating': rating,
                        'bundleId': tmp_item.get('bundleId',''),
                        'icon': tmp_item['icon'], 'sort': tmp_item['sort'],
                        'country': tmp_item['country'],
                        'id': tmp_item['id'], 'language': tmp_item['language'],
                        'version': d_version,
                        'size': tmp_item.get('size', '')
                    }
                    temp_d2.update(download_info)
                    filter_items.append(temp_d2)
            data = sort_items(filter_items)
            return {'title': title, 'identifier': res['identifier'], 'data': data if num is None else data[0:num]}
        except Exception, ex:
            print ex
            return {}
