#!/usr/bin/env python
# encoding: utf-8


import pytz
import datetime
from www.controller.app.header import mongo_db

E_SUCESSS_UPDATED = 1000  # The update is successful
E_FAILURE_UPDATE = 2000   # Update failed


class LimitAppProcess(object):

    """Docstring for AppProcess. """

    def finish_process(self, track_id, bundle_version, apple_account):

        if apple_account:
            storage_time = datetime.datetime.now(pytz.timezone('Asia/Shanghai'))
            conditions = {'track_id': track_id, 'new_version': bundle_version}

            sets = {'apple_account': apple_account,
                    'local_version': bundle_version,
                    'new_version': bundle_version}
            try:
                # update
                conditions['apple_account'] = {'$exists': True}
                sets['status'] = 'updated'
                process1 = mongo_db.limit_app_process.update(conditions, {'$set': sets})
                sets['storage_time'] = storage_time
                log1 = mongo_db.limit_app_process_log.update(conditions, {'$set': sets})
                # buy
                conditions['apple_account'] = {'$exists': False}
                sets['status'] = 'bought'
                sets.pop('storage_time')
                process2 = mongo_db.limit_app_process.update(conditions, {'$set': sets})
                sets['storage_time'] = storage_time
                log2 = mongo_db.limit_app_process_log.update(conditions, {'$set': sets})
                if process1['nModified'] == 1 and log1 == 1:
                    return E_SUCESSS_UPDATED
                if process2['nModified'] == 1 and log2 == 1:
                    return E_SUCESSS_UPDATED
                return E_FAILURE_UPDATE
            except:
                return E_FAILURE_UPDATE
        else:
            return E_FAILURE_UPDATE
