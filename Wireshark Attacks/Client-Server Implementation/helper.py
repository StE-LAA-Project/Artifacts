import pickle, time

kl = 256
packl = 1024  # packet length
HOST = "127.0.0.2"
PORT = 80  # The port used by the server

tot_num = 0

def s_pad(msg):
    msg += b"\x01"
    if len(msg) % packl == 0: return msg
    return msg + (packl - len(msg) % packl) * b"\x02"


def s_unpad(msg):
    if len(msg) == 0: return msg
    last_one = -1
    while msg[last_one] != 1:
        last_one -= 1
        if last_one == -len(msg): break
    return msg[:last_one]


def send_size(s, size):
    s.sendall(s_pad(pickle.dumps(size + packl)))
    s.sendall(s_pad(b""))


def send_msg(s, msg):
    global tot_num
    blocks = len(msg) // packl
    for i in range(blocks):
        if (tot_num + i) % 100 == 0: time.sleep(1) # so rng queries doesn't drop packets
        s.sendall(msg[i * packl:(i + 1) * packl])
    tot_num += blocks


def send(s, msg):
    msg = s_pad(msg)
    send_size(s, len(msg))
    send_msg(s, msg)
    # apparently I need to break this into 2 functions for socket to recognise I sent a size over


def recv(s):
    data = []
    received_length = 0
    try: length = pickle.loads(s_unpad(s.recv(packl))) - packl
    except: return

    first_pack = True
    while received_length < length:
        pack = s.recv(packl)
        if first_pack:
            first_pack = False
        elif pack:
            data.append(pack)
            received_length += len(pack)

    if not data: raise ValueError("empty data")
    return s_unpad(b"".join(data))
