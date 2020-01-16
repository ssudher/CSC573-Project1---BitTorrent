import threading
import logging

logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

def worker(arg1):
    # logging.debug("Running")
    print(str(arg1),"st.")
    input()
    print("here")
    # print(threading.currentThread().getName(),str(arg1),".Threading has been done here!\n")
    return

def ham():
    # logging.debug("Running")
    print("I am groot")
    # print(threading.currentThread().getName(), "Different daw")


threads = []
for i in range(5):
    t = threading.Thread(name = "Worker func",target=worker, args=(i,))
    t2 = threading.Thread(name = "Different func", target=ham)
    threads.append(t)
    t.start()
    t2.start()