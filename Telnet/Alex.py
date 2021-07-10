class EricssonBscCommands:
    @staticmethod
    def rxasp(moty='RXOCF') -> str:
        return "RXASP:MOTY=" + moty + ";"

    @staticmethod
    def rlcrp(cell='ALL'):
        return "RLCRP:CELL=" + cell + ";"

    @staticmethod
    def rlstp(cell='ALL', state='HALTED'):
        return "RLSTP:CELL=" + cell + ",STATE=" + state + ";";

    @staticmethod
    def rlstc(cell, state='HALTED'):
        return "RLSTC:CELL=" + cell + ",STATE=" + state + ";";

    @staticmethod
    def rxtcp(cell=''):
        cellArg = ''
        if len(cell):
            cellArg = ",CELL=" + cell
        return "RXTCP:MOTY=RXOTG" + cellArg + ";"

    @staticmethod
    def rxmsp(moty='RXOTG', mo='', tg='', trx=''):
        if len(mo) and len(tg):
            if len(trx) and not trx.startswith('-') and not tg.endswith('-'):
                trx = '-' + trx
            if tg.startswith('-') or mo.endswith('-'):
                pass
            else:
                tg = '-' + tg
            return "RXMSP:MO=" + mo + tg + trx + ",SUBORD;"
        return "RXMSP:MOTY=" + moty + ";"

    @staticmethod
    def rxbli(tg):
        return "RXBLI:MO=RXOTG-" + tg + ",SUBORD,FORCE;"

    @staticmethod
    def rxbli(tg, trx):
        return "RXBLI:MO=RXOTRX-" + tg + "-" + trx + ",SUBORD,FORCE;"