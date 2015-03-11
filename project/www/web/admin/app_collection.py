#encoding=UTF8
#code by LP
#2013-11-21

import time
import random
from __header__ import AdminView, FlaskView, DB, route, request, session, redirect, url_for, file_size_format
from bson.objectid import ObjectId
from www.controller.app.app_collection import AppCollectionController
from www.controller.app.header import artworkUrl512_to_114_icon
import pymongo
from collections import defaultdict, OrderedDict

class View(FlaskView):

    route_base = '/app_collection'

    def before_request(self, name):
        self._view = AdminView()


class ListView(View):

    @route('/list', endpoint='admin_app_collection_list')
    def get(self):
        res = DB.app_collection.find().sort("_id", pymongo.ASCENDING)
        languages = DB.client_support_language.find()
        if languages:
            languages = list(languages)
        self._view.assign('languages', languages)
        return self._view.render('app_collection_list', app_collection_list=list(res))


class AddView(View):

    @route('/add', methods=['POST'], endpoint='admin_app_collection_add')
    def do_request(self):
        try:
            if DB.app_collection.find({"identifier": request.form['identifier']}).count()!= 0:
                status, message = 'error', "重复的标识项"
                return self._view.ajax_response(status, message)
            data = {'identifier': request.form['identifier'], 'name': request.form['name'], 'title': {}, "items": []}
            language_count = 0
            for item in request.form:
                if item == 'identifier' or item == 'name':
                    continue
                language_code = item.replace('title_', '')
                if len(request.form[item]) > 0:
                    data['title'][language_code] = request.form[item]
                    if request.form[item]:
                        language_count += 1
            if language_count == 0:
                status, message = 'error', "至少填写一项语言"
                return self._view.ajax_response(status, message)
            DB.app_collection.insert(data)
            status, message = 'success', '添加成功'

        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)

