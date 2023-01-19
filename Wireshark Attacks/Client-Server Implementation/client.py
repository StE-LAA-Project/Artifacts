import time
import hmac
import shlex
import socket
import hashlib

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from pandas import read_csv
from tqdm import tqdm

from helper import *
from params import *


total_queries = [0]
total_time = [0]


def query(q):
    start_time = time.time()

    searchK = hmac.new(K_F_N, pickle.dumps(q), hashlib.sha256).digest()
    labelK = hmac.new(K_S_N, pickle.dumps(q), hashlib.sha256).digest()
    to_send = {"option": "query", "searchK": searchK, "labelK": labelK}

    send(s, pickle.dumps(to_send))
    enc_rows = pickle.loads(recv(s))
    dec_rows = [AES.new(K_S_M, AES.MODE_CTR, nonce=nonce).decrypt(ct) for ct, nonce in enc_rows]
    lst = [unpad(r, kl).decode() for r in dec_rows]

    total_queries[0] += 1
    total_time[0] += time.time() - start_time

    return lst


def rng_queries(select, join, col_filter=None):
    rng = []
    if join:
        for (tbl1, tbl2), col_pairs in join_cols.items():
            for (col1, col2) in col_pairs:
                rng.append(('J', tbl1, tbl2, col1, col2))

    if select:
        for tbl_idx, cols in enumerate(select_cols):
            for col in cols:
                if col_filter is None or col_filter(col):
                    for value in set(tbls[tbl_idx][col]):
                        rng.append(('S', tbl_idx, col, value))

    print("Total number of possible queries:", len(rng))
    for q in rng:
        print(q, hmac.new(K_F_N, pickle.dumps(q), hashlib.sha256).digest())
        query(q)


print("Reading tbls")
tbls = [read_csv(f, dtype=str, keep_default_na=False) for f in table_files]
tbl_all = [t.to_string().split("\n") for t in tbls]
tbl_headers = [t[0] for t in tbl_all]
tbl_rows = [t[1:] for t in tbl_all]

for i in range(tables):
    if select_cols[i] == True: select_cols[i] = tbls[i].columns.tolist()

for key, val in join_cols.items():
    if val == True:
        a, b = key
        join_cols[key] = [(col1, col2) for col1 in tbls[a].columns for col2 in tbls[b].columns]


join_pt = {}
select_pt = {}

print("Full Precomp for Join:")
FP = {}
for (tbl1, tbl2), col_pairs in tqdm(join_cols.items()):
    for col1, col2 in tqdm(col_pairs, leave=False):
        for idx1, row1 in tqdm(enumerate(tbl_rows[tbl1]), total=len(tbl_rows[tbl1]), leave=False):
            for idx2, row2 in tqdm(enumerate(tbl_rows[tbl2]), total=len(tbl_rows[tbl2]), leave=False):
                if tbls[tbl1][col1][idx1] == tbls[tbl2][col2][idx2]:
                    hashed_row1 = hmac.new(K_F_M, pickle.dumps((tbl1, idx1)), hashlib.sha256).digest()
                    hashed_row2 = hmac.new(K_F_M, pickle.dumps((tbl2, idx2)), hashlib.sha256).digest()
                    join_pt[hashed_row1] = tbls[tbl1][col1][idx1]
                    join_pt[hashed_row2] = tbls[tbl1][col1][idx1]
                    try: FP[('J', tbl1, tbl2, col1, col2)].extend(((tbl1, idx1), (tbl2, idx2)))
                    except: FP[('J', tbl1, tbl2, col1, col2)] = [(tbl1, idx1), (tbl2, idx2)]

print("Precomp for Select:")
for tbl_idx, tbl in tqdm(enumerate(tbls), total=tables):
    for col in tqdm(select_cols[tbl_idx], leave=False):
        for idx, val in tqdm(enumerate(tbl[col]), total=len(tbl[col]), leave=False):
            searchK = hmac.new(K_F_N, pickle.dumps(('S', tbl_idx, col, val)), hashlib.sha256).digest()
            select_pt[searchK] = val
            try: FP[('S', tbl_idx, col, val)].append((tbl_idx, idx))
            except: FP[('S', tbl_idx, col, val)] = [(tbl_idx, idx)]

