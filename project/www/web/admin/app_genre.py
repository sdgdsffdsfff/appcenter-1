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


class View(FlaskView):
    route_base = '/genre'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @route('/list', endpoint='admin_genre_list')
    @login_required
    def get(self):
        genre_list = DB.app_genre.find().sort('genre_id', -1)
        genre_id = request.args.get("genre_id", "")

        self._view.assign('create_pic_url', create_pic_url)
        self._view.assign('create_pic_url_by_path', create_pic_url_by_path)
        self._view.assign('genre_list', genre_list)
        return self._view.render('app_genre_list', genre_id=genre_id)

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
        bundleId = request.args.get("bundleId", "")
        page= int(request.args.get("page",1))
        langs = list(DB.client_support_language.find())

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
            items_list = list(DB.AppBase.find({'bundleId':bundleId}))
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


            appinfo = dict(DB.AppBase.find_one({'bundleId':bundleId}))
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
            for appkey in appkeys:
                DB.AppKeylists.update({"appKey" : appkey}, {"$set": {
                            "bundleId" : bundleId,
                            "trackName" : appinfo["trackName"],
                            "supportIpad" :appinfo['supportIpad'] ,
                            "supportIphone" : appinfo['supportIphone'],
                            "icon" :appinfo['icon'] ,
                            "averageUserRating" : appinfo["averageUserRating"],
                            "size" : appinfo["size"],
                            "order" : order
                        }}, True)
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
        language = request.args.get("language", "en") if request.args.get("language", "en") in ['zh-Hans','en', 'ar'] else 'en'
        device = request.args.get("device", "iphone_1")
        genre_id = request.args.get("genre_id", 0)
        #appkey = re.compile(r'^%s.*%s_%s_%s$' % (device, language,genre_id, sort))
        appkey = '%s_%s_%s_%s' % (device, language,genre_id, sort)
        item_list = list(DB.AppKeylists.find({'appKey':appkey}).sort([('order',pymongo.DESCENDING)]))
        self._view.ajax_response('success', 'message')
        return self._view.ajax_render('app_genre_ajaxright',item_list=item_list)   # P0ST
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
            DB.AppKeylists.remove({'bundleId':bundleId})
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


