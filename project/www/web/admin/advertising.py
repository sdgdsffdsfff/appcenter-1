#encoding=UTF8
#code by LP
#2013-11-13

import os
import time
import random
from __header__ import AdminView, FlaskView, DB, route, request, session, redirect, url_for, upload_hash_file
from conf.settings import settings
from www.lib.form import Form, FormElementField, FormElementSubmit, FormException, FormValidatorAbstract
from www.controller.app.header import create_pic_url
from bson.objectid import ObjectId
import pymongo

class View(FlaskView):

    route_base = '/app_advertising'

    def before_request(self, name):
        self._view = AdminView()


class ListView(View):
    '''
    广告列表
    '''
    @route('/list', endpoint='admin_advertising_list')
    def get(self):
        advertising_list = DB.advertising.find().sort("_id", pymongo.ASCENDING)
        return self._view.render('advertising_list', advertising_list=list(advertising_list))


class ItemSearchView(View):
    '''
    search for app or topic by query type
    '''
    @route('/query', endpoint="admin_advertising_item_query")
    def get(self):
        tp = request.args.get("type", "app")
        q = request.args.get("q", "")
        limit = int(request.args.get("page_limit", 10))
        status = "success"
        items = None
        if tp == "app":
            apps = DB.AppBase.find({"trackId": int(q)}, { "trackName": 1, "trackId": 1, "_id":1 }).limit(limit)
            items = [{"name": app["trackName"], "trackId": app["trackId"], "_id": app["_id"]} for app in apps]
        elif tp == "topic":
            topics = DB.app_topic.find({"name": q} , { "name": 1, "_id":1 })
            temp_items = []
            items = [topic for topic in topics]
            for item in items:
                temp_items.append({"_id": item["_id"], "name": str(item["_id"])+str(item["name"])})
            items = temp_items
        elif tp == "weburl":
            items = [{"name": q, "_id": {"$oid": q}}]
        return self._view.ajax_response(status=status, data={"items": items})


class AddView(View):
    '''
    广告添加
    '''
    @route('/add', methods=['POST'], endpoint='admin_advertising_add')
    def post(self):
        try:
            data = {
                'identifier': request.form['identifier'],
                'name': request.form['name']
            }
            DB.advertising.insert(data)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)


class AdOrderUpdateView(View):
    '''
    广告排序修改
    '''
    @route('/order/update', methods=['POST'], endpoint='admin_advertising_order_update')
    def post(self):
        try:
            #dangers to use eval, but since we use internal, that's would be find.
            pk, identifier = eval(request.form["pk"])
            value = request.form["value"]
            DB.advertising.update({"identifier": identifier, "items.id": int(pk)}, {"$set": {"items.$.order": int(value)}})
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)

