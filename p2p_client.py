import socket
import os
import threading
import subprocess
import pickle
from client_rs import *
import threading
import time
import timeit
import my_init as ini

HOST = ini.my_ip
PORT = 65400
ttl_flag = 0
# peer_list = {}
my_ip = ''
# rfc_list = []
super_list = []
counter_s_ttl = 0
lock = threading.Lock()
temp_flag = 0

def initial_func():
  global super_list
  rfc_index = {}
  rfc_index[HOST] = {}
  rfc_index[HOST]['rfc_nos'] = []
  rfc_index[HOST]['title'] = []
  rfc_index[HOST]['owner'] = []
  rfc_index[HOST]['TTL'] = []

  rfc_details = os.listdir('./RFC')
  temp_list1 = []
  temp_list2 = []
  for x in rfc_details:
      if x == 'received':
          continue
      else:
          local_count = int((x.lower().split(".")[0]).split("c")[1])
          temp_list1.append(local_count)
          temp_list2.append(x.split('.')[0])
          rfc_index[HOST]['owner'].append(str(HOST))
          rfc_index[HOST]['TTL'].append(7200)
  rfc_index[HOST]['rfc_nos'] = temp_list1
  rfc_index[HOST]['title'] = temp_list2
  super_list.append(rfc_index)
#  print("Super_LIST")
 # print(super_list)

def ttl():
  while True:
      length = len(super_list)
      time.sleep(5)
      lock.acquire()
      #print(len(super_list))
#        print(super_list)
      try:
          if length > 1:
              for no,value in enumerate(super_list):
                  for k, v in value.items():
                      #print(k)
                      if k == ini.my_ip:
                          continue
                      else:
                          temp_len = 0
                          for name,val in v.items():
                              # print(name,val)
                              if name == 'TTL':
                                  temp_len = len(val)
                          for each in range(temp_len):
                              # print(v['TTL'][each])
                              value[k]['TTL'][each] -= 400
                              if value[k]['TTL'][each] == 0:
                                  print("Deleting RFC index of" + str(k) +  "as TTL expired\n")
                                  del value[k]
                                  print("current content")
                                  print(super_list)
                                  length = len(super_list)
      except Exception as e:
          print(e)
      lock.release()

def fetch_rfc(peer_list):
  #    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
  #        print(s.getsockname())
  #        print(peer_list)
  main_list = []
  # for key, val in peer_list.items():
  #     print("KEY: ", key)
  for key, val in peer_list.items():
      #        print("KEY: ", key)
      temp_ip = ''
      temp_port = ''
      for k, v in val.items():
          if k == 'hostname':
              temp_ip = v
          if k == 'port_num':
              temp_port = v
      print(temp_ip, temp_port)
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          if (ini.my_ip == temp_ip):
              continue
          else:

              # adding for the protocol
              with open("./protocol/1_2.txt", "r", encoding='utf-8') as file:
                  protocol = file.read()
              protocol = protocol.replace("<hostname>", str(temp_ip))
              protocol = protocol.replace("<port>", str(temp_port))
              s.connect((temp_ip, int(temp_port)))
              # send = input("what to send to server?")
              send_message = []
              send_message.append("1")
              send_message.append("")
              send_message.append(str(protocol))
              s.sendall(str(send_message).encode())
              data_arr = b""
              while True:
                  packet = s.recv(4096)
                  if not packet: break
                  data_arr += packet

              data = pickle.loads(data_arr)
              print(data)
              print("Received this!\n", data)
              main_list.append(data)
              s.close()
  return (main_list)
  # for i in data:
  #    print(i)


