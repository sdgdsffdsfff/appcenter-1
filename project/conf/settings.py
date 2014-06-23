#encoding=UTF8
#code by T
#2013-8-19

settings = {
    'new_app_redis': {
        'redis_master': {
            'host': '10.2.0.53',
            'port': 6379,
            'password': 'fuckall'
        },
        'redis_slave': [
            {
                'host': '10.2.0.54',
                'port': 6379,
                'password': 'fuckall'
            }
        ]
    },
    'mongodb': {
        'host': 'mongodb://10.2.0.40:27017',
        'ids_name': 'ids'
    },
    'elasticsearch': {
        'host': '10.2.0.40',
        'port': 9200,
        'index': 'appcenter'
    },
    'geoip_data': '/data0/www/appcenter/www/data/GeoIP.dat',
    'pic_upload_dir': './www/static/uploads',
    'pic_url_host': 'http://ios.vshare.com/static/uploads',
    'tmp_dir': '/tmp',
    'ipa_dir': './www/static/ipa',
    'download_server_host': 'http://dl.appvv.com',
    'client_url_host': 'http://vvdl.appvv.com',
    'client_upload_dir': './www/static/vshare/download'
}

try: from settings_local import *
except Exception, e: print e.message
