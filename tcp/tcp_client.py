#!/usr/bin/env python

import socket # tcp methods
import sys    # command line methods

def tcp_client_connect( ip_address = '127.0.0.1', tcp_port = 5005 ):
    "create and connect a tcp socket on the client to the server"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # prep a socket for server operation
    try:
        sock.connect((ip_address, tcp_port))                 # give address of server to connect to
    except socket.error as err:
        print("Socket connection failed:\n {0}".format(err))
        return -1
    return sock

def tcp_client_send( sock, data ):
    "data should be a byte array; sends the length of the data, waits for an ack', then sends the data, then waits for another ack'"
    size = len(data)
    try:
        sock.send((size).to_bytes(4, byteorder='big')) # send data size in 4 bytes
    except socket.error as err:
        print("size transmission failed:\n {0}".format(err))
        return -1
    ack_flag = sock.recv(1)                            # read-in acknowledge
    print ("size transmission response: ", ack_flag.decode("utf-8"))
    try:
        sock.send(data)                                # send the data
    except socket.error as err:
        print("data transmission failed:\n {0}".format(err))
        return -1
    ack_flag = sock.recv(1)                            # read-in acknowledge
    print ("data transmission response: ", ack_flag.decode("utf-8"))
    return 0

def tcp_client_close( sock ):
    "sever the connection to the server"
    sock.close() # done talking to server
    return

if __name__ == "__main__":
    # command line parse
    if (len(sys.argv) > 1 and len(sys.argv) < 5): # anticipate 1-3 arguments
        file_name = str(sys.argv[1])              # path and name for file to send
        if (len(sys.argv) > 2):                   # optional argument #1
            ip_addr = str(sys.argv[2])            # IP of the server socket
            if (len(sys.argv) == 4):              # optional argument #2
                t_port = int(sys.argv[3])         # port # of the server socket
            else:
                t_port = 5005
        else:
            ip_addr = '127.0.0.1'
            t_port = 5005
    else:                                         # print usage info if no args or too many
        print('Usage: ', sys.argv[0], ' filename ip_address tcp_port')
        exit(2)
    
    # client code
    sourceFile = open(file_name, "rb") # open passed-in file
    fileData = sourceFile.read()       # read-in file
    data = bytearray(fileData)         # split into bytes for transfer
    sourceFile.close()                 # clean
    size = len(data)                   # file size
    print("file size: ", size)         # debug: display read file size
    
    sock = tcp_client_connect(ip_addr, t_port)               # establish server connection
    if (sock == -1):
        print("error encountered at connection, exitting\n")
        exit(2)
    e_code = tcp_client_send(sock, data)                     # send data to server
    if (e_code == -1):
        print("error encountered at send, exitting\n")
        exit(2)
    tcp_client_close(sock)                                   # close connection to server
    print("Done")
