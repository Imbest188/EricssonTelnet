class Header:
    def __init__(self, name, index):
        self.name = name.strip()
        self.index = index
        self.endIndex = index
        self.data = dict()

    def setEnd(self, endIndex):
        self.endIndex = endIndex

    def getIndexes(self):
        return [self.index, self.end]

    def getName(self):
        return self.name

    def start(self):
        return self.index

    def end(self):
        return self.endIndex


class EricssonParser:
    def __init__(self):
        self.keywords = ['MO', 'RSITE', 'PSTU', 'CELL', 'SCGR', 'DEV']

    def parse(self, printText):
        self.data = []
        text = printText.split('END')
        for splittedPrint in text:
            self.__parse(splittedPrint)
        return self.data

    def checkIdentity(self, header):  # проверяем, есть ли в строке элемент, к которому относится весь принт
        for head in header:
            for key in self.keywords:
                if head.getName() == key:
                    return head
        return None

    def getHeaders(self, line):
        result = []
        args = line.split('  ')
        lastIndex = 0
        for arg in args:
            if len(arg):
                index = line.find(arg, lastIndex)
                if index == -1:
                    print(arg)
                lastIndex = index + len(arg)
                if len(result):
                    result[-1].setEnd(index)
                result.append(Header(arg, index))
        result[-1].setEnd(-1)
        return result

    def __parse(self, text):
        lines = text.split('\n')
        headers = []
        valueLine = False
        __values = dict()
        mo = ''
        startOfData = False
        for line in lines:
            if len(line) and '<' not in line and ':' not in line and startOfData:
                if valueLine:
                    key = self.checkIdentity(headers)
                    if key and line[key.start(): key.end()].isspace() == False:
                        if len(__values) > 0:
                            self.data.append(__values)
                            __values = dict()
                    for arg in headers:
                        end = arg.end()
                        if end == -1:
                            end = len(line)
                        value = line[arg.start(): end].strip()
                        if arg.getName() in __values.keys() and len(__values[arg.getName()]):
                            if len(value):
                                __values[arg.getName()] += ',' + value
                        else:
                            __values[arg.getName()] = value
                else:
                    # if len(__values) > 0:
                    #    self.data.append(__values)
                    #    __values = dict()
                    headers = self.getHeaders(line)
                    valueLine = True

            else:
                valueLine = False
                if len(line) < 3:
                    startOfData = True
        if len(__values) > 0:
            self.data.append(__values)
            __values = dict()