# for local testing while adversary.py is not working
# S_ciph_freq, J_ciphs_FP = [], ()
# for key, value in FP.items():
#     if key[0] == 'S': S_ciph_freq.append((hmac.new(K_F_N, pickle.dumps(key), hashlib.sha256).digest(), len(value)))
#     else: J_ciphs_FP = ([hmac.new(K_F_M, pickle.dumps(i), hashlib.sha256).digest() for i in value[0::2]],
#                             [hmac.new(K_F_M, pickle.dumps(i), hashlib.sha256).digest() for i in value[1::2]])
# with open("S_ciph_freq", "wb") as f: f.write(pickle.dumps(S_ciph_freq))
# with open("J_ciphs_FP", "wb") as f: f.write(pickle.dumps(J_ciphs_FP))

print("Initialising M (index of row to row contents):")
M = {}
for tbl_idx, tbl in tqdm(enumerate(tbl_rows), total=len(tbl_rows)):
    for idx, row in tqdm(enumerate(tbl), total=len(tbl), leave=False):
        # M[(tbl_idx, idx)] = row
        K = hmac.new(K_F_M, pickle.dumps((tbl_idx, idx)), hashlib.sha256).digest()
        key = hmac.new(K, b"\x00\x00\x00", hashlib.sha256).digest()
        nonce = get_random_bytes(8)
        val = AES.new(K_S_M, AES.MODE_CTR, nonce=nonce).encrypt(pad(row.encode(), kl))
        M[key] = (val, nonce)

print("Initialising N (RR-encrypted FP):")
N = {}
for label, values in tqdm(FP.items()):
    searchK = hmac.new(K_F_N, pickle.dumps(label), hashlib.sha256).digest()
    labelK = hmac.new(K_S_N, pickle.dumps(label), hashlib.sha256).digest()
    for i, value in tqdm(enumerate(values), total=len(values), leave=False):
        val_dec = hmac.new(K_F_M, pickle.dumps(value), hashlib.sha256).digest()
        key = hmac.new(searchK, i.to_bytes(3, "big"), hashlib.sha256).digest()
        nonce = get_random_bytes(8)
        val_enc = AES.new(labelK, AES.MODE_CTR, nonce=nonce).encrypt(val_dec)
        N[key] = (val_enc, nonce)

join_pt_2 = {}
for key, value in join_pt.items():
    join_pt_2[M[hmac.new(key, b"\x00\x00\x00", hashlib.sha256).digest()]] = value

print("Writing select and join plaintexts for score calculation:")
with open("join_pt", "wb") as f: f.write(pickle.dumps(join_pt_2))
with open("select_pt", "wb") as f: f.write(pickle.dumps(select_pt))

print("Connecting to server", flush=True)
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Sending data to server", flush=True)
to_send = pickle.dumps({"option": "client_init", "data": (M, N)})
send(s, to_send)
print(f"Client sent {len(to_send)} bytes for client_init")
print(pickle.loads(recv(s)))  # a confirmation message should be printed out
print("\n\n\n\n\n")
print("Input query of either form:")
print("1) SELECT <tbl_idx> <attr> <value>                     = SELECT * FROM tbl WHERE attr=value")
print("2) JOIN <tbl1_idx> <tbl2_idx> <attr1> <attr2>          = SELECT * FROM tbl1 JOIN tbl2 ON tbl1.attr1=tbl2.attr2")
print("Use quotation marks around inputs if they contain spaces.")
print("Also, up and down arrows work yay")

while True:
    try:
        inp = shlex.split(input(">>> "))
        if inp[0] == "RNG" and inp[1] == "S":
             rng_queries(True, False, col_filter=lambda x: x == inp[2])
        elif inp == ["rng", "s"]: rng_queries(True, False)
        elif inp == ["rng", "j"]: rng_queries(False, True)
        elif inp == ["rng", "sj"]: rng_queries(True, True)
        elif inp[0] == "SELECT":
            tbl_idx, attr, value = inp[1:]
            tbl_idx = int(tbl_idx)
            res = query(('S', tbl_idx, attr, value))
            if res:
                print(tbl_headers[tbl_idx])
                for row in res: print(row)
                print(f"{len(res)} results found.")
            else:
                print("No results found.")
        elif inp[0] == "JOIN":
            tbl1, tbl2, attr1, attr2 = inp[1:]
            tbl1, tbl2 = int(tbl1), int(tbl2)
            res = query(('J', tbl1, tbl2, attr1, attr2))
            if res:
                print(tbl_headers[tbl1], " | ", tbl_headers[tbl2])
                for row1, row2 in zip(res[::2], res[1::2]): print(row1, " | ", row2)
                print(f"{len(res) // 2} results found.")
            else:
                print("No results found.")
        else:
            print("Invalid command.")
    except KeyboardInterrupt:
        print()
        print(f"Average Query Time: {total_time[0] / total_queries[0]}")
        s.close()
        exit()
