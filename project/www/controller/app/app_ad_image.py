from header import *

class AppAdImageController(ControllerBase):

    def get(self):
        app_ad_images = mongo_db.app_add_image.find({})
        return [{"image_url": aai["image_url"], "link_url": aai["link_url"]} for aai in app_ad_images]
