#!/usr/bin/import pdb;pdb.set_trace()
# coding=UTF-8
'''
@Author: recar
@Date: 2019-05-30 17:49:08
LastEditTime: 2021-05-20 17:19:42
'''

import sys
sys.path.append("..")
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
from collections import defaultdict
from y_subdomain.config.html_template import (
    html_head, html_title, html_body_head, html_body_title,
    html_body_a, html_body_end, html_style
                )

from y_subdomain.config.config import DNS_THRESHOLD
import dns
from dns import resolver
import os
import importlib
import ipaddress
import sys
import re
import json
import random
import string
import queue
import threading
import time
import signal


def ctrl_c(signum,frame):
    print()
    print("[-] input ctrl c")
    sys.exit()

# def print_queue_size(signum, frame):
#     print()
#     print(f"[*] queue size: {frame.f_locals['self'].sub_dict_queue.qsize()}")
#     print(f"[*] find subdomain: {len(frame.f_locals['self'].domain_ips_dict)}")

# ctrl+c
signal.signal(signal.SIGINT, ctrl_c)
# HUP
# signal.signal(signal.SIGHUP, print_queue_size)

def print_log(message):
    # ljust(50) 实现长度不够存在显示残留 左对齐以空格达到指定长度
    print ("\r[*] {0}".format(message).ljust(50), end="")

def print_flush():
    print ("\r\r", end="")

def print_info(message):
    print(("[+] {0}".format(message)))

def print_debug(message):
    print("[*] {0}".format(message))

def print_error(message):
    print(("\n[-] {0}".format(message)))

def print_progress(currne_size, all_size, start, find_size):
    """输出进度条
    :param currne_size 当前队列大小
    :param all_size 总体队列大小
    :param start 开启时间
    :param find_size 找到多少条
    """
    out_u = int(currne_size/all_size*50) # ##
    out_l = 50 - out_u
    percentage = 100-(currne_size/all_size*100)
    use_time = time.perf_counter() - start
    print(
        '\r'+'[' + '>' * out_l + '-' * out_u +']'
        + f'{percentage:.2f}%'
        + f'|size: {currne_size}'
        + f'|use time: {use_time:.2f}s'
        + f'|find: {find_size} ', end="")

class SaveDate(object):
    """用于保存域名结果"""
    def __init__(
        self, scan_domain, engine_domain_ips_dict=None, exh_domain_ips_dict=None,
            is_text=False, is_json=False, is_html=False
            ):
        self.engine_domain_ips_dict = engine_domain_ips_dict
        self.exh_domain_ips_dict = exh_domain_ips_dict
        self.domain_ips_dict = dict()
        self.clean_data()
        self.scan_domain = scan_domain
        self.is_text = is_text
        self.is_json = is_json
        self.is_html = is_html

        self.get_output()

    def clean_data(self):
        if self.engine_domain_ips_dict and not self.exh_domain_ips_dict:
            # 只有 engine_domain_ips_dict
            self.domain_ips_dict = self.engine_domain_ips_dict
        elif self.exh_domain_ips_dict and not self.engine_domain_ips_dict:
            # 只有 exh_domain_ips_dict
            self.domain_ips_dict = self.exh_domain_ips_dict
        elif self.engine_domain_ips_dict and self.exh_domain_ips_dict:
            # 都有
            for domain, ips in self.engine_domain_ips_dict.items():
                if domain in self.exh_domain_ips_dict.keys():
                    self.exh_domain_ips_dict[domain] = self.exh_domain_ips_dict[domain] + ips
                else:
                    self.exh_domain_ips_dict[domain] = ips
            self.domain_ips_dict = self.exh_domain_ips_dict

    def get_output(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(base_path, "../", "output", self.scan_domain)
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir)
        self.out_out_dir = output_dir
        self.output_txt = os.path.join(output_dir, "subdomain_ips.txt")
        self.output_html = os.path.join(output_dir, "subdomain_ips.html")
        self.output_json = os.path.join(output_dir, "subdomain_ips.json")

    def save_text(self):
        with open(self.output_txt, "w") as f:
                for domain, ips in self.domain_ips_dict.items():
                    f.write(f"{domain}    {ips}\n")
        print_info("save txt success\n")

    def save_json(self):
        with open(self.output_json, "w") as f:
            json.dump(self.domain_ips_dict, f, indent=3)
        print_info("save json success\n")

    def save_html(self):
        html = html_head
        html +=  html_title.format(self.scan_domain)
        html += html_body_head
        html += html_body_title.format(self.scan_domain)
        for domain in self.domain_ips_dict.keys():
            html += html_body_a.format(domain)
        html += html_body_end
        html += html_style
        with open(self.output_html, "w") as f:
            f.write(html)
        print_info("save html success\n")

    def save_other(self):
        subdomain_txt = os.path.join(self.out_out_dir, "subdomain.txt")
        ip_txt = os.path.join(self.out_out_dir, "ip.txt")
        ipc_txt = os.path.join(self.out_out_dir, "ipc.txt")
        domains = self.domain_ips_dict.keys()
        ips_list = self.domain_ips_dict.values()
        ipcs = list()
        for ips in ips_list:
            for ip in ips:
                ip_net = ".".join([str(i) for i in ip.split(".")[0:-1]+[0]])
                ipcs.append(ip_net+"/24")
        ipcs = list(set(ipcs))
        with open(subdomain_txt, "w") as f:
            for domain in domains:
                f.write(domain+"\n")
        with open(ip_txt, "w") as f:
            for ips in ips_list:
                for ip in ips:
                    f.write(ip+"\n")
        with open(ipc_txt, "w") as f:
            for ipc in ipcs:
                f.write(ipc+"\n")

    def save_doamin_ips(self):
        # 应朋友需求这里将结果都分开
        if not self.domain_ips_dict: # 空的话就不保存文件
            return
        print_info(f"output_dir {self.out_out_dir}")
        if self.is_text:
            self.save_text()
        if self.is_json:
            self.save_json()
        if self.is_html:
            self.save_html()
        self.save_other()
        return self.domain_ips_dict

