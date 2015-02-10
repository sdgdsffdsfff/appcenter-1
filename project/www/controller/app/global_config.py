from header import *

class GlobalConfigController(ControllerBase):

    def get(self):
        global_config = mongo_db.global_config.find({})
        if global_config: return dict()
        else: return global_config[0]["data"]
