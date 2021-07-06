from Telnet.EricssonTelnet import EricssonTelnet as Telnet
from Telnet.EricssonParser import EricssonParser as Parser


if __name__ == '__main__':
    bsc = Telnet('10.140.3.7', 'ts_user', 'apg43l2@')
    #answer = bsc.get("RXASP:MOTY=RXOTG;")
    answer = bsc.get("RLSTP:CELL=ALL,STATE=HALTED;")
    print(answer)
    parsedAnswer = Parser().parse(answer)
    print(parsedAnswer)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
