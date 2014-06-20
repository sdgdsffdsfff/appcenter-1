import json


def update_app_info():
    for line in file("/Users/qijianbiao/Desktop/example.txt", "r"):
        app_info = json.loads(line)
        print app_info
