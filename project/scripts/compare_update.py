#encoding=UTF-8
import os
import json
import time
import logging
from datetime import datetime
import sys

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

api_url = "https://itunes.apple.com/cn/lookup?id="

host_url = "http://54.183.93.130/"
get_file_url = host_url + "get-file/trackid/"
get_file_failed_url = host_url + "fail-getting-file/"
finish_handle_url = host_url + "finish-handling-file/"
post_file_url = host_url + "post-file/"

group_num = 100
send_num = 10000


def group_list(l,block):
    size = len(l)
    return [l[i:i+block] for i in range(0,size,block)]

def compare_to_apple(filename):
	"""here we read all content to memory"""
	start = datetime.now()
	headers = {
		'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36',
		"Accept-Encoding": "gzip,deflate,sdch",
		"Host": "itunes.apple.com"
	}
	with open(filename, "r") as f:
		lines = group_list(f.readlines(), group_num)
		for line in lines:
			url = api_url + (",".join(line)).replace("\n", "")
			try:
				res = requests.get(url, headers=headers)
			except requests.exceptions.ConnectionError as ce:
				print ce, url
				continue
			try:
				data = res.json()
			except Exception as e:
				print e
				continue
			results = data.get("results", {})
			for rs in results:
				with open("%s.json"%filename, "a") as fs:
					try:
						fs.write(json.dumps(rs) + "\n")
					except UnicodeDecodeError as ue:
						print ue, rs
						continue
	end = datetime.now()
	print("process takes %s seconds" % (end - start).total_seconds())

def track_need_to_update():
	while True:
		res = requests.post(get_file_url)
		data = res.json()
		if data.get("data", {}).get("appid_file", {}) is None or \
		   data.get("data", {}).get("appid_file", {}) == "None":
			print("no job get, try in 5 minute later! waiting...")
			time.sleep(60 * 5)
			continue
		oid = data.get("data", {}).get("appid_file", {}).get("_id", {}).get("$oid", "")
		if data.get("code", "")  == 0:
			file_type = data.get("data", {}).get("appid_file", {}).get("file_type", "")
			file_name = data.get("data", {}).get("appid_file", {}).get("filename", "")
			priority = data.get("data", {}).get("appid_file", {}).get("priority", "")
			task_name = data.get("data", {}).get("appid_file", {}).get("task_name", "")
			try:
				raw_res = requests.get(file_name)
				if raw_res.status_code == 404:
					print("download %s failed!" % file_name)
					continue
			except requests.exceptions.ConnectionError as ec:
				print ec
				requests.post(get_file_failed_url + oid + "/")
			file_to_update = file_name.split("/")[-1]
			with open(file_to_update, "w") as f:
				f.write(raw_res.text)
			try:
				compare_to_apple(file_to_update)
				requests.post(finish_handle_url + oid + "/")
				files = {'file': open('%s.json' % file_to_update, 'r')}
				requests.post(post_file_url + task_name + "/appinfo/" + str(priority) + "/", files=files)
				print("upload %s.json success!" % file_to_update)
				#then remove the txt and json file
				os.remove(file_to_update)
				print("file %s removed!" % file_to_update)
				os.remove(file_to_update + ".json")
				print("file %s.json removed!" % file_to_update)
			except requests.exceptions.ConnectionError as ce:
				print ce
				requests.post(get_file_failed_url + oid + "/")
		else:
			requests.post(get_file_failed_url + oid + "/")


def read_in_chunks(file_object, chunk_size=1024):
    """Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k."""
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data


if __name__ == '__main__':
	track_need_to_update()
	#requests.post(get_file_failed_url + "53a3b9dc8475b6064bf5f020/")

