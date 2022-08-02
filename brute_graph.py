import matplotlib.pyplot as plt
from rsa import keygen, encrypt2
from brute import brute_force
import time


# length of n -> time to decrypt using brute force attack
data = {}
msg = "Lorem ipsum dolor sit amet, qui minim labore adipisicing minim sint cillum sint consectetur cupidatat."


def plot_data():
    plt.plot(data.keys(), data.values())
    plt.show()


def main():
    for p in range(8, 25):
        e, d, n = keygen(p)
        c = encrypt2(msg=msg, e=e, n=n)
        start = time.time()
        dec = brute_force(n=n, e=e, c=c)
        end = time.time()
        data[p**2] = end - start
        # print(f"[*] enc {c}\n[*]dec {dec}\n")
        # print(f"[*] p: {p**2} take: {end - start}")
    plot_data()


if __name__ == "__main__":
    main()
    with open("./graphs-data/brute-data.txt", "w") as f:
        for k, v in data.items():
            f.write(f"{k} {v}\n")
    print("[*] data saved to brute-data.txt")
