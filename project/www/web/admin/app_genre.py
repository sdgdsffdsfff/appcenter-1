#encoding=UTF8
#code by LP
#2013-11-8

import re
import requests
import HTMLParser

from __header__ import (AdminView, FlaskView, DB, route, request,
                        upload_hash_file, settings, redirect, url_for,
                        hash_to_path, create_pic_url_by_path)
from www.controller.app.header import create_pic_url
from flask.ext.login import login_required

class View(FlaskView):

    route_base = '/genre'

    def before_request(self, name):
        self._view = AdminView()


class ListView(View):

    @route('/list', endpoint='admin_genre_list')
    @login_required
    def get(self):
        genre_list = DB.app_genre.find().sort('genre_id', -1)
        self._view.assign('create_pic_url', create_pic_url)
        self._view.assign('create_pic_url_by_path', create_pic_url_by_path)
        return self._view.render('app_genre_list', genre_list=genre_list)

    @route("/icon", endpoint="admin_genre_icon")
    @login_required
    def show_page(self):
        genre_id = request.args.get("genre_id", "")
        return self._view.render("app_genre_icon", genre_id=genre_id)

    @login_required
    def post(self):
        genre_id = request.form["genre_id"]
        if request.files["icon"].filename != '':
            icon = request.files["icon"]
            hash_str, abs_save_file, save_file = upload_hash_file(icon, settings["pic_upload_dir"])
            DB.app_genre.update({'genreId': int(genre_id)}, {'$set':{"icon_file": save_file}}, upsert=True)
        return redirect(url_for("admin_genre_list"))


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
