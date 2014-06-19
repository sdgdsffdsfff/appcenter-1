#encoding=UTF8
#code by LP
#2013-11-7


from __header__ import AdminView, FlaskView, route, request, session, redirect
from flask.ext.login import login_required

class DashboardView(FlaskView):

    def before_request(self, name):
        self._view = AdminView()

    @route('/index', endpoint='admin_index_dashboard')
    @login_required
    def get(self):
        return self._view.render('dashboard', title="维享管理系统")
