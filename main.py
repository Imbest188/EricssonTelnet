from Telnet.ControllerPool import BaseStationsControllersPool as Pool
import time


if __name__ == '__main__':
    pool = Pool()
    pool.addController('**.***.*.*', '*******', '*******', 'BSC04')
    pool.addController('**.**.**.**', '*******', '*******', 'BSC05')

    # Можно складывать аварии ( полезно :) )
    #summary = pool.getAlarms() + pool.getHaltedCells()

    # Можно по отдельности
    #print(pool.getAlarms())
    #print(pool.getWorstCells())
    #print(pool.getHaltedCells())
    #print(pool.getBlockedObjects())

    # Всё что на текущий момент в аварии (бс, соты, MBL, захалченные)
    print(pool.getAlarms())
    # Не обновляет массивы с авариями, берет напрямую с BSC

    # Получаем изменения по авариям (аварии по бс, соты, MBL, захалченные)
    # Только эта команда обновляет списки аварий
    print('changes:', pool.getChanges())
    print('changes:', pool.getChanges())
    while True:
        time.sleep(180)
        # Получаем аварии которые сыплются в канал
        channelOutput = pool.getChannelsOutput()
        print(channelOutput)
        time.sleep(180)
        changes = pool.getChanges()
        if not changes:
            print('No changes')
        else:
            print(changes)
