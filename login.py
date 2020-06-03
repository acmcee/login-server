#!/usr/bin/env python
# coding:utf8
import logging
import pyotp
import json
import pexpect
import sys
import os
import termios
import struct
import fcntl
import signal


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

config_file = os.path.join(BASE_DIR, '.config.json')


class ServerConfig(object):
    def __init__(self):
        self.cas_user = None
        self.cas_key = None
        self.totp_keyword = None
        self.login_success_keyword = None
        self.login_failed_keyword = None
        self.login_answer_yes_keyword = None
        self.login_cmd = None
        self.login_log = None
        self.servers = {}


class LoginServer(object):

    def __init__(self):
        self.config = None
        self._load_config()
        self._google_code = None
        self._win_size = None
        self._child = None

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
            self.config.login_answer_yes_keyword = data.get('login_answer_yes_keyword', 'yes/no')
            self.config.login_cmd = data['login_cmd']
            self.config.login_log = data['login_log']

    def _get_google_code(self):
        totp = pyotp.TOTP(self.config.cas_key)
        self._google_code = totp.now()

    def _sigwinch_passthrough(self, sig, data):
        self._getwinsize()
        self._child.setwinsize(self._win_size[0], self._win_size[1])

    def _getwinsize(self):
        """This returns the window size of the child tty.
        The return value is a tuple of (rows, cols).
        """
        if 'TIOCGWINSZ' in dir(termios):
            TIOCGWINSZ = termios.TIOCGWINSZ
        else:
            TIOCGWINSZ = 1074295912  # Assume
        s = struct.pack('HHHH', 0, 0, 0, 0)
        x = fcntl.ioctl(sys.stdout.fileno(), TIOCGWINSZ, s)
        self._win_size = struct.unpack('HHHH', x)[0:2]

    def login_server(self, server_alias):
        output = open(self.config.login_log, 'ab')
        server_dns = self.config.servers.get(server_alias)
        if not server_dns:
            print("%s alias is not exist in %s" % (server_alias, config_file))
            sys.exit(-1)
        login_cmd = self.config.login_cmd.format(cas_user=self.config.cas_user, server_alias=server_dns)
        print(login_cmd)
        self._child = pexpect.spawn(login_cmd)
        self._sigwinch_passthrough(None, None)
        signal.signal(signal.SIGWINCH, self._sigwinch_passthrough)

        self._child.logfile = output

        for i in range(4):
            index = self._child.expect([self.config.totp_keyword.encode('utf8'),
                                        self.config.login_success_keyword.encode('utf8'),
                                        self.config.login_failed_keyword.encode('utf8'),
                                        self.config.login_answer_yes_keyword.encode('utf8'),
                                        pexpect.EOF,
                                        pexpect.TIMEOUT])
            if index == 0:
                self._get_google_code()
                self._child.sendline(self._google_code)
            elif index == 1:
                self._child.interact()
                self._child.close()
                self._child.wait()
                output.close()
                return
            elif index == 2:
                print("login failed, get %s" % self.config.login_failed_keyword )
                output.close()
                return
            elif index == 3:
                print("send yes")
                self._child.sendline('yes')
            elif index == 5:
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