class EngineScan(object):
    """接口解析类
    :param scan_domain 测试域名
    :param engine 指定引擎列表 默认全部
    :param thread_count 线程 默认100
    :param get_black_ip 是否返回泛解析的ip 默认不返回
    :param is_private 是否保留内网ip 默认不保留
    :return domain_ips_dict, (black_ip) 选择返回泛解析ip则有第二个 否则只返回域名对于ip
    
    """
    def __init__(self, scan_domain, engine=None, thread_count=100, get_black_ip=False, is_private=False):
        self.scan_domain = scan_domain
        self.engine = engine
        self.thread_count = thread_count
        # dns
        #self.resolver = resolver
        self.resolver = dns.resolver.Resolver()
        # 设置dns超时时间
        self.resolver.timeout = 2
        self.resolver.lifetime = 2
        #self.resolver.nameservers=['8.8.8.8', '114.114.114.114']
        # 存储变量
        self.domains_set = set()
        self.domain_ips_dict = defaultdict(list)
        self.get_black_ip = get_black_ip
        # 去除泛解析
        self.black_ip = list()
        # {ip:{ domains: [域名], count: 计数}  }
        self.ip_domain_count_dict = dict()
        # 去除内网ip
        self.is_private = is_private
    def add_domain(self, domains):
        # 去除掉其他后缀不是 .scan_domain的域名
        for domain in domains:
            if domain.endswith(f".{self.scan_domain}"):
                self.domains_set.add(domain)
        
    def run_scripts(self):
        base_path = os.path.dirname(os.path.abspath(__file__))
        scripts_path = os.path.join(base_path, "../","scripts")
        # 添加到搜索路径
        sys.path.append(scripts_path)
        scrips_list = list()
        scripts_class = list()
        if not self.engine: # 没有指定引擎 遍历scrips文件夹
            for root, dirs, files in os.walk(scripts_path):  
                for filename in files:
                    name = os.path.splitext(filename)[0]
                    suffix = os.path.splitext(filename)[1]
                    if suffix == '.py' and name!="base":
                        metaclass=importlib.import_module(os.path.splitext(filename)[0])
                        # 通过脚本的 enable属性判断脚本是否执行  
                        if metaclass.Scan(self.scan_domain).enable:
                            print_info("run script: "+metaclass.Scan(self.scan_domain).name)
                            result = metaclass.Scan(self.scan_domain).run()
                            self.add_domain(result)
                            print_info(f"add: {len(result)}  all count: {len(self.domains_set)}")
        else: # 指定了引擎
            for name in self.engine: # 这里不判断是否开启引擎 直接使用
                metaclass=importlib.import_module(name)
                print_info("run script: "+metaclass.Scan(self.scan_domain).name)
                result = metaclass.Scan(self.scan_domain).run()
                self.domains_set = self.domains_set | result
                print_info(f"add {len(result)}  all count: {len(self.domains_set)}")
                        
    def threadpool_dns(self):
        pool = ThreadPoolExecutor(self.thread_count) # 定义线程池
        all_task = list()
        for domain in self.domains_set:
            all_task.append(pool.submit(self.analysis_dns, domain))
        for task in all_task:
            task.result()

    def analysis_dns(self, domain):
        try:
            ans = self.resolver.resolve(domain, "A")
            if ans:
                ips = list()
                for i in ans.response.answer:
                    for j in i.items:
                        if hasattr(j, "address"):
                            self.domain_ips_dict[domain].append(j.address)
        except dns.resolver.NoAnswer:
            pass
        except dns.exception.Timeout:
            pass
        except Exception as e:
            pass
    
    def remove_black_ip(self):
        # 对于接口返回域名的泛解析结果的去除  
        for domain, ips in self.domain_ips_dict.items():
            for ip in ips:
                if ip in self.ip_domain_count_dict.keys():
                    self.ip_domain_count_dict[ip]["count"] +=1
                    self.ip_domain_count_dict[ip]["domains"].append(domain)
                else:
                    self.ip_domain_count_dict[ip] = {"domains": [domain], "count": 1}
        # remove
        for ip, domains_count in self.ip_domain_count_dict.items():
            if domains_count["count"] > DNS_THRESHOLD: # 有50个域名指向了同一个ip jd的有大量指向一个ip 
                # 将泛解析的ip存下来 返回回去 
                self.black_ip.append(ip)
                for domain in domains_count["domains"]:
                    if domain in self.domain_ips_dict.keys():
                        # print(domain,  ip, domains_count["count"])
                        self.domain_ips_dict.pop(domain)

    def remove_private(self):
        # 移除内网ip
        print_info("del private ip domain")
        for domain in list(self.domain_ips_dict.keys()):
            ips = self.domain_ips_dict[domain]
            if ipaddress.ip_address(ips[0]).is_private: # if private ip del
                self.domain_ips_dict.pop(domain)

    def run(self):
        # 先用script下的接口获取子域名
        self.run_scripts()
        # 对这些接口进行dns解析 获取对应的ip列表
        print_info("start dns query")
        self.threadpool_dns()
        # 是否保留内网ip结果
        if not self.is_private:
            self.remove_private()
        # 对接口返回含有泛解析的域名去除  
        self.remove_black_ip()
        if self.get_black_ip: # 是否返回泛解析的ip  
            return self.domain_ips_dict, self.black_ip
        else:
            return self.domain_ips_dict


