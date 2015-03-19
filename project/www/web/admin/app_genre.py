#encoding=UTF8
#code by LP
#2014-12-29


import re
import requests
import HTMLParser
from __header__ import (AdminView, FlaskView, DB, route, request,
                        upload_hash_file, settings, redirect, url_for,
                        hash_to_path, create_pic_url_by_path)
from www.controller.app.header import create_pic_url,artworkUrl512_to_114_icon
from flask.ext.login import login_required
import pymongo
import math
from bson import ObjectId

class View(FlaskView):
    route_base = '/genre'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_genre_list')
    @login_required
    def get(self):
        get_genre = request.args.get("get_genre", "6014")  # 默认为游戏
        if get_genre == '1000':
            where = {'parentGenre':{'$nin': [6014, 6021]}, 'genreId':{'$nin':[6014, 6021, 36, 1000]}}
            genre_list = list(DB.app_genre.find(where).sort('genre_id', -1))
        else:
            genre_list = list(DB.app_genre.find({"parentGenre":int(get_genre)}).sort('genre_id', -1))

        genre_id = request.args.get("genre_id", "")
        self._view.assign('create_pic_url', create_pic_url)
        self._view.assign('create_pic_url_by_path', create_pic_url_by_path)
        self._view.assign('genre_list', genre_list)
        self._view.assign('get_genre', get_genre)

        return self._view.render('app_genre_list', genre_id=genre_id,genre_list= genre_list)


    @route("/icon", endpoint="admin_genre_icon")
    @login_required
    def show_page(self):
        genre_id = request.args.get("genre_id", "")
        return self._view.render("app_genre_icon", genre_id=genre_id)

    # 点"管理"后触发
    @route("/items", endpoint="admin_genre_items")
    @login_required
    def show_items(self):
        genre_id = request.args.get("genre_id", 0)
        #bundleId = request.args.get("bundleId", "")
        langs = list(DB.client_support_language.find())

        self._view.assign('lang_options', langs)
        self._view.assign('genre_id', genre_id)
        self._view.assign('page', 1)
        return self._view.render("app_genre_items")

    #左边应用列表 点"搜索"  luoluo0
    @route("/items/show", methods=['GET', 'POST'], endpoint="admin_genre_left")
    @login_required
    def show_itemleft(self):
        genre_id = request.args.get("genre_id", 0)
        #bundleId = request.args.get("bundleId", "")
        trackId = request.args.get("trackId",0)

        page= int(request.args.get("page",1))
        langs = list(DB.client_support_language.find())

        print genre_id,'genre_id'

        if genre_id:
            page_size = 12
            #count = DB.AppBase.find({"genreIds": {"$all": [genre_id]}}).count()
            count = DB.AppBase.find({'review': 1}).count()
            total_page = int(math.ceil(count / float(page_size)))
            prev_page = (page - 1) if page - 1 > 0 else 1
            next_page = (page + 1) if page + 1 < total_page else total_page
            #items_list = list(DB.AppBase.find({"genreIds": {"$all": [genre_id]}}).skip((page-1)*page_size).limit(page_size))
            items_list = list(DB.AppBase.find({'review': 1}).sort([('_id',pymongo.DESCENDING)]).skip((page-1)*page_size).limit(page_size))
        else:
            #items_list = list(DB.AppBase.find({'bundleId':bundleId}))
            items_list = list(DB.AppBase.find({'trackId':int(trackId)}))
            count = total_page = prev_page = next_page = 1

        for item in items_list:
            item['icon'] = artworkUrl512_to_114_icon(item['artworkUrl512'])
        self._view.assign('lang_options', langs)
        self._view.ajax_response('success', 'message')
        return self._view.ajax_render("app_genre_ajaxleft",items_list=items_list,total_page=total_page,count=count,prev_page=prev_page,next_page=next_page,genre_id=genre_id)

    @login_required
    def post(self):
        genre_id = request.form["genre_id"]
        if request.files["icon"].filename != '':
            icon = request.files["icon"]
            hash_str, abs_save_file, save_file = upload_hash_file(icon, settings["pic_upload_dir"])
            DB.app_genre.update({'genreId': int(genre_id)}, {'$set':{"icon_file": save_file}}, upsert=True)
        return redirect(url_for("admin_genre_list"))


