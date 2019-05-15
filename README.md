# Y-SubDomain

子域名获取工具

## 分析如下:
分析结合几个现有的工具发现都是如下几点实现:
1. 多种第三方接口 获取子域名
2. 字典加异步dns暴力穷举
3. 利用ca证书获取

### 泛解析的解决办法
都是采用 先测试一个不存在的域名然后是否成功解析

### 都没有做再深一层的子域名获取
一般都是获取到第一层

### 为什么要做
1. 重复造轮子 深入理解轮子 做出更好用的轮子
2. 是大扫描器的信息收集的一部分功能的实现


## 具体功能设计
1. 命令行形式执行 基于python3
2. 这次增加进度条功能(之前我写的东西进度条都不好看)
3. 结合多个现有的工具 结合多个接口 高扩展性
4. 增加网页爬取获取子域名信息
5. ...

