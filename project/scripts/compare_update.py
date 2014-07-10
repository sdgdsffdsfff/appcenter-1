#encoding=UTF-8
from collections import defaultdict
import os
import json
import time
import logging
from datetime import datetime
import sys

import requests

logger = logging.getLogger()
logger.setLevel(logging.INFO)

country = ["us", "cn"]

api_id_url = "https://itunes.apple.com/%s/lookup?id="
api_bundleId_url = "https://itunes.apple.com/%s/lookup?bundleId="

host_url = "http://54.183.93.130/"
get_file_url = host_url + "get-file/trackid/"
get_file_failed_url = host_url + "fail-getting-file/"
finish_handle_url = host_url + "finish-handling-file/"
post_file_url = host_url + "post-file/"

group_num = 100
send_num = 10000

WRITE_DIR = "/mnt/spider_result/"


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
	with open(WRITE_DIR + filename, "r") as f:
		lines = group_list(f.readlines(), group_num)
		d = defaultdict(list)
		for line in lines:
			if "." in line:
				url = api_bundleId_url + (",".join(line)).replace("\n", "")
			else:
				url = api_id_url + (",".join(line)).replace("\n", "")

			try:
				res = requests.get(url % country[0], headers=headers)
			except requests.exceptions.ConnectionError as ce:
				print ce, url
				continue
			try:
				data = res.json()
			except Exception as e:
				print e
				continue

			try:
				res_cn = requests.get(url % country[1], headers=headers)
			except requests.exceptions.ConnectionError as ce:
				print ce, url
				continue
			try:
				data_cn = res_cn.json()
			except Exception as e:
				print e
				continue

			results = data.get('results', {})
			results_cn = data_cn.get("results", {})

			[d[rs["trackId"]].append(rs) for rs in results]
			[d[rs["trackId"]].append(rs) for rs in results_cn]

			with open(WRITE_DIR + "%s.json"%filename, "a") as fs:
				for ha in d.values():
					fs.write("[")
					for item in ha:
						try:
							fs.write(json.dumps(item) + ",")
							fs.write("{},"*(len(country) - len(ha)))
						except UnicodeDecodeError as ue:
							print ue, rs
							continue
					fs.write("]\n")
	end = datetime.now()
	print("process takes %s seconds" % (end - start).total_seconds())

def track_need_to_update():
	while True:
		res = requests.post(get_file_url)
		data = res.json()
		if data.get("data", {}).get("appid_file", {}) is None or \
		   data.get("data", {}).get("appid_file", {}) == "None":
			print("date: %s, no job get, try in 1 minute later! waiting..." % (datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
			time.sleep(60 * 1)
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
			with open(WRITE_DIR + file_to_update, "w") as f:
				f.write(raw_res.text)
			try:
				compare_to_apple(file_to_update)
				requests.post(finish_handle_url + oid + "/")
				num_lines = sum(1 for line in open(WRITE_DIR + '%s.json' % file_to_update))
				if num_lines > send_num:
					all_file_content = open(WRITE_DIR + '%s.json' % file_to_update, "r")
					file_piece_list = group_list(all_file_content.readlines(), send_num)
					for index, file_piece in enumerate(file_piece_list):
						files = {'file': ("%s.json-%s" % (file_to_update, index), "\n".join(file_piece))}
						upload_res = requests.post(post_file_url + task_name + "/appinfo/" + str(priority) + "/", files=files)
						print("upload file part-%s status: %s" % (index, upload_res.status_code))
				else:
					files = {'file': open(WRITE_DIR + '%s.json' % file_to_update, 'r')}
					requests.post(post_file_url + task_name + "/appinfo/" + str(priority) + "/", files=files)
				print("upload %s.json success!" % file_to_update)
				#then remove the txt and json file
				os.remove(WRITE_DIR + file_to_update)
				print("file %s removed!" % file_to_update)
				os.remove(WRITE_DIR + file_to_update + ".json")
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
	#compare_to_apple("test.txt")
	#requests.post(get_file_failed_url + "53a645288475b60e77f618f3/")
	# num_lines = sum(1 for line in open('rs.json'))
	# if num_lines > send_num:
	# 	all_file_content = open('rs.json', "r")
	# 	file_piece_list = group_list(all_file_content.readlines(), send_num)
	# 	for index, file_piece in enumerate(file_piece_list):
	# 		files = {'file': ("rs.json-%s" % index, "\n".join(file_piece))}
	# 		res = requests.post(post_file_url + "hot-app/appinfo/10/", files=files)
	# 		print res
	# else:
	# 	files = {'file': open('%s.json' % file_to_update, 'r')}
	# 	requests.post(post_file_url + "hot-app/appinfo/" + str(priority) + "/", files=files)
	# print("upload rs.json success!")