def download_all(peer_list,rfc_list):
    global super_list
    if super_list == []:
        print("There is no rfc indexes to iterate, please fetch\n")
        return (0)
    else:
        for dicton in super_list:
            hostname = ''
            port = 0
            rfc_numbers = []
            test_flag = 0
            for key, value in dicton.items():
                #print(key)
                #print(str(ini.my_ip))
                if str(key) == str(ini.my_ip):
                    continue
                for k, v in value.items():
                    if k == 'rfc_nos':
                        for count, each in enumerate(v):
                            if each == '':
                                continue
                            if os.path.exists("./RFC/rfc" + str(each) + ".txt"):
                                print("You already have rfc number: " + str(each))
                                continue
                            else:
                                rfc_numbers.append(each)
                            hostname = value['owner'][count]
                            port = peer_list[hostname]['port_num']
                            test_flag = 1

            # adding for the protocol
            with open("./protocol/2_22.txt", "r", encoding='utf-8') as file:
                protocol = file.read()
            protocol = protocol.replace("<hostname>", str(hostname))
            protocol = protocol.replace("<port>", str(port))
            print("I got out successfullt")
            print("hostname and port! \n")
            print(hostname, int(port))
            if test_flag == 1:
                print("Downloading RFCs")
                csv_flag = 0
                for rfc_val in rfc_numbers:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.connect((hostname, int(port)))
                        #print(rfc_val)
                        send_message = []
                        send_message.append('2')
                        send_message.append(rfc_val)
                        #adding for the protocol
                        send_message.append(str(protocol))
                        s.sendall(str(send_message).encode())
                        timer_start = time.time()
                        with open('./RFC/received/RFC' + str(rfc_val) + '.txt', 'w+') as f:
                            while True:
                                data = s.recv(1024).decode()
                                f.write(data)
                                print(data)
                                #print("hh")
                                if not data:
                                    f.close()
                                    break
                        temp_val = time.time() - timer_start
                        print("time to download rfc number: ", str(rfc_val), temp_val)
                        if csv_flag == 0:
                            with open('cumulative.csv','w+') as csv:
                                csv.write(str(rfc_val) + ',' + str(temp_val) + '\n')
                                csv_flag = 1
                        elif csv_flag == 1:
                            with open('cumulative.csv','a') as csv:
                                csv.write(str(rfc_val) + ',' + str(temp_val) + '\n')

                        # print(time.time() - timer_start)
                        s.close()


def download_rfc(peer_list, rfc_list):
    global super_list, temp_flag
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        rfc_val = input("Enter RFC number which you need")
        if os.path.exists("./RFC/rfc" + str(rfc_val) + ".txt"):
            print("You already have it")
        else:
            flag = 0
            hostname = ''
            port = 0
            super_flag = 0
            if super_list != []:
              print("I ma into the main wala")
              for dicton in super_list:
                  for key, value in dicton.items():
                      for k, v in value.items():
                          if k == 'rfc_nos':
                              for count, each in enumerate(v):
                                  if int(each) == int(rfc_val):
                                      hostname = value['owner'][count]
                                      port = peer_list[hostname]['port_num']
                                      flag = 1
            if (flag == 0 or super_list == []):
              for req_dict in rfc_list:
                  for key, val in req_dict.items():
                      lock.acquire()
                      if str(key) != str(s.getsockname()):
                        super_list.append(req_dict)
                      lock.release()
                      for k, v in val.items():
                          if k == 'rfc_nos':
                              for count, each in enumerate(v):
                                  if int(each) == int(rfc_val):
                                      hostname = val['owner'][count]
                                      port = peer_list[hostname]['port_num']
                                      flag = 1

            print("I got out successfullt")
            print(hostname, port)
            # adding for the protocol
            with open("./protocol/2_2.txt", "r", encoding='utf-8') as file:
                protocol = file.read()
            protocol = protocol.replace("<hostname>", str(hostname))
            protocol = protocol.replace("<port>", str(port))

            if flag == 1:
                s.connect((hostname, int(port)))
                send_message = []
                send_message.append('2')
                send_message.append(str(rfc_val))
                #adding for the portocol
                send_message.append(str(protocol))
                print("Downloading RFCs")
                s.sendall(str(send_message).encode())
                timer_start = time.time()
                with open('./RFC/received/rfc' + str(rfc_val) + '.txt', 'w+') as f:
                  while True:
                      data = s.recv(2048).decode()
                      print(data)
                      f.write(data)
                      if not data:
                          break
                  s.close()
                  f.close()
                timer_final = time.time() - timer_start
                print("Time to download the rfc numbered: ", str(rfc_val), timer_final)
                if temp_flag == 0:
                    with open('singular.csv', 'w+') as csv:
                        csv.write(str(rfc_val) + ',' + str(timer_final) + '\n')
                        temp_flag = 1
                elif temp_flag == 1:
                    with open('singular.csv', 'a') as csv:
                        csv.write(str(rfc_val) + ',' + str(timer_final) + '\n')
            else:
                print("EH")

