import telnetlib
import re
from threading import Thread
import time

import socket


class EricssonTelnet:
    ip = ''
    login = ''
    password = ''
    telnet = None

    def __init__(self, ip, login, password):
        self.ip = ip
        self.login = login
        self.password = password
        self.__connect()

    def __connect(self):
        try:
            self.telnet = telnetlib.Telnet(self.ip)
        except:
            self.telnet = None
            print("Can't connect to host " + self.ip)
            return False
        self.__auth()

    def checkConnection(self):
        self.telnet.write(b'\r\n')
        time.sleep(0.2)
        checkState = self.telnet.read_very_eager().decode('ascii').lower()
        if 'timeout' in checkState or 'login' in checkState:
            self.__connect()

    def get(self, message):
        self.checkConnection()
        self.telnet.write(message.encode('ascii') + b'\r\n')
        result = ''
        for count in range(10):
            result += self.telnet.read_very_eager().decode('ascii')
            time.sleep(0.2)
            if 'END' in result or 'CELL NOT DEFINED' in result or 'EXTERNAL' in result:
                break
        return result

    def send(self, message):
        self.checkConnection()
        self.telnet.write(message.encode('ascii') + b'\r\n')
        self.telnet.write(b';\r\n')

    def __auth(self):
        time.sleep(1)
        for i in range(6):
            time.sleep(1)
            answ = self.telnet.read_very_eager()
            if b'login' in answ:
                self.telnet.write(self.login.encode('ascii') + b'\r\n')
            elif b'assword' in answ:
                self.telnet.write(self.password.encode('ascii') + b'\r\n')
            elif b'terminal' in answ:
                self.telnet.write(b'xterm\r\n')

        self.telnet.write(b'\r\n')
        self.telnet.write(b'mml -a\r\n')

    def __del__(self):
        self.telnet.write(b'exit;')
        self.telnet.get_socket().shutdown(socket.SHUT_WR)
        self.telnet.read_all()
        self.telnet.close()
        self.telnet = None