import matplotlib.pyplot as plt
from rsa import keygen, encrypt2, decrypt2
import time


# length of n -> time to decrypt using brute force attack
data = {}
msg = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."


def plot_data():
    plt.plot(data.keys(), data.values())
    plt.show()


def main():
    for p in range(8, 1024):
        e, d, n = keygen(p)
        c = encrypt2(msg=msg, e=e, n=n)
        start = time.time()
        state, dec = decrypt2(cipher=c, d=d, n=n)
        end = time.time()
        if not state:
            continue
        data[p**2] = end - start
        # print(f"[*] enc {c}\n[*]dec {dec}\n")
        # print(f"[*] p: {p**2} take: {end - start}")
    plot_data()


if __name__ == "__main__":
    main()
    with open("./graphs-data/efficiency-data.txt", "w") as f:
        for k, v in data.items():
            f.write(f"{k} {v}\n")
    print("[*] data saved to efficiency-data.txt")
