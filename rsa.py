from binascii import hexlify, unhexlify
from gmpy2 import mpz_urandomb, next_prime, random_state
import math
import os
import sys
import random

if sys.version_info < (3, 9):
    import gmpy2

    math.gcd = gmpy2.gcd
    math.lcm = gmpy2.lcm


DEBUG = False
BITS = 1024
SEED = int(hexlify(os.urandom(32)).decode(), 16)
STATE = random_state(SEED)

if DEBUG:
    BITS = 8


def get_prime(bits):
    return next_prime(mpz_urandomb(STATE, bits) | (1 << (bits - 1)))


def keygen(bits=BITS):
    p = get_prime(bits)
    q = get_prime(bits)
    if p == q:
        return keygen()
    n = p * q
    m = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, m)
    if DEBUG:
        print(f"p: {p}\n")
        print(f"q: {q}\n")
        print(f"e: {e}\n")
        print(f"d: {d}\n")
    return (f"{e:x}", f"{d:x}", f"{n:x}")


def encrypt2(msg, n, e):
    n = int(n, 16)
    e = int(e, 16)
    msg = int(hexlify(msg.strip().encode()), 16)
    msg = str(msg)
    # 123 2 50|23|46 >>> +++ +++ ++
    stride = len(str(n)) - 1
    if stride < 1:
        stride = 1
    msg_cut = [msg[i : i + stride] for i in range(0, len(msg), stride)]
    cipher = ""
    for cur in msg_cut:
        if len(cipher) > 0:
            cipher += " "
        cipher += f"{hex(pow(int(cur), e, n))}"
    return cipher


def decrypt2(cipher, n, d):
    n = int(n, 16)
    d = int(d, 16)
    msg = ""
    tmp_msg_b16 = ""
    for enc_num_b16 in cipher.split(" "):
        enc_num = int(enc_num_b16, 16)
        enc_num = int(enc_num)
        cur = pow(enc_num, d, n)
        msg += f"{cur}"
        if len(tmp_msg_b16) > 0:
            tmp_msg_b16 += " "
        tmp_msg_b16 += f"{(hex(cur)[2:])}"

    msg = int(msg)
    msg_b16 = f"{hex(msg)[2:]}"
    msg_b16 = msg_b16.encode()
        return True, dec
    except Exception as e:
        if DEBUG:
            print(e)
        return False, tmp_msg_b16
    try:
        dec = unhexlify(msg_b16).decode("utf-8")