from Telnet.EricssonBsc import EricssonBsc as Telnet
from threading import Thread
from concurrent.futures import ThreadPoolExecutor
import time


class ControllerPool:
    def __init__(self):
        self.__pool = []

    def addController(self, host, login, password, name='BSC'):
        bsc = Telnet(host, login, password, name)
        self.__pool.append(bsc)
        #Thread(target=self.__addController, args=(host, login, password, name), daemon=True).start()

    def __addController(self,  host, login, password, name):
        bsc = Telnet(host, login, password, name)
        self.__pool.append(bsc)

    def getAlarms(self):
        result = []
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putAlarms, args=(result,), daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getWorstCells(self):
        result = []
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putWorstCells, args=(result,), daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getHaltedCells(self):
        result = []
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putHaltedCells, args=(result,), daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getChannelsOutput(self):
        result = []
        for bsc in self.__pool:
            result.append({'BSC' : bsc.name, 'ALARMS' : bsc.getChannelOutput()})
        return result
