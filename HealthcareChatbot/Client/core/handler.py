# -*- coding:utf-8 -*-
# handler模块中只有一个ArgvHandler类；
# 在main模块中也是实例化了一个ArgvHandler类的对象，并将调用参数传递进去；
# 首先，初始化方法会保存调用参数，然后执行parse_args()方法分析参数；
# 如果ArgvHandler类有参数指定的功能，则执行该功能，如果没有，打印帮助说明。
# 目前ArgvHandler类只有两个核心方法：collect_data和report_data；
# collect_data收集数据并打印到屏幕，用于测试；report_data方法才会将实际的数据发往服务器。
# 数据的收集由info_collection.InfoCollection类负责，一会再看；
# report_data方法会将收集到的数据打包到一个字典内，并转换为json格式；
# 然后通过settings中的配置，构造发送目的地url；
# 通过Python内置的urllib.parse对数据进行封装；
# 通过urllib.request将数据发送到目的url；
# 接收服务器返回的信息；
# 将成功或者失败的信息写入日志文件中。

import json
import time
import urllib.parse
import urllib.request
from core import info_collection
from conf import settings


class ArgvHandler(object):

    def __init__(self, args):
        self.args = args
        self.parse_args()

    def parse_args(self):
        """
        分析参数，如果有参数指定的方法，则执行该功能，如果没有，打印帮助说明。
        :return:
        """
        if len(self.args) > 1 and hasattr(self, self.args[1]):
            func = getattr(self, self.args[1])
            func()
        else:
            self.help_msg()

    @staticmethod
    def help_msg():
        """
        帮助说明
        :return:
        """
        msg = '''
        参数名               功能

        collect_data        测试收集硬件信息的功能

        report_data         收集硬件信息并汇报
        '''
        print(msg)

    @staticmethod
    def collect_data():
        """收集硬件信息,用于测试！"""
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        print(asset_data)

    @staticmethod
    def report_data():
        """
        收集硬件信息，然后发送到服务器。
        :return:
        """
        # 收集信息
        info = info_collection.InfoCollection()
        asset_data = info.collect()
        # 将数据打包到一个字典内，并转换为json格式
        data = {"asset_data": json.dumps(asset_data)}
        # 根据settings中的配置，构造url
        url = "http://%s:%s%s" % (settings.Params['server'], settings.Params['port'], settings.Params['url'])
        print('正在将数据发送至： [%s]  ......' % url)
        try:
            # 使用Python内置的urllib.request库，发送post请求。
            # 需要先将数据进行封装，并转换成bytes类型
            data_encode = urllib.parse.urlencode(data).encode()
            response = urllib.request.urlopen(url=url, data=data_encode, timeout=settings.Params['request_timeout'])
            print("\033[31;1m发送完毕！\033[0m ")
            message = response.read().decode()
            print("返回结果：%s" % message)
        except Exception as e:
            message = '发送失败' + "   错误原因：  {}".format(e)
            print("\033[31;1m发送失败，错误原因： %s\033[0m" % e)
        # 记录发送日志
        with open(settings.PATH, 'ab') as f:  # 以byte的方式写入，防止出现编码错误
            log = '发送时间：%s \t 服务器地址：%s \t 返回结果：%s \n' % (time.strftime('%Y-%m-%d %H:%M:%S'), url, message)
            f.write(log.encode())
            print("日志记录成功！")