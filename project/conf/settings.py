#encoding=UTF8
#code by T
#2013-8-19

settings = {
    'new_app_redis': {
        'redis_master': {
            'host': '192.168.16.70',
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
        'host': 'mongodb://192.168.16.112:27017',
        'ids_name': 'ids'
    },
    'elasticsearch': {
        'host': '192.168.16.112',
        'port': 9200,
        'index': 'appcenter'
    },
    'geoip_data': '/home/www/pcl/appcenter/www/data/GeoIP.dat',
    'pic_upload_dir': './www/static/uploads',
    'pic_url_host': 'http://127.0.0.1:5000/static/uploads',
    'tmp_dir': '/tmp',
    'ipa_dir': './www/static/ipa',
    'client_url_host': 'http://vvdl.appvv.com',
    'client_upload_dir': './www/static/vshare/download'
}

try: from settings_local import *
except Exception, e: print e.message
