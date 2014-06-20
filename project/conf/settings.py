#encoding=UTF8
#code by T
#2013-8-19

settings = {
    'new_app_redis': {
        'redis_master': {
            'host': '127.0.0.1',
            'port': 6379,
            'password': 'fuckall'
        },
        'redis_slave': [
            {
                'host': '192.168.2.20',
                'port': 6401,
                'password': 'c00e6ceec1f19205d9528721af24fd5d7948696da0103891adbdc38e45a5a85a'
            },
            {
                'host': '192.168.2.20',
                'port': 6402,
                'password': 'c00e6ceec1f19205d9528721af24fd5d7948696da0103891adbdc38e45a5a85a'
            }
        ]
    },
    'mongodb': {
        'host': 'mongodb://127.0.0.1:27017',
        'ids_name': 'ids'
    },
    'elasticsearch': {
        'host': '127.0.0.1',
        'port': 9200,
        'index': 'appcenter'
    },
    'geoip_data': '/data0/www/appcenter/www/data/GeoIP.dat',
    'pic_upload_dir': './www/static/uploads',
    'pic_url_host': 'http://61.155.215.40:5000/static/uploads',
    'tmp_dir': '/tmp',
    'ipa_dir': './www/static/ipa',
    'download_server_host': 'http://dl.appvv.com',
    'client_url_host': 'http://vvdl.appvv.com',
    'client_upload_dir': './www/static/vshare/download'
}

try: from settings_local import *
except Exception, e: print e.message
