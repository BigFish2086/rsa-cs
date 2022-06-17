# import cgitb
import socket
import threading
import os
import pickle
import time
import string
import random
import re
import argparse

DEBUG = False
# cgitb.enable(format='text')


class Server:
    def __init__(self, host, port, save_logs=False):
        self.host = host
        self.port = port
        self.save_logs = save_logs
        self.log_filename = "./logs/" + "".join(random.choice(string.ascii_letters + string.digits) for _ in range(8))
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        self.sock.listen(5)
        self.clients = {}  # {client: [pub(e, n), username]}
        self.talking_clients = {}  # {client: other_client}
        self.header_len = 10  # used to detect the size of the message
        welcom_msg = "I Server started {}:{} at {}".format(self.host, self.port, time.ctime())
        print(welcom_msg)
        print("[*] Logs will be saved in {}".format(self.log_filename))
        self.log(welcom_msg + "\n")

    def start(self):
        while True:
            client, address = self.sock.accept()
            client.settimeout(60)
            threading.Thread(target=self.listen_to_client, args=(client,)).start()
            print("[*] Client connected at {}".format(address))
            self.log("I Client connected at {} at {}\n".format(address, time.ctime()))

    def log(self, data):
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        if self.save_logs:
            with open(self.log_filename, "a") as f:
                f.write(data)

    def custom_send(self, client, data):
        # We must encode the message to bytes, or the receiver will not understand it
        if isinstance(data, str):
            data = data.encode()
        # Encode the length of the message (as a byte)
        message_length = f"{len(data):<{self.header_len}}".encode("utf-8")
        client.send(message_length)
        client.send(data)

    def custom_recv(self, client):
        try:
            # Receive our "header" containing message length, it's size is defined and constant
            message_header = client.recv(self.header_len)
            if not len(message_header):
                return False
            # Convert header to int value
            message_length = int(message_header.decode("utf-8").strip())
            # Return an object of message header and message data
            return client.recv(message_length)
        except Exception as e:
            if DEBUG:
                print(e)
            return False

    def listen_to_client(self, client):
        pass

    def __del__(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


def create_dirs():
    def create_dir(path):
        if not os.path.exists(path):
            os.makedirs(path)

    try:
        create_dir(os.path.join(os.getcwd(), "logs"))
        create_dir(os.path.join(os.getcwd(), "mails"))
        return True
    except Exception as e:
        if DEBUG:
            print(e)
        return False


if __name__ == "__main__":
    if create_dirs():
        server = Server("localhost", 9998, save_logs=True)
        server.start()
    else:
        print("[!] Can't Create `logs`, `mails` directories")
        print("[*] Check permisions or try creating them manual first")
        exit(1)
