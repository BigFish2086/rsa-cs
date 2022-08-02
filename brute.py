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


