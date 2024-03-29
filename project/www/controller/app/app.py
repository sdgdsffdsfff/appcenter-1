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
from conf.settings import settings
from collections import defaultdict

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

    def __init__(self, language='en'):
        #语言
        self.request_language = language_code_format(language)
        self._language = language

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

    def get_app_detail(self, object_id, vv_version="common"):
        data = mongo_db.AppBase.find_one({'_id': ObjectId(object_id)})
        if self._language == "zh-Hans":
            data_cn = mongo_db.AppBase_CN.find_one({'bundleId': data.get('bundleId', "")})
            if data_cn:
                data_cn["_id"] = data["_id"]
                data_cn["cnname"] = data.get("cnname", "")
                data.update(data_cn)
            data["trackName"] = data["trackName"] if data.get("cnname", "") == "" else data["cnname"]
        elif self._language == "ar":
            data["trackName"] = data["trackName"] if data.get("arname", "") == "" else data["arname"]
        data = self.filter_app_output(data)

        downloads = self.get_app_downloads(data['bundleId'], vv_version)
        data['systemRequirements'] = "ios" + data.get("minimumOsVersion", "6.0") + "+"
        try: rating = data['averageUserRating']
        except: rating = 0
        try: size = file_size_format(data['fileSizeBytes'])
        except: size = 'unknown'
        try: download_version = downloads['ipaVersion']
        except: download_version = {'jb':'0', 'signed': '0'}
        dict_merged = dict(downloads, **data)
        data = dict_merged
        try: data['ipaHistoryDownloads']['jb'] = sort_dict_keys(data['ipaHistoryDownloads']['jb'])
        except:pass
        try:data['ipaHistoryDownloads']['signed'] = sort_dict_keys(data['ipaHistoryDownloads']['signed'])
        except: pass
        ipadScreenshotUrls = [
            isu.replace("#IMG_HOST#", settings["pic_url_host"] + "/") for isu in data["ipadScreenshotUrls"]]
        screenshotUrls = [
            isu.replace("#IMG_HOST#", settings["pic_url_host"] + "/") for isu in data["screenshotUrls"]]
        data["ipadScreenshotUrls"] = ipadScreenshotUrls
        data["screenshotUrls"] = screenshotUrls
        app_info_result =  convertAppIpaHashToIpaURL(data)
        superurl = data.get("superurl", "").strip()
        superurl_sign = data.get("superurl_sign", "").strip()
        if superurl != "": app_info_result["ipaDownloadUrl"]["jb"] = superurl
        if superurl_sign != "": app_info_result["ipaDownloadUrl"]["signed"] = superurl_sign
        return app_info_result

    def set_app_cache(self, object_id):
        """
        设置应用缓存
        """
        try:
            data = mongo_db.AppBase.find_one({'_id': ObjectId(object_id)})
            if self._language == "zh-Hans":
                data_cn = mongo_db.AppBase_CN.find_one({'bundleId': data.get('bundleId', "")})
                if data_cn:
                    data_cn["_id"] = data["_id"]
                    data = data_cn
            data = self.filter_app_output(data)
            downloads = self.get_app_downloads(data['bundleId'])
            for lang in self._get_ext_data_language():
                data['systemRequirements'] = "ios" + data.get("minimumOsVersion", "6.0") + "+"
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
            ipadScreenshotUrls = [
                isu.replace("#IMG_HOST#", settings["pic_url_host"] + "/") for isu in data["ipadScreenshotUrls"]]
            screenshotUrls = [
                isu.replace("#IMG_HOST#", settings["pic_url_host"] + "/") for isu in data["screenshotUrls"]]
            data["ipadScreenshotUrls"] = ipadScreenshotUrls
            data["screenshotUrls"] = screenshotUrls
            return convertAppIpaHashToIpaURL(data)
        except Exception, ex:
            traceback.print_exc()

        return None

    def filter_app_output(self, data):
        try:
            data['icon'] = artworkUrl512_to_114_icon(data['artworkUrl512'])
        except:
            data['icon'] = artworkUrl512_to_114_icon(data.get('artworkUrl100', 'http://pic.api.vshare.com/84/fe/5d/8f/5420fd96434eae6143156820c9b7f61d.png'))

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
        m = mongo_db.AppBase.find(where).sort("sort", -1)
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
        apps = mongo_db.AppBase.find(where, {
            "trackId":1, "trackName": 1, "bundleId": 1, "artworkUrl512": 1,
            "averageUserRating": 1, "screenshotUrls": 1, "ipadScreenshotUrls": 1,
            "fileSizeBytes": 1, "version": 1, 'cnname': 1, 'arname':1
        }).limit(limit).sort(sort[0], sort[1])
        apps = list(apps)
        if "sign" in where and where["sign"] == 1: sign = 1
        else: sign = 0
        bundle_ids = [app["bundleId"] for app in apps if app.get("bundleId", "") != ""]
        downloads = self.get_downloads_of_allbundleids(bundle_ids, sign)
        res = []
        collection = 'AppBase_' + lang
        apps_cn = mongo_db[collection].find({'bundleId': bundle_ids})
        apps_cn_dict = dict()
        for app_cn in apps_cn: apps_cn_dict[app_cn.get("bundleId", "")] = app_cn
        for app in apps:
            ext_data = apps_cn_dict.get(app.get("bundleId", ""), None)
            if ext_data: app['trackName'] = ext_data.get('trackName', app.get('trackName', ''))
            list_data = {}
            list_data['ipaHash'] = downloads[app["bundleId"]]['ipaHash']
            list_data['ipaVersion'] = downloads[app["bundleId"]]['ipaVersion']
            try: list_data['icon'] = artworkUrl512_to_114_icon(app['artworkUrl512'])
            except: list_data['icon'] = ''
            try: list_data['trackName'] = app['trackName']
            except: list_data['trackName'] = []
            try: list_data['averageUserRating'] = app['averageUserRating']
            except: list_data['averageUserRating'] = 0
            list_data['bundleId'] = app['bundleId']
            if 'screenshotUrls' in app and len(app['screenshotUrls']) > 0: list_data['supportIphone'] = 1
            else: list_data['supportIphone'] = 0
            if 'ipadScreenshotUrls' in app and len(app['ipadScreenshotUrls']) > 0:
                list_data['supportIpad'] = 1
            else: list_data['supportIpad'] = 0
            try: list_data['size'] = file_size_format(app['fileSizeBytes'])
            except: list_data['size'] = 'unknown'
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
            keys['iphone_signed_key'] = self.app_list_redis_key % ('iphone', 1, lang,genre_id,self.limit, sort[0])
            keys['ipad_jb_key'] = self.app_list_redis_key % ('ipad', 0, lang, genre_id, self.limit, sort[0])
            keys['ipad_signed_key'] = self.app_list_redis_key % ('ipad', 1, lang, genre_id, self.limit, sort[0])

            sign = {'signed': 1, 'jb': 0}

            for s in sign.keys():
                print 'Push to redis, lang:%s, genre: %s, sign: %s' % (lang, genre_id, s)
                #查询签名的
                if sign[s] == 1: where['sign'] = 1
                apps = self.get_apps(where, lang, sort, self.limit)

                redis_master.delete(keys['iphone_'+ s +'_key'])
                redis_master.delete(keys['ipad_'+ s +'_key'])

                for app in apps:
                    data = cjson.encode(app)
                    if app['supportIpad'] == 1 or app['supportIphone'] == 1:
                        redis_master_pipeline.lpush(keys['ipad_'+ s +'_key'], data)
                    if app['supportIphone'] == 1:
                        redis_master_pipeline.lpush(keys['iphone_'+ s +'_key'], data)
            redis_master_pipeline.execute()

    def set_apps_cache_new(self, genre_id, sort):
        """
        设置应用列表缓存 50页 每页12个  luoluo0
        """
        genre_id = int(genre_id)
        myappkey = ''
        if (7000 <= genre_id < 8000) or (13000 <= genre_id < 14000):
            where = {'review': 1, 'genreIds': {'$all': [str(genre_id)]}}
        else:
            where = {'review': 1, 'primaryGenreId': genre_id}
        larguage = self._language if self._language in ['zh-Hans','en', 'ar'] else 'en'
        for lang in self._get_ext_data_language():
            sign = {'signed': 1, 'jb': 0}
            for s in sign.keys():
                #print 'Push to redis, lang:%s, genre: %s, sign: %s' % (lang, genre_id, s)
                #查询签名的
                if sign[s] == 1: where['sign'] = 1
                else :where['sign'] = 0
                apps = self.get_apps(where, lang, sort, self.limit)

                for app in apps:
                    try:app["order"]
                    except: app["order"] = 0
                    if app['supportIpad'] == 1 or app['supportIphone'] == 1:
                        myappkey = "%s_%s_%s_%s_%s" % ('ipad', where['sign'], larguage, genre_id, sort[0])
                    if app['supportIphone'] == 1:
                        myappkey = "%s_%s_%s_%s_%s" % ('iphone', where['sign'], larguage, genre_id, sort[0])

                    mongo_db.AppKeylists.insert({
                        "appKey" : myappkey,
                        "bundleId" : app["bundleId"],
                        "trackName" : app["trackName"],
                        "supportIpad" : app["supportIpad"],
                        "supportIphone" :app["supportIphone"],
                        "icon" : app["icon"],
                        "averageUserRating" : app["averageUserRating"],
                        "size" : app["size"],
                        "order" : app["order"]
                    })

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
        lists = [convertAppIpaHashToIpaURL(cjson.decode(x)) for x in lists]
        return {
            'results': lists,
            'pageInfo': {
                'count': count, 'page': page, 'totalPage': total_page, 'prevPage': prev_page,
                'nextPage': next_page
            }
        }

    def get_apps_cache_mg(self, device, sign, genre_id, page, sort):
        """
        获取app列表展示  luoluo0
        """
        language = self._language if self._language in ['zh-Hans','en', 'ar'] else 'en'
        key = "%s_%s_%s_%s_%s" % (device, sign, language, genre_id, sort)
        count = mongo_db.AppKeylists.find({'appKey':key}).count()

        page_size = 12 # 每页显示12行
        total_page = int(math.ceil(count / float(page_size)))
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page

        lists1 = list(mongo_db.AppKeylists.find(
            {'appKey':key},
            {'appKey':0,'order':0}
        ).sort([('order',pymongo.DESCENDING)]).skip((page-1)*page_size).limit(page_size))

        bundleIdlist = [i['bundleId'] for i in lists1 if 'bundleId' in i]
        download = AppDownloadController()
        ipaHashdic = download.get_by_bundleids(bundleIdlist)
        ipaHashlist = [i[0] for i in ipaHashdic.values()]

        for i in lists1:
            i['ID'] = str(i['_id'])
            del i['_id']
            for x in ipaHashlist:
                if i['bundleId'] == x['bundleId']:
                    i['ipaHash'] = str(x['hash'])
                    i['ipaVersion'] = x.get('version', '1.0')
        lists = [convertAppIpaHashToIpaURL(x) for x in lists1]
        return {
            'results': lists,
            'pageInfo': {
                'count': count, 'page': page, 'totalPage': total_page, 'prevPage': prev_page,
                'nextPage': next_page
            }
        }

    def check_update_by_all(self, local_packages, sign):
        app_downloads = mongo_db.AppDownload.find({"bundleId": {"$in": local_packages.keys()}, "sign": sign})
        app_downloads = list(app_downloads)
        results = {}
        to_update_bundleids = []
        max_app_downloads = {}
        for app_download in app_downloads:
            bundle_id = app_download["bundleId"]
            cur_version = "0" if app_download.get("version", "") == "" else app_download["version"]
            if bundle_id not in max_app_downloads:
                max_app_downloads[bundle_id] = [cur_version, app_download]
            else:
                if version_compare(cur_version, max_app_downloads[bundle_id][0]) == 1:
                    max_app_downloads[bundle_id] = [cur_version, app_download]
        for bundle_id, version_app_download in max_app_downloads.items():
            local_version = local_packages[bundle_id]
            app_download = version_app_download[1]
            ipa_version = version_app_download[0]
            if version_compare(ipa_version, local_version) != 1: continue
            to_update_bundleids.append(bundle_id)
            results[bundle_id] = {
                'ipaDownloadUrl': create_ipa_url(app_download["hash"]),
                'update': 1,
                'bundleId': bundle_id,
                'localVersion': local_version,
                'version': ipa_version,
            }
        app_base = list(mongo_db.AppBase.find({"bundleId": {"$in": to_update_bundleids}}))
        ulti_results = []
        if self._language == "zh-Hans":
            appbase_cn = list(mongo_db.AppBase_CN.find({"bundleId": {"$in": to_update_bundleids}}))
        for app_d in app_base:
            app_d_bundle_id = app_d["bundleId"]
            if app_d_bundle_id  not in results: continue
            results[app_d_bundle_id].update({
                'ID': str(app_d['_id']),
                'trackName': app_d.get('trackName', ''),
                'icon': app_d.get('artworkUrl512', ''),
                'averageUserRating': app_d.get('averageUserRating', 3),
                'size': file_size_format(app_d.get('fileSizeBytes', 1))
            })
            temp_r = results[app_d_bundle_id]
            if self.request_language == "ZH":
                app_single_cn = None
                for app_single_cn_t in appbase_cn:
                    if app_single_cn_t.get("bundleId", "") == app_d_bundle_id:
                        app_single_cn = app_single_cn_t
                if app_single_cn: temp_r["trackName"] = app_single_cn["trackName"]
            ulti_results.append(temp_r)
        return ulti_results

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

    def get_app_downloads(self, bundle_id, vv_version="common"):
        """
        获取应用详细信息
        """
        all_downloads = self.get_all_downloads(bundle_id, vv_version)
        jb, signed = all_downloads["jb"], all_downloads["sign"]

        # #越狱版
        # jb = self.get_downloads(bundle_id, 0)
        # #签名版
        # signed = self.get_downloads(bundle_id, 1)
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

    def get_downloads_of_allbundleids(self, bundle_ids, sign, vv_version="common"):
        """add by kq for bundle search"""

        download_direct = AppDownloadController()
        reses = download_direct.get_by_bundleids(bundle_ids, sign, vv_version)
        download_netdisk = AppDownloadNetDiskController()
        reses2 = download_netdisk.get_by_bundleids(bundle_ids, sign)

        result_for_download = {}
        for bundle_id in bundle_ids:

            ipaHash = "" #最新版
            ipaVersion = "" #最新版本号
            ipaHistoryDownloads = "" #历史版本
            res = reses.get(bundle_id, None)
            tmp_download_list = {}
            if res:
                for down in res:
                    down_version = "0" if down.get('version', "") == "" else down["version"]
                    try:
                        tmp = {
                            'ipaHash': down['hash'],
                            'version': down_version,
                            'addTime': str(down['addTime'])
                        }
                        if down_version not in tmp_download_list:
                            tmp_download_list[down_version] = []
                        tmp_download_list[down_version].append(tmp)
                    except Exception, ex: continue
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
            res2 = reses2.get(bundle_id, None)
            if res2:
                for down in res2:
                    try:
                        tmp = {
                            'webURL': down['downloadUrl'],
                            'version': down['version'],
                            'addTime': str(down['addTime'])
                        }
                        if down['version'] not in tmp_download_list:
                            tmp_download_list[down['version']] = []
                        tmp_download_list[down['version']].append(tmp)
                    except Exception, ex: continue
                try:
                    ipaHistoryDownloads = sort_dict_keys(tmp_download_list)
                except Exception, ex:
                    print ex
            result_for_download[bundle_id] = {
                'ipaHash': ipaHash, 'ipaVersion': ipaVersion,
                'ipaHistoryDownloads': ipaHistoryDownloads
            }
        return result_for_download

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
                    d_version = "1.0" if down.get("version", "") == "" else down["version"]
                    tmp = {
                        'ipaHash': down['hash'], 'version': d_version,
                        'addTime': str(down['addTime'])
                    }
                    if d_version not in tmp_download_list:
                        tmp_download_list[d_version] = []
                    tmp_download_list[d_version].append(tmp)
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
        if len(res) < num:
            res_len = len(res)
        else:
            res_len = num
        for i in xrange(0, res_len):
            try:
                apps.append(random.choice(res))
            except IndexError:
                pass
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

    def _extract_direct_download_info(self, downloads):
        tmp_download_list = defaultdict(list)
        for down in downloads:
            d_version = "1.0" if down.get("version", "") == "" else down["version"]
            tmp_download_list[d_version].append({
                'ipaHash': down.get('hash', ''),
                'version': d_version,
                'addTime': str(down['addTime'])
            })
        try: ipaHistoryDownloads = sort_dict_keys(tmp_download_list)
        except Exception, ex: ipaHistoryDownloads = tmp_download_list
        try:
            key = ipaHistoryDownloads.keys()[0]
            ipaHash = ipaHistoryDownloads[key][0]['ipaHash']
            ipaVersion = ipaHistoryDownloads[key][0]['version']
        except:
            ipaHash, ipaVersion = "", ""
        return {
            'ipaHash': ipaHash, 'ipaVersion': ipaVersion,
            'ipaHistoryDownloads': ipaHistoryDownloads,
            "tmp_download_list": tmp_download_list
        }

    def _extract_netdisk_download_info(self, downloads, direct_download_list):
        for down in downloads:
            d_version = "1.0" if down.get("version", "") == "" else down["version"]
            direct_download_list[d_version].append({
                'webURL': down.get('downloadUrl', ''),
                'version': d_version,
                'addTime': str(down['addTime'])
            })
        try:
            ipaHistoryDownloads = sort_dict_keys(direct_download_list)
        except:
            ipaHistoryDownloads = tmp_download_list
        return {'ipaHistoryDownloads': ipaHistoryDownloads}

    def get_all_downloads(self, bundle_id, vv_version="common"):
        """取得该应用下的所有下载包"""
        #直接下载数据

        download = AppDownloadController()
        sign_downloads, jb_downloads = download.get_all_downloads_of_app(bundle_id, vv_version)
        sign_downloads_info = self._extract_direct_download_info(sign_downloads)
        jb_downloads_info = self._extract_direct_download_info(jb_downloads)

        netdisk = AppDownloadNetDiskController()
        sign_nd_downloads, jb_nd_downloads = netdisk.get_all_downloads_of_app(bundle_id)
        sign_nd_downloads_info = self._extract_netdisk_download_info(
            sign_nd_downloads, sign_downloads_info["tmp_download_list"])
        jb_nd_downloads_info = self._extract_netdisk_download_info(
            jb_nd_downloads, jb_downloads_info["tmp_download_list"])

        sign_downloads_info["ipaHistoryDownloads"] = sign_nd_downloads_info["ipaHistoryDownloads"]
        jb_downloads_info["ipaHistoryDownloads"] = jb_nd_downloads_info["ipaHistoryDownloads"]
        return {"sign": sign_downloads_info, "jb": jb_downloads_info}
