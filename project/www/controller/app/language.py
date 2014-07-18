from header import *

class LanguageController(ControllerBase):

    def get(self):
        languages = mongo_db.client_support_language.find({})
        return [{"code": lang["code"], "name": lang["name"], "nameoflanguage": lang["nameoflanguage"]} for lang in languages]
