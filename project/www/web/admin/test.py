# -*- coding: utf-8 -*-
# Created by pengchangliang on 14-4-9.

from flask.ext.classy import FlaskView

from flask import Flask
from flask.ext.classy import FlaskView

# we'll make a list to hold some quotes for our app
quotes = [
    "A noble spirit embiggens the smallest man! ~ Jebediah Springfield",
    "If there is a way to do it better... find it. ~ Thomas Edison",
    "No one knows what he can do till he tries. ~ Publilius Syrus"
]

app = Flask(__name__)

class QuotesView(FlaskView):
    def index(self):
        return "<br>".join(quotes)