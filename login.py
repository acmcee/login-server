#!/usr/bin/env python
# coding:utf8
import logging
import pyotp
import json
import pexpect
import sys
import os


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(BASE_DIR, '.config.json')


class ServerConfig(object):
    def __init__(self):
        self.cas_user = None
        self.cas_key = None
        self.totp_keyword = None
        self.login_success_keyword = None
        self.login_failed_keyword = None
        self.login_cmd = None
        self.login_log = None
        self.servers = {}


class LoginServer(object):

    def __init__(self):
        self.config = None
        self._load_config()
        self._google_code = None

    def _load_config(self):
        self.config = ServerConfig()
        with open(config_file, 'r', encoding='utf8') as f:
            data = json.loads(f.read())
            self.config.cas_user = data['cas_user']
            self.config.cas_key = data['cas_key']
            self.config.servers = data['servers']
            self.config.totp_keyword = data['totp_keyword']
            self.config.login_success_keyword = data['login_success_keyword']
            self.config.login_failed_keyword = data['login_failed_keyword']
            self.config.login_cmd = data['login_cmd']
            self.config.login_log = data['login_log']

    def _get_google_code(self):
        totp = pyotp.TOTP(self.config.cas_key)
        self._google_code = totp.now()

    def login_server(self, server_alias):
        output = open(self.config.login_log, 'ab')
        server_dns = self.config.servers.get(server_alias)
        if not server_dns:
            print("%s alias is not exist in %s" % (server_alias, config_file))
            sys.exit(-1)
        login_cmd = self.config.login_cmd.format(cas_user=self.config.cas_user, server_alias=server_dns)
        print(login_cmd)
        child = pexpect.spawn(login_cmd)
        child.logfile = output

        for i in range(3):
            index = child.expect([self.config.totp_keyword.encode('utf8'),
                                  self.config.login_success_keyword.encode('utf8'),
                                  self.config.login_failed_keyword.encode('utf8'),
                                  pexpect.EOF,
                                  pexpect.TIMEOUT])
            if index == 0:
                self._get_google_code()
                child.sendline(self._google_code)
            elif index == 1:
                child.interact()
                child.close()
                child.wait()
                output.close()
                return
            elif index == 2:
                print("login failed, get %s" % self.config.login_failed_keyword )
                output.close()
                return
            elif index == 4:
                print("login server timeout")
                output.close()
                return
        print("try timeout ...")


if __name__ == '__main__':
    args = sys.argv
    if len(args) < 2:
        print("usage %s server alias" % args[0])
        sys.exit(-1)
    loginser = LoginServer()
    loginser.login_server(args[1])
