# this should show how the chosen cipher attack works for rsa

import argparse
import random
import math
import time
from parse_logs import parse_logs
from binascii import unhexlify
from client import Client


DEBUG = False


# extended euclidean algorithm iterative version
def egcd(a, b):
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b // a, b % a
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    gcd = b
    return gcd, x, y


# modulue inversion
def modinv(a, m):
    g, x, _ = egcd(a, m)
    if g != 1:
        raise Exception("modular inverse does not exist")
    else:
        return x % m
        # return pow(a, m - 2, m)


# b -> a | S b a <msg_cipher> | b, a - a | r -> msg_cipher * (r^e % n) | S attacker a <new_cihper> | B --- |
def gen_bad_message(old_cipher, n, e):
    n = int(n, 16)
    e = int(e, 16)
    # generate random number r such gcd(r, n) = 1
    # r = 2
    r = random.randint(1, n)
    while math.gcd(r, n) != 1:
        r = random.randint(1, n)
    # old_cipher from being hex to int
    new_cipher_b16 = ""
    for enc_num_b16 in old_cipher.split(" "):
        enc_num = int(enc_num_b16, 16)
        if len(new_cipher_b16) > 0:
            new_cipher_b16 += " "
        new_cipher_b16 += f"{hex(enc_num * pow(r, e, n))}"
    return new_cipher_b16, hex(r)[2:]


# ((msg^e % n) * (r^e % n)) ^ d % n
def chosen_cipher_attack(cipher, r, n):
    n = int(n, 16)
    r = int(r, 16)
    rinv = modinv(r, n)
    cipher_b10 = ""
    for enc_num_b16 in cipher.split(" "):
        enc_num = int(enc_num_b16, 16)
        cipher_b10 += str((enc_num * rinv) % n)
    msg_b16 = hex(int(cipher_b10))[2:]
    dec = ""
    try:
        dec = unhexlify(msg_b16).decode("utf-8")
        return True, dec
    except Exception as e:
        # if DEBUG:
        print(e)
        return False, msg_b16


def spwan_attacker_client(victim_name):
    client = Client("localhost", 9998, "attacker")
    client.custom_send("/list")
    client.recv_list_of_users(victim_name)
    return client


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="Brute force attack on N")
    parser.add_argument("-f", "--file", help="server logs file", required=True, type=str, dest="file")

    args = parser.parse_args()
    file = args.file

    # parse the server logs file
    public_keys, enc_sent_messages, bad_recieved_messages, disconnected = parse_logs(file)
    bad_prev_len = len(bad_recieved_messages)

    if DEBUG:
        print(f"{public_keys}\n\n")
        print(f"{enc_sent_messages}\n\n")
        print(f"{bad_recieved_messages}\n\n")
        print(f"{disconnected}\n\n")

    # delete the disconnected clients
    for client in disconnected:
        public_keys.pop(client, None)
        enc_sent_messages.pop(client, None)
        bad_recieved_messages.pop(client, None)

    # check if there is still active clients
    print("[*] This attack only work with active clients.")
    if len(public_keys) == 0:
        print("[!] No active clients")
        exit()

    # get the user to choose which client to brute force
    print("[*] Which client do you want to attack?")
    just_names = [c.split("-")[0] for c in public_keys.keys()]
    for c in just_names:
        print(" - " + c.split("-")[0])

    victim_name = input("[*] Client: ")
    # check if the client is in the list of clients
    if victim_name not in just_names:
        print("[!] Client not found")
        exit(1)

    complete_victim_name = [c for c in public_keys.keys() if c.split("-")[0] == victim_name][-1]

    print("[*] Decrypting that client last message")
    # get the public key and cipher text
    e = public_keys[complete_victim_name][0]
    n = public_keys[complete_victim_name][1]
    c1 = enc_sent_messages[complete_victim_name][-1]
    c2, r = gen_bad_message(c1, n, e)

    attacker_client = spwan_attacker_client(victim_name)
    attacker_client.custom_send(c2)  # won't decrypt it, logs it in b16 form

    print("[*] Wait for the victim to open his mail box")
    _, _, bad_recieved_messages, _ = parse_logs(file)
    bad_curr_len = len(bad_recieved_messages)
    while True:
        if bad_curr_len > bad_prev_len and complete_victim_name in bad_recieved_messages.keys():
            break
        else:
            _, _, bad_recieved_messages, _ = parse_logs(file)
            bad_prev_len = bad_curr_len
            bad_curr_len = len(bad_recieved_messages)
        time.sleep(1)

    print("[*] Decrypting the message")
    d1 = bad_recieved_messages[complete_victim_name][-1]
    state, d2 = chosen_cipher_attack(d1, r, n)
    if state:
        print(f"[*] Decrypted message: {d2}")
    else:
        print("[!] Failed to decrypt the message")
