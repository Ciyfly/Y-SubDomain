# y_subdomain

子域名获取工具


## 使用

使用加速下载
`git clone https://github.com.cnpmjs.org/Ciyfly/y_subdomain.git`

**如果是下载的zip 或者tar包需要修改文件夹名为 y_subdomain**

**基于python3 linux环境下**

适用于 扫描器前置信息收集 简单子域名获取 学习等  
基本使用内置原生库

[![asciicast](https://asciinema.org/a/m7mqlsHux1TinM2oWB6D6LZoD.png)](https://asciinema.org/a/m7mqlsHux1TinM2oWB6D6LZoD)


### 泛解析的解决办法
先测试一个不存在的域名然后是否成功解析


### 为什么要做
1. 重复造轮子 深入理解轮子 做出更好用的轮子
2. 是大扫描器的信息收集的一部分功能的实现
3. 工作中擅于使用轮子 学习中擅于造轮子  


## 实现  
### 接口的实现
这里参考 poc的形式 动态的从script文件夹下的脚本
动态载入实例化并执  
继承Base类默认有个 `self.enable=True` 可以控制是否开启脚本  
如果使用 -e 指定接口 enable是False也会强制执行  
对于接口返回的域名会使用线程池再去dns解析验证 (默认线程池大小 50)

**接口引擎脚本完成：**
1. 百度云检测  
2. hackertarget
3. virustotal (**需要在config/config.py 中添加api key才能使用不然默认不会执行**)
4. 通过证书获取

### 暴力穷举的实现  
一口气加载字典到内存中 占内存不大  
使用共享队列+多线程的形式进行解析dns 默认线程开启100个  
这个地方有进度条功能 可以在实例化穷举类的时候进行选择是否开启  


## 版本

**v1.2**   
2021 0520
去掉大字典 影响下载速度  
保存的结果拆分为 ip ipc段 域名 域名+ip  
增加获取title功能 `--title`  
增加动态生成字典加入测试字典功能 `--gen`  

**v1.1.0**   
修改一些bug  
增加三级四级域名穷举  
修改为默认小字典2w (使用的onforall的字典)  
指定`big_dict` 可以使用大字典200w  
增加可以指定字典参数  
穷举增加超时时间 默认为2h  
dns增加超时时间10s  

**v1.0.0**  
修改bug  
进度条增加find输出  
增加对内网ip的剔除参数  
增加指定字典的参数  

**V0.2**  
修改 穷举采用共享队列+多线程的形式  
去除多余代码  
修改了代码结构 便于作为api使用  
穷举增加了进度条  
扩大了字典 目前字典 2350706 (235w) (跑一次大概 40分钟左右)  
增加了HUP小调试 发起HUP信号会输出 此时队列大小 (在 api形式使用不输出进度条的时候 如果长时间未结束可调试使用)  
`kill -HUP 进程id`  

**V0.1**  
采用多接口的形式获取域名 动态插件形式添加接口脚本  
接口验证和穷举都采用线程池的形式进行dns解析  



# api形式使用  
使用接口解析
```python
from y_subdomain.lib.core import EngineScan

engine_scan = EngineScan(scan_domain, engine)
# scan_domain 为扫描的域名 engine 是指定的接口 空的话就全部都跑 默认也是全部都跑  
engine_domain_ips_dict = engine_scan.run()
# 调用 run方法会返回 解析的结果 是 字典形式 子域名对应ip列表  

接口类如下:
class EngineScan(object):
    """接口解析类
    :param scan_domain 测试域名
    :param engine 指定引擎列表 默认全部
    :param thread_count 线程 默认100
    :param get_black_ip 是否返回泛解析的ip 默认不返回
    :param is_private 是否保留内网ip 默认不保留
    :return domain_ips_dict, (black_ip) 选择返回泛解析ip则有第二个 否则只返回域名对于ip
    
    """
```
使用穷举解析
```python
from y_subdomain.lib.core import ExhaustionScan
scan_domain = "测试域名" # 穷举只支持单个域名
exhaustion_scan =  ExhaustionScan(scan_domain, thread_count=100, is_output=True)
# is_output 是否输出进度条 默认是False的
exh_domain_ips_dict = exhaustion_scan.run()

穷举类如下:
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
```  

## update
2019 0813
修改一些bug  
增加三级四级域名穷举  
修改为默认小字典2w (使用的onforall的字典)  
指定`big_dict` 可以使用大字典200w  
增加可以指定字典参数  
穷举增加超时时间 默认为2h  
dns增加超时时间10s  

---

2019 0719  
修改bug  
进度条增加find输出  
增加对内网ip的剔除参数  
增加指定字典的参数 

---
2019 0711  
增加对内网ip的忽略 默认是清除掉的 可以通过命令行参数进行控制  
增加指定字典的功能参数  
增加只进行穷举的功能参数  
没有把去除内网ip的方法写到savedata中是为了当接口api使用的时候 对内网ip的处理类内部就进行处理

---
2019 0709  
经测试 修改对于泛解析的解决  
如果随机字符串跑出来泛解析还继续进行穷举但是过滤掉这个泛解析的ip  
对于接口里的也进行泛解析剔除  
对于暴力穷举的会默认使用配置文件中的 50 阈值 作为判断泛解析的条件 当超过50个域名指向一个ip进行剔除  


# TODO
多增加几个模块
优化下代码结构

## 参考

[ESD](https://github.com/FeeiCN/ESD)  

[wydomain](https://github.com/ring04h/wydomain)  
