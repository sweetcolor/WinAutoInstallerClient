import socket
import sys
import os
import pickle

host = '192.168.0.63'
# host = 'localhost'
port = 2000

if len(sys.argv) > 1:
    host = sys.argv[1]

socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        socket_obj.connect((host, port))
        print('connected...')
        break
    except ConnectionRefusedError:
        pass
bin_buff_size = 1024
num_buff_size = 16
num_size = int(socket_obj.recv(num_buff_size).decode(), num_buff_size)
recv = socket_obj.recv(num_size)
print(recv)
print(len(recv))
installers_count = int(recv.decode())
for i in range(installers_count):
    # installer_desc = b''
    num_size = int(socket_obj.recv(num_buff_size).decode(), num_buff_size)
    installer_desc = socket_obj.recv(num_size)
    print(installer_desc)
    print(len(installer_desc))
    # name_part = socket_obj.recv(buff_size)
    # while name_part:
    #     installer_desc += name_part
    #     name_part = socket_obj.recv(buff_size)
    installer_desc = pickle.loads(installer_desc)
    name = installer_desc[0] + '.exe'
    argv = installer_desc[1]
    os.chdir(os.environ['USERPROFILE'])
    installer = open(name, 'wb')
    installer_size = int(socket_obj.recv(num_buff_size).decode(), num_buff_size)
    for i in range(installer_size // bin_buff_size):
        installer_part = socket_obj.recv(bin_buff_size)
        installer.write(installer_part)
        diff = bin_buff_size - len(installer_part)
        while diff:
            installer_part = socket_obj.recv(diff)
            installer.write(installer_part)
            diff -= len(installer_part)
    installer_part = socket_obj.recv(installer_size % bin_buff_size)
    installer.write(installer_part)
    installer.close()
    print(name + ' ' + argv)
    print('Installing... ')
    c = os.popen(name + ' ' + argv)
    print('Installing done.\n')
print('All programs installed.')


    # while True:
    #     installer_part = socket_obj.recv(buff_size)
    #     if not installer_part:
    #         break
    #     print(installer_path)
    #     res_file = open(installer_path, 'wb')
    #     while installer_part:
    #         res_file.write(installer_part)
    #         installer_part = socket_obj.recv(buff_size)
    #     res_file.close()
    #     os.popen(installer_path)

    # curr_get_data = socket_obj.recv(1024)
    # res_data = b''
    # while curr_get_data:
    #     res_data += curr_get_data
    #     curr_get_data = socket_obj.recv(1024)
    # print('++', len(res_data), '++')
    # print('Get from server: ', pickle.loads(res_data))

socket_obj.close()
