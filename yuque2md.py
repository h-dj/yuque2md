# -*- coding: utf-8 -*-
# Author : huangjiajian

import argparse
import hashlib
import json
import mimetypes
import re
import sys
import typing
import os
import uuid
from urllib.parse import urlparse
import requests

from MyYuque import MyYuque

cache_dir = os.getcwd() + '/.cache'
# 匹配图片URL的正则
pic_pattern = re.compile(r'!\[.*?\]\((.*?)\)', re.S)
md_a_pattern = re.compile(r'<a\s+?name="(\w+?)"></a>', re.S)
md_br_pattern = re.compile(r'<br\s+?/>', re.S)
md_blank_pattern = re.compile(u'[\u200B]', re.S)


class Yuque2md(object):

    def __init__(self):
        parser = argparse.ArgumentParser(description="cmd arguments")
        parser.add_argument("--save_path", type=str, default=os.getcwd() + "/save_file_md")
        parser.add_argument("--token", type=str, default="")
        parser.add_argument("--login", type=str, default="")
        parser.add_argument("--api_host", type=str, default="https://www.yuque.com/api/v2")
        args = parser.parse_args()

        if args.token == "" or args.login == "":
            print("specify token first!!!")
            sys.exit(0)
        self.api_host = args.api_host
        self.save_path = args.save_path
        self.token = args.token
        self.login = args.login
        self.yuque = MyYuque(api_host=self.api_host, user_token=self.token)

    def get_user_repos(self, login_id: str, params: typing.Dict = {'type': 'Book', 'offset': 0}):
        """
        获取用户的所有知识库列表
        :return:
        """
        repos_json = self.yuque.repos.list(user=login_id, data=params)
        repos_list = repos_json['data']
        size = len(repos_list)
        if size > 0:
            params['offset'] = params['offset'] + size + 1
            temp_list = self.get_user_repos(login_id, params)
            return temp_list + repos_list
        else:
            return repos_list

    def get_repos_toc(self, repo_namespace):
        """
        获取仓库下目录
        :return:
        """
        cache_toc_path = cache_dir + '/toc/' + repo_namespace
        cache_toc_path_file = cache_toc_path + '/toc.json'
        # 判断结果
        if not os.path.exists(cache_toc_path):
            os.makedirs(cache_toc_path)

        if os.path.isfile(cache_toc_path_file):
            with open(cache_toc_path_file, 'r') as f:
                toc_json_str = f.read()
                toc_json = json.loads(toc_json_str)
                return toc_json['data']
        else:
            toc_json = self.yuque.repos.toc(repo_namespace)
            with open(cache_toc_path_file, 'w') as f:
                f.write(json.dumps(toc_json, ensure_ascii=False))
            return toc_json['data']

    def get_user_docs(self, repo_namespace, slug, raw=1):
        """
        获取文档详情
        :return:
        """
        doc_json_path = os.path.join(cache_dir, 'docs', repo_namespace)
        doc_json_file_path = os.path.join(doc_json_path, slug + '.json')

        # 判断结果
        if not os.path.exists(doc_json_path):
            os.makedirs(doc_json_path)

        if os.path.isfile(doc_json_file_path):
            try:
                with open(doc_json_file_path, 'r', encoding='utf-8') as f:
                    doc_json_str = f.read()
                    if doc_json_str is '':
                        print('----------------> 删除错误文件 ', doc_json_file_path)
                        os.remove(doc_json_file_path)
                    else:
                        _doc = json.loads(doc_json_str)
                        title = _doc['data']['title']
                        print('---> 解析文档(缓存) --->', title, '---', repo_namespace, ' -- ', slug)
                        return _doc
            except:
                print(doc_json_file_path)
                os.remove(doc_json_file_path)
        else:
            print('---> 解析文档 --->', repo_namespace, ' -- ', slug)
            doc_json = self.yuque.docs.get(namespace=repo_namespace, slug=slug, data={'raw': raw})
            with open(doc_json_file_path, 'w', encoding='utf-8') as f:
                if doc_json is not None and doc_json is not '':
                    f.write(json.dumps(doc_json, ensure_ascii=False))
            title = doc_json['data']['title']
            print('--->  ---> ---> --->', title)
            return doc_json

    @staticmethod
    def get_toc_path(repos_name, toc_map, cur_toc):
        """
               获取父目录
               :param repos_name:
               :param toc_map: toc 字典
               :param cur_toc: 当前toc
               :return:
               """
        parent_uuid = cur_toc['parent_uuid']
        # 如果是空，则返回
        if parent_uuid is None or parent_uuid == '':
            return repos_name
        toc_temp = toc_map[parent_uuid]
        toc_path = ''
        while toc_temp is not None:
            parent_uuid = toc_temp['parent_uuid']
            title = toc_temp['title']
            toc_path = os.path.join(title, toc_path)
            if parent_uuid is None or parent_uuid == '':
                return os.path.join(repos_name, toc_path)
            toc_temp = toc_map[parent_uuid]
        return ''

    @staticmethod
    def format_doc(md_content) -> str:
        """
        格式化md 文档，去掉多余字符
        :param md_content:
        :return:
        """
        md_content = re.sub(md_a_pattern, '', md_content)
        md_content = re.sub(md_br_pattern, '\n', md_content)
        md_content = re.sub(md_blank_pattern, ' ', md_content)
        return md_content

    @staticmethod
    def get_image_url(md_content) -> list:
        image_url_list = re.findall(pic_pattern, md_content)
        return image_url_list

    @staticmethod
    def get_file_name(content_type, url) -> str:
        """
        生成文件名称
        :param content_type:
        :param url:
        :return:
        """
        try:
            path = urlparse(url).path
            len_path = len(path)
            dot_index = path.rfind(".")
            if dot_index == -1:
                mimetype = content_type.split(';')[0]
                suffix = mimetypes.guess_extension(mimetype)
            else:
                suffix = path[dot_index:len_path]
            return hashlib.md5(url.encode(encoding='utf-8')).hexdigest() + suffix
        except:
            print('url ', url)
        return None

    @staticmethod
    def download_image(cur_path, image_list: list, repo_namespace, slug) -> dict:
        """
        离线图片，下载到当前文件夹下的 asserts 目录中
        :param image_list:
        :param cur_path: 当前路径
        :param repo_namespace:
        :param slug:
        :return:
        """
        image_dict = {}
        image_dict_path = os.path.join(cache_dir, 'url', repo_namespace)
        image_dict_file_path = os.path.join(image_dict_path, slug + '.json')

        if not os.path.exists(image_dict_path):
            os.makedirs(image_dict_path)
        if os.path.isfile(image_dict_file_path):
            with open(image_dict_file_path, 'r', encoding='utf-8') as f:
                image_dict_json = f.read()
                image_dict = json.loads(image_dict_json)

        image_relative_path = 'asserts'
        for image_src in image_list:
            if image_dict.get(image_src):
                print('-- skip download file -------->', image_src)
                continue

            image_absolute_path = os.path.join(cur_path, image_relative_path)
            if os.path.exists(image_absolute_path) is False:
                os.makedirs(image_absolute_path)

            if image_src.startswith("http") is False:
                print('-----------> 非法图片', image_src)
                continue
            print('-----------> download_image ', image_src)
            resp = requests.get(image_src, stream=True)
            if resp.status_code != 200:
                print('-----------> 非法响应吗: ', resp.status_code, image_src)
                continue
            file_name = Yuque2md.get_file_name(resp.headers.get('Content-Type'), image_src)
            image_file_absolute_path = os.path.join(image_absolute_path, file_name)
            with open(image_file_absolute_path, 'wb') as f:
                f.write(resp.content)
                image_dict[image_src] = os.path.join(image_relative_path, file_name)

        # 缓存当前的image_dict
        with open(image_dict_file_path, 'w', encoding='utf-8') as f:
            f.write(json.dumps(image_dict, ensure_ascii=False))

        return image_dict

    def start(self):
        # 获取用户的所有仓库
        repos_list = self.get_user_repos(login_id=self.login)
        for repos in repos_list:
            repo_name = repos['name']
            repo_namespace = repos['namespace']
            print('解析仓库 --->', repo_name)
            # 获取仓库下的 toc
            _toc_list = self.get_repos_toc(repo_namespace=repo_namespace)
            _toc_dict = {}
            for _toc in _toc_list:
                _toc_dict[_toc['uuid']] = _toc

            for _toc in _toc_list:

                _toc_title = _toc['title']
                _toc_url = _toc['url']
                _toc_doc_id = _toc['doc_id']
                _toc_type = _toc['type']

                # 过滤掉未发布文档
                if _toc_type == 'UNCREATED_DOC':
                    print('---> 文档未发布 ----> ', _toc_title)
                    continue

                _path = self.get_toc_path(repos_name=repo_name, toc_map=_toc_dict, cur_toc=_toc)
                _md_path = os.path.join(self.save_path, _path)

                # 创建目录
                if os.path.exists(_md_path) is False:
                    os.makedirs(_md_path)

                # 获取文档详情
                if _toc_url != '':
                    _doc_detail_json = self.get_user_docs(repo_namespace=repo_namespace, slug=_toc_url)
                    if _doc_detail_json is None and _doc_detail_json is '':
                        print('--->  ---> 解析失败', _toc_title)
                        continue
                    _data = _doc_detail_json['data']
                    _doc_title = _data['title']
                    _doc_body = self.format_doc(_data['body'])
                    image_list = self.get_image_url(_doc_body)
                    _image_dict = self.download_image(_md_path, image_list, repo_namespace, _toc_url)
                    for _image_src in _image_dict:
                        _doc_body = _doc_body.replace(_image_src, _image_dict[_image_src])

                    _md_file_path = os.path.join(_md_path, _toc_title + '.md')
                    with open(_md_file_path, 'w', encoding='utf-8') as f:
                        f.write(_doc_body)


if __name__ == '__main__':
    yuque2md = Yuque2md()
    yuque2md.start()
