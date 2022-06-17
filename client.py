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
        self.header_len = 10  # used to detect the size of the message
        self.other_public_key = []
        print("[*] Connected to the server")
        self.send_username(username)
        self.set_keys()
        print("[*] Sent The public key to the server")
        print("[*] Use command /list to see the list of users")
        print("[*] Use command /quit to quit the chatroom")

    def custom_send(self, data):
        # We must encode the message to bytes, or the receiver will not understand it
        if isinstance(data, str):
            data = data.encode("utf-8")
        # Encode the length of the message (as a byte)
        message_length = f"{len(data):<{self.header_len}}".encode("utf-8")
        self.sock.send(message_length)
        self.sock.send(data)

    def custom_recv(self):
        try:
            # Receive our "header" containing message length, it's size is defined and constant
            message_header = self.sock.recv(self.header_len)
            if not len(message_header):
                return False
            # Convert header to int value
            message_length = int(message_header.decode("utf-8").strip())
            # Return an object of message header and message data
            return self.sock.recv(message_length)
        except Exception as e:
            if DEBUG:
                print(f"[!] ERROR {e}")
            return False

    def send_username(self, username=None):
        # 1. receive `[*] Enter a username: `
        msg = self.custom_recv()
        if msg is False:
            return False
        print(msg.decode("utf-8"))

        # 2. send username
        # TODO: check if username is valid
        self.username = str(input()) if not username else username
        self.username += "-" + str(time.time()).replace(".", "")
        self.custom_send(self.username)

        # 3. receive `[*] Welcome to the chatroom, {username}` or `[!] Username already taken` and exit
        msg = self.custom_recv()
        if msg is False:
            return False
        msg = msg.decode("utf-8")
        print(msg)
        if "Welcome" not in msg:
            exit()


    def recv_list_of_users(self, other_username=None):
        # recive list of users in a form of picled string and print them out
        users = self.custom_recv()
        if users is False:
            return False
        elif b"Wait" in users:
            print(users.decode("utf-8"))
            return True
        print("[*] Send your next message to:")
        users = pickle.loads(users)
        for user in users:
            print(" - " + user)

        print("[*] Enter the username of the client you want to talk to: ")

        # TODO: check if choice is valid
        choice = str(input(f"{self.username} #> ")) if not other_username else other_username
        self.custom_send(choice.encode("utf-8"))

        # receive `[*] Send your next message to: {username}` or `[!] No such client` and exit
        msg = self.custom_recv()
        if msg is False:
            return False
        msg = msg.decode("utf-8")
        print(msg)
        if "No such client" in msg:
            if choice in self.username:
                print("[!] You can not talk to yourself")
            print("[!] Try again with a valid username")
            return False

        # recive other client public key
        other_e = self.custom_recv()
        other_n = self.custom_recv()
        if other_n is False or other_e is False:
            return False
        self.other_public_key = [other_n, other_e]

        if DEBUG:
            print(f"Other public key: \n\nn: {other_n}\n\ne: {other_e}\n\n")

        return True

    def set_keys(self, n=None, e=None, d=None):
        if n is None or e is None or d is None:
            e, d, n = keygen()
        self.public_key = [n, e]
        self.private_key = [n, d]
        self.custom_send(str(n))
        self.custom_send(str(e))

    def __del__(self):
        self.custom_send("/quit")
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()


