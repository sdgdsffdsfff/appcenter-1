# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-3-15.

import app
import site

urls = [
    #common api
    ('/', site.Index),
    ('/apps', app.RequestList),
    ('/app/<string:bundleid>', app.RequestByBundleid),
    ('/search', app.Search),
]