def action(flag1):
  global super_list
  if int(flag1) == 1:
      #    if peer_list == {}:
      #        print("No data in hand to contact peers\nWill generate now")
      peer_list = get_peer_list()
      if "not registered" in peer_list:
          print(peer_list)
          return 0
      rfc_list = fetch_rfc(peer_list)
      super_ip_list = []
      temp_count = 0
      for count,ips in enumerate(super_list):
          for k,v in ips.items():
              super_ip_list.append(k)
          for value in rfc_list:
              for each in super_ip_list:
                  for key,val in value.items():
                      if str(key) == str(each):
                          print("Already there")
                          print(super_list[count])
                          del super_list[count]
                          super_list.append(value)
                          temp_count = 1
                          break
                      else:
                          temp_count = 0
      if temp_count == 0:
          for x in rfc_list:
              super_list.append(x)

      print("PEER LIST\n")
      print(peer_list)
      print("RFC LIST\n")
      print(rfc_list)

  elif int(flag1) == 2:
      print("RFC LIST\n")
      peer_list = get_peer_list()
      if "not registered" in peer_list:
          print(peer_list)
          return 0
      rfc_list = fetch_rfc(peer_list)
      super_ip_list = []
      temp_count = 0
      for count, ips in enumerate(super_list):
          for k, v in ips.items():
              super_ip_list.append(k)
          for value in rfc_list:
              for each in super_ip_list:
                  for key, val in value.items():
                      if str(key) == str(each):
                          print("Already there")
                          print(super_list[count])
                          del super_list[count]
                          super_list.append(value)
                          temp_count = 1
                          break
                      else:
                          temp_count = 0
      if temp_count == 0:
          for x in rfc_list:
              super_list.append(x)
      print("RFC:\n")
      print(rfc_list)
      print("Super list:\n")
      print(super_list)
      download_rfc(peer_list, rfc_list)

  elif int(flag1) == 3:
      print("RFC LIST\n")
      peer_list = get_peer_list()
      if "not registered" in peer_list:
          print(peer_list)
          return 0
      rfc_list = fetch_rfc(peer_list)
      super_ip_list = []
      temp_count = 0
      for count, ips in enumerate(super_list):
          for k, v in ips.items():
              super_ip_list.append(k)
          for value in rfc_list:
              for each in super_ip_list:
                  for key, val in value.items():
                      if str(key) == str(each):
                          print("Already there")
                          print(super_list[count])
                          del super_list[count]
                          super_list.append(value)
                          temp_count = 1
                          break
                      else:
                          temp_count = 0
      if temp_count == 0:
          for x in rfc_list:
              super_list.append(x)
      print("RFC:\n")
      print(rfc_list)
      print("Super list:\n")
      print(super_list)
      download_all(peer_list, rfc_list)

  elif int(flag1) == 4:
      pass

def ask_iterative():
  global super_list, counter_s_ttl
  print("This is the updated SUPER LIST (MERGED)\n")
  print(super_list)
  flag = input("Do you want to 1.Register 2.unregister 3.Fetch Peer List 4.Nothing?")
  if int(flag) == 1:
      register()
  elif int(flag) == 2:
      deregister()
  elif int(flag) == 3:
      peer_list = get_peer_list()
      print(peer_list)
  elif int(flag) == 4:
      pass
  flag1 = input("Do you want to 1.Fetch RFC Details 2.Download a RFC? 3.Download all RFCs 4.Do Nothing.")
  counter_s_ttl +=1
  print(counter_s_ttl)
  if counter_s_ttl == 2:
      print("im here")
      keepalive()
      counter_s_ttl = 0
  action(flag1)
  ask_again = input("Do you want to repeat the process?? (Yy/Nn)")
  if ask_again == 'Y' or ask_again == 'y':
      ask_iterative()
  elif ask_again == 'N' or ask_again == 'n':
  #    print(super_list)
      exit()

initial_func()
ttl_thread = threading.Thread(name = "Threading keepalive", target = ttl)
ttl_thread.setDaemon(True)
ttl_thread.start()
ask_iterative()







  # t2 = threading.Thread(name="Service func", target=inst1.service, args=(conn, addr, hostIP_port))
  # t2.start()



