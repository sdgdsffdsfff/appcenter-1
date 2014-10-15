#encoding=UTF8
#code by LP
#2014-06-16

import os
import urllib
from collections import OrderedDict
from conf.settings import settings, DOMAIN_URL
from common.ng_mongo import NGMongoConnect
from urllib import urlencode, quote

mongo = NGMongoConnect(settings['mongodb']['host'], replica_set=settings["mongodb"].get("replica_set", None))
mongo_db = mongo.get_database('appcenter')

class ClientController(object):

	def get_latest_version(self, client_type, language="zh-Hans"):
		res = mongo_db.client.find({"type":client_type, "review": "true"}).sort('build', -1).limit(1)
		try:
			client = res[0]
		except:
			return {}
		return {
			'clientType': client_type,
			'version': client['version'], 
			'build': client['build'], 
			'description': client['desc'],
			'fileURL': os.path.join(settings['client_url_host'], client['store_path']),
                        'plistURL': quote("https://ssl-api.appvv.com/update.plist?type=%s&language=%s" % (client_type, language))
		}

	def get_latest_version_plist(self, client_type, language="zh-Hans"):
		data = self.get_latest_version(client_type)
		if str(client_type).find('signed') != -1:
			bundle_id = 'com.appvv.vsharenojbhz'
		else:
			bundle_id = 'com.appvv.vsharejbhz'
		plist = """
                <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
                <?xml version="1.0" encoding="UTF-8"?>
			<plist version="1.0">
				<dict>
					<key>items</key>
					<array>
						<dict>
							<key>assets</key>
							<array>
								<dict>
									<key>kind</key>
									<string>software-package</string>
									<key>url</key>
									<string>{0}</string>
								</dict>
								<dict>
									<key>kind</key>
									<string>display-image</string>
									<key>needs-shine</key>
									<false/>
									<key>url</key>
									<string>http://pic.appvv.com/vshare_{1}.png</string>
								</dict>
							</array>
							<key>metadata</key>
							<dict>
								<key>bundle-identifier</key>
								<string>{2}</string>
								<key>kind</key>
								<string>software</string>
								<key>bundle-version</key>
								<string>{3}</string>
								<key>subtitle</key>
								<string>vshare</string>
								<key>title</key>
								<string>vshare{4}(Jail Break)</string>
							</dict>
						</dict>
					</array>
				</dict>
			</plist>
		""".format(data['fileURL'], client_type, bundle_id, data['version'], data['version'])

		return plist.strip()
