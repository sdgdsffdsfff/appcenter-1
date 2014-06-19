#encoding=UTF8

import main, hashlib
from flask.ext.login import UserMixin
from __header__ import AdminView, FlaskView
from __header__ import DB, route
from flask.ext.login import current_user
from functools import wraps
from flask import request, abort
from bson.objectid import ObjectId
from flask.ext.login import AnonymousUserMixin

@main.login_manager.user_loader
def load_user(username):
    return User.find_one(username = username)

class User(UserMixin):
    def __init__(self, username, password="", password_hash=None, role="Editor"):
        self.username = username
        self.role = Role.find_one(role)
        if password_hash: self.password_hash = password_hash
        else: self.password_hash = User.encrypt(password)

    @staticmethod
    def encrypt(plain):
        return hashlib.md5(plain).hexdigest()

    @property
    def password(self): raise Exception(u"明文密码不可读")

    @password.setter
    def password(self, plain_password):
        self.password_hash = User.encrypt(plain_password)

    def verify_password(self, plain_password):
        return self.password_hash == User.encrypt(plain_password)

    def get_id(self):
        return unicode(self.username)

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    @staticmethod
    def find_one(username=None):
         c_user = DB.User.find_one({"username": username})
         if not c_user: return None
         return User(c_user["username"], password_hash=c_user["password_hash"], role=c_user["role"])

class Permission:
    MANAGE_APP = 0x01
    MANAGE_EDITOR = 0x02

class Role:
    def __init__(self, role, permissions):
        self.role = role
        self.permissions = permissions

    @staticmethod
    def insert_roles():
        roles = {
            "Editor": Permission.MANAGE_APP,
            "Admin": Permission.MANAGE_APP | Permission.MANAGE_EDITOR
        }
        for r in roles.items():
            DB.Role.insert({"role": r[0], "permissions": r[1]})

    @staticmethod
    def find_one(role=None):
        m_role =  DB.Role.find_one({"role": role})
        if not m_role: return None
        return Role(m_role["role"], m_role["permissions"])

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user or current_user.is_anonymous() or \
               not current_user.can(permission):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class View(FlaskView):
    route_base = '/users-manager'
    def before_request(self, name):
        self._view = AdminView()

class ListView(View):
    @permission_required(Permission.MANAGE_EDITOR)
    @route('/list', endpoint='admin_user_list')
    def get(self):
        user_list = DB.User.find()
        return self._view.render('user_manage', user_list=list(user_list))

class AddView(View):
    @permission_required(Permission.MANAGE_EDITOR)
    @route('/add', methods=['POST'], endpoint='admin_user_add')
    def post(self):
        try:
            if request.form['username'].strip() == "": raise Exception(u"不正确的用户名")
            data = {
                'username': request.form['username'],
                'password_hash': User.encrypt(request.form['password']),
                'role': request.form["role"]
            }
            DB.User.update({"username": request.form['username']}, data, True)
            status, message = 'success', '添加成功'
        except Exception, ex:
            status, message = 'error', str(ex.message)
        return self._view.ajax_response(status, message)

class DeleteView(View):
    @permission_required(Permission.MANAGE_EDITOR)
    @route('/delete', endpoint='admin_user_delete')
    def get(self):
        try:
            _id = request.args.get('_id')
            res = DB.User.remove({'_id': ObjectId(_id)})
            status, message = 'success', '删除成功'
        except Exception, ex:
            status, message = 'error', str(ex)
        return self._view.ajax_response(status, message)
