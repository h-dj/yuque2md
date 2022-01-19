# -*- coding: utf-8 -*-
# Author : huangjiajian
import hashlib
import json
import mimetypes
import os
import re
import uuid
from urllib.parse import urlparse

import requests

from MyYuque import MyYuque

common_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}


def download_image():
    # image_src = "https://g.yuque.com/gr/latex?%5Clog_2%20n%2B1#card=math&code=%5Clog_2%20n%2B1"
    # image_src = "https://cdn.nlark.com/yuque/0/2020/png/438760/1593962284016-avatar/de512e87-8d97-43ec-a53e-72e9a8b7dca6.png"
    # image_src = "https://cdn.nlark.com/yuque/0/2020/jpeg/438760/1597369082994-e5d62267-cee3-49b3-a390-c2953035e00f.jpeg#align=left&display=inline&height=472&margin=%5Bobject%20Object%5D&name=49b4e64cb39814ad995bbde5848e7eac.jpg&originHeight=472&originWidth=1022&size=85643&status=done&style=none&width=1022"
    #image_src = "https://www.yuque.com/attachments/yuque/0/2022/txt/438760/1642494472927-fe03edd4-a6f4-45d7-8e2b-84bc874883f5.txt?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2022%2Ftxt%2F438760%2F1642494472927-fe03edd4-a6f4-45d7-8e2b-84bc874883f5.txt%22%2C%22name%22%3A%22%E6%B5%8B%E8%AF%95%E9%99%84%E4%BB%B6.txt%22%2C%22size%22%3A0%2C%22type%22%3A%22text%2Fplain%22%2C%22ext%22%3A%22txt%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22u3ee0cfae-5f25-486c-bd85-5f75661112c%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u5fb9d639%22%2C%22card%22%3A%22file%22%7D"
    image_src = "https://upload-images.jianshu.io/upload_images/4840929-39a7cf695fe80ca9.gif?imageMogr2/auto-orient/strip#alt=brute-force.gif"
    resp = requests.get(image_src, stream=True, headers=common_header)
    print()
    print(resp.headers.keys())
    print(resp.headers.get('Content-Type'))
    path = os.getcwd() + "/.cache"
    if os.path.isdir(path) is False:
        os.makedirs(path)
    with open(path + "/test.gif", 'wb') as f:
        f.write(resp.content)


def get_file_name():
    # image_src = "https://www.yuque.com/attachments/yuque/0/2022/txt/438760/1642494472927-fe03edd4-a6f4-45d7-8e2b-84bc874883f5.txt?_lake_card=%7B%22src%22%3A%22https%3A%2F%2Fwww.yuque.com%2Fattachments%2Fyuque%2F0%2F2022%2Ftxt%2F438760%2F1642494472927-fe03edd4-a6f4-45d7-8e2b-84bc874883f5.txt%22%2C%22name%22%3A%22%E6%B5%8B%E8%AF%95%E9%99%84%E4%BB%B6.txt%22%2C%22size%22%3A0%2C%22type%22%3A%22text%2Fplain%22%2C%22ext%22%3A%22txt%22%2C%22status%22%3A%22done%22%2C%22taskId%22%3A%22u3ee0cfae-5f25-486c-bd85-5f75661112c%22%2C%22taskType%22%3A%22upload%22%2C%22id%22%3A%22u5fb9d639%22%2C%22card%22%3A%22file%22%7D"
    # image_src = "https://g.yuque.com/gr/latex?%5Clog_2%20n%2B1#card=math&code=%5Clog_2%20n%2B1"
    image_src = "http://www.**.net/images/logo?#xx=xxx&x=xx#xxx.txt"
    filename = os.path.basename(image_src)
    print('-->', filename)

    url = urlparse(image_src)
    print(url)
    print(url.path)
    print(str(url.path).rfind("."))
    print('. --> ', url.path.rfind("."))
    print(url.path[url.path.rfind("."):len(url.path)])


def download_doc():
    token = os.getenv('token')
    yuque2md = MyYuque(api_host="https://www.yuque.com/api/v2", user_token=token)
    _doc_detail_json = yuque2md.docs.get(namespace='h_dj/kd0g9f', slug="czmyit", data={'raw': 1})
    _data = _doc_detail_json['data']
    print(_data['body'])


def re_test():
    md = '''
    <a name="ZBlq3"></a>
    ### aaaaa
    <a name="W1p4e"></a>
    ### 一、下载JDK
    
    <br>
    '''
    md_a_pattern = re.compile(r'<a\s+?name="(\w+?)"></a>')
    print(md_a_pattern.findall(md))
    print(re.sub(md_a_pattern, ' ', md))


if __name__ == '__main__':
    # get_file_name()
    # print(uuid.uuid4())
    # print(hashlib.md5("https://www.yuque.com/api/v2".encode(encoding='utf-8')).hexdigest())
    # print(mimetypes.guess_extension('text/html'))
    download_image()
    # print("text/html".split(';')[0])
    # re_test()
