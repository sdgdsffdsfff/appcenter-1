#!/usr/bin/env python
# encoding: utf-8


import pytz
import datetime
from www.controller.app.header import mongo_db


class AppProcess(object):

    """Docstring for AppProcess. """

    def finish_process(self, track_id, bundle_version, apple_account):
        storage_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        res = mongo_db.app_process.update(
            {'track_id': track_id,
             'status': 'processing'},
            {'$set': {'apple_account': apple_account,
                      'storage_time': storage_time,
                      'apple_account': apple_account,
                      'status': 'finished',
                      'local_version': bundle_version},
             '$unset': {'new_version': ''}})
        return res['nModified']

    def do_log(self, ptype, track_id, bundle_version, apple_account):
        if ptype == 'buy':
            ptime = 'buy_time'
        elif ptype == 'update':
            ptime = 'update_time'

        storage_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        res = mongo_db.app_process_log.update(
            {'track_id': track_id,
             'status': 'processing',
             ptime: {'$exists': True}},
            {'$set': {'apple_account': apple_account,
                      'storage_time': storage_time,
                      'apple_account': apple_account,
                      'status': 'finished',
                      'local_version': bundle_version},
             '$unset': {'new_version': ''}})
        return res['nModified']
