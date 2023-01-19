import pyshark as ps
from Crypto.Cipher import AES
from helper import *


# converts pairs to frequencies
def pairs_to_frequencies(pairs):
    pairs = sorted(pairs)

    lst_1 = []
    lst_2 = []
    for pair in pairs:
        for i in range(len(lst_1)):
            if pair[0] in lst_1[i] and pair[1] not in lst_2[i]:
                lst_2[i].add(pair[1])
                break
            elif pair[0] not in lst_1[i] and pair[1] in lst_2[i]:
                lst_1[i].add(pair[0])
                break
            elif pair[0] in lst_1[i] and pair[1] in lst_2[i]: break
        else:
            lst_1.append(set())
            lst_2.append(set())
            lst_1[-1].add(pair[0])
            lst_2[-1].add(pair[1])

    # print(lst_1, lst_2)

    A, C = [], []
    for i in range(len(lst_1)):
        temp = list(lst_1[i])[0]
        A.append((temp, len(lst_1[i])))
        C.append((temp, len(lst_2[i])))

    return A, C



from helper import HOST
capture = ps.LiveCapture(interface="lo", bpf_filter="host 127.0.0.2", debug=True)
gen = capture.sniff_continuously()

cur_msg = []
state = 0  # 0 = waiting for next message, 1 = waiting for dummy packet, 2 = waiting for rest of message
exp_len = 0

ciph_freq = {}
tot_ciphs = 0
searchK = b''
labelK = b''

query_type = ""


def new_gen():
    leftovers = b""
    for pack in gen:
        try:
            payload = leftovers + bytes.fromhex(pack.tcp.payload.raw_value.replace(":", ""))
            for i in range(len(payload)//packl): yield payload[i*packl:(i+1)*packl]
            leftovers = payload[len(payload)//packl * packl:]
        except AttributeError: continue

for payload in new_gen():
    assert(len(payload) == packl)
    if state == 0:
        exp_len = pickle.loads(s_unpad(payload))
        state = 1
    elif state == 1:
        exp_len -= len(payload)
        state = 2  # bypass the dummy packet
    else:
        exp_len -= len(payload)
        cur_msg.append(payload)
        if exp_len <= 0:  # whole message received
            try: msg = pickle.loads(s_unpad(b"".join(cur_msg)))
            except Exception as e:
                print(e) # b"".join(cur_msg))
                # print(s_unpad(b"".join(cur_msg)))
                exit()

            cur_msg = []
            state = 0

            # process message here
            print("\nIntercepted message:", str(msg)[:100], "...", str(msg)[-100:])
            print()
            if type(msg) == list:  # server response to query
                rows = msg

                # check if JOIN or SELECT query
                # JOIN queries always return an even number of rows and generally will return duplicate rows
                # SELECT queries can return an odd number of rows and have no duplicates
                DF = False
                if len(rows) % 2 == 0 and len(set(rows)) != len(rows):
                    query_type = "JOIN"
                    pairs = list(zip(rows[0::2], rows[1::2]))
                    if len(set(rows)) == len(M): DF = True # check for DF / DI (assume only 2 tables)
                else: query_type = "SELECT"

                # output some information
                print(f"{query_type} Query {'' if query_type == 'SELECT' else ('DF' if DF else 'DI')}")
                print("-" * 40)
                print(f"searchK: {searchK}")
                print(f"labelK: {labelK}")
                print()

                if query_type == "SELECT" and searchK not in ciph_freq.keys():
                    ciph_freq[searchK] = len(msg)
                    tot_ciphs += len(msg)
                    print(f"Added {searchK} to keys, tot_ciphs = {tot_ciphs}, len(M) = {len(M.values())}, num keys = {len(ciph_freq.keys())}")
                    if tot_ciphs == len(M.values()):
                        # All possible SELECT queries have been made. Here we assume can only select on one column,
                        # thus if total received rows across distinct attributes is equal to total number of rows in
                        # the table, this means that every row was returned exactly once --> all queries made Here we
                        # are also assuming the server-client system is only run with one table (i.e. no joins,
                        # because otherwise M will contains rows from the second table, which the attacker has no way
                        # of distinuishing from those of the first table Alternative, we can scrape the whole "wait
                        # till all queries are made" idea, and just continually maintain a list of cipherext
                        # frequencies that grows live with the client making queries. The attacker can retrieve this
                        # list anytime to run attacks albeit it will be SI instead of SF.
                        print("All possible queries made, SF")
                        with open("ciph_freq", "wb") as f: f.write(pickle.dumps(list(ciph_freq.items())))
                elif query_type == "JOIN":
                    frequencies = pairs_to_frequencies(pairs)
                    if not DF: c, d = frequencies

                    print("Join query made, writing frequencies")
                    with open("join_frequencies", "wb") as f: f.write(pickle.dumps(frequencies))
            elif type(msg) == bytes: assert (msg == b'client_init received and processed')
            else:
                assert type(msg) == dict  # client_init, or query
                if msg['option'] == 'client_init':
                    M, N = msg['data']
                    ciph_freq = {}
                    tot_ciphs = 0
                    print("client_init intercepted, M, N initialised")
                elif msg['option'] == 'query':
                    searchK = msg['searchK']
                    labelK = msg['labelK']
                else: assert(False)
