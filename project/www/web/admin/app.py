#encoding=UTF8
#code by LP
#2013-11-8

'''
应用相关操作
'''
import copy
import os
import time
import cjson
import re
import shutil
import requests
from __header__ import AdminView, FlaskView, DB, route, request, session, redirect, url_for
from conf.settings import settings
from www.controller.app.app import AppController
from www.controller.app.header import artworkUrl512_to_114_icon, sha1_of_file, hash_to_path, create_pic_url
from www.lib.form import Form, FormElementField, FormException, FormValidatorAbstract
from bson.objectid import ObjectId

country = ["us", "cn"]

class View(FlaskView):

    route_base = '/app'

    def before_request(self, name):
        self._view = AdminView()
        self.app = AppController()


class ListView(View):

    @route('/list', endpoint='admin_app_list')
    def get(self):
        self._view.assign('search_use', 'default')
        return self._view.render('app_list')

    @route('/ajaxlist', endpoint='admin_app_ajaxlist')
    def ajax(self):
        page = request.args.get('page', 1)
        track_name = request.args.get('trackName', '')
        track_id = request.args.get('trackId', '')
        bundle_id = request.args.get('bundleId', '')
        use = request.args.get('use', 'default')
        version = request.args.get("version", "")

        where = {'review': 1}
        sign = 0
        if version != "":
            sign = 1 if version == "pb" else 0
        if sign == 1: where["sign"] = 1
        if track_name != '':
            regex = re.compile(track_name, re.IGNORECASE)
            where["trackName"] = regex
        if track_id != '':
            where['trackId'] = int(track_id)
        if bundle_id != '':
            where['bundleId'] = bundle_id

        app_list, page_info = self.app.get_base_apps(where, ('sort', -1), int(page), 10)

        query_params = {'trackName': track_name, 'trackId': track_id, 'bundleId': bundle_id, 'use': use,
                        'page': page_info['prev_page']}
        prev_page_params = query_params
        import copy
        query_params2 = copy.copy(prev_page_params)
        query_params2['page'] = page_info['next_page']
        next_page_params = query_params2

        query_params3 = copy.copy(prev_page_params)
        query_params3['page'] = page_info['page']
        current_page_params = query_params3

        if use == 'collection':
            #语言选项
            langs = DB.client_support_language.find()
            self._view.assign('lang_options', list(langs))

            #国家选项
            countries = DB.country.find()
            self._view.assign('country_options', list(countries))
        import urllib
        self._view.assign('use', use)
        self._view.assign('app_list', app_list)
        self._view.assign('page_info', page_info)
        self._view.assign('prev_page_params', urllib.urlencode(prev_page_params))
        self._view.assign('next_page_params', urllib.urlencode(next_page_params))
        self._view.assign('current_page_params', urllib.urlencode(current_page_params))
        self._view.assign('icon', artworkUrl512_to_114_icon)

        return self._view.ajax_render('app_list_ajax')

class SortView(View):
    '''
    排序
    '''
    @route('/sort', methods=['POST'], endpoint='admin_app_sort')
    def do_request(self):
        try:
            for key in request.form:
                _id = key.split("_")[1]
                sort = 0
                if request.form[key] != "":
                    sort = int(request.form[key])
                DB.AppBase.update({'_id':ObjectId(_id)}, {'$set':{'sort': sort}})
            status, message = 'success', '更新排序成功'
        except Exception, ex:
            status, message = 'error', str(ex)
            pass
        return self._view.ajax_response(status, message)

class AddView(View):
    '''
    添加
    '''
    def _init_form(self):
        try:
            self._form = Form('app_add_form', request, session)
            self._form.add_field('text', '苹果应用地址', 'apple_url', data={'attributes':{'class':'m-wrap large'}})
            self._form.add_validator(AppAddValidator)
        except FormException, ex:
            return self.error(str(ex))

    @route('/add', methods=['GET', 'POST'], endpoint='admin_app_add')
    def GET(self):
        self._init_form()

        if request.method != 'POST':
            return self._view.render('app_add', form=self._form)

        if self._form.validate():
            try:
                r = re.search(r"""itunes\.apple\.com\/(.*?)\/app\/.*?\/id(.*?)\?.*?""", request.form['apple_url'])
                track_id = int(r.group(2))
                url = 'http://itunes.apple.com/%s/lookup?id=%s' % (r.group(1), track_id)
                apple_data = requests.get(url)
                data = str(apple_data.content).decode('utf-8')
                data = cjson.decode(data)

                if int(data['resultCount']) == 0:
                    message = {'status':'error', 'message':'找不到苹果官方数据，可能此应用已经下架'}
                else:
                    data = data['results'][0]
                    app = DB.AppBase.find_one({'trackId':track_id})
                    if app is None:
                        _id = DB.AppBase.insert(data)
                        app = DB.AppBase.find_one({'trackId':track_id})
                    else:
                        _id = app['_id']
                        DB.AppBase.update({'_id':ObjectId(_id)}, {'$set':data})

                    return redirect(url_for("admin_app_edit") + "?_id=" + str(app["_id"]))
            except Exception, ex:
                message = {'status':'error', 'message':str(ex)}
        else:
            message = {'status':'error', 'message':'添加失败'}

        self._form.add_message(**message)

        return self._view.render('app_add', form=self._form)

