from header import *
import copy

class OtherAdController(ControllerBase):
    def __init__(self, language='', ip=None, location=None, cs=None):
        self._language = language
        self._cs = cs
        if location is None: self._location = get_country_code(ip)
        else: self._location = location

    def get(self):
        data = {
            "language": self._language,
            "cs": self._cs,
            "location": self._location
        }
        try:
            other_ads = mongo_db.other_ad.find({}, {"_id": 0})
            res = []
            for other_ad in other_ads:
                temp_status1, temp_status2, temp_status3 = 0, 0, 0
                if "all" in other_ad["cses"] or self._cs in other_ad["cses"]: temp_status1 = 1
                if "all" in other_ad["languages"] or self._language in other_ad["languages"]: temp_status2 = 1
                if "all" in other_ad["locations"] or self._location in other_ad["locations"]: temp_status3 = 1
                total_status = temp_status1 & temp_status2 & temp_status3 & int(other_ad["status"])
                data_clone = copy.copy(data)
                data_clone["status"] = total_status
                data_clone["position"] = other_ad["position"]
                data_clone["source"] = other_ad["source"]
                data_clone["data"] = []
                temp_data = other_ad.get("data", [])

                for di in temp_data:
                    if "all" in di.get("locations", []) or self._location in di.get("locations", []):
                        data_clone["data"].append({
                            "name": di["name"],
                            "link_url": di["link_url"],
                            "image_url": create_pic_url_by_path(di.get("url", ""))
                        })
                data_clone["child_positions"] = other_ad["child_positions"]
                res.append(data_clone)
            return res
        except Exception, ex:
            print ex.message
            return []
