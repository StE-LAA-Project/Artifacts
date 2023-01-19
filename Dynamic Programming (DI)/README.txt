The script takes in four columns of data (two auxiliary and two ciphertext), runs multiple DI attacks, and calculates the v-score and r-score for each attack. When run, each attack is run on the different distribution cases for 10000 and 1000000 rows, with 5%, 10% and 20% noise introduced to the auxiliary data.

POAA.cpp should be compiled before running the script.





------------------------------------------------------------------------------------------
DP1:
This experiment extends the SI-LAA DP algorithm very naively into the DI-LAA by running the SI-LAA algorithm on both columns and taking the greater probability of the two mappings.
Important details:
1. “noise” refers to the percentage error introduced into the auxiliary dataset.
2. For datasets containing 50 ciphertexts, auxiliary probabilities are rounded to 5dp.
3. For datasets containing 100 ciphertexts, auxiliary probabilities are rounded to 3dp.
4. Experiments were not run on 200 or 500 ciphertexts as they could not terminate after a long period of time.
5. For the partitioning optimisation algorithm, values were rounded to 5dp.
------------------------------------------------------------------------------------------


DP2A:
Heuristic sorting was used to sort (a_i, b_i) pairs before running the DP attack on the data.
Pairs were sorted using the order of one column and repeating with the other column, and the mapping with the higher probability is chosen.


Important information:
1. Only results for 10 ciphertexts are recorded as 50 ciphertexts took a very long time, even after rounding all auxiliary values to the nearest 0.005.
2. For POAA, all auxiliary values were rounded to 5dp and were scaled by 10^5.
------------------------------------------------------------------------------------------


DP2B:
Heuristic sorting was used to sort (a_i, b_i) pairs before running the DP attack on the data.
Pairs were sorted using the sum of a_i+b_i.


Important information:
1. Only results for 10 ciphertexts are recorded as 50 ciphertexts took a very long time, even after rounding all auxiliary values to the nearest 0.005.
2. For POAA, all auxiliary values were rounded to 5dp and were scaled by 10^5.
------------------------------------------------------------------------------------------
