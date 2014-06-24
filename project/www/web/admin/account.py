#encoding=UTF8
#code by LP
#2013-11-7


from www.lib.form import Form, FormElementField, FormElementSubmit
from __header__ import AdminView, FlaskView, request, session, redirect, url_for, DB
from flask.ext.login import login_user, UserMixin, logout_user, login_required
import main, hashlib
from flask import flash
from __header__ import route
from users import User

class LoginView(FlaskView):

    def before_request(self, name):
        self._view = AdminView()
        self.login_form = Form('login_form', request, session)
        self.login_form.add_field('text', '用户名', 'username', data={'attributes': {'class': 'm-wrap placeholder-no-fix', 'placeholder': 'Username'}})
        self.login_form.add_field('password', '密码', 'password', data={'attributes': {'class': 'm-wrap placeholder-no-fix', 'placeholder': 'Password'}})
        self._view.assign('FormField', FormElementField)

    def get(self):
        return self._view.render('login', title="维享管理系统", form=self.login_form)

    def post(self):
        if not self.login_form.has_error():
            username, password = request.form["username"], request.form["password"]
            user = User.find_one(username=username)
            if user and user.verify_password(password):
                login_user(user)
                return redirect(url_for('admin_genre_list'))
        flash(u"错误的用户名或者密码")
        return self._view.render('login', title="维享管理系统", form=self.login_form)


class LogoutView(FlaskView):
    @route('/admin/logout', endpoint='admin_logout')
    def get(self):
        logout_user()
        return redirect(url_for('LoginView:get'))
