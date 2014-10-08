# -*- coding: utf-8 -*-
'''
Created on 2013-4-10

@author: pcl
'''

import zipfile,biplist,os

def read_plist(plist_data):
    '''
    读取plist信息
    @param plist_data: plist数据
    '''

    plist = biplist.readPlistFromString(plist_data)

    info = {}
    info['bundleid'] = plist['CFBundleIdentifier']
    info['shortversion'] = ''
    info['bundleversion'] = ''
    try:
        info['version'] = info['shortversion'] = plist['CFBundleShortVersionString']
    except:
        info['version'] = plist['CFBundleVersion']
    try:
        info['bundleversion'] = plist['CFBundleVersion']
    except:
        pass
    try:
        info['min_os_version'] = plist['MinimumOSVersion']
    except:
        info['min_os_version'] = ''
    try:
        info['support_iphone'] = 0
        if 1 in plist['UIDeviceFamily']:
            info['support_iphone'] = 1
    except:
        info['support_iphone'] = None

    try:
        info['support_ipad'] = 0
        if 2 in plist['UIDeviceFamily']:
            info['support_ipad'] = 1
    except:
        info['support_ipad'] = None

    return info
       
def get_info_from_ipa(zipfilename):
    '''
    从ipa中提取信息
    @param zipfilename: ipa包
    '''
    #解压提取info.plist信息
    z = zipfile.ZipFile(zipfilename, 'r')
    for name in z.namelist():
        name = name.replace('\\','/')
        nameArr = name.split('/')
        if name[-11:] == '/Info.plist' and len(nameArr) == 3:
            return read_plist(z.read(name))    
    raise Exception('NO_PLIST_FILE')

def check_sign_from_ipa(zipfilename):
    f_zip = zipfile.ZipFile(zipfilename, 'r')
    for f in f_zip.namelist():
        index = f.find("_CodeSignature/CodeResources")
        if index > 0:
            f_zip.close()
            return 1
    f_zip.close()
    return 0
