#encoding=UTF8
#code by LP
#2013-12-25

from header import *


class AppSearchController(ControllerBase):

	def __init__(self, language='EN'):
		#语言
		self.request_language = language_code_format(language)

	def query(self, word, page=1, page_size=12):
		pass