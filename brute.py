# this is a brute force attack on N for rsa encryption
# this is made possible after parsing the server logs file

import argparse
from parse_logs import parse_logs

# from rsa import decrypt
from rsa import decrypt2


DEBUG = False


def brute_force(n, e, c):
    dec_n = int(n, 16)
    dec_e = int(e, 16)
    for i in range(2, dec_n):
        if dec_n % i == 0:
            p = i
            q = dec_n // i
            m = (p - 1) * (q - 1)
            d = pow(dec_e, -1, m)
            if d != 0:
                hex_d = f"{d:x}"
                state, dec = decrypt2(c, n, hex_d)
                return dec


if __name__ == "__main__":
    # parse arguments
    parser = argparse.ArgumentParser(description="Brute force attack on N")
    parser.add_argument("-f", "--file", help="server logs file", required=True, type=str, dest="file")

    args = parser.parse_args()
    file = args.file

    # parse the server logs file
    public_keys, enc_sent_messages, bad_recieved_messages, disconnected = parse_logs(file)

    if DEBUG:
        print(f"{public_keys}\n\n")
        print(f"{enc_sent_messages}\n\n")
        print(f"{bad_recieved_messages}\n\n")
        print(f"{disconnected}\n\n")

    # get the user to choose which client to brute force
    print("[*] Which client do you want to brute force?")
    allowd_clients = [i for i in list(enc_sent_messages.keys())[-2:]]
    just_names = [c.split("-")[0] for c in allowd_clients]
    just_names = list(dict.fromkeys(just_names))
    for c in just_names:
        print(" - " + c)

    victim_name = input("[*] Client: ")
    # check if the client is in the list of clients
    if victim_name not in just_names:
        print("[!] Client not found")
        exit(1)

    complete_victim_name = [c for c in allowd_clients if c.split("-")[0] == victim_name][-1]

    if DEBUG:  # check if it's the last client
        print(f"[*] Brute forcing {complete_victim_name}")

    try:
        print(f"[*] Brute forcing client {victim_name} last message ")
        # get the public key and cipher text
        e = public_keys[complete_victim_name][0]
        n = public_keys[complete_victim_name][1]
        c = enc_sent_messages[complete_victim_name][-1]
        # brute force the cipher text
        plain_text = brute_force(n, e, c)
        print(f"[*] Plain text: {plain_text}")
    except Exception as e:
        print("[!] Error May be that client didn't send any messages")
        if DEBUG:
            print(e)
