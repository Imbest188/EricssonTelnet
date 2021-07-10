from Telnet.EricssonTelnet import EricssonTelnet as Telnet
from Telnet.Alex import EricssonBscCommands as Alex
from Telnet.EricssonParser import EricssonParser
import time


class AlarmContainer:
    def __init__(self, controller, alarmType, container=[]):
        self.controller = controller
        self.type = alarmType
        self.alarmsContainer = container

    def message(self):
        if not self:
            return ""
        textView = '\n'.join(self.alarmsContainer)
        return f"{self.type}:\n" + textView

    def __str__(self):
        return f"{self.controller}\n{self.message()}"

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.alarmsContainer)

    def __bool__(self):
        return len(self) > 0

    def __lt__(self, other):
        return self.controller < other.controller


class AlarmChanges:
    def __init__(self, name):
        self.name = name
        self.newAlarms = []
        self.ceasedAlarms = []
        self.newWorstCells = []
        self.ceasedWorstCells = []
        self.newHaltedCells = []
        self.ceasedHaltedCells = []
        self.newBlockedObjects = []
        self.ceasedBlockedObjects = []

    def message(self):
        if not self:
            return ""#'На ' + self.name + ' изменений не было :)'
        result = f"{self.name}\n"
        if len(self.newAlarms):
            result += "Новые аварии:\n" + '\n'.join(self.newAlarms) + "\n"
        if len(self.ceasedAlarms):
            result += f"Ушедшие аварии:\n" + '\n'.join(self.ceasedAlarms) + "\n"
        if len(self.newWorstCells):
            result += f"Новые сектора в аварии:\n" + '\n'.join(self.newWorstCells) + "\n"
        if len(self.ceasedWorstCells):
            result += f"Сектора восстановились:\n" + '\n'.join(self.ceasedWorstCells) + "\n"
        if len(self.newHaltedCells):
            result += f"Сектора захалчены:\n" + '\n'.join(self.newHaltedCells) + "\n"
        if len(self.ceasedHaltedCells):
            result += f"Сектора расхалчены:\n" + '\n'.join(self.ceasedHaltedCells) + "\n"
        if len(self.newBlockedObjects):
            result += f"Выключенные RBS:\n" + '\n'.join(self.newBlockedObjects) + "\n"
        if len(self.ceasedBlockedObjects):
            result += f"RBS были разблокированы:\n" + '\n'.join(self.ceasedBlockedObjects) + "\n"
        return result

    def __str__(self):
        return self.message()

    def __repr__(self):
        return str(self)

    def __len__(self):
        size = len(self.newAlarms)
        size += len(self.ceasedAlarms)
        size += len(self.newWorstCells)
        size += len(self.ceasedWorstCells)
        size += len(self.newHaltedCells)
        size += len(self.ceasedHaltedCells)
        size += len(self.newBlockedObjects)
        size += len(self.ceasedBlockedObjects)
        return size

    def __bool__(self):
        return len(self) > 0


class EricssonObject:
    __connection = None

    def __init__(self, host, login, password, name='OBJECT'):
        self.name = name
        self.__connection = Telnet(host, login, password)

    def getChannelOutput(self):
        return self.__connection.getAlarms()


