#!/usr/bin/python
# coding=UTF-8
'''
@Author: recar
@Date: 2019-05-15 18:40:51
@LastEditTime: 2019-06-05 17:38:40
'''
from lib.parser import get_options
from config.config import BANNER
from lib.core import get_output, run_scripts, asyn_dns
from lib.command import print_log, print_info
import signal
import gevent 
from gevent import monkey;monkey.patch_all()
def ctrl_c(signum,frame):
    print()
    print("[-] input ctrl c")
    exit(1)

signal.signal(signal.SIGINT, ctrl_c)


def main():
    print(BANNER)
    options,args = get_options()
    scan_domain = options.domain
    is_html = options.is_html
    engine = options.engine
    print_info("scan {0}\n".format(scan_domain))
    target_output_txt, target_output_html = get_output(scan_domain)
    # for i in range(10000):
    #     print_log("scan scripts: "+str(i))
    # print()
    engine_result = run_scripts(scan_domain, engine)
    domain_ips = asyn_dns(engine_result)
    print(domain_ips)
    print(len(domain_ips))
    

        

if __name__ == "__main__":
    main()
