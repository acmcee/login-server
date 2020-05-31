# 两步Google验证的服务器登录


## 运行环境：

* python 3 ， python 2 未测试


## 配置文件 .config.json 中添加以下信息

* 添加动态码的关键字
* 添加登录服务器后的关键字
* 添加服务器的列表以及对应的map


```angular2
{
  "cas_user": "harvey",   // 登录服务器的用户名
  "cas_key": "xxxxxxxxxxxx",  // Google的秘钥
  "totp_keyword": "数字验证码",  // 提示输入Google动态码的关键字
  "login_success_keyword": "机房内网",  // 服务器登录成功的关键字
  "login_failed_keyword": "Permission denied'",  // 登录失败的关键字
  "login_cmd": "ssh -A {cas_user}@{server_alias}", // 服务器登录的命令
  "login_log": "/tmp/login-server.log",  // 服务器登录的日志，方便排查问题
  "servers": {
    "server_alias": "server_dns",  // 服务器列表
    "s1": "xxx.xxx.com",
    "s2": "xxx.xxx.com",
    "s3": "xxx.xxx.com"
  }
}

```


## Usage:

### 1. bash_profile 添加 alias
* alias login-server='/xx/bin/python /xx/login-server/login.py'
* alias server_alias="login-server server_alias"

### 2. login server 

* server_alias