class AppAddValidator(FormValidatorAbstract):
    '''
    表单验证
    '''
    def rules(self):
        return {
            'apple_url':{'required':True, 'validate':self.validate_url}
        }

    def validate_url(self, url):
        r = re.search('itunes\.apple\.com\/(.*?)\/app\/.*?\/id(.*?)\?.*?', url)
        if r == None:
            return '地址格式不正确'
        return True

class CreateView(View):
    '''
    创建
    '''
    def _init_form(self):

        self._view.assign('FormField', FormElementField)
        #语言选项
        lang_options = []
        langs = DB.language.find()
        for lang in langs:
            lang_options.append((lang['name'],lang['code']))

        #主分类选项
        genre_options = []
        genres = DB.app_genre.find({'parentGenre': 36})
        for genre in genres:
            name = ''
            try:
                name = genre['genreName']['ZH']
            except:
                name = genre['genreName']['EN']
            if genre['genreId'] == 6014: name = "游戏"
            elif genre['genreId'] == 6021: name = "报刊杂志"
            genre_options.append((name, str(genre['genreId'])))

        self._form = Form('app_create_form', request, session)
        self._form.add_field('text', 'trackId', 'trackId', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', 'trackName', 'trackName', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', 'bundleId', 'bundleId', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', '官方版本', 'version', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('radio', '主分类', 'primaryGenreId', data={'option': genre_options})
        self._form.add_field('checkbox', '支持设备', 'supportedDevices', data={'value': '', 'option': [("iPad", "iPad"), ("iPhone", "iPhone")]})

        self._form.add_field('checkbox', '语言', 'languageCodesISO2A', data={ 'value': '', 'option': lang_options})
        self._form.add_field('textarea', '描述', 'description', data={'attributes':{'class':'m-wrap huge'}})
        self._form.add_field('textarea', '更新介绍', 'releaseNotes', data={'attributes':{'class':'m-wrap huge'}})
        self._form.add_validator(AppInfoValidator)

    @route('/create', methods=["GET","POST"], endpoint='admin_app_create')
    def get(self):
        try:
            self._init_form()
        except FormException, ex:
            return self._view.error(str(ex))
        if request.method == "POST":
            if self._form.validate():
                #_id = MongoId()
                data = {
                    'trackId':int(request.form['trackId']),
                    'trackName':request.form['trackName'],
                    'bundleId':request.form['bundleId'],
                    'version':request.form['version'],
                    'primaryGenreId':int(request.form['primaryGenreId']),
                    'languageCodesISO2A':request.form.getlist('languageCodesISO2A'),
                    'description':request.form['description'],
                    'releaseNotes':request.form['releaseNotes'],
                    'supportedDevices': request.form.getlist('supportedDevices')
                }
                DB.AppBase.update({'bundleId':request.form['bundleId']}, {'$set':data}, upsert=True)
                app = DB.AppBase.find_one({"trackId": int(request.form["trackId"])})
                #return redirect(create_url('.app.edit', {'_id':app._id}))
                return redirect(url_for("admin_app_edit") + "?_id=" + str(app["_id"]))
            else:
                message = {'status':'error', 'message':'添加失败'} 

            self._form.add_message(**message)
        return self._view.render('app_create', form=self._form)

    """this method is deprecated, not used in this project"""
    @route('/create_post', endpoint='admin_app_create_post')
    def post(self):
        try:
            self._init_form()
        except FormException, ex:
            return self._view.error(str(ex))
        if self._form.validate():
            _id = MongoId()
            data = {
                '_id': _id,
                'trackId':int(request.form['trackId']),
                'trackName':request.form['trackName'],
                'bundleId':request.form['bundleId'],
                'version':request.form['version'],
                'primaryGenreId':int(request.form['primaryGenreId']),
                'languageCodesISO2A':request.form.getlist('languageCodesISO2A'),
                'description':request.form['description'],
                'releaseNotes':request.form['releaseNotes'],
                'review': int(request.form['review'])
            }
            DB.AppBase.update({'bundleId':request.form['bundleId']}, {'$set':data}, upsert=True)
            return redirect(create_url('.app.edit', {'_id':_id}))
        else:
            message = {'status':'error', 'message':'添加失败'} 

        self._form.add_message(**message)

        return self._view.render('app_create', form=self._form)


class AppDetailBaseView(View):
    '''
    应用详细信息基类
    '''
    def before_request(self, name):
        super(AppDetailBaseView, self).before_request(name)

        self._id = request.args.get('_id', None)
        self.bundle_id = request.args.get('bundleId', None)

        list_params = '#'
        for key in request.args.keys():
            if key == '_id' or key == 'bundleId':
                continue
            list_params = '%s&%s=%s' % (list_params, key, request.args.get(key))
        self._view.assign('list_params', list_params)


class EditView(AppDetailBaseView):
    '''
    编辑
    '''
    def before_request(self, name):
        super(EditView, self).before_request(name)

        _id = self._id
        bundle_id = self.bundle_id

        if _id is None and bundle_id is None:
            return self.error('参数不正确')

        if _id is None:
            self.app_data = DB.AppBase.find_one({'bundleId':bundle_id})
        else:
            self.app_data = DB.AppBase.find_one({'_id':ObjectId(_id)})

        if self.app_data == None:
            return self.error('该应用不存在')

        self.icon = {}
        if 'artworkUrl512' in self.app_data:
            self.icon['apple'] = artworkUrl512_to_114_icon(self.app_data['artworkUrl512'])
        if 'local_icon' in self.app_data:
            self.icon['local'] = self.app_data['local_icon']

    def _init_form(self, data=None):

        self._view.assign('FormField', FormElementField)
        #语言选项
        lang_options = []
        langs = DB.language.find()
        for lang in langs:
            lang_options.append((lang['name'], lang['code']))

        #主分类选项
        genre_options = []
        genres = DB.app_genre.find({'parentGenre':36})
        for genre in genres:
            name = ''
            try:
                name = genre['genreName']['ZH']
            except:
                name = genre['genreName']['EN']
            if genre['genreId'] == 6014: name = "游戏"
            elif genre['genreId'] == 6021: name = "报刊杂志"
            genre_options.append((name, str(genre['genreId'])))
        #check device support, check if supportIphone or supportIpad
        self.supportIphone = 0
        self.supportIpad = 0
        if "supportIphone" in self.app_data:
            self.supportIphone = self.app_data["supportIphone"]
        else:
            if "supportedDevices" in self.app_data:
                if True in [item.startswith("iPhone") for item in self.app_data["supportedDevices"]]:
                    self.supportIphone = 1
            else:
                supportIphone = 0
        if "supportIpad" in self.app_data:
            self.supportIpad = self.app_data["supportIpad"]
        else:
            if "supportedDevices" in self.app_data:
                if True in [item.startswith("iPad") for item in self.app_data["supportedDevices"]]:
                    self.supportIpad = 1
            else:
                self.supportIpad = 0
        if data:
            data["supportIphone"]= self.supportIphone
            data["supportIpad"] = self.supportIpad
            app_cn = DB.AppBase_CN.find_one({"trackId": data["trackId"]})
            if app_cn:
                data["trackName_CN"] = app_cn["trackName"]
                data["description_cn"] = app_cn.get("description", "")
                data["releaseNotes_cn"] = app_cn.get("releaseNotes", "")


        self._form = Form('app_edit_form', request, session)
        self._form.add_field('file', '上传图标', 'pic', data={'attributes': {}})
        self._form.add_field('text', 'trackId', 'trackId', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', 'trackName', 'trackName', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', '应用中文名称', 'trackName_CN', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', '编辑翻译(中文)', 'cnname', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', '编辑翻译(阿拉伯)', 'arname', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', 'bundleId', 'bundleId', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', '官方应用地址', 'trackViewUrl', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', '官方版本', 'version', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('text', '可下载版本', 'downloadVersion', data={'attributes':{'class':'m-wrap large'}})
        self._form.add_field('radio', '主分类', 'primaryGenreId', data={'option': genre_options})
        self._form.add_field('radio', '支持iPhone', 'supportIphone', data={'option': [("是", "1"), ("否", "0")]})
        self._form.add_field('radio', '支持iPad', 'supportIpad', data={'option': [("是", "1"), ("否", "0")]})
        self._form.add_field('checkbox', '语言', 'languageCodesISO2A', data={'option': lang_options})
        self._form.add_field('textarea', '描述', 'description', data={'attributes':{'class':'m-wrap large','rows':'10'}})
        self._form.add_field('textarea', '描述(中)', 'description_cn', data={'attributes':{'class':'m-wrap large','rows':'10'}})
        self._form.add_field('textarea', '更新介绍', 'releaseNotes', data={'attributes':{'class':'m-wrap large','rows':'10'}})
        self._form.add_field('textarea', '更新介绍(中)', 'releaseNotes_cn', data={'attributes':{'class':'m-wrap large','rows':'10'}})
        self._form.add_field('radio', '审核', 'review', data={'option': [("审核通过", "1"), ("未审核", "0")]})
        self._form.set_value(data)
        self._form.add_validator(AppInfoValidator)

    @route('/edit', methods=['GET', 'POST'],  endpoint='admin_app_edit')
    def do_request(self):

        if request.method != 'POST':
            try:
                self._init_form(self.app_data)
            except FormException, ex:
                return self.error(str(ex))

            return self._view.render('app_edit', form=self._form, app=self.app_data, icon=self.icon)


        try:
            self._init_form(dict(request.form))
        except FormException, ex:
            return self.error(str(ex))

        if self._form.validate():
            data = {
                'trackId':int(request.form['trackId']),
                'trackName':request.form['trackName'],
                'cnname': request.form["cnname"],
                'arname': request.form["arname"],
                'bundleId':request.form['bundleId'],
                'trackViewUrl':request.form['trackViewUrl'],
                'version':request.form['version'],
                'primaryGenreId':int(request.form['primaryGenreId']),
                'languageCodesISO2A':request.form.getlist('languageCodesISO2A'),
                'description':request.form['description'],
                'releaseNotes':request.form['releaseNotes'],
                'review': int(request.form['review'])
            }
            if int(request.form["supportIphone"]) != self.supportIphone:
                data["supportIphone"] = int(request.form["supportIphone"])
            if int(request.form["supportIpad"]) != self.supportIpad:
                data["supportIpad"] = int(request.form["supportIpad"])

            data_cn = {
                "trackName": request.form["trackName_CN"],
                "description": request.form["description_cn"],
                "releaseNotes": request.form["releaseNotes_cn"]
            }
            app_cn = DB.AppBase_CN.find_one({"trackId": int(request.form["trackId"])})
            if app_cn:
                DB.AppBase_CN.update({"_id": app_cn["_id"]}, {"$set": data_cn})
            else:
                data_cn = {
                    "trackId": int(request.form["trackId"]),
                    "trackName": request.form["trackName_CN"],
                    "description": request.form["description_cn"],
                    "releaseNotes": request.form["releaseNotes_cn"]
                }
                DB.AppBase_CN.insert(data_cn)
            file = request.files["pic"]
            ext = file.filename.split('.')[-1]
            name = str(time.time()) + '_' + file.filename
            tmp_file = os.path.join(settings['tmp_dir'], name)
            file.save(tmp_file)
            sha1 = sha1_of_file(tmp_file)
            pic_path = hash_to_path(sha1) + '.' +ext
            pic_path = os.path.join(settings['pic_upload_dir'], pic_path)
            dir_path = os.path.dirname(pic_path)
            if not os.path.isdir(dir_path):os.makedirs(dir_path)
            shutil.move(tmp_file, pic_path)
            pic_url = settings['pic_url_host'] + '/%s.%s' % (hash_to_path(sha1), ext)
            data["artworkUrl512"] = pic_url
            DB.AppBase.update({'_id':self.app_data['_id']}, {'$set':data})
            message = {'status':'success', 'message':'修改成功'} 
        else:
            message = {'status':'error', 'message':'修改失败'} 

        self._form.add_message(**message)

        return self._view.render('app_edit', form=self._form, app=self.app_data, icon=self.icon)

class AppInfoValidator(FormValidatorAbstract):
    '''
    验证
    '''
    def rules(self):
        return {
            'trackId':{'required':True, 'max_length':12, 'min_length':5},
            'trackName':{'required':True, 'max_length':200, 'min_length':1},
            'version':{'required':True},
            'bundleId':{'required':True},
            'primaryGenreId':{'required':True}
        }


class SyncIconView(View):
    '''
    sync the icon with the apple
    '''
    @route('/sync_icon', methods=['GET'], endpoint='admin_app_sync_icon')
    def do_request(self):
        try:
            trackId = request.args.get("trackId", "")
            _id = request.args.get("_id", "")
            url = 'http://itunes.apple.com/us/lookup?id=%s' % (trackId)
            apple_data = requests.get(url)
            data = apple_data.json()
            if len(data["results"]) == 0:
                status, message = 'error', u'找不到苹果官方数据，可能此应用已经下架'
            else:
                data = data["results"][0]
                DB.AppBase.update({'_id':ObjectId(_id)}, {'$set':{'artworkUrl60': data['artworkUrl60'],
                                  'artworkUrl512': data["artworkUrl512"],
                                  "artworkUrl100": data["artworkUrl100"]}})
                status, message = 'success', '更新图标成功'
        except Exception, ex:
            status, message = 'error', str(ex)
            pass
        return self._view.ajax_response(status, message)


class SyncInfoView(View):
    '''
    sync the app info with the apple
    '''
    @route('/sync_app_info', methods=['GET'], endpoint='admin_app_sync_info')
    def do_request(self):
        try:
            trackId = request.args.get("trackId", "")
            _id = request.args.get("_id", "")
            for coun in country:
                url = 'http://itunes.apple.com/%s/lookup?id=%s' % (coun, trackId)
                apple_data = requests.get(url)
                data = apple_data.json()
                if len(data["results"]) == 0:
                    status, message = 'error', u'找不到苹果官方数据，可能此应用已经下架'
                else:
                    data = data["results"][0]
                    if coun == "us":
                        db = DB.AppBase
                    elif coun == "cn":
                        db = DB.AppBase_CN
                    app = db.find_one({'trackId':int(trackId)})
                    if app is None:
                        _id = db.insert(data)
                    else:
                        _id = app['_id']
                        db.update({'_id':ObjectId(_id)}, {'$set':data})
                status, message = 'success', '更新应用信息成功'
        except Exception, ex:
            status, message = 'error', str(ex)
            pass
        return self._view.ajax_response(status, message)


class ScreenshotView(View):

    @route('/screenshot', endpoint='admin_app_screenshot')
    def index(self):
        bundle_id = request.args.get('bundleId', None)
        if bundle_id is None:
            return self._view.error('参数不正确')
        app = DB.AppBase.find_one({'bundleId': bundle_id})
        self._view.assign('app', app)
        return self._view.render('app_screenshot')

    @route('/screenshot/list', endpoint='admin_app_screenshot_list')
    def get(self):
        bundle_id = request.args.get('bundleId', None)
        if bundle_id is None:
            return self._view.error('参数不正确')
        device = request.args.get('device', 'iphone')
        lang = request.args.get("lang", "en")

        app = DB.AppBase.find_one({'bundleId': bundle_id})
        app_cn = DB.AppBase_CN.find_one({"bundleId": bundle_id})
        apple_screenshot = []
        if device == 'iphone':
            if lang == "en" and 'screenshotUrls' in app:
                apple_screenshot = app['screenshotUrls'] if app else []
            else:
                apple_screenshot = app_cn.get("screenshotUrls", "") if app_cn else []
        else:
            if lang == "en" and 'ipadScreenshotUrls' in app:
                apple_screenshot = app['ipadScreenshotUrls'] if app else []
            else:
                apple_screenshot = app_cn.get('ipadScreenshotUrls', "") if app_cn else []
        self._view.assign('device', device)
        self._view.assign('lang', lang)
        self._view.assign('screenshot', apple_screenshot)
        self._view.assign('create_pic_url', create_pic_url)
        return self._view.ajax_render('app_screenshot_list')

    @route('/screenshot/sync', methods=['POST'], endpoint='admin_app_screenshot_sync')
    def sync_screenshot(self):
        langs = ["us", "cn"]
        bundle_id = request.form.get('bundleId', None)
        if bundle_id is None:
            status, message = 'error', '参数不正确'
            return self._view.ajax_response(status, message)

        app = DB.AppBase.find_one({'bundleId': bundle_id})
        app_cn = DB.AppBase_CN.find_one({"bundleId": bundle_id})
        url = 'http://itunes.apple.com/%s/lookup?bundleId=%s'
        try:
            for lang in langs:
                apple_data = requests.get(url % (lang, bundle_id))
                data = apple_data.json()
                if len(data["results"]) == 0:
                    status, message = 'error', u'找不到苹果官方数据，可能此应用已经下架'
                else:
                    data = data["results"][0]
                    if lang == "us":
                        DB.AppBase.update({"bundleId": bundle_id}, {"$set": {"ipadScreenshotUrls": data["ipadScreenshotUrls"],
                                                                             "screenshotUrls": data["screenshotUrls"]}}, upsert=True)
                    elif lang == "cn":
                        DB.AppBase_CN.update({"bundleId": bundle_id}, {"$set": {"ipadScreenshotUrls": data["ipadScreenshotUrls"],
                                                                               "screenshotUrls": data["screenshotUrls"]}}, upsert=True)
                    status, message = 'success', '更新截图成功'
        except Exception:
            status, message = 'error', str(ex)
            pass
        return self._view.ajax_response(status, message)

    def allowed_file(self, filename):
        return '.' in filename and filename.rsplit('.', 1)[1] in ['jpg', 'png', 'jpeg']

    @route('/screenshot/upload', methods=['POST'], endpoint='admin_app_screenshot_upload')
    def upload(self):
        try:
            bundle_id = request.form['bundleId']
            file = request.files['Filedata']
            if file and self.allowed_file(file.filename):
                ext = file.filename.split('.')[-1]
                name = str(time.time()) + '_' + file.filename
                tmp_file = os.path.join(settings['tmp_dir'], name)
                file.save(tmp_file)
                sha1 = sha1_of_file(tmp_file)
                pic_path = hash_to_path(sha1) + ".114x114-75" + '.' +ext
                pic_path = os.path.join(settings['pic_upload_dir'], pic_path)
                dir_path = os.path.dirname(pic_path)
                if not os.path.isdir(dir_path):
                    os.makedirs(dir_path)
                shutil.move(tmp_file, pic_path)
                pic_url = '#IMG_HOST#%s.%s' % (hash_to_path(sha1), ext)
                if request.form['device'] == 'iphone':
                    data = {'screenshotUrls': pic_url}
                if request.form['device'] == 'ipad':
                    data = {'ipadScreenshotUrls': pic_url}
                if request.form["lang"] == "en":
                    DB.AppBase.update({'bundleId': bundle_id}, {'$addToSet': data})
                else:
                    try:
                        DB.AppBase_CN.update({'bundleId': bundle_id}, {'$addToSet': data})
                    except Exception:
                        data = data.update({'bundleId': bundle_id})
                        DB.AppBase_CN.insert(data)
                status, message = 'success', u'上传成功'
            else:
                raise Exception(u'必须是jpg,png文件')
        except Exception, ex:
            status, message = 'error', u'上传失败:' + str(ex)
        return self._view.ajax_response(status, message)

    @route('/screenshot/delete', methods=['POST'], endpoint='admin_app_screenshot_delete')
    def do_request(self):
        try:
            bundle_id = request.form['bundleId']
            device = request.form['device']
            lang = request.form["lang"]
            url = request.form['url']
            app = DB.AppBase.find_one({'bundleId': bundle_id})
            app_cn = DB.AppBase_CN.find_one({'bundleId': bundle_id})
            if not app:
                raise Exception("应用不存在")
            pic_array = []
            if lang == "en":
                pic_array = app["screenshotUrls"] if device=="iphone" else app["ipadScreenshotUrls"]
            elif lang == "cn":
                pic_array = app["screenshotUrls"] if device=="iphone" else app["ipadScreenshotUrls"]
            if len(pic_array) == 0:
                raise Exception("没有该截图")
            print pic_array
            pic_array.remove(url)
            print pic_array
            data = {}
            if device == 'iphone':
                data = {'screenshotUrls': pic_array}
            if device == 'ipad':
                data = {'ipadScreenshotUrls': pic_array}
            if data:
                if lang == "en":
                    DB.AppBase.update({'bundleId': bundle_id}, {'$set': data})
                else:
                    DB.AppBase_CN.update({'bundleId': bundle_id}, {'$set': data})
            status, message = 'success', u'删除成功'
        except Exception, ex:
            import traceback
            traceback.print_exc()
            status, message = 'error', u'删除失败:' + str(ex)
        return self._view.ajax_response(status, message)
