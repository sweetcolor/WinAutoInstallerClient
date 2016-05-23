import socket
import sys
import os
import pickle


class Client:
    def __init__(self):
        self.host = '192.168.0.63'
        # host = 'localhost'
        self.port = 2000
        self.socket_obj = None
        os.chdir(os.environ['USERPROFILE'])
        self.name_log_file = 'win_auto_installer.log'
        self.log_file = open(self.name_log_file, 'w')
        self.start_connection()
        self.get_installer()
        
    def start_connection(self):
        self.socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while True:
            try:
                self.socket_obj.connect((self.host, self.port))
                print('connected...')
                break
            except ConnectionRefusedError:
                pass
        
    def get_installer(self):
        bin_buff_size = 1024
        num_buff_size = 16
        num_size = int(self.socket_obj.recv(num_buff_size).decode(), num_buff_size)
        installers_count = int(self.socket_obj.recv(num_size).decode())
        for i in range(installers_count):
            num_size = int(self.socket_obj.recv(num_buff_size).decode(), num_buff_size)
            installer_desc = self.socket_obj.recv(num_size)
            print(installer_desc)
            print(len(installer_desc))
            installer_desc = pickle.loads(installer_desc)
            name = installer_desc[0] + '.exe'
            argv = installer_desc[1]
            installer = open(name, 'wb')
            installer_size = int(self.socket_obj.recv(num_buff_size).decode(), num_buff_size)
            for i in range(installer_size // bin_buff_size):
                installer_part = self.socket_obj.recv(bin_buff_size)
                installer.write(installer_part)
                diff = bin_buff_size - len(installer_part)
                while diff:
                    installer_part = self.socket_obj.recv(diff)
                    installer.write(installer_part)
                    diff -= len(installer_part)
            installer_part = self.socket_obj.recv(installer_size % bin_buff_size)
            installer.write(installer_part)
            installer.close()
            self.add_to_log_file(name + ' ' + argv)
            self.add_to_log_file('Installing... ')
            c = os.popen(name + ' ' + argv)
            self.add_to_log_file('Installing done.\n')
        self.add_to_log_file('All programs installed.')
        self.log_file.close()
        self.send_log_file()
        self.socket_obj.close()

    def add_to_log_file(self, text):
        print(text)
        self.log_file.write(text + '\n')

    def send_log_file(self):
        self.log_file = open(self.name_log_file, 'rb')
        installer_size = os.path.getsize(self.name_log_file)
        self.socket_obj.send('{:016x}'.format(installer_size).encode())
        self.socket_obj.send(self.log_file.read())

if __name__ == '__main__':
    if len(sys.argv) > 1:
        host = sys.argv[1]
    client = Client()
