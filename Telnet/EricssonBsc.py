from Telnet.EricssonTelnet import EricssonTelnet as Telnet
from Telnet.Alex import EricssonBscCommands as Alex
from Telnet.EricssonParser import EricssonParser
import time


class EricssonBsc:
    __connection = None

    def __init__(self, host, login, password, name='BSC'):
        self.name = name
        self.__connection = Telnet(host, login, password)
        self.__parser = EricssonParser()

    def getChannelOutput(self):
        return self.__connection.getAlarms()

    def getAlarms(self):
        answer = self.__connection.get(Alex.rxasp())
        alarmsList = self.__parser.parse(answer)
        result = []
        for alarm in alarmsList:
            rsite = alarm.get('RSITE')
            alarmText = alarm.get('ALARM SITUATION')
            if alarmText not in ['BTS INT UNAFFECTED']:
                result.append({'RSITE' : rsite, 'ALARM' : alarmText})
        return result

    def putAlarms(self, container):
        result = self.getAlarms()
        container.append({'BSC' : self.name, 'ALARMS' : result})

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

    def getWorstCells(self):
        worstCells = self.__getWorstCells()
        haltedCells = self.getHaltedCells()
        result = list(set(worstCells) - set(haltedCells))
        return sorted(result)

    def putWorstCells(self, container):
        result = self.getWorstCells()
        container.append({'BSC' : self.name, 'CELLS' : result})

    def getHaltedCells(self):
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
            result.append(name)
        return result

    def putHaltedCells(self, container):
        result = self.getHaltedCells()
        container.append({'BSC' : self.name, 'CELLS' : result})