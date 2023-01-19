The experiments were run according to the planned SF experiments except that the data files used had 10000 columns so that the experiments would run faster.
The auxiliary data files had 1000000 rows.

To run on wireshark, we first ran the client and server.
Then, packets passing between the client and server were sniffed.
This allows us to reconstruct the queries and responses from the server.
After waiting for all possible SELECT queries to be made, the queries and the server responses are saved to a pickle file.
Then, the attack is run on the ciphertext frequencies.