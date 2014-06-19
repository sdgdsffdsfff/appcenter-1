# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-3-25.

import pymongo, time

old_mongo = pymongo.Connection("192.168.2.20", 27017)
old_db = old_mongo.appdb
new_mongo = pymongo.Connection("192.168.3.228", 50000)
new_db = new_mongo.appcenter


def import_app_download():
    """
    导入老的下载数据到新系统里面
    """
    i = 0
    for down in old_db.app_download.find(timeout=False):
        try:
            data = {
                'addTime': down['addtime'],
                "bundleId": down['bundleid'],
                "version": down['version'],
                "hash": down['hash'],
                "jb": down['jb'],
                "review": down['review']
            }
            new_db.AppDownload.insert(data)
        except Exception, ex:
            print ex
        i += 1
        print i





def export_download_info():
    """
    导入superurl
    """
    i = 0
    f = open('tmp.txt', 'a+')
    for app in old_db.app.find({'review': 1}, timeout=False):
        try:
            f.write("%s\t%s\t%s\t%s\n" % (app['bundleid'], app['download_version'], app['down'], app['superurl']))
        except Exception, ex:
            print ex
        i += 1
        print i

    f.close()

def import_download_info():
    fp = open("./tmp.txt", "r")
    i = 0
    print 'start'
    for line in fp:
        try:
            data = line.replace("\n", '').split("\t")
            bundleid = str(data[0]).strip()
            download_version = data[1]
            down = int(data[2])
            superurl = data[3]
            new_db.AppBase.update({'bundleId': bundleid}, {
                '$set': {'downloadVersion': download_version, 'downloadCount': int(down),
                         'downloadURL': superurl}})
            time.sleep(0.001)
        except Exception, ex:
            print ex
        i += 1
        print i
    fp.close()

import_download_info()