# 穷举类 
class ExhaustionScan(object):
    """暴力穷举
    :param scan_domain 要测试的域名
    :param thread_count 线程数 默认100
    :param is_output 是否输出进度条 默认不输出
    :param black_ip 泛解析的ip     默认为空
    :param is_private 是否保留内网ip 默认不保留
    :param sub_dict 指定的字典 默认读取配置文件下字典 
    :param next_sub 是否是三级或者四级的域名扫描
    :param timeout 超时时间 默认穷举超时时间为 2h
    :return domain_ips_dict 域名对应解析的ip结果
    
    """
    def __init__ (
        self, scan_domain, thread_count=100,
        is_output=False, black_ip=list(),
        is_private=False, sub_dict=None, next_sub=False,
        big_dict=False, timeout=7200, gen_rule=False
        ):
        self.base_path  = os.path.dirname(os.path.abspath(__file__))
        # dns
        self.resolver = resolver
        #self.resolver.nameservers=['8.8.8.8', '114.114.114.114']
        self.scan_domain = scan_domain
        # 默认线程100个
        self.thread_count = thread_count
        self.is_output = is_output
        self.timeout = timeout
        self.sub_dict = sub_dict
        self.big_dict = big_dict
        self.next_sub = next_sub
        self.domain_ips_dict = defaultdict(list)
        self.sub_dict_queue = queue.Queue()
        # 是否添加动态字典
        self.gen_rule = gen_rule        
        self.load_subdomain_dict()
        self.all_size = self.sub_dict_queue.qsize()
        # 泛解析的ip 默认是空 可以将接口返回的 black_ip 传入这里 
        self.black_ip = black_ip
        # {ip:{ domains: [域名], count: 计数}  }
        self.ip_domain_count_dict = dict()
        # 内网ip
        self.is_private = is_private


    def load_subdomain_dict(self):
        if not self.next_sub:
            print_info("load sub dict")
        if self.sub_dict: # 使用指定的字典 
            if os.path.exists( self.sub_dict):
                dict_path = self.sub_dict
            else:
                print_error("字典不存在")
        else:
            dict_path = os.path.join(self.base_path, "../","config", "subdomains.txt")
            # 如果使用大字典
            if self.big_dict:
                dict_path = os.path.join(self.base_path, "../","config", "big_subdomains.txt")
        # 是否是三级或者四级扫描使用 小字典
        if self.next_sub:
            dict_path = os.path.join(self.base_path, "../","config", "next_subdomains.txt")
        with open(dict_path, "r") as f:
            for sub in f:
                self.sub_dict_queue.put(f"{sub.strip()}.{self.scan_domain}")
        if self.gen_rule:
            genrule_subdomain_list = GenSubdomain(self.scan_domain).gen()
            for sub in genrule_subdomain_list:
                self.sub_dict_queue.put(f"{sub.strip()}.{self.scan_domain}")
        #if not self.next_sub:
        print_info(f"quque all size: {self.sub_dict_queue.qsize()}")

    def is_analysis(self):
        """ 
        泛解析判断 
        通过不存在的域名进行判断
        """
        try:
            ans = self.resolver.resolve(
                ''.join(random.sample(string.ascii_lowercase,5))+"."+self.scan_domain , "A")
            if ans:
                ips = list()
                for i in ans.response.answer:
                    for j in i.items:
                            ip = j.to_text()
                            if ip:
                                return True
        except dns.resolver.NoAnswer:
            return False
        except dns.exception.Timeout:
            return False
        except dns.resolver.NXDOMAIN:
            return False
        except Exception as e:
            print(e)
            return False
    
    def analysis_dns(self, domain):
        try:
            # print(domain)
            ans = resolver.query(domain, "A")
            if ans:
                ips = list()
                for i in ans.response.answer:
                    for j in i.items:
                        if hasattr(j, "address"):
                            # 增加对内网ip的判断 if not save private
                            if not self.is_private:
                                if not ipaddress.ip_address(j.address).is_private:
                                    # 增加对泛解析的操作 
                                    if self.remove_black_ip(domain, j.address):
                                        self.domain_ips_dict[domain].append(j.address)
                            else: # 如果对内网结果进行保存 
                                if self.remove_black_ip(domain, j.address):
                                    self.domain_ips_dict[domain].append(j.address)
        except dns.resolver.NoAnswer:
            pass
        except dns.exception.Timeout:
            pass
        except Exception as e:
            pass

    def remove_black_ip(self, domain, ip):
        """ 对解析后的域名ip判断是否是泛解析 超过阈值进行忽略和删除"""
        if ip in self.black_ip:
            return False
        if ip in self.ip_domain_count_dict.keys():
            self.ip_domain_count_dict[ip]["count"] +=1
            self.ip_domain_count_dict[ip]["domains"].append(domain)
        else:
            self.ip_domain_count_dict[ip] = {"domains": [domain], "count": 1}
        # 判断是否达到泛解析ip阈值 达到则删除记录下来的并增加黑ip  
        if self.ip_domain_count_dict[ip]["count"] > DNS_THRESHOLD:
            for domain in self.ip_domain_count_dict[ip]["domains"]:
                if domain in self.domain_ips_dict.keys():
                    self.domain_ips_dict.pop(domain)
            self.black_ip.append(ip)
            return False
        else:# 没有达到阈值
            return True

    def worker(self):
        while not self.sub_dict_queue.empty():
            domain = self.sub_dict_queue.get()
            if domain is None:
                break
            self.analysis_dns(domain)
            # self.sub_dict_queue.task_done()

    def all_done(self, threads):
        done_count = 0
        for t in threads:
            if not t.is_alive():
                done_count +=1
        if done_count == len(threads):
            return True
        return False

    def run(self):
        # 先进行泛解析判断
        if self.is_analysis():
            if not self.next_sub:
                print_debug("存在泛解析")
        threads = []
        for i in range(self.thread_count):
            t = threading.Thread(target=self.worker)
            t.setDaemon(True)
            t.start()
            threads.append(t)
        # 阻塞 等待队列消耗完
        if not self.next_sub:
            print_info("start thread ")
        start = time.perf_counter()
        #while not self.sub_dict_queue.empty() and self.all_done(threads):
        while not self.sub_dict_queue.empty():
            time.sleep(1)
            if self.is_output:
                # 输出进度条
                print_progress(
                    self.sub_dict_queue.qsize(), self.all_size,
                    start, len(self.domain_ips_dict)
                    )
        if not self.next_sub: # 不然下一级扫描的进度条会有问题
            print() # 最后输出的问题加一个print来实现换行
        # self.sub_dict_queue.join() # 这里暂时不需要使用队列来阻塞
        return self.domain_ips_dict

class GenSubdomain(object):
    def __init__(self, domain):
        # 我们这里拿三级子域名字典与domain结合生成字典
        self.scan_domain = domain
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def gen(self):
        subdomain_dict_path = os.path.join(self.base_dir, "../","config", "next_subdomains.txt")
        gen_subdomain_list = list()
        rule_list = [
            "-",
            ".",
            "_",
            "@"
        ]
        with open(subdomain_dict_path, "r") as f:
            for sub in f:
                for rule in rule_list:
                    gen_subdomain_list.append(f'{self.scan_domain}{sub}')
                    gen_subdomain_list.append(f'{sub}{self.scan_domain}')
                    gen_subdomain_list.append(f'{sub}{rule}{self.scan_domain}')
                    gen_subdomain_list.append(f'{self.scan_domain}{rule}{sub}')
        print_info(f"gen subdomain count: {len(gen_subdomain_list)}")
        return gen_subdomain_list
