#!/usr/bin/python3
import sys
import socket
import getopt
import threading
import subprocess

#定义一些全局变量
listen      = False
command     = False
upload      = False
target      = ""
upload_des  = ""
port        = 0


def client_sender():
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        client.connect((target,port))
        response = ""
        # while True:
        #     data = client.recv(4096)
        #     response += str(data,encoding='gb2312')
        #     if len(data)<4096:
        #         break
        # print(response)
        while True:
            buffer = sys.stdin.readline()
            if len(buffer):
                client.send(bytes(buffer,encoding='gb2312'))
            response = ""
            while True:
                data = client.recv(4096)
                response += str(data,encoding='gb2312')
                if len(data)<4096:
                    break
            # print("the res is %s" % response)
            print(response)
    except:
        print("Some error in client_sender!")
        client.close()

def run_command(command):
    try:
        output = subprocess.check_output(command,shell = True,)
    except:
        output = "Failed to execute command.\r\n"
    finally:
        return str(output,encoding='gb2312')

def client_handle(client_socket):
    global upload
    global execute
    global command
    
    if command:
        # client_socket.send(bytes("now,you can exec some shell command!",encoding='gb2312'))
        while True:
            cmd_str = ""
            while True:
                cmd_str += str(client_socket.recv(1024),encoding='gb2312')
                if "\n" in cmd_str:
                    break
            print(cmd_str)
            response = run_command(cmd_str)
            client_socket.send(bytes(response,encoding='gb2312'))

def server_loop():
    global target
    if not len(target):
        target = '0.0.0.0'
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(10)
    while True:
        client_socket,addr = server.accept()
        client_thread = threading.Thread(target = client_handle,args=(client_socket,))
        client_thread.start()

def usage():
    print("BHP NET TOOL")
    print()
    print("Usage:bhpnet.py -t target_host -p port")
    print("-l --listen  listen on [host]:[port]")
    # print("-e --execute=file_to_run     execute the given fiel")
    print("-c --command     initialize a command shell")
    print("-u --upload=destination")
    print()
    print()
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_des
    global target

    if not len(sys.argv[1:]):
        usage()
    try:
        opts,args = getopt.getopt(sys.argv[1:],"hle:t:p:cu",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as e:
        print(e)
        usage()
    print(opts)
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        # elif o in ("-e","--execute"):
        #     execute = a
        elif o in ("-c","--command"):
            command = True
        elif o in ("-u","upload"):
            upload_des = a 
        elif o in ("-t","--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            assert False,"Unhandled Option"
    if not listen:
        client_sender()
    elif listen:
        server_loop()

if __name__ == '__main__':
    main()



