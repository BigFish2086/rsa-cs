# this file is used to read the json config file passed to client
# and return the parsed public key or private key or both
# since you can extract the public key from the private key and vice versa

import json
import os
import sys
import math
import re

from binascii import hexlify
from gmpy2 import mpz_urandomb, next_prime, random_state, is_prime

if sys.version_info < (3, 9):
    import gmpy2

    math.gcd = gmpy2.gcd
    math.lcm = gmpy2.lcm

DEBUG = False
SEED = int(hexlify(os.urandom(32)).decode(), 16)
STATE = random_state(SEED)


def get_prime(bits):
    return next_prime(mpz_urandomb(STATE, bits) | (1 << (bits - 1)))


def check(key, config):
    # check if key is in the confi and is correct int decimal or hex
    x = None
    if key in config:
        x = config[key]
        if re.fullmatch(r"[0-9]+", x):
            x = int(x)
        elif re.fullmatch(r"0x[0-9a-fA-F]+", x):
            x = int(x, 16)
        else:
            print(f"{key} is not an int or hex")
    return x


def parse_config(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

    p, q, e, d = [check(key, config) for key in ["p", "q", "e", "d"]]

    if p is None or q is None or e is None or d is None:
        print("[!] missing p, q, e or d")
        return False, None

    if not is_prime(p) or not is_prime(q):
        print("[!] p and q should be primes")
        return False, None

    if p == q:
        print("[!] p and q should not be equal")
        return False, None

    n = p * q

    if e < 3 or e % 2 == 0:
        print("[!] e should be an odd number greater than 2")
        return False, None

    m = (p - 1) * (q - 1)
    if math.gcd(e, m) != 1:
        print("[!] e and (p-1)(q-1) should be coprime")
        return False, None

    if d < 0 or d > m:
        print("[!] d should be between 0 and (p-1)(q-1)")
        return False, None

    if d * e % m != 1:
        print("[!] d and e should be a modular inverse")
        return False, None

    print(f"p: {p}\n")
    print(f"q: {q}\n")
    print(f"e: {e}\n")
    print(f"d: {d}\n")

    return True, (hex(n)[2:], hex(e)[2:], hex(d)[2:])


def parse_config2(config_file):
    with open(config_file, "r") as f:
        config = json.load(f)

    p, q, e = [check(key, config) for key in ["p", "q", "e"]]

    if p is None or q is None or e is None:
        print("[!] missing p, q, e")
        return False, None

    if not is_prime(p) or not is_prime(q):
        print("[!] p and q should be primes")
        return False, None

    if p == q:
        print("[!] p and q should not be equal")
        return False, None

    n = p * q

    if e < 3 or e % 2 == 0:
        print("[!] e should be an odd number greater than 2")
        return False, None

    m = (p - 1) * (q - 1)
    if math.gcd(e, m) != 1:
        print("[!] e and (p-1)(q-1) should be coprime")
        return False, None

    if e > m:
        print("[!] e should be less than PHI")
        return False, None

    d = pow(e, -1, m)

    print(f"p: {p}\n")
    print(f"q: {q}\n")
    print(f"e: {e}\n")
    print(f"d: {d}\n")

    return True, (hex(n)[2:], hex(e)[2:], hex(d)[2:])


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python parse_config.py <config_file>")
        sys.exit(1)
    config_file = sys.argv[1]
    if not os.path.isfile(config_file):
        print("Error: config file not found")
        sys.exit(1)
    status, keys = parse_config(config_file)
