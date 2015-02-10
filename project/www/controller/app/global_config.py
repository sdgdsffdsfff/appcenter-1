from header import *

class GlobalConfigController(ControllerBase):

    def get(self):
        global_config = mongo_db.global_config.find({}, {"_id": 0})
        if global_config.count() == 0: return {}
        return list(global_config)[0]
