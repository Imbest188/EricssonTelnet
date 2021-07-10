import telnetlib
from threading import Thread
import time
import socket


class EricssonTelnet:
    __ip = ''
    __login = ''
    __password = ''
    __telnet = None
    __isBusy = True
    __alarms = []

    def __init__(self, ip, login, password):
        self.__ip = ip
        self.__login = login
        self.__password = password
        self.__connect()
        self.__runListening()

    def __connect(self):
        try:
            self.__telnet = telnetlib.Telnet(self.__ip)
        except:
            self.__telnet = None
            print("Can't connect to host " + self.__ip)
            return False
        self.__auth()
        time.sleep(1)
        self.__listenMode()
        return True

    def __heartbeat(self):
        self.__isBusy = True
        self.__telnet.write(b'\r\n')
        self.__telnet.write(b'\x04')
        self.__isBusy = False

    def __parse(self, alarmText):
        for alarm in alarmText.split('END'):
            if len(self.__alarms) > 1000:
                self.__alarms.pop(0)
            self.__alarms.append(alarm.strip())

    def __cleanOutSpecialSymbols(self, text):
        return text.replace('\x04', '').replace('<', '').replace('\x03', '').strip()

    def getAlarms(self):
        result = []
        for alarm in self.__alarms:
            if len(alarm) and alarm not in ['\x04', '<']:
                alarmText = self.__cleanOutSpecialSymbols(alarm)
                result.append(alarmText)
        self.__alarms.clear()
        return result

    def __listening(self):
        self.__telnet.read_very_eager()
        secondsCounter = 0
        while True:
            time.sleep(1)
            if self.__isBusy:
                secondsCounter = 0
            else:
                channelOutput = self.__telnet.read_very_eager().decode('ascii')
                secondsCounter += 1
                if secondsCounter > 200 or 'Timeout' in channelOutput:
                    secondsCounter = 0
                    self.__heartbeat()
                self.__parse(channelOutput)

    def __runListening(self):
        Thread(target=self.__listening, daemon=True).start()

    def __listenMode(self):
        #self.__telnet.read_very_eager()
        self.__telnet.write(b'\x04')
        self.__isBusy = False

    def __checkConnection(self):
        self.__telnet.write(b'\r\n')
        time.sleep(0.2)
        checkState = self.__telnet.read_very_eager().decode('ascii').lower()
        if 'timeout' in checkState or 'login' in checkState:
            print('reconnect')
            self.__connect()

    def get(self, message) -> str:
        while self.__isBusy:
            time.sleep(0.2)
        self.__isBusy = True
        self.__checkConnection()
        self.__telnet.write(message.encode('ascii') + b'\r\n')
        result = ''
        for count in range(30):
            result += self.__telnet.read_very_eager().decode('ascii')
            time.sleep(0.2)
            if 'END' in result or 'CELL NOT DEFINED' in result or 'EXTERNAL' in result:
                break
        self.__listenMode()
        return result

    def send(self, message):
        while self.__isBusy:
            time.sleep(0.2)
        self.__isBusy = True
        self.__checkConnection()
        self.__telnet.write(message.encode('ascii') + b'\r\n')
        time.sleep(0.5)
        self.__telnet.write(b';\r\n\r\n')
        result = self.__telnet.read_very_eager().decode('ascii').lower()
        self.__listenMode()
        if 'ordered' in result or 'executed' in result or 'preop' in result:
            return True
        return False

    def __auth(self):
        time.sleep(1)
        for i in range(6):
            time.sleep(1)
            answ = self.__telnet.read_very_eager()
            if b'login' in answ:
                self.__telnet.write(self.__login.encode('ascii') + b'\r\n')
            elif b'assword' in answ:
                self.__telnet.write(self.__password.encode('ascii') + b'\r\n')
            elif b'terminal' in answ:
                self.__telnet.write(b'xterm\r\n')
            elif b'WO' in answ:
                break

        self.__telnet.write(b'\r\n')
        self.__telnet.write(b'mml -a\r\n')

    def __del__(self):
        self.__telnet.write(b'exit;')
        self.__telnet.get_socket().shutdown(socket.SHUT_WR)
        self.__telnet.read_all()
        self.__telnet.close()
        self.__telnet = None
