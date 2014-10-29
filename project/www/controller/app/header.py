#encoding=UTF8
#code by LP
#2013-11-4

import time
import re
import datetime
import pygeoip
import base64
import hashlib
from distutils.version import LooseVersion
from conf.settings import settings
from common.ng_mongo import NGMongoConnect
from common.ng_redis import NGRedis
from collections import OrderedDict

mongo = NGMongoConnect(settings['mongodb']['host'], replica_set=settings["mongodb"].get("replica_set", None))
mongo_db = mongo.get_database('appcenter')

redis = NGRedis(settings['new_app_redis'])
redis_master = redis.get_redis(source=True)
redis_master_pipeline = redis_master.pipeline()


class ControllerBase(object):

    def _output_format(self, data):
        '''
        整理输出数据格式
        '''

        if data == None:
            return ''
        try:
            del data['_id']
        except:
            pass

        for key in data.keys():
            if isinstance(data[key], datetime.datetime):
                data[key] = str(data[key])

        return data


def language_code_format(code):
    langs = {
        'JP': 'JA',
        'CN': 'ZH',
    }
    return langs[code] if code in langs else code


def hash_to_path(s):
    '''
    hash to path
    '''
    return '%s/%s/%s/%s/%s' % (s[0:2], s[2:4], s[4:6], s[6:8], s[8:])

def get_hash(strings, type='sha1'):
    """
    hash  strings
    """
    import hashlib
    if type == 'md5':
        return hashlib.md5(strings).hexdigest()
    return hashlib.sha1(strings).hexdigest()


def sha1_of_file(filepath):
    """
    file to sha1
    """
    import hashlib
    with open(filepath, 'rb') as f:
        return hashlib.sha1(f.read()).hexdigest()


def create_pic_url(path):
    '''
    create pic url
    '''
    if path.startswith('http'):
        return path
    if path.startswith('#IMG_HOST#'):
        return path.replace('#IMG_HOST#', settings['pic_url_host']+'/')
    return '%s/%s' % (settings['pic_url_host'], path)

def create_pic_url_by_path(path):
    return '%s/%s' % (settings['pic_url_host'], path)

def create_ipa_url(hash_str):

    return build_download_url(settings['download_server_host'], hash_str, 'fuck2088y33oumei', 172800)

def build_download_url(host,  hash_str, secret, expire):
    '''
    构造下载地址
    '''

    expire = int(time.time()) + expire
    file_path = '/%s.ipa' % hash_str
    md5_str = secret + file_path + str(expire)
    obj = hashlib.md5()
    obj.update(md5_str)
    md5_str = obj.digest()
    md5_str = base64.encodestring(md5_str)
    md5_str = md5_str.replace('+', '-').replace('/','_').replace('=', '').strip()
    
    return '%s%s?st=%s&e=%s' % (host, file_path, md5_str, expire) 

def artworkUrl512_to_175_icon(artworkUrl512):
    '''
    artworkUrl512 icon file to 175px icon
    '''
    return re.sub(r"(.*?)\.png$", r"\1.175x175-75.png", artworkUrl512)


def artworkUrl512_to_114_icon(artworkUrl512):
    '''
    artworkUrl512 icon file to 114px icon
    '''
    return re.sub(r"(.*?)\.png$", r"\1.114x114-75.png", artworkUrl512)


def version_compare(version1, version2):
    """
    版本比较
    """
    if LooseVersion(version1) < LooseVersion(version2):
        return -1
    elif LooseVersion(version1) == LooseVersion(version2):
        return 0
    elif LooseVersion(version1) > LooseVersion(version2):
        return 1


def sort_items(data):
    '''
    items排序
    '''
    length = len(data)
    if length == 0:
        return data
    for i in range(len(data) - 1):
        for j in range(len(data) - 1):
            if (data[j]['sort'] < data[j+1]['sort']):
                tmp = data[j]
                data[j] = data[j+1]
                data[j+1] = tmp
    return data

def sort_downloads(data):
    '''
    items排序
    '''
    length = len(data)
    if length == 0: return data
    return sorted(
        data,
        key = lambda x: (LooseVersion('0' if x.get('version', '') == "" else x["version"]), x.get("addTime", datetime.datetime(2013,1,1))),
        reverse=True
    )

def sort_dict_keys(data):
    '''
    items排序
    '''
    new_data = OrderedDict()
    for key in sorted(data, version_compare, reverse=True):
        new_data[key] = data[key]
    return new_data

def get_country_code(ip):
    '''
    根据ip获取国家代码
    '''
    code = 'US'
    if ip == None:
        return code
    try:
        gi4 = pygeoip.GeoIP(settings['geoip_data'], pygeoip.MEMORY_CACHE)
        code2 = gi4.country_code_by_addr(ip)
        if code2 != '':
            code = code2
    except:
        pass
    return code if code != 'CN' else 'ZH'

def file_size_format(size_byte):
    return '%.2fMB' % (int(size_byte) / 1024.0 / 1024)

def datetime_format(date_time):
    return date_time.strftime('%Y-%m-%d')

def convertAppIpaHashToIpaURL(app):
    if type(app["ipaHash"])== str:
        try:
            ipa = create_ipa_url(app['ipaHash'])
        except:
            ipa = None
        app['ipaDownloadUrl'] = ipa
    else:
        try:
            jb = create_ipa_url(app['ipaHash']['jb'])
        except:
            jb = None
        try:
            signed = create_ipa_url(app['ipaHash']['signed'])
        except:
            signed = None
        app['ipaDownloadUrl'] = {
            'jb': jb,
            'signed': signed
        }

    try:
        for key in app['ipaHistoryDownloads']['jb'].keys():
            tmp = app['ipaHistoryDownloads']['jb'][key]
            items = []
            for down in tmp:
                ipa_hash = down.get('ipaHash', None)
                if ipa_hash:
                    down['ipaDownloadUrl'] = create_ipa_url(ipa_hash)
                items.append(down)
            app['ipaHistoryDownloads']['jb'][key] = items
    except:
        pass

    try:
        for key in app['ipaHistoryDownloads']['signed'].keys():
            tmp = app['ipaHistoryDownloads']['signed'][key]
            items = []
            for down in tmp:
                ipa_hash = down.get('ipaHash', None)
                if ipa_hash:
                    down['ipaDownloadUrl'] = create_ipa_url(ipa_hash)
                items.append(down)
            app['ipaHistoryDownloads']['signed'][key] = items
    except:
        pass
    return app

def language_to_dbname(language):
    result = {"zh-Hans": "CN"}
    return result.get(language, "CN")
