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

    def get_pub_key(self, client):
        # get the client public key
        n = self.custom_recv(client)
        if n is False:
            self.remove_client(client)
            return False
        e = self.custom_recv(client)
        if e is False:
            self.remove_client(client)
            return False
        n = n.decode("utf-8")
        e = e.decode("utf-8")

        # add that public_key to clients
        self.clients[client][0] = e
        self.clients[client][1] = n

        # save that event in the log file
        self.log("I {} changed key at {}\n".format(self.username(client), time.ctime()))
        self.log("P {} {} {}\n".format(self.username(client), e, n))

    def listen_to_client(self, client):
        # get the client username, for first connection
        client_username = self.set_client_username(client)
        if client_username is False:
            return

        # gen public key for the cur client
        self.clients[client] = [None, None, client_username]
        self.get_pub_key(client)

        # get the client's message
        while True:
            try:
                # receive the message from the client until he disconnects
                data = self.custom_recv(client)
                # if the client sends just "/list", send him the list of clients, if changing other client
                if DEBUG and data is not False:
                    print(data)
                if data == b"/key":
                    self.get_pub_key(client)
                elif data == b"/list":
                    self.send_clients_list(client)
                # if data is "/quit", remove the client from the list and close the connection
                elif data == b"/quit":
                    self.remove_client(client)
                    return False
            except Exception as e:
                self.remove_client(client)
                if DEBUG:
                    print(e)
                return False

    def username(self, client):
        return self.clients[client][-1]

    def set_client_username(self, client):
        self.custom_send(client, "[*] Enter a username: ")
        client_username = self.custom_recv(client)
        if client_username is False:
            return False
        # if the client is already in the list, send him a message
        if client_username is not False and client_username in [self.username(c) for c in self.clients.keys()]:
            self.custom_send(client, "[!] Username already taken")
            client.close()
            return False
        # if the client is not in the list, send him a message
        else:
            self.custom_send(client, "[*] Welcome to the chatroom, " + client_username.decode("utf-8").split("-")[0])
            # add the client to the list with his username
            return client_username.decode("utf-8")

    def send_clients_list(self, client):
        # check how many clients are in the list
        if len(self.clients) == 1:
            self.custom_send(client, "[*] There is only you in the chatroom. Wait for someone to connect")
            return False
        # build a pickle list of all the clients usernames
        clients_list = [self.username(c).split("-")[0] for c in self.clients.keys() if c is not client]
        pobj = pickle.dumps(clients_list)
        self.custom_send(client, pobj)
        if DEBUG:
            print(pobj)
        # get the client's message
        client_choice = self.custom_recv(client)
        if DEBUG:
            print(client_choice)
        if client_choice is False:
            return False
        client_choice = client_choice.decode("utf-8")
        # if the client is not in the list, send him a message
        if client_choice is not False and client_choice not in clients_list:
            self.custom_send(client, "[!] No such client")
            return False
        # if the client is in the list, send him a message
        else:
            self.custom_send(client, f"[*] Send your next message to: {client_choice}")
            # get the other client
            other_client = [c for c in self.clients.keys() if self.username(c).split("-")[0] == client_choice][-1]
            # add the other client to the list of clients that are talking
            self.talking_clients[client] = other_client
            # send other client public key
            other_e = self.clients[other_client][0]
            other_n = self.clients[other_client][1]
            self.custom_send(client, str(other_e))
            self.custom_send(client, str(other_n))
            return True

    def remove_client(self, client):
        # save the disconnection in the logs file
        print("[*] Client {} has disconnected at {}".format(self.username(client), time.ctime()))
        self.log("D {} {}\n".format(self.username(client), time.ctime()))
        self.clients.pop(client, None)
        self.talking_clients.pop(client, None)
        for c1, c2 in self.talking_clients.items():
            if c2 == client:
                self.talking_clients[c1] = None
        client.close()

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
