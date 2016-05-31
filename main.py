import socket
import sys
import os
from command_file import CommandFile
from thread_decorator import thread


class Client:
    def __init__(self):
        self.host = '192.168.0.63'
        # host = 'localhost'
        self.port = 2000
        self.socket_obj = None
        self.bin_buff_size = 1024
        self.num_buff_size = 16
        os.chdir(os.environ['USERPROFILE'])
        self.name_log_file = 'win_auto_installer.log'
        self.log_file = open(self.name_log_file, 'w')
        self.start_connection()
        start = b'START'
        if self.socket_obj.recv(len(start)):
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
            except TimeoutError:
                pass

    def get_installer(self):
        self.add_to_log_file('Start preparing to installation')
        self.add_to_log_file('Loading service data... ')
        installers_name = self.get_bin_file(CommandFile()).pickle_loads_data()
        self.add_to_log_file('Service data downloaded')
        for installer_name in installers_name:
            self.add_to_log_file('Loading %s... ' % installer_name)
            self.get_bin_file(open(installer_name, 'wb'))
            self.add_to_log_file('%s downloaded' % installer_name)
        self.add_to_log_file('Loading installation scripts... ')
        installers_scripts = self.get_bin_file(CommandFile()).pickle_loads_data()
        self.add_to_log_file('Installation scripts downloaded')
        self.add_to_log_file('Preparing to installation done')
        self.add_to_log_file('Start installation')
        for installer_name in installers_scripts:
            self.add_to_log_file('Installing %s... ' % installer_name)
            self.add_to_log_file('%s' % installers_scripts[installer_name])
            os.popen(installers_scripts[installer_name])
            self.add_to_log_file('%s installed.' % installer_name)
        self.add_to_log_file('All programs installed.')
        self.add_to_log_file('END')
        self.socket_obj.close()
        for installer_name in installers_name:
            os.remove(installer_name)

    def get_bin_file(self, file_):
        installer_size = int(self.socket_obj.recv(self.num_buff_size).decode(), self.num_buff_size)
        for i in range(installer_size // self.bin_buff_size):
            installer_part = self.socket_obj.recv(self.bin_buff_size)
            file_.write(installer_part)
            self.update_progress(len(installer_part))
            diff = self.bin_buff_size - len(installer_part)
            while diff:
                installer_part = self.socket_obj.recv(diff)
                file_.write(installer_part)
                self.update_progress(len(installer_part))
                diff -= len(installer_part)
        installer_part = self.socket_obj.recv(installer_size % self.bin_buff_size)
        file_.write(installer_part)
        self.update_progress(len(installer_part))
        file_.close()
        return file_

    def update_progress(self, size_get_part):
        self.send_data(str(size_get_part).encode())

    def send_data(self, data):
        self.socket_obj.send('{:016x}'.format(len(data)).encode())
        self.socket_obj.send(data)

    def add_to_log_file(self, text):
        print(text)
        message = text.encode() + b'\n'
        self.send_data(message)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        host = sys.argv[1]
    client = Client()