class ItemAddView(View):
    '''
    # 点"添加"后触发  luoluo0
    '''
    @route('/item/add', methods=['GET', 'POST'], endpoint='app_genre_item_add')
    @login_required
    def add_items(self):
        try:
            langs = DB.client_support_language.find()
            self._view.assign('lang_options', list(langs))
            bundleId = request.args.get('bundleId', '')
            languages = request.args.get('language', 'en').split(',')
            device_sign = request.args.get('device_sign', '').split(':')
            sort = request.args.get('sort', 'sort').split('*')
            genre_id = request.args.get("genre_id", 0)
            order = int(request.args.get('order', 0))

            upd = int(request.args.get('update', 0))
            itemId = request.args.get('itemId', 0)

            appinfo = dict(DB.AppBase.find_one({'bundleId':bundleId}))
            ID = list(DB.AppBase.find({'bundleId':bundleId}))[0]['_id']

            appkeys = []
            mylanguage = []
            [mylanguage.append(language) for language in languages if language in ['zh-Hans', 'ar']]
            [mylanguage.append('en') for language in languages if language not in ['zh-Hans', 'ar']]
            [appkeys.append("%s_%s_%s_%s" % (ds, la, genre_id, so)) for ds in device_sign for la in set(mylanguage) for so in sort]

            try: appinfo['icon'] = artworkUrl512_to_114_icon(appinfo['artworkUrl512'])
            except: appinfo['icon'] = ''
            if 'screenshotUrls' in appinfo and len(appinfo['screenshotUrls']) > 0: appinfo['supportIphone'] = 1
            else: appinfo['supportIphone'] = 0
            if 'ipadScreenshotUrls' in appinfo and len(appinfo['ipadScreenshotUrls']) > 0: appinfo['supportIpad'] = 1
            else: appinfo['supportIpad'] = 0
            try: appinfo['size'] = file_size_format(appinfo['fileSizeBytes'])
            except: appinfo['size'] = 'unknown'
            try: int(appinfo['averageUserRating'])
            except: appinfo['averageUserRating'] = 3


            if upd:
                DB.AppKeylists.remove({'_id':ObjectId(itemId)})
            for appkey in appkeys:
                hasfind = DB.AppKeylists.find({"appKey" : appkey,
                            "bundleId" : bundleId,
                            "trackName" : appinfo["trackName"],
                            "supportIpad" :appinfo['supportIpad'] ,
                            "supportIphone" : appinfo['supportIphone'],
                            "icon" :appinfo['icon'] ,
                            "averageUserRating" : appinfo["averageUserRating"],
                            "size" : appinfo["size"],
                            "ID":ID
                        }).count()
                if not hasfind:
                    DB.AppKeylists.insert({"appKey" : appkey,
                                "bundleId" : bundleId,
                                "trackName" : appinfo["trackName"],
                                "supportIpad" :appinfo['supportIpad'] ,
                                "supportIphone" : appinfo['supportIphone'],
                                "icon" :appinfo['icon'] ,
                                "averageUserRating" : appinfo["averageUserRating"],
                                "size" : appinfo["size"],
                                "order" : order,
                                "ID":ID
                            })
            status, message = 'success', ''
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message, '')


class ItemListView(View):
    '''
    右边应用列表  luoluo0
    '''
    @route('/item/list', methods=['GET', 'POST'], endpoint='admin_genre_right')
    @login_required
    def show_itemright(self):
        sort = request.args.get("sort", "sort")
        language = request.args.get("language", "all") if request.args.get("language", "all") in ['zh-Hans','en', 'ar','all'] else 'en'
        device = request.args.get("device", "iphone_1")
        genre_id = request.args.get("genre_id", 0)
        appkey= request.args.get("appkey",0)
        page= int(request.args.get("pagerig",1))
        langs = list(DB.client_support_language.find())  # by 0317 17:32

        #appkey = re.compile(r'^%s.*%s_%s_%s$' % (device, language,genre_id, sort))
        if not appkey:
            appkey = '%s_%s_%s_%s' % (device, language,genre_id, sort)

        page_size = 12
        if language=='all' or '_all_' in appkey:
            appkey = '%s_.*_%s_%s'  % (device,genre_id, sort)

        count = DB.AppKeylists.find({'appKey':re.compile(appkey)}).count()
        total_page = int(math.ceil(count / float(page_size)))
        prev_page = (page - 1) if page - 1 > 0 else 1
        next_page = (page + 1) if page + 1 < total_page else total_page
        item_list = list(DB.AppKeylists.find({'appKey':re.compile(appkey)}).sort([('order',pymongo.DESCENDING)]).skip((page-1)*page_size).limit(page_size))

        #item_list = list(DB.AppKeylists.find({'appKey':appkey}).sort([('order',pymongo.DESCENDING)]))
        for item in item_list:
            item['trackId'] = list(DB.AppBase.find({'bundleId':item['bundleId']}))[0]['trackId']

        self._view.ajax_response('success', 'message')
        return self._view.ajax_render('app_genre_ajaxright',item_list=item_list,langs=langs,appkey=appkey,total_pagerig=total_page,countrig=count,prev_pagerig=prev_page,next_pagerig=next_page,genre_id=genre_id)   # P0ST
        #return self._view.render('app_genre_ajaxright',item_list=item_list)  #  GET