class DeleteView(View):

    @route('/delete', endpoint='admin_advertising_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.advertising.remove({'_id':ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)


class ItemListView(View):
    '''
    广告列表
    '''
    @route('/item/list', endpoint='admin_advertising_item_list')
    def get(self):
        identifier = request.args.get('identifier')
        lang_s = request.args.get("lang", "")
        country_s = request.args.get("country", "")
        res = DB.advertising.find_one({'identifier':identifier})
        ad_list = []
        if res and 'items' in res:
            tmp_ad_list = res['items']
            ad_list = sorted(tmp_ad_list, key=lambda k: k.get("order", ""))
            if lang_s != "" or country_s != "":
                ad_list = [item for item in ad_list if lang_s in item["language"] or country_s in item["country"]]

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
        self._view.assign('create_pic_url', create_pic_url)
        self._view.assign("lang_options", lang_options)
        self._view.assign("country_options", country_options)
        self._view.assign("lang_s", lang_s)
        return self._view.render('advertising_item_list', ad_list=ad_list, ad=res,
                                 identifier=identifier, country_s=country_s)


class ItemAddView(View):
    '''
    广告添加
    '''
    def before_request(self, name):
        super(ItemAddView, self).before_request(name)
        self._identifier = request.args.get('identifier')
        try:
            self._init_form(self._identifier)
        except FormException, ex:
            return self._view.error(str(ex))

    def _init_form(self, identifier):

        self._view.assign('FormField', FormElementField)
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
        #广告位选项
        identifier_options = []
        ads = DB.advertising.find()
        for ad in ads:
            identifier_options.append((ad['name'], ad['identifier']))

        self._form = Form('advertising_add_form', request, session)
        self._form.add_field('text', '标题', 'title', data={'attributes':{'class':'m-wrap large', 'placeholder': '标题'}})
        self._form.add_field('select', '所属广告位', 'identifier', data={'value':identifier, 'option': identifier_options, 'attributes':{'class':'m-wrap large'}})
        self._form.add_field('radio', '广告类型', 'adtype', data={'value': '1', 'option': [("应用", "1"), ("专题", "0"), ("web", "2")]})
        #self._form.add_field('text', '链接', 'link', data={'attributes':{'class':'m-wrap large', 'placeholder': 'id=应用ID/topic_id=专题ID'}})
        self._form.add_field('text', '链接', 'link', data={'attributes':{'class':'m-wrap large', 'id': 'adlink'}})
        self._form.add_field('text', '排序', 'order', data={'attributes':{'class':'m-wrap large', 'placeholder': '排序'}})
        self._form.add_field('checkbox', '投放语言', 'language', data={ 'value': '', 'option': lang_options})
        self._form.add_field('checkbox', '投放国家（优先）', 'country', data={ 'value': '', 'option': country_options})
        self._form.add_field('file', '上传图片(jpg格式，iPhone 640*251，iPad 408*178)', 'pic', data={ 'attributes': {}})
        self._form.add_validator(AdvertisingItemValidator)

    @route('/item/add', methods=['GET', 'POST'], endpoint='admin_advertising_item_add')
    def do_request(self):
        if request.method != 'POST':
            return self._view.render('advertising_item_add', form=self._form, identifier=self._identifier)

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
            if request.form["adtype"] == "1":
                #it's a app
                link = "ID=" + request.form["link"]
            elif request.form["adtype"] == "0":
                #it's a topic
                link = "TOPIC_ID=" + request.form["link"]
            elif request.form["adtype"] == "2":
                link = "WEB_URL=" + request.form["link"]
            item_id = '%s%s' % (int(time.time()), random.randint(1000, 9999))
            #入库 
            items = {
                'id': int(item_id),
                'title': request.form['title'],
                'link': link,
                'order': int(request.form["order"]),
                'hash': hash_str,
                'store_path': save_file,
                'language': language,
                'country': country
            }
            try:
                DB.advertising.update({'identifier':request.form['identifier']}, {'$push':{'items':items}})
            except Exception, ex:
                message = {'status':'error', 'message':ex}
            message = {'status':'success', 'message':'添加成功'}
            self._form.clean_value()
        else:
            message = {'status':'error', 'message':'添加失败，有些表单数据不正确！'}

        self._form.add_message(**message)
        

        return self._view.render('advertising_item_add', form=self._form, identifier=self._identifier)


class AdvertisingItemValidator(FormValidatorAbstract):

    def rules(self):
        return {
            'title': {'required': True},
            'link': {'required': True},
            'pic': {'required': True}
        }


class ItemDeleteView(View):
    '''
    广告删除
    '''
    @route('/item/delete',  endpoint='admin_advertising_item_delete')
    def get(self):
        try:
            identifier = request.args.get('identifier')
            item_id = request.args.get('id')
            lans = request.args.get('lans').split('*')[:-1]
            if len(lans):
                res = DB.advertising.update({'identifier':identifier,'items':{"$elemMatch":{'id':int(item_id)}}},{'$set':{'items.$.language':lans}})
            else:
                res = DB.advertising.update({'identifier':identifier}, {'$pull':{'items':{'id':int(item_id)}}})
            #res = DB.advertising.update({'identifier':identifier}, {'$pull':{'items':{'id':int(item_id)}}})

            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)
