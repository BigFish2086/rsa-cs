import socket

# import cgitb
from rsa import keygen, encrypt2, decrypt2

import pickle
import time
import os

DEBUG = False
# cgitb.enable(format="text")


class Client:
    def __init__(self, host, port, username=None):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.connect((self.host, self.port))
        print("[*] Connected to the server")