class DeleteView(View):
    '''
    app collection delete  luoluo0
    '''
    @route('/item/delete', methods=['GET'], endpoint='app_genre_item_delete')
    @login_required
    def delete_items(self):
        try:
            bundleId = request.args.get('bundleId')
            id = request.args.get('id', 0)
            DB.AppKeylists.remove({'_id':ObjectId(id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)


class SyncView(View):
    @route('/sync', endpoint='admin_genre_sync')
    @login_required
    def get(self):
        countries = {'EN': 'us', 'ZH': 'cn', 'RU': 'ru', 'FR': 'fr', 'ES': 'es', 'JP': 'jp'}
        url = 'https://itunes.apple.com/%s/genre/ios/id36?mt=8'
        message = '同步完成'
        status = 'success'
        for language in countries.keys():
            country = countries[language]
            try:
                res = requests.get(url % country)
            except Exception, ex:
                message = '同步失败: %s' % ex
                status = 'error'
                continue
            for genre_id, genre_name in  re.findall(r'''<a\s+href="https:\/\/itunes\.apple\.com\/%s\/genre\/[a-zA-Z0-9\-]+\/id([0-9]+?)\?mt=8"\s+class="top\-level\-genre"\s+title=".+?">(.+?)<\/a>''' % country, res.content):
                try:
                    self._save(language, genre_id, genre_name, 36)
                except Exception, ex:
                    message = '同步失败: %s' % ex
                    status = 'error'
            for parent_genre_id, html in re.findall(r'id([0-9]+?)\?mt=8"\s+class="top\-level\-genre"\s+title="[^<]+?">[^<]+?<\/a><ul.*?>(.+?)<\/ul>', res.content):
                for genre_id, genre_name in re.findall(r'<a\s+href="https:\/\/itunes\.apple\.com\/%s\/genre\/[a-zA-Z0-9\-]+\/id([0-9]+?)\?mt=8"\s+title=".*?">(.*?)<\/a>' % country, html):
                    self._save(language, genre_id, genre_name, parent_genre_id)
        return self._view.ajax_response(status, message)

    def _save(self, language, genre_id, genre_name, parent_genre_id):
        h = HTMLParser.HTMLParser()
        genre_id = int(genre_id)
        try:
            genre_name = h.unescape(genre_name)
        except:
            pass
        r = DB.app_genre.find_one({'genreId': genre_id})
        if not r:
            data = {'genreId': genre_id, 'genreName':{language:genre_name}, 'parentGenre':int(parent_genre_id)}
            DB.app_genre.insert(data)
        else:
            r['genreName'][language] = genre_name
            genre_name = r['genreName']
            data = {'genreName': genre_name}
            DB.app_genre.update({'genreId': genre_id}, {'$set':data})
        #insert visual genre
        DB.app_genre.update({'genreId':36}, {'$set': {'genreId': 36, 'genreName':{'RU': 'All', 'FR': 'All', 'ZH': '全部', 'EN': 'All', 'JP': 'All', 'ES': 'All'}, 'parentGenre': 0}}, upsert=True)
        DB.app_genre.update({'genreId':1000}, {'$set': {'genreId': 1000, 'genreName':{'RU': 'All', 'FR': 'All', 'ZH': '全部', 'EN': 'All', 'JP': 'All', 'ES': 'All'}, 'parentGenre': 36}}, upsert=True)
        DB.app_genre.update({'genreId':6014}, {'$set': {'genreId': 6014, 'genreName':{'RU': 'All', 'FR': 'All', 'ZH': '全部', 'EN': 'All', 'JP': 'All', 'ES': 'All'}, 'parentGenre': 36}}, upsert=True)
        DB.app_genre.update({'genreId':6021}, {'$set': {'genreId': 6021, 'genreName':{'RU': 'All', 'FR': 'All', 'ZH': '全部', 'EN': 'All', 'JP': 'All', 'ES': 'All'}, 'parentGenre': 36}}, upsert=True)


