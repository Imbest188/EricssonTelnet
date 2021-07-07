from Telnet.EricssonBsc import EricssonBsc as Telnet
from Telnet.ControllerPool import ControllerPool as Pool
import time


if __name__ == '__main__':
    pool = Pool()
    pool.addController('10.140.3.7', 'ts_user', 'apg43l2@', 'BSC04')
    pool.addController('10.140.27.68', 'ts_user', 'apg43l1@', 'BSC05')
    print(pool.getAlarms())
    print(pool.getWorstCells())
    print(pool.getHaltedCells())

    counter = 0
    while True:
        time.sleep(10)
        alarms = pool.getChannelsOutput()
        print(alarms)
        counter += 1
        if counter > 5:
            counter = 0
            print(pool.getAlarms())
