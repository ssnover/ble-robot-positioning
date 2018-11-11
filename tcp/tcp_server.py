#!/usr/bin/env python

import socket # tcp methods
import sys    # command line methods

def tcp_server_init( ip_address = '127.0.0.1', tcp_port = 5005 ):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # prep a socket for server operation
    sock.bind((ip_address, tcp_port))                        # assign address for clients to find
    return sock

def tcp_server_listen( sock ):
    sock.listen(1)                      # await connections
    conn, addr = sock.accept()          # grab the client's info
    print ('Connection address:', addr) # debug: display client info
    return conn

def tcp_conn_receive( conn ):
    size = conn.recv(4)                               # receive size of imminent file (4 bytes = 4GB max)
    file_buffer_size = int.from_bytes(size, 'big')    # interpret data as a single number
    print ('projected data size: ', file_buffer_size) # debug: display file byte count
    conn.send(b'g')                                   # signal the file send
    data = conn.recv(file_buffer_size)                # buffer sized to match the file
    print ('received data size: ', len(data))         # debug: report file_buffer_size
    conn.send(b'd')                                   # report result of transfer
    return data

def tcp_conn_close( conn ):
    conn.close()
    return

if __name__ == "__main__":
    # command line parse
    if (len(sys.argv) > 1 and len(sys.argv) < 5): # anticipate 1-3 arguments
        file_name = str(sys.argv[1])              # path and name for file to store server-side
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

    # server code:
    sock = tcp_server_init(ip_addr, t_port) # start the server
    conn = tcp_server_listen(sock)          # wait for a client to connect to the server
    destFile = open(file_name, "wb+")       # create/overwrite file with incoming data
    data = tcp_server_receive(conn)         # receive file data from client
    destFile.write(data)                    # assemble the new file server-side
    destFile.close()                        # server accomplished file transfer job
    tcp_server_close(conn)                  # done talking to client, sever connection
    print ('done')
