import socket
import os
import threading
import subprocess
import pickle

HOST = '10.152.13.188'
#HOST = '192.168.0.10'
PORT = 65423
ttl_flag = 0
rfc_server = 65400

def register():
    global rfc_server
    print("Im here")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST,PORT))
#        print(s.getpeername())
        my_det = (s.getsockname())

        # adding for the protocol
        with open("./protocol/1_1.txt", "r", encoding='utf-8') as file:
            protocol = file.read()
        protocol = protocol.replace("<hostname>", str(HOST))
        protocol = protocol.replace("<port>", str(PORT))
        print(protocol)
        if os.path.exists(os.getcwd().join('./cookie.txt')):
            print("OLD CONNECTION")
            with open("cookie.txt", 'r', encoding='utf-8') as file:
                cookie_data = file.readlines()[0]
            send_message = []
            send_message.append('1')
            send_message.append(str(my_det[0]))
            send_message.append(str(rfc_server))
            send_message.append(str(protocol))
			to_send = pickle.dumps(send_message)
            s.sendall(to_send)
#            s.sendall(str(send_message).encode())
            data = s.recv(1024).decode()
#            print("Received this!\n", data)
            with open("cookie.txt", 'w+', encoding='utf-8') as file:
                file.writelines(data)
            s.close()
        else:
            send_message = []
            send_message.append('1')
            send_message.append(str(my_det[0]))
            send_message.append(str(rfc_server))
            send_message.append(str(protocol))
            to_send = pickle.dumps(send_message)
            s.sendall(to_send)
            data = s.recv(1024).decode()
#            print("Received this!\n", data)
            with open("cookie.txt", 'w+', encoding='utf-8') as file:
                file.writelines(data)
            s.close()
        print('Received', data)


def deregister():
    global rfc_server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        my_det = (s.getsockname())
        # adding for the protocol
        with open("./protocol/2_1.txt", "r", encoding='utf-8') as file:
            protocol = file.read()
        protocol = protocol.replace("<hostname>", str(HOST))
        protocol = protocol.replace("<port>", str(PORT))
        print(protocol)
        send_message = []
        send_message.append('2')
        send_message.append(str(my_det[0]))
        send_message.append(str(rfc_server))
        send_message.append(str(protocol))
        to_send = pickle.dumps(send_message)
        s.sendall(to_send)
#        s.sendall(pickle.dumps(send_message))
#        send_message = '2'
#        s.sendall(str(send_message).encode())
        print("Deleting the cookie stored in cache\n")
        subprocess.getoutput("rm ./cookie.txt")
        data = s.recv(1024).decode()
#        print(data)
        s.close()


def get_peer_list():
    global rfc_server
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        my_det = (s.getsockname())
        #adding the code for protocols
        with open("./protocol/3_1.txt","r",encoding='utf-8') as file:
            protocol = file.read()
        protocol = protocol.replace("<hostname>", str(HOST))
        protocol = protocol.replace("<port>", str(PORT))
        print(protocol)
        send_message = []
        send_message.append('3')
        send_message.append(str(my_det[0]))
        send_message.append(str(rfc_server))
        send_message.append(str(protocol))
        print("Gothaaa")
        print(send_message)
        to_send = pickle.dumps(send_message)
        s.sendall(to_send)
#        send_message = '3'
#        s.sendall(str(send_message).encode())
#        data = s.recv(1024).decode()
        data = pickle.loads(s.recv(1024))
        print("Fetching Details of other clients\n")
 #       print(data)
  #      print(type(data))
        s.close()
        return(data)


def keepalive():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        my_det = (s.getsockname())

        #adding for the protocol
        with open("./protocol/700_1.txt","r",encoding='utf-8') as file:
            protocol = file.read()
        protocol = protocol.replace("<hostname>", str(HOST))
        protocol = protocol.replace("<port>", str(PORT))
        print(protocol)
        send_message = []
        send_message.append('700')
        send_message.append(str(my_det[0]))
        send_message.append("")
        send_message.append(str(protocol))
        to_send = pickle.dumps(send_message)
        s.sendall(to_send)
        data = s.recv(1024).decode()
        print("Updated keepalive ACK\n")
        print(data)
        s.close()
