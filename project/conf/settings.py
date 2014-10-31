#encoding=UTF8
#code by T
#2013-8-19

settings = {
    'new_app_redis': {
        'redis_master': {
            'host': '54.183.152.170',
            'port': 6379,
            'password': 'jm*7yrt@13'
        },
        'redis_slave': [
            {
                'host': '198.100.110.18',
                'port': 6379,
                'password': 'jm*7yrt@13'
            }
        ]
    },
    'mongodb': {
        'host': '',
        'replica_set': {
            "connection_str": "mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter",
            "replica_set_name": "appvv"
        }
    },
    'elasticsearch': {
        'host': '172.31.7.125',
        'port': 9200,
        'index': 'appcenter'
    },
    'geoip_data': '/data0/www/appcenter/www/data/GeoIP.dat',
    'pic_upload_dir': '/data0/storage/pic',
    'pic_url_host': 'http://pic.api.vshare.com',
    'tmp_dir': '/tmp',
    'ipa_dir': '/data0/storage/down',
    'download_server_host': 'http://dl.appvv.com',
    'client_url_host': 'http://vvdl.appvv.com',
    'client_upload_dir': '/data0/storage/client'
}

DOMAIN_URL = 'http://api.vshare.com'
CACHE_TIME = 60 * 10
APP_PROCESS = {
    'redis_master': {
        'host': '54.183.93.130',
        'port': 7379,
        'password': 'vS!t_rt1@2aT'
    }
}
try: from settings_local import *
except Exception, e: print e.message
