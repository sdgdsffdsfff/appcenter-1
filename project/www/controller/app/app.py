#encoding=UTF8
#code by LP
#2013-11-4

import time
import math
import cjson
import json
import traceback
import random
from bson.objectid import ObjectId
from www.controller.app.header import *
from www.controller.app.app_download import AppDownloadController
from www.controller.app.app_download_netdisk import AppDownloadNetDiskController


class AppController(ControllerBase):
    """
    APP 基本信息数据
    """
    #应用列表缓存key
    app_list_redis_key = "APPLIST_%s_SIGN_%s_LANG_%s_GENRE_%s_LIMIT_%s_SORT_%s_DESC"
    #应用名称缓存key
    app_info_redis_key = "APPINFO_%s"
    app_version_redis_key = "APPVERSION_%s"
    #列表缓存长度
    limit = 600
    #默认语言
    default_language = 'CN'

    def __init__(self, language='EN'):
        #语言
        self.request_language = language_code_format(language)

    def get_by_objectid(self, _id):
        """
        通过objectid获取app
        """
        data = mongo_db.AppBase.find_one({'_id': ObjectId(_id)})
        return self._output_format(data)


    def get_by_trackid(self, trackid):
        """
        通过trackid获取app
        """
        data = mongo_db.AppBase.find_one({'trackId': trackid})
        return self._output_format(data)

    def get_by_bundleid(self, bundle_id):
        """
        通过bundleid获取app
        """
        data = mongo_db.AppBase.find_one({'bundleId': bundle_id})
        return self._output_format(data)

    def set_app_cache(self, object_id):
        """
        设置应用缓存
        """
        try:
            data = mongo_db.AppBase.find_one({'_id': ObjectId(object_id), 'review': 1})
            data = self.filter_app_output(data)
            downloads = self.get_app_downloads(data['bundleId'])
            for lang in self._get_ext_data_language():
                data['systemRequirements'] = 'IOS5.0+' #temp
                try: rating = data['averageUserRating']
                except: rating = 0
                try: size = file_size_format(data['fileSizeBytes'])
                except: size = 'unknown'
                try: download_version = downloads['ipaVersion']
                except: download_version = {'jb':'0', 'signed': '0'}
                dict_merged = dict(downloads, **data)
                json_str = json.dumps(super(AppController, self)._output_format(dict_merged))
                redis_master_pipeline.hset(self.app_info_redis_key % lang, object_id, json_str)
                version_data = json.dumps({
                    'ID': str(object_id), 'trackName': data['trackName'],
                    'icon': data['icon'], 'ipaVersion': download_version,
                    'bundleId': data['bundleId'], 'ipaHash': downloads['ipaHash'],
                    'averageUserRating': rating, 'size': size
                    })
                redis_master_pipeline.hset(self.app_version_redis_key % lang, data['bundleId'], version_data)
            redis_master_pipeline.execute()
        except Exception, ex:
            traceback.print_exc()
            pass

    def get_app_version_cache(self, bundle_id, lang='EN'):
        key = self.app_version_redis_key % lang
        app = None
        try:
            json_str = redis_master.hget(key, bundle_id)
            app = cjson.decode(json_str)
        except: pass
        return app

    def get_app_cache(self, object_id, refresh_cache=False):
        """
        获取应用缓存
        """
        cache_key = self.app_info_redis_key % language_to_dbname(self.request_language)
        try:
            json_str = redis_master.hget(cache_key, object_id)

            if not json_str or refresh_cache is True:
                self.set_app_cache(object_id)
                json_str = redis_master.hget(cache_key, object_id)
            data = json.loads(json_str)
            try:
                data['ipaHistoryDownloads']['jb'] = sort_dict_keys(data['ipaHistoryDownloads']['jb'])
            except:
                pass
            try:
                data['ipaHistoryDownloads']['signed'] = sort_dict_keys(data['ipaHistoryDownloads']['signed'])
            except:
                pass
            data['cacheKey'] = cache_key
            return convertAppIpaHashToIpaURL(data)
        except Exception, ex:
            traceback.print_exc()

        return None

    def filter_app_output(self, data):
        try:
            data['icon'] = artworkUrl512_to_114_icon(data['artworkUrl512'])
        except:
            data['icon'] = artworkUrl512_to_114_icon(data['artworkUrl100'])

        filter_fields = ['contentAdvisoryRating', 'trackCensoredName', 'artworkUrl512', 'artistId', 'userRatingCountForCurrentVersion',
             'artworkUrl60', 'averageUserRatingForCurrentVersion', 'sellerUrl', 'artworkUrl100', 'wrapperType', 'supportedDevices', 
            'isGameCenterEnabled', 'features', 'formattedPrice', 'primaryGenreName', 'trackContentRating', 'artistName', 'kind']

        data['ID'] = str(data['_id'])
        del data['_id']

        try:
            data['fileSizeBytes'] = int(data['fileSizeBytes'])
            data['size'] = file_size_format(data['fileSizeBytes'])
        except: 
            data['size'] = ''

        for field in filter_fields:
            try:
                del data[field]
            except: pass

        return data

    def get_base_apps(self, where, sort=None, page=1, page_size=10):
        """
        获取应用基本数据
        """
        m = mongo_db.AppBase.find(where)
        count = m.count()
        total_page = int(math.ceil(count / float(page_size)))
        offset = (page - 1) * page_size
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page

        res = m.skip(offset).limit(page_size)
        if sort is not None:
            res.sort(sort[0], sort[1])
        if res:
            res = list(res)

        return res, {'count': count, 'page': page, 'total_page': total_page, \
                     'prev_page': prev_page, 'next_page': next_page}

    def get_apps(self, where, lang, sort=None, limit=600):
        """
        获取应用
        """

        apps = mongo_db.AppBase.find(where).limit(limit).sort(sort[0], sort[1])
        res = []
        collection = 'AppBase_' + lang

        for app in apps:
            try:
                ext_data = mongo_db[collection].find_one({'trackId': app['trackId']})
                if ext_data:
                    app['trackName'] = ext_data['trackName']
            except Exception, ex:
                print ex

            list_data = {}
            try:
                list_data['icon'] = artworkUrl512_to_114_icon(app['artworkUrl512'])
            except:
                list_data['icon'] = ''
            try:
                list_data['trackName'] = app['trackName']
            except:
                list_data['trackName'] = []
            try:
                list_data['averageUserRating'] = app['averageUserRating']
            except:
                list_data['averageUserRating'] = 0

            list_data['bundleId'] = app['bundleId']

            if 'screenshotUrls' in app and len(app['screenshotUrls']) > 0:
                list_data['supportIphone'] = 1
            else:
                list_data['supportIphone'] = 0

            if 'ipadScreenshotUrls' in app and len(app['ipadScreenshotUrls']) > 0:
                list_data['supportIpad'] = 1
            else:
                list_data['supportIpad'] = 0

            try:
                list_data['size'] = file_size_format(app['fileSizeBytes'])
            except:
                list_data['size'] = 'unknown'

            try:
                #从redis中取出最新版本
                key = self.app_version_redis_key % 'EN'
                json_str = redis_master.hget(key, app['bundleId'])
                app_version = cjson.decode(json_str)
                if 'sign' in where and where['sign'] == 1:
                    ipa_version = app_version['ipaVersion']['signed']
                else:
                    ipa_version = app_version['ipaVersion']['jb']
                list_data['version'] = ipa_version
            except:
                list_data['version'] = 'unknown'

            list_data['ID'] = str(app['_id'])

            res.append(list_data)

        return res

    def set_apps_cache(self, genre_id, sort):
        """
        设置应用列表缓存 50页 每页12个
        """
        genre_id = int(genre_id)

        if (7000 <= genre_id < 8000) or (13000 <= genre_id < 14000):
            where = {'review': 1, 'genreIds': {'$all': [str(genre_id)]}}
        else:
            where = {'review': 1, 'primaryGenreId': genre_id}

        for lang in self._get_ext_data_language():
            keys = {}
            keys['iphone_jb_key'] = self.app_list_redis_key % ('iphone', 0, lang, genre_id, self.limit, sort[0])
            keys['iphone_signed_key'] = self.app_list_redis_key % ('iphone', 1, lang, genre_id, self.limit, sort[0])
            keys['ipad_jb_key'] = self.app_list_redis_key % ('ipad', 0, lang, genre_id, self.limit, sort[0])
            keys['ipad_signed_key'] = self.app_list_redis_key % ('ipad', 1, lang, genre_id, self.limit, sort[0])
            
            sign = {'signed': 1, 'jb': 0}

            for s in sign.keys():
                print 'Push to redis, lang:%s, genre: %s, sign: %s' % (lang, genre_id, s)
                #查询签名的
                if sign[s] == 1:
                    where['sign'] = 1
                apps = self.get_apps(where, lang, sort, self.limit)

                redis_master.delete(keys['iphone_'+ s +'_key'])
                redis_master.delete(keys['ipad_'+ s +'_key'])

                for app in apps:
                    data = cjson.encode(app)
                    #ipad兼容iphone应用
                    if app['supportIpad'] == 1 or app['supportIphone'] == 1:
                        redis_master_pipeline.lpush(keys['ipad_'+ s +'_key'], data)
                    if app['supportIphone'] == 1:
                        redis_master_pipeline.lpush(keys['iphone_'+ s +'_key'], data)

            redis_master_pipeline.execute()

    def get_apps_cache(self, device, sign, genre_id, page, sort):
        """
        获取app列表缓存
        """
        key = self.app_list_redis_key % (device, sign, self.request_language, genre_id, self.limit, sort)
        count = redis_master.llen(key)
        if count == 0:
            key = self.app_list_redis_key % (device, sign, self.default_language, genre_id, self.limit, sort)
            count = redis_master.llen(key)
            
        page_size = 12
        total_page = int(math.ceil(count / float(page_size)))
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page

        start = (page - 1) * page_size
        end = start + page_size

        lists = redis_master.lrange(key, start, end-1)
        lists = [cjson.decode(x) for x in lists]
        return {'results': lists,
                'pageInfo': {'count': count, 'page': page, 'totalPage': total_page, 'prevPage': prev_page,
                             'nextPage': next_page}}

    def check_update(self, bundle_id, version, sign):
        """
        检查更新
        """
        results = None
        key = self.app_version_redis_key % 'EN'
        try:
            json_str = redis_master.hget(key, bundle_id)
            app = cjson.decode(json_str)

            if sign == 1:
                ipa_version = app['ipaVersion']['signed']
            else:
                ipa_version = app['ipaVersion']['jb']
            if version_compare(ipa_version, version) == 1:
                if sign == 1:
                    ipa = app['ipaHash']['signed']
                else:
                    ipa = app['ipaHash']['jb']
                
                results = {
                    'ID': app['ID'],
                    'trackName': app['trackName'],
                    'icon': app['icon'],
                    'bundleId': bundle_id, 
                    'ipaURL': create_ipa_url(ipa), 
                    'version': ipa_version,
                    'localVersion': version,
                    'averageUserRating': app['averageUserRating'],
                    'size': app['size'],
                    'update': 1
                }
        except Exception, ex:
            print ex
            pass
        return results

    def _get_ext_data_language(self):
        """
        获取有app数据的语言
        """
        langs = ["CN"]
        return langs

    def get_app_downloads(self, bundle_id):
        """
        获取应用详细信息
        """
        #越狱版
        jb = self.get_downloads(bundle_id, 0)
        #签名版
        signed = self.get_downloads(bundle_id, 1)
        data = {
            #最新版hash值
            'ipaHash': {
                'jb': jb['ipaHash'],
                'signed': signed['ipaHash']
            },
            #最新版本号
            'ipaVersion': {
                'jb': jb['ipaVersion'],
                'signed': signed['ipaVersion']
            },
            #历史下载版本
            'ipaHistoryDownloads': {
                'jb': jb['ipaHistoryDownloads'],
                'signed': signed['ipaHistoryDownloads']
            }
        }
        return data

    def get_downloads(self, bundle_id, sign):

        ipaHash = "" #最新版
        ipaVersion = "" #最新版本号
        ipaHistoryDownloads = "" #历史版本
        #直接下载数据
        download = AppDownloadController()
        res = download.get_by_bundleid(bundle_id, sign)
        tmp_download_list = {}
        if res:
            for down in res:
                try:
                    tmp = {'ipaHash': down['hash'], 'version': down['version'],
                           'addTime': str(down['addTime'])}
                    if down['version'] not in tmp_download_list:
                        tmp_download_list[down['version']] = []
                    tmp_download_list[down['version']].append(tmp)
                except Exception, ex:
                    print ex
                    pass
            try:
                ipaHistoryDownloads = sort_dict_keys(tmp_download_list)
            except Exception, ex:
                print ex
            try:
                key = ipaHistoryDownloads.keys()[0]
                ipaHash = ipaHistoryDownloads[key][0]['ipaHash']
                ipaVersion = ipaHistoryDownloads[key][0]['version']
            except Exception, ex:
                traceback.print_exc()
                pass

        #网盘下载数据
        netdisk = AppDownloadNetDiskController()
        res = netdisk.get_by_bundleid(bundle_id, sign)
        if res:
            for down in res:
                try:
                    tmp = {'webURL': down['downloadUrl'], 'version': down['version'],
                           'addTime': str(down['addTime'])}
                    if down['version'] not in tmp_download_list:
                        tmp_download_list[down['version']] = []
                    tmp_download_list[down['version']].append(tmp)
                except Exception, ex:
                    print ex
                    pass
            try:
                ipaHistoryDownloads = sort_dict_keys(tmp_download_list)
            except Exception, ex:
                print ex

        return {'ipaHash': ipaHash, 'ipaVersion': ipaVersion, 'ipaHistoryDownloads': ipaHistoryDownloads}

    def _sort_items_by_version(self, data):
        '''
        版本比较排序
        '''
        length = len(data)
        if length == 0:
            return data
        for i in range(length - 1):
            for j in range(length - 1):
                if version_compare(data[j]['version'], data[j + 1]['version']) == -1:
                    tmp = data[j]
                    data[j] = data[j + 1]
                    data[j + 1] = tmp
        return data

    def _output_format(self, data):
        """
        整理输出数据格式
        """
        return self._get_request_language_data(super(AppController, self)._output_format(data))

    def _get_request_language_data(self, data):
        """
        获取国别数据
        """
        if self.request_language == '' or self.request_language is None:
            return data

        collection = 'AppExt_' + self.request_language

        ext_data = mongo_db[collection].find_one({'application_id': str(data['trackId'])})

        if not ext_data:
            return data
        try:
            data['description'] = ext_data['description']
        except:
            pass
        try:
            data['trackName'] = ext_data['title']
        except:
            pass
        try:
            data['releaseNotes'] = ext_data['release_notes']
        except:
            pass

        return data

    def get_related_app(self, _id, lang, num=4):
        """
        获取相关文件
        """
        key = 'APP_RELATED_%s_%s' % (lang, _id)
        res = redis_master.get(key)
        if not res:
            app = mongo_db.AppBase.find_one({'_id': ObjectId(_id)})
            genre_id = app['primaryGenreId']
            res = self.get_apps({'primaryGenreId': genre_id, 'review': 1}, lang, ('downloadCount', -1), 100)
            redis_master.set(key, json.dumps(res))
        else:
            res = json.loads(res)
        apps = []
        for i in xrange(0, num):
            apps.append(random.choice(res))
        return apps

    def get_cached_appinfo_count(self, lang='EN'):
        """
        获取缓存的appinfo数量
        """
        cache_key = self.app_info_redis_key % lang
        return redis_master.hlen(cache_key)
    def get_cached_appversion_count(self, lang='EN'):
        """
        获取缓存的appversion数量
        """
        cache_key = self.app_version_redis_key % lang
        return redis_master.hlen(cache_key)
