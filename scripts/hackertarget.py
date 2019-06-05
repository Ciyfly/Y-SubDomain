#!/usr/bin/python
# coding=UTF-8
'''
@Author: recar
@Date: 2019-05-30 18:05:15
@LastEditTime: 2019-05-31 16:47:38
'''
from lib.base import Base
from lib.command import print_error
import requests

class Scan(Base):
    def __init__(self, scan_domain):
        super().__init__(scan_domain)
        self.name = "hackertarget"
        self.base_url = "https://api.hackertarget.com/hostsearch/?q={0}"

    def run(self):
        try:
            get_url = self.base_url.format(self.scan_domain)
            response = requests.get(get_url)
            if response.status_code == 200:
                for data in response.text.split("\n"):
                    domain = data.split(",")[0]
                    self.sub.add(domain)
                return self.sub
            else:
                return set()
        except Exception as e:
            print_error("ERROR: "+self.name+" : "+str(e))