class EricssonBsc(EricssonObject):
    def __init__(self, host, login, password, name='BSC'):
        self.name = name
        self.__connection = Telnet(host, login, password)
        self.__parser = EricssonParser()
        self.__currentAlarms = []
        self.__oldAlarms = []
        self.__currentWorstCells = []
        self.__oldWorstCells = []
        self.__currentHaltedCells = []
        self.__oldHaltedCells = []
        self.__currentBlocked = []
        self.__oldBlocked = []

    def getAlarms(self, update=False, current=False):
        if current:
            return self.__currentAlarms
        answer = self.__connection.get(Alex.rxasp())
        alarmsList = self.__parser.parse(answer)
        result = []
        for alarm in alarmsList:
            rsite = alarm.get('RSITE')
            alarmText = alarm.get('ALARM SITUATION')
            if alarmText not in ['BTS INT UNAFFECTED']:
                result.append(rsite + ' ' + alarmText)
        result.sort()
        if update:
            self.__oldAlarms = self.__currentAlarms
            self.__currentAlarms = result
        return result

    def putAlarms(self, container, current=False):
        result = self.getAlarms(current=current)
        data = AlarmContainer(self.name, "RBS в аварии", result)
        container.append(data)

    def getBlockedObjects(self, update=False, current=False):
        if current:
            return self.__currentBlocked
        answer = self.__connection.get(Alex.rxmsp(moty='RXOTG'))
        blockedObjects = self.__parser.parse(answer)
        answer2 = self.__connection.get(Alex.rxtcp())
        tgToName = self.__parser.parse(answer2)
        result = []
        for obj in blockedObjects:
            state = obj.get('BLSTATE')
            if state == 'MBL':
                mo = obj.get('MO')
                for group in tgToName:
                    mo2 = group.get('MO')
                    if mo == mo2:
                        cells = group.get('CELL')
                        firstCell = cells.split(',')[0]
                        rbs = firstCell[:-1]
                        result.append(rbs)
                        break
        result.sort()
        if update:
            self.__oldBlocked = self.__currentBlocked
            self.__currentBlocked = result
        return result

    def putBlockedObjects(self, container, current=False):
        result = self.getBlockedObjects(current=current)
        data = AlarmContainer(self.name, "Выключенные RBS", result)
        container.append(data)

    def __getWorstCells(self):
        answer = self.__connection.get(Alex.rlcrp())
        cellsList = self.__parser.parse(answer)
        result = []
        for cell in cellsList:
            timeslots = cell.get('NOOFTCH')
            if timeslots == '0':
                name = cell.get('CELL')
                result.append(name)
        return result

    def getWorstCells(self, update=False, broadcast=False):
        worstCells = self.__getWorstCells()
        haltedCells = self.getHaltedCells(update=broadcast)
        blockedObjects = self.getBlockedObjects(update=broadcast)
        currentAlarms = self.getAlarms(update=broadcast)
        disabledRbs = []
        disabledRbs += blockedObjects
        for obj in currentAlarms:
            name = obj.split(' ')[0]
            disabledRbs.append(name)
        subresult = list(set(worstCells) - set(haltedCells))
        result = []

        for cell in subresult:
            find = False
            for obj in disabledRbs:
                if obj in cell:
                    find = True
                    break;
            if not find:
                result.append(cell)
        result.sort()
        if update:
            self.__oldWorstCells = self.__currentWorstCells
            self.__currentWorstCells = result
        return result

    def putWorstCells(self, container, update=False, broadcast=False):
        result = self.getWorstCells(update=update, broadcast=broadcast)
        data = AlarmContainer(self.name, "Соты не в эфире", result)
        container.append(data)

    def getHaltedCells(self, update=True, current=False):
        if current:
            return self.__currentHaltedCells
        answer = self.__connection.get(Alex.rlstp(state='HALTED'))
        if 'FUNCTION BUSY' in answer:
            for i in range(6):
                time.sleep(2)
                answer = self.__connection.get(Alex.rlstp(state='HALTED'))
                if 'FUNCTION BUSY' in answer:
                    pass
                else:
                    break
        cellsList = self.__parser.parse(answer)
        result = []
        for cell in cellsList:
            name = cell.get('CELL')
            if name != 'NONE':
                result.append(name)
        result.sort()
        if update:
            self.__oldHaltedCells = self.__currentHaltedCells
            self.__currentHaltedCells = result
        return result

    def putHaltedCells(self, container, current=False):
        result = self.getHaltedCells(current=current)
        data = AlarmContainer(self.name, "Захалченные соты", result)
        container.append(data)

    def getChanges(self):
        result = AlarmChanges(self.name)
        self.getWorstCells(update=True, broadcast=True)
        result.ceasedAlarms = list(set(self.__oldAlarms) - set(self.__currentAlarms))
        result.newAlarms = list(set(self.__currentAlarms) - set(self.__oldAlarms))
        result.ceasedWorstCells = list(set(self.__oldWorstCells) - set(self.__currentWorstCells))
        result.newWorstCells = list(set(self.__currentWorstCells) - set(self.__oldWorstCells))
        result.ceasedHaltedCells = list(set(self.__oldHaltedCells) - set(self.__currentHaltedCells))
        result.newHaltedCells = list(set(self.__currentHaltedCells) - set(self.__oldHaltedCells))
        result.ceasedBlockedObjects = list(set(self.__oldBlocked) - set(self.__currentBlocked))
        result.newBlockedObjects = list(set(self.__currentBlocked) - set(self.__oldBlocked))
        return result

    def putChanges(self, container):
        container.append(self.getChanges())
