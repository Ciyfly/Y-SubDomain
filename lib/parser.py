#!/usr/bin/python
# coding=UTF-8
'''
@Author: recar
@Date: 2019-05-30 16:07:49
@LastEditTime: 2019-05-30 17:59:14
'''
from optparse import OptionParser
from config.config import VERSION
USAGE = "python domain -d xxx.com"
import sys
def get_options():
    parser = OptionParser(usage=USAGE,version=VERSION)

    parser.add_option('-d', type=str, dest="domain", help="指定要测试的域名")

    parser.add_option('--html',action='store_true', dest="is_html", default=False, help="是否生成html报告")
    (options,args) = parser.parse_args()
    if  options.domain==None:
        parser.print_help()
        sys.exit(0)
    if "www" in options.domain or "http://" in options.domain :
        options.domain =options.domain.replace("www","").replace("http://", "")
    return options,args