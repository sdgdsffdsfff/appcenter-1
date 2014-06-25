#encoding=UTF8
#code by LP
#2013-11-26

import random
import time, datetime
from www.lib.form import Form, FormElementField, FormElementSubmit, FormException, FormValidatorAbstract
from __header__ import AdminView, FlaskView, DB, route, request, session, redirect, url_for, language_code_to_name, file_size_format, country_code_to_name, upload_hash_file
from conf.settings import settings
from bson.objectid import ObjectId
from www.controller.app.app_collection import AppCollectionController
from www.controller.app.header import artworkUrl512_to_114_icon, create_pic_url, sort_items


class View(FlaskView):

    route_base = '/app_topic'

    def before_request(self, name):
        self._view = AdminView()


class ListView(View):
    '''
    专题列表
    '''
    @route('/list', endpoint='admin_app_topic_list')
    def get(self):

        res = DB.app_topic.find()

        self._view.assign('create_pic_url', create_pic_url)
        self._view.assign('language_code_to_name', language_code_to_name)
        self._view.assign('country_code_to_name', country_code_to_name)

        return self._view.render('app_topic_list', topic_list=list(res))


class AppTopicInfoBaseView(View):
    '''
    专题信息添加修改基类
    '''

    def get_country_and_language_options(self):
        #语言选项
        lang_options = []
        langs = DB.client_support_language.find()
        for lang in langs:
            lang_options.append((lang['name'],lang['code']))
        #国家选项
        country_options = []
        countries = DB.country.find()
        for country in countries:
            country_options.append((country['name'], country['code']))

        return lang_options, country_options

    def _init_form(self):

        self._view.assign('FormField', FormElementField)

        lang_options, country_options = self.get_country_and_language_options()

        self._form = Form('app_topic_add_form', request, session)
        self._form.add_field('text', '专题名称', 'name', data={'attributes': {'class': 'm-wrap large'}})
        self._form.add_field('textarea', '描述', 'description', data={'attributes': {'class': 'm-wrap large'}})
        self._form.add_field('checkbox', '投放语言', 'language', data={'value': '', 'option': lang_options})
        self._form.add_field('checkbox', '投放国家', 'country', data={'value': '', 'option': country_options})
        self._form.add_field('file', '专题图标', 'pic', data={'attributes': {}})
        self._form.add_field('radio', '状态', 'status', data={'value': '0', 'option':[('发布','1'), ('未发布','0')]})


class AddView(AppTopicInfoBaseView):
    '''
    专题添加
    '''
    def before_request(self, name):
        super(AddView, self).before_request(name)
        try:
            self._init_form()
        except FormException, ex:
            return self._view.error(str(ex))


    @route('/add', methods=['GET', 'POST'], endpoint='admin_app_topic_add')
    def do_request(self):
        if request.method != 'POST':
            return self._view.render('app_topic_add', form=self._form)

        #上传文件
        try:
            hash_str, abs_save_file, save_file= upload_hash_file(request.files['pic'], settings['pic_upload_dir'], ['png', 'jpg'])
        except Exception, ex:
            self._form.add_error('pic', str(ex))

        language = []
        country = []
        try:
            language = request.form.getlist('language')
            country = request.form.getlist('country')
        except:
            pass

        if self._form.validate():
            #入库 
            data = {
                'name': request.form['name'],
                'description': request.form['description'],
                'icon_hash': hash_str,
                'icon_store_path': save_file,
                'language': language,
                'country': country,
                'items': [],
                'status': int(request.form['status']),
                'update_time': datetime.datetime.now()
            }
            try:
                DB.app_topic.insert(data)
            except Exception, ex:
                message = {'status': 'error', 'message': ex}
            message = {'status': 'success', 'message': '添加成功'}
        else:
            message = {'status': 'error', 'message': '添加失败，有些表单数据不正确！'}

        self._form.add_message(**message)
        self._form.clean_value()

        return self._view.render('app_topic_add', form=self._form)


class EditView(AppTopicInfoBaseView):
    '''
    专题编辑
    '''
    def before_request(self, name):
        self._id = request.args.get('_id', None)
        if self._id is None:
            return self._view.error("参数不正确")
        self.topic_data = DB.app_topic.find_one({'_id': ObjectId(self._id)})

        super(EditView, self).before_request(name)

    @route('/edit', methods=['GET', 'POST'], endpoint='admin_app_topic_edit')
    def do_request(self):

        if request.method != 'POST':
            try:
                self._init_form()
                self._form.add_validator(AppTopicEditValidator)
                self._form.set_value(self.topic_data)
            except FormException, ex:
                return self._view.error(str(ex))

            return self._view.render('app_topic_add', form=self._form)

        try:
            self._init_form()
            self._form.add_validator(AppTopicEditValidator)
        except FormException, ex:
            return self._view.error(str(ex))

        #上传文件
        try:     
            hash_str, abs_save_file, save_file= upload_hash_file(request.files['pic'], settings['pic_upload_dir'], ['png', 'jpg'])
        except Exception, ex:
            #self._form.add_error('pic', str(ex))
            hash_str, abs_save_file, save_file = None, None, None

        try:
            language = request.form.getlist('language')
            country = request.form.getlist('country')
        except:
            language, country = None, None

        if self._form.validate():
            try:
                #入库
                data = {}
                data['name'] = request.form['name']
                data['description'] = request.form['description']
                if hash_str and save_file:
                    data['icon_hash'] = hash_str
                    data['icon_store_path'] = save_file
                if language:
                    data['language'] = language
                if country:
                    data['country'] = country
                data['status'] = int(request.form['status'])
                DB.app_topic.update({'_id': ObjectId(self._id)}, {'$set': data})
                message = {'status': 'success', 'message': '编辑成功'}
            except Exception, ex:
                message = {'status': 'error', 'message': ex}
        else:
            message = {'status': 'error', 'message': '编辑失败，有些表单数据不正确！'}

        self._form.add_message(**message)
        self._form.clean_value()

        return self._view.render('app_topic_add', form=self._form)


class AppTopicAddValidator(FormValidatorAbstract):

    def rules(self):
        return {
            'name': {'required':True},
            'pic': {'required':True}
        }


class AppTopicEditValidator(FormValidatorAbstract):

    def rules(self):
        return {
            'name': {'required':True}
        }


class DeleteView(View):

    @route('/delete', endpoint='admin_app_topic_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            DB.app_topic.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)

class ItemAddView(View):

    @route('/item/add', methods=['GET', 'POST'],  endpoint='admin_app_topic_item_add')
    def do_request(self):
        _id = request.args.get('_id')
        if request.method != 'POST':
            res = DB.app_topic.find_one({'_id':ObjectId(_id)})
            if not res:
                return self._view.error("专题不存在")
            self._view.assign('search_use', 'topic')
            self._view.assign('app_topic', res)

            return self._view.render('app_topic_item_add')


        try:
            app = DB.AppBase.find_one({'_id': ObjectId(request.form['_appid'])})
            if app == None:
                raise Exception("app not exists")

            item_id = '%s%s' % (int(time.time()), random.randint(1000, 9999))
            try:
                rating = app['averageUserRating']
            except:
                rating = 0
            try:
                download_version = app['downloadVersion']
            except:
                download_version = ''
            #check if items already in app_topic
            if DB.app_topic.find({"_id": ObjectId(_id), "items":\
                {"$elemMatch": {"trackName": app['trackName']}}}).count() != 0:
                raise ValueError(u"应用已经存在")
            items = {
                'id': int(item_id),
                'sort':int(request.form['sort']),
                'trackName':app['trackName'],
                'icon': artworkUrl512_to_114_icon(app['artworkUrl512']),
                'ID': str(app['_id']),
                'averageUserRating': rating,
                'size': file_size_format(app['fileSizeBytes']),
                'version': download_version
            }

            DB.app_topic.update({'_id': ObjectId(request.args.get('_id'))}, 
                {
                    '$set':{'update_time': datetime.datetime.now()}, 
                    '$push': {'items': items}
                })
            status, message = 'success', ''
        except Exception, ex:
            print ex
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message, '')


class ItemListView(View):
    '''
    集合列表ajax
    '''
    @route('/item/list', endpoint='admin_app_topic_item_list')
    def get(self):
        _id = request.args.get('_id')
        res = DB.app_topic.find_one({'_id': ObjectId(_id)})
        topic_list = []
        if res and 'items' in res:
            topic_list = sort_items(res['items'])
        return self._view.ajax_render('app_topic_item_list_ajax', topic_list=topic_list, topic=res)


class ItemDeleteView(View):
    '''
    应用集合列表删除
    '''
    @route('/item/delete', endpoint='admin_app_topic_item_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            item_id = request.args.get('id')
            DB.app_topic.update({'_id': ObjectId(_id)}, {'$pull': {'items': {'id':int(item_id)}}})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)

class ItemSortView(View):
    '''
    应用集合列表排序
    '''
    @route('/item/sort', methods=['POST'], endpoint='admin_app_topic_item_sort')
    def do_request(self):
        try:
            for key in request.form.keys():
                id = int(key.split('_')[1])
                DB.app_topic.update({'_id':ObjectId(request.args.get('_id')), 'items.id': id}, {'$set': {'items.$.sort': int(request.form[key])}})
            status, message = 'success', ''
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)
