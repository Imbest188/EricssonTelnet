from Telnet.EricssonBsc import EricssonBsc as Telnet
from threading import Thread
from concurrent.futures import ThreadPoolExecutor


class Alarms:
    def __init__(self):
        self.alarms = []

    def append(self, alarms):
        if alarms:
            self.alarms.append(alarms)

    def __bool__(self):
        return len(self.alarms) > 0

    def __str__(self):
        result = ""
        controller = ''
        self.alarms.sort()
        for alarm in self.alarms:
            if alarm.controller != controller:
                result += alarm.controller + '\n'
                controller = alarm.controller
            result += alarm.message() + '\n'
        return result

    def __repr__(self):
        return str(self)

    def __add__(self, other):
        self.alarms += other.alarms
        return self


class Changes:
    def __init__(self):
        self.changes = []

    def append(self, change):
        if change:
            self.changes.append(change)

    def __bool__(self):
        return len(self.changes) > 0

    def __str__(self):
        result = ""
        for change in self.changes:
            result += str(change) + '\n'
        return result

    def __repr__(self):
        return str(self)


class MobileSwitchingCentersPool:
    __pool = []

    def getChannelsOutput(self):
        result = []
        for obj in self.__pool:
            result.append({'OBJECT': obj.name, 'ALARMS': obj.getChannelOutput()})
        return result


class BaseStationsControllersPool(MobileSwitchingCentersPool):
    __pool = []

    def addController(self, host, login, password, name='BSC'):
        bsc = Telnet(host, login, password, name)
        self.__pool.append(bsc)

    def __addController(self,  host, login, password, name):
        bsc = Telnet(host, login, password, name)
        self.__pool.append(bsc)

    def getAlarms(self, update=False):
        result = Alarms()
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putAlarms, args=(result,), kwargs={'current': update}, daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getBlockedObjects(self, update=False):
        result = Alarms()
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putBlockedObjects, args=(result,), kwargs={'current': update}, daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getWorstCells(self, update=False):
        result = Alarms()
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putWorstCells, args=(result,), kwargs={'update': False}, daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getHaltedCells(self, update=False):
        result = Alarms()
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putHaltedCells, args=(result,), kwargs={'current':update}, daemon=True)
            threads.append(thread)
            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getChanges(self):
        result = Changes()
        threads = []
        for bsc in self.__pool:
            thread = Thread(target=bsc.putChanges, args=(result,), daemon=True)
            threads.append(thread)

            thread.start()
        for thr in threads:
            thr.join()
        return result

    def getStates(self):
        return self.getWorstCells(update=False) + self.getAlarms(update=False) +\
               self.getHaltedCells(update=False) + self.getBlockedObjects(update=False)
