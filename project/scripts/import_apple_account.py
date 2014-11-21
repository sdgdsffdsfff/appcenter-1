# encoding: utf-8


import xlrd
import pymongo

MONGOURL = 'mongodb://appcenter:tuj62_Iga1e4_a@54.183.152.170:37017,54.72.191.195:37017,61.155.215.40:37017/appcenter'
filepath = '/Users/qijianbiao/Downloads/buyed.xlsx'

db = pymongo.MongoClient(MONGOURL).appcenter
editor = 'luohao'

def readxls(filepath):
    book = xlrd.open_workbook(filepath)
    table = book.sheet_by_index(1)

    for row in range(1, table.nrows-1, 1):
        value = table.row_values(row)
        data = {
            'track_id': str(int(value[0])),
            'track_name': str(value[1].encode('utf-8')),
            'price': float(value[2]),
            'new_version': str(value[3]),
            'loacl_version': str(value[3]),
            'apple_account': str(value[4].encode('utf-8')),
            'status': 'finished',
            'currency': 'USD',
            'country': 'US',
            'editor': editor,
            'link_url': 'https://itunes.apple.com/app/id%s' %
            str(int(value[0]))
        }
        print data["track_id"]
        try:
            db.app_process.update({'track_id': data['track_id']}, {'$set': data}, upsert=True)
        except:
            print "error %s" % str(data['track_id'])

readxls(filepath)
