#encoding=UTF8
#code by LP
#2013-11-28

from header import *

class AppGenreController(ControllerBase):

    def __init__(self, language='EN'):
        self._language = language

    def get_list(self, parent_genre=None):

            if parent_genre is None:
                where = {}  
            elif parent_genre == 0:
                #把分类自定义输出为 软件 游戏 杂志
                root_genre=[
                        {
                             "genreName": {
                                           'ZH': u"游戏",
                                           'EN': "Games",
                                           'FR': "Juex",
                                           'ES': "Juegos",
                                           'JP': u"ゲーム"
                                           },
                             "genreId": 6014,
                             'items':[]
                         },
                        {
                             "genreName": {
                                           'ZH': u"软件",
                                           'EN': "Apps",
                                           'FR': "Apps",
                                           'ES': "Aplicaciones",
                                           'JP': u"アプリケーション"
                                           },
                             "genreId": 1000,
                             'items':[]
                         },
                        {
                             "genreName": {
                                           'ZH': u"杂志",
                                           'EN': "Newsstand",
                                           'FR': "Kiosque",
                                           'ES': "Quiosco",
                                           'JP': u"新聞や雑誌"
                                           },
                             "genreId": 6021,
                             'items':[]
                         }
                ]
                where = {'parentGenre':6014}
                game_genre = self._get_genres(where)
                where = {'parentGenre':6021}
                newsstand_genre = self._get_genres(where)
                where = {'parentGenre':{'$nin': [6014, 6021]}, 'genreId':{'$nin':[6014, 6021]}}
                soft_genre = self._get_genres(where)

                output = []
                for item in root_genre:
                    try:
                        item['genreName'] = item['genreName'][self._language]
                    except:
                        item['genreName'] = item['genreName']['EN']
                    if item['genreId'] == 6014:
                        item['items'] = game_genre
                    if item['genreId'] == 6021:
                        item['items'] = newsstand_genre
                    if item['genreId'] == 1000:
                        item['items'] = soft_genre
                    output.append(item)
                return output
            else:
                if parent_genre == 1000:
                    where = {'parentGenre':{'$nin': [6014, 6021]}, 'genreId':{'$nin':[6014, 6021]}}
                else:
                    where = {'parentGenre':int(parent_genre)}

            return self._get_genres(where)

    def _get_genres(self, where):
        try:
            res = mongo_db.app_genre.find(where)

            if not res:
                return []

            output = []
            for item in res:
                try:
                    name = item['genreName'][self._language]
                except:
                    name = item['genreName']['EN']
                try:
                    icon = item['icon_file']
                except:
                    icon = ''
                tmp = {
                   'genreName':name,
                   'genreId':item['genreId'],
                   'icon': create_pic_url(icon),
                   'appCount': 1000
                }
                output.append(tmp)
            return output
        except:
            return []

    def get_apps_count(self, genre_id):
      return 1000,