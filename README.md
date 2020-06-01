# 两步Google验证的服务器登录


## 运行环境：

* python 3 ， python 2 未测试


## 将.config-example.json 重命名为 .config.json 修改对应的配置以及添加服务器列表

* cas_user: 登录服务器的用户名
* cas_key: 秘钥
* totp_keyword: 提示输入动态码的关键字
* login_success_keyword: 登录成功的关键字
* login_failed_keyword: 登录失败的关键字
* login_answer_yes_keyword: 提示 Are you sure you want to continue connecting 的关键字
* login_cmd: 登录命令
* login_log: 登录的日志，所有的命令输入和输出，可以排除问题
* servers: 服务器的map，前面的alias，后面是服务器的地址


```angular2
{
  "cas_user": "harvey",
  "cas_key": "xxxxxxxxxxxx",
  "totp_keyword": "数字动态码",
  "login_success_keyword": "Last login:",
  "login_failed_keyword": "Permission denied",
  "login_answer_yes_keyword": "yes/no",
  "login_cmd": "ssh -A {cas_user}@{server_alias}",
  "login_log": "/tmp/login-server.log",
  "servers": {
    "server_alias": "server_dns",
    "s1": "xxx.xxx.com",
    "s2": "xxx.xxx.com",
    "s3": "xxx.xxx.com"
  }
}


```


## Usage:

### 1. bash_profile 添加 alias
* alias login-server='/xx/bin/python /xx/login-server/login.py'
* alias s1="login-server server_alias"

### 2. login server 

>   $ s1
