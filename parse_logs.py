# this is a script to parse the logs from the server


# the log file is a text file with the following format:
# [action] [from/to] [data]
# [action] is the action that was performed like I, P, S, R, D, etc.
#   I = Ignore (from the server like a client is connected, and welcome messages)
#   P = Public Key (e.g. P client_id public_key.e public_key.n)
#   S = Message Sent (e.g. S client_id.from client_id.to message)
#   B = Bad Message Received (e.g. B client_id.from client_id.to message)
#       (in case of `test_rcv` mode enabled to try the chosen cipher-text attack)
#   D = Client Disconnected (e.g. D client_id.from time)
# [from/to] `from` one client to `to` another (could be one of them only like in case of P, D, R)
# [data] is the data that was sent to the server


# client: public key(e, n)
public_keys = {}

# client: received messages (in encrypted form)
# will be used later by the brute-force attack
enc_sent_messages = {}

# client: received messages (in encrypted form)
# will be used later by the chosen cipher-text attack
bad_recieved_messages = {}

# disconnects the client from the server
disconnected = []


def parse_logs(log_file):
    global public_keys
    global enc_sent_messages
    global bad_recieved_messages
    global disconnected
    # open the log file
    with open(log_file, "r") as f:
        # read the file line by line
        lines = f.readlines()
        # iterate through the lines
        for line in lines:
            # split the line by the spaces
            line_split = line.strip().split(" ")
            action = line_split[0]
            if action == "I":
                continue
            # if the action is `P` (public key), then add the public key to the dictionary
            elif action == "P":
                public_keys[line_split[1]] = [line_split[2], line_split[3]]
            # if the action is `S` (sent message), then add the sent message to the dictionary
            elif action == "S":
                if line_split[2] not in enc_sent_messages.keys():
                    enc_sent_messages[line_split[2]] = []
                enc_sent_messages[line_split[2]].append(" ".join(line_split[3:]))
            # if the action is `R` (received message), then add the received message to the dictionary
            elif action == "B":
                if line_split[2] not in bad_recieved_messages.keys():
                    bad_recieved_messages[line_split[2]] = []
                bad_recieved_messages[line_split[2]].append(" ".join(line_split[3:]))
            # if the action is `D` (disconnected), then remove the client from the dictionary
            elif action == "D":
                disconnected.append(line_split[1])
    return public_keys, enc_sent_messages, bad_recieved_messages, disconnected
