#encoding=UTF8
#code by LP
#2013-11-11

import cjson
import os, main
import shutil
from werkzeug import secure_filename

from conf.settings import settings
from www.controller.app.header import (mongo_db, redis_master, sha1_of_file, redis_ap_master,
                                       hash_to_path, create_pic_url_by_path, file_size_format)
from www.web.base import WebView
from flask.ext.classy import FlaskView, route
from flask import redirect, session, request, url_for
from flask.ext.login import current_user
import uuid

DB = mongo_db
rsm = redis_ap_master

def upload_hash_file(file, target_dir, allow_ext=['png', 'jpg', 'jpeg']):
    '''
    上传文件
    '''
    if file:
        #filename = secure_filename(file.filename)
        filename = file.filename.lower()
        if '.' not in filename or filename.rsplit('.', 1)[1] not in set(allow_ext):
            raise Exception('文件类型不允许上传')
        filename = str(uuid.uuid1()) + "." + filename.rsplit('.', 1)[1]
        tmpfile = os.path.join(settings['tmp_dir'], filename)
        file.save(tmpfile)
        hash_str = sha1_of_file(tmpfile)
        save_file = '%s.%s' % (hash_to_path(hash_str), filename.rsplit('.', 1)[1])
        abs_save_file = os.path.join(target_dir, save_file)
        save_file_dir = os.path.dirname(abs_save_file)
        if not os.path.exists(save_file_dir):
            os.makedirs(save_file_dir)
        shutil.move(tmpfile, abs_save_file)
    else:
        raise Exception('上传失败')

    return hash_str, abs_save_file, save_file

def upload_client_file(file, name, version, fileversion, review, target_dir, allow_ext=['ipa']):
    '''
    上传文件
    :param file: File object
    :type file: File object
    :param name: if review is "true" save the file with this name
    :type: str
    :param version:  the last client version with same client type
    :type version: str
    :param fileversion:  the file version
    :type fileversion: str
    :param review: if review is "true" save the file with param name
    :type review: str
    :param target_dir: the target folder the save the file object
    :type target_dir: str
    '''
    if file:
        filename = secure_filename(file.filename)
        filename = filename.lower()
        if '.' not in filename or filename.rsplit('.', 1)[1] not in set(allow_ext):
            raise Exception('文件类型不允许上传')
        tmpfile = os.path.join(settings['tmp_dir'], name)
        file.save(tmpfile)
        if review == "true":
            dest = os.path.join(target_dir, name)
        else:
            dest = os.path.join(target_dir, filename)
        changed = False
        fileName, fileExtension = os.path.splitext(dest)
        if os.path.isfile(dest):
            if review == "true":
                changed = True
                new_file_path = fileName + version + fileExtension
                shutil.move(dest, new_file_path)
                shutil.move(tmpfile, dest)
            else:
                new_file_path = fileName + fileversion + fileExtension
                shutil.move(tmpfile, new_file_path)
        else:
            shutil.move(tmpfile, dest)
            new_file_path = fileName + fileversion + fileExtension
    else:
        raise Exception('上传失败')
    if review == "true":
        return "/".join(dest.split("/")[3:]), changed
    return "/".join(new_file_path.split("/")[3:]), changed

def language_code_to_name(codes):
    '''
    语言代码转为语言名称
    '''
    output = []
    for code in codes:
        res = mongo_db.client_support_language.find_one({'code': code})
        tmp = res['name'] if res else code
        output.append(tmp)
    return output

def country_code_to_name(codes):
    '''
    语言代码转为语言名称
    '''
    output = []
    for code in codes:
        res = mongo_db.country.find_one({'code':code})
        tmp = res['name'] if res else code
        output.append(tmp)
    return output


class AdminView(WebView):

    def __init__(self):

        super(AdminView, self).__init__(__file__)
        self.assign('layout', request.args.get('layout', 'default'))

