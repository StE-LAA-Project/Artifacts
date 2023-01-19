import time
import socket, pickle
import hmac, hashlib
import traceback
from helper import *
from Crypto.Cipher import AES

HOST = "0.0.0.0"  # allow all connections

print(f"HOST = {HOST}")
print(f"PORT = {PORT}")

D = {}

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    while True:
        print("Listening for new connection")
        s.listen()
        conn, addr = s.accept()

        with conn:
            print(f"Connected by {addr}")
            try:
                while True:
                    rec = recv(conn)
                    if not rec: break  # client closed the connection
                    data = pickle.loads(rec)

                    if not "option" in data: raise ValueError("No option in data sent")
                    elif data["option"] == "client_init":
                        M, N = data["data"]
                        print("server send client_init processed")
                        send(conn, pickle.dumps(b"client_init received and processed"))
                    elif data["option"] == "query":
                        searchK = data["searchK"]
                        labelK = data["labelK"]

                        hashed_rows = []
                        for i in range(len(N)):
                            try:
                                ct, nonce = N[hmac.new(searchK, i.to_bytes(3, "big"), hashlib.sha256).digest()]
                                hashed_rows.append(AES.new(labelK, AES.MODE_CTR, nonce=nonce).decrypt(ct))
                            except: break # no more values under this label

                        enc_rows = []
                        for hashed_row in hashed_rows:
                            enc_rows.append(M[hmac.new(hashed_row, b"\x00\x00\x00", hashlib.sha256).digest()])

                        send(conn, pickle.dumps(enc_rows))
                    else: raise ValueError("Invalid option")

                print("Client closed connection")
            except:
                traceback.print_exc()
