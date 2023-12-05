import threading
import time
isAllStop = False
def thread1():
    for i in range(50):
        print("thread 1")
        time.sleep(0.5)
        if isAllStop: break

def thread2():
    time.sleep(0.1)
    for i in range(50):
        print("thread 2")
        time.sleep(0.5)
        if isAllStop: break


if __name__ == '__main__':
    
    x = threading.Thread(target=thread1, args=())
    x.start()
    #x.join()

    x2 = threading.Thread(target=thread2, args=())
    x2.start()
    #x2.join()

    try:
        while True:
            print('main thread')
            time.sleep(0.5)
    except KeyboardInterrupt:
        isAllStop = True
        print("stop all")
