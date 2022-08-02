import time
from client import Client


# this is used to receive the message from client b
# then wait and checks his mail
# if the attacker sends him a message it should be read then
# then this client will resend it as a bad message to the server
# the attacker will then be able to read the message from the logs
def spwan_test_client_a():
    client = Client("localhost", 9998, username="a")
    return client


# this serves as a client sending
def spwan_test_client_b():
    client = Client("localhost", 9998, username="b")
    client.custom_send("/list")
    client.recv_list_of_users("a")
    client.send_enc_msg("Hello, How are you doing?")
    client.send_enc_msg("FLAG{RSA_IS_FUN}")
    return client


def test():
    a = spwan_test_client_a()
    b = spwan_test_client_b()
    time.sleep(10)
    a.check_enc_mail()


if __name__ == "__main__":
    test()
