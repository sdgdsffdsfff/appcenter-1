#!/usr/bin/env python
# encoding: utf-8


import pytz
import datetime
from www.controller.app.header import mongo_db


class AppProcess(object):

    """Docstring for AppProcess. """

    def finish_process(self, track_id, bundle_version, apple_account):
        storage_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
        conditions = {'track_id': track_id, 'new_version': bundle_version}
        sets = {'apple_account': apple_account,
                'local_version': bundle_version,
                'new_version': bundle_version}
        try:
            # update
            conditions['apple_account'] = {'$exists': True}
            sets['status'] = 'updated'
            process1 = mongo_db.app_process.update(conditions, {'$set': sets})
            sets['storage_time'] = storage_time
            log1 = mongo_db.app_process_log.update(conditions, {'$set': sets})
            # buy
            conditions['apple_account'] = {'$exists': False}
            sets['status'] = 'bought'
            sets.pop('storage_time')
            process2 = mongo_db.app_process.update(conditions, {'$set': sets})
            sets['storage_time'] = storage_time
            log2 = mongo_db.app_process_log.update(conditions, {'$set': sets})

            if process1['nModified'] == 1 and log1['nModified'] == 1:
                return 1000
            if process2['nModified'] == 1 and log2['nModified'] == 1:
                return 1000
            return 2000
        except:
            return 2000
