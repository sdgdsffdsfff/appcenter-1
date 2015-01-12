from header import *

class AdsLinkController(ControllerBase):

    def get(self):
        links = mongo_db.adslink.find({})
        return [{"ID": lnk["edit_id"], "bundleId": lnk["bundle_id"], "url": lnk["url"]} for lnk in links]