class DeleteView(View):
    '''
    app collection delete
    '''
    @route('/delete', methods=['GET'], endpoint='admin_app_collection_delete')
    def do_request(self):
        try:
            _id = request.args.get('_id')
            DB.app_collection.remove({'_id':ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)

class ItemListView(View):
    '''
    集合列表ajax
    '''
    @route('/item/list', methods=['GET', 'POST'], endpoint='admin_app_collection_item_list')
    def do_request(self):
        if request.method == 'POST':
            identifier = request.args.get('identifier')
            language = request.form['language']
            country = request.form['country']
            collection_list = defaultdict(list)
            for item in DB.app_collection.find_one(
                    {'identifier': identifier})["items"]:
                if item['bundleId'] in collection_list:
                    if language == "" and country == "":
                        collection_list[item['bundleId']].append(item)
                    else:
                        if language in item["language"]:
                            collection_list[item['bundleId']].append(item)
                        if country in item["country"]:
                            collection_list[item['bundleId']].append(item)
                else:
                    if language == "" and country == "":
                        collection_list[item['bundleId']] = [item]
                    else:
                        if language in item["language"]:
                            collection_list[item['bundleId']] = [item]
                        if country in item["country"]:
                            collection_list[item['bundleId']] = [item]
            self._view.assign('use', 'list')
            result_collection_list = OrderedDict(sorted(collection_list.items(),key=lambda x: x[1][0]["sort"], reverse=True))
            return self._view.ajax_render('app_collection_item_list_ajax',
                                          collection_list=result_collection_list,
                                          identifier=identifier)
        if request.method == 'GET':
            identifier = request.args.get('identifier')
            _id = request.args.get('_id')

            collection = []
            for item in DB.app_collection.find_one(
                    {'identifier': identifier})["items"]:
                if item['ID'] == _id:
                    collection.append(item)

            # 语言选项
            langs = DB.client_support_language.find()
            self._view.assign('lang_options', list(langs))

            # 国家选项
            countries = DB.country.find()
            self._view.assign('country_options', list(countries))
            self._view.assign('use', 'edit')
            return self._view.ajax_render('app_collection_item_list_ajax',
                                          collection=collection,
                                          identifier=identifier,_id=_id)

    def sort_item(self, items, filters):
        '''
        排序过滤
        '''
        data = []
        for item in items:
            if filters['language'] != 'ALL' and filters['language'] not in item['language']:
                continue
            if filters['country'] != 'ALL' and filters['country'] not in item['country']:
                continue
            tmp = ''
            for lang_code in item['language']:
                language = DB.client_support_language.find_one({'code':lang_code})
                if language:
                    tmp = '%s %s' % (tmp, language['name'])
            item['language'] = tmp

            tmp = ''
            for country_code in item['country']:
                country = DB.country.find_one({'code':country_code})
                if country:
                    tmp = '%s %s' % (tmp, country['name'])
            item['country'] = tmp

            data.append(item)

        length = len(data)
        for i in range(length-1):
            for j in range(length-1):
                if (data[j]['sort'] < data[j+1]['sort']):
                    tmp=data[j]
                    data[j]=data[j+1]
                    data[j+1]=tmp
        return data


class ItemAddView(View):
    '''
    应用集合列表添加
    '''

    @route('/item/add', methods=['GET', 'POST'], endpoint='admin_app_collection_item_add')
    def do_request(self):
        self._identifier = request.args.get('identifier')
        if request.method != 'POST':
            res = DB.app_collection.find_one({'identifier':self._identifier})
            if not res:
                return self._view.error("应用集不存在")
            #语言选项
            langs = DB.client_support_language.find()
            self._view.assign('lang_options', list(langs))

            #国家选项
            countries = DB.country.find()
            self._view.assign('country_options', list(countries))

            self._view.assign('search_use', 'collection')
            self._view.assign('app_collection', res)

            return self._view.render('app_collection_item_add')

        # Get each tag from webpage
        temp_data = request.form.getlist('edit_res')
        data = []
        language_list = []
        for ele in temp_data:
            sort = int(ele.split('|')[0].strip())
            isAdvertisement = str(ele.split('|')[2].strip())
            lan_list = []
            if ele.split('|')[1].strip() == "":
                return self._view.ajax_response('error', '不能选择空的语言', '')
            for lan in ele.split('|')[1].strip().split(' '):
                if len(lan) > 0:
                    if lan in language_list:
                        status, message = 'error', '请勿重复选择语言'
                        return self._view.ajax_response(status, message, '')
                    lan_list.append(lan)
                    language_list.append(lan)

            data.append({'sort': sort, 'isAdvertisement':isAdvertisement,'lan': lan_list})
        try:
            app = DB.AppBase.find_one({'_id': ObjectId(request.form['_id'])})
            if app is None:
                raise Exception("应用不存在")

            item_id = '%s%s' % (int(time.time()), random.randint(1000, 9999))
            try:
                rating = app['averageUserRating']
            except:
                rating = 0
            try:
                download_version = app['downloadVersion']
            except:
                download_version = ''
            # check if items already in app_collection
            i_collection = list(DB.app_collection.find(
                {'identifier': self._identifier,
                 "items": {"$elemMatch": {"trackName": app['trackName']}}}))
            # remove old records directly --- web page has old records kept
            if len(i_collection) != 0:
                items = i_collection[0]["items"]
                for item in items:
                    if item["trackName"] == app['trackName']:
                        DB.app_collection.update(
                            {'identifier': request.args.get('identifier')},
                            {'$pull': {'items':
                                       {'trackName': app['trackName']}}})

            # add new record
            items = {
                'id': int(item_id),
                'country': request.form.getlist('country'),
                'trackName': app['trackName'],
                'cnname': app.get('cnname', ""),
                'arname': app.get('arname', ""),
                'averageUserRating': rating,
                'icon': artworkUrl512_to_114_icon(app['artworkUrl512']),
                'ID': str(app['_id']),
                'bundleId': app['bundleId'],
                'size': file_size_format(app['fileSizeBytes']),
                'version': download_version,
                'superurl': app.get("superurl", ""),
                'superurl_sign': app.get("superurl_sign", "")
            }

            item_list = []
            for ele in data:
                if len(ele['lan']) > 0:
                    temp_item = dict(items)
                    temp_item['sort'] = ele['sort']
                    temp_item['isAdvertisement'] = ele['isAdvertisement']
                    temp_item['language'] = ele['lan']
                    item_list.append(temp_item)

            DB.app_collection.update(
                {'identifier': request.args.get('identifier')},
                {'$push': {'items': {'$each': item_list}}})
            status, message = 'success', ''
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message, '')

class ItemDeleteView(View):
    '''
    应用集合列表删除
    '''
    @route('/item/delete', methods=['GET'], endpoint='admin_app_collection_item_delete')
    def do_request(self):
        try:
            identifier = request.args.get('identifier')
            item_id = request.args.get('id')
            DB.app_collection.update({'identifier': identifier},
                                     {'$pull': {'items': {'ID': item_id}}})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)

class ItemSortView(View):
    '''
    应用集合列表排序
    '''
    @route('/item/sort', methods=['POST'], endpoint='admin_app_collection_item_sort')
    def do_request(self):
        try:
            for key in request.form.keys():
                id = int(key.split('_')[1])
                DB.app_collection.update({'identifier':request.args.get('identifier'), 'items.id':id}, {'$set':{'items.$.sort':int(request.form[key])}})
            status, message = 'success', ''
        except Exception, ex:
            status, message = 'error', str(ex)

        return self._view.ajax_response(status, message)
