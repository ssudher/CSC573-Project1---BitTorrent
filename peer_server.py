import random
import socket
import threading
from datetime import datetime
import pickle
import os
import time
import my_init as ini

HOST = ini.my_ip
#HOST = '192.168.0.22'
#HOST = '10.152.43.217'
PORT = 65400


class Threads:

    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((HOST, PORT))
        self.rfc_index = {}
        self.rfc_index[HOST] = {}
        self.rfc_index[HOST]['rfc_nos'] = []
        self.rfc_index[HOST]['title'] = []
        self.rfc_index[HOST]['owner'] = []
        self.rfc_index[HOST]['TTL'] = []

        rfc_details = os.listdir('./RFC')
        temp_list1 = []
        temp_list2 = []
        rfc_details.sort()
        for x in rfc_details:
            if x == 'received':
                continue
 #           print(x)
            local_count = int((x.lower().split(".")[0]).split("c")[1])
 #           print(local_count)
            temp_list1.append(local_count)
            temp_list2.append(x.split('.')[0])
            self.rfc_index[HOST]['owner'].append(str(HOST))
            self.rfc_index[HOST]['TTL'].append(7200)
        self.rfc_index[HOST]['rfc_nos'] = temp_list1
        self.rfc_index[HOST]['title'] = temp_list2

        print(self.rfc_index)

    def rfc_init(self, hostIP_port):
        global ttl_val
        self.rfc_index[hostIP_port] = []

    def listner(self):
        self.s.listen()
        print("Listening at port:" + str(PORT))
        while True:
            conn, addr = self.s.accept()
            # collecting the time stamp immediately after the connection has been accepted
            time_stamp = datetime.now()

            print("addr", addr)

            hostIP_port = str(addr[0])

            t2 = threading.Thread(name="Service func", target=self.service, args=(conn, addr, hostIP_port, time_stamp))
            t2.start()

    def service(self, conn, addr, hostIP_port, time_stamp):
        print('Connected by', addr)
        value = conn.recv(1024).decode()
#        print(value)
#        print(type(value))
        temp1 = value.replace('[',' ').replace(']',' ').replace("'","")
        data = temp1.split(",")
 #       print(data)
  #      print(type(data))
        if int(data[0]) == 1:
            print(data[2])
            to_print = data[2].split("\\n")
            for x in to_print:
                print(x)
            #print(self.rfc_index)
            conn.sendall(pickle.dumps(self.rfc_index))
            conn.close()
        if int(data[0]) == 2:
            to_print = data[2].split("\\n")
            for x in to_print:
                print(x)
            file_name = ""
            flag = 0
            for key, value in self.rfc_index.items():
                for k, v in value.items():
                    if k == "rfc_nos":
                        for count, each in enumerate(v):
                            if int(each) == int(data[1]):
                                file_name = value['title'][count]
                                flag = 1
                                break
            if flag == 1:
                print('./RFC/' + str(file_name) + '.txt')
                with open('./RFC/' + str(file_name) + '.txt', 'rb') as w:
                    lines = w.readlines()
                    while True:
                        for line in lines:
                            conn.sendall(line)
                        break
                    # conn.sendfile(w,0)
                    # conn.sendall(pickle.dumps(data))
                    conn.close()
            else:
                send1 = "Sorry, Not available now"
                conn.sendall(pickle.dumps(data))
                conn.close()
            #        conn.close()

inst1 = Threads()
t = threading.Thread(name="Listening func", target=inst1.listner)
t.start()
