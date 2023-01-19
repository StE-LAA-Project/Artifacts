import pandas as pd
import numpy as np
import itertools
import csv
from scipy.optimize import linear_sum_assignment

flag = input("Show only R-score and V-score? Y/N")

columns_aux = [ ] #fill in columns of auxiliary dataset
columns_ciph = [ ] #fill in columns of ciphertext dataset
auxiliary_input_file = #fill in with file directories
auxiliary_output_file =
ciphertext_input_file =
ciphertext_output_file =

with open("R-Score of hybrid.csv", 'w') as f: #output files for the scores
    with open('V-Score of hybrid.csv', 'w') as v:
        writerf = csv.writer(f)
        writerv = csv.writer(v)
        header = ['Column (HCUP 2018-HCUP 2019)', 'L1', 'L2', 'L3']
        writerf.writerow(header)
        writerv.writerow(header)
        values_r = []
        values_v = []
        print("Auxiliary input file: ", auxiliary_input_file)
        print("Ciphertext input file: ", ciphertext_input_file)
        for l in range(len(columns_ciph)):
            values_r.append(columns_aux[l] + '-' + columns_ciph[l])
            values_v.append(columns_aux[l] + '-' + columns_ciph[l])
            # Lp-optimization
            for p in range(1, 4):
                ciphertext_data = pd.read_csv(ciphertext_input_file)
                ciph_data = ciphertext_data[columns_ciph[l]]
                ciph_data.to_csv(ciphertext_output_file, index=False)
                with open(ciphertext_output_file) as file_name:
                    ci_data = np.loadtxt(file_name, delimiter=",", dtype=str)
                    c_data = ci_data[1:]
                    c_data = [name.upper() for name in c_data]
                    c_data = list(filter(None, c_data))

                auxiliary_data = pd.read_csv(auxiliary_input_file)
                aux_data = auxiliary_data[columns_aux[l]]
                aux_data.to_csv(auxiliary_output_file, index=False)
                with open(auxiliary_output_file) as file_name:
                    au_data = np.loadtxt(file_name, delimiter=",", dtype=str)
                    a_data = au_data[1:]
                    a_data = [name.upper() for name in a_data]
                    a_data = list(filter(None, a_data))

                # 1st input xform for aux
                longer = 0
                if (len(c_data) > len(a_data)):
                    diff = len(c_data) - len(a_data)
                    for i in range(diff):
                        a_data.append("NULL" + str(i))
                elif (len(c_data) < len(a_data)):
                    longer = 1

                a_freq = {}
                for item in a_data:
                    if (item in a_freq):
                        a_freq[item] += 1
                    else:
                        a_freq[item] = 1
                dict(sorted(a_freq.items(), key=lambda item: item[1]))
                a_freq = dict(itertools.islice(a_freq.items(), 2000))
                aux_freqs = []
                for key, value in a_freq.items():
                    aux_freqs.append(value / 1000)

                # 1st input xform for ciphertext
                c_freq = {}
                for item in c_data:
                    if (item in c_freq):
                        c_freq[item] += 1
                    else:
                        c_freq[item] = 1
                dict(sorted(c_freq.items(), key=lambda item: item[1]))
                c_freq = dict(itertools.islice(c_freq.items(), 2000))
                cipher_freqs = []
                for key, value in c_freq.items():
                    cipher_freqs.append(value / 1000)

                if (longer == 1):
                    difference = len(aux_freqs) - len(cipher_freqs)
                    del aux_freqs[len(aux_freqs) - difference:]

                if flag == "N":
                    print("\nAuxiliary frequencies:")
                    print(aux_freqs)
                    print("\nCiphertext frequencies:")
                    print(cipher_freqs)

                # creating the cost matrix
                cost_arr = []
                sorted_arr = []
                for i in aux_freqs:
                    for n in cipher_freqs:
                        cost_arr.append(abs(i - n) ** p)
                        sorted_arr.append(abs(i - n) ** p)

                # scaling the inputs
                x = 0
                sorted_arr.sort()
                for n in range(len(sorted_arr)):
                    if sorted_arr[n] > 0:
                        x = sorted_arr[n]
                        break
                k = 0
                while x < 1:
                    x = x * 10
                    k += 1

                new_cost_arr = []
                for n in range(len(cost_arr)):
                    new_cost_arr.append(cost_arr[n] * (10 ** k))

                cost_matrix = np.reshape(new_cost_arr, (len(aux_freqs), len(cipher_freqs)))

                if flag == "N":
                    print("\nCost matrix:")
                    print(cost_matrix)

                # LSAP
                row_vals = list(a_freq.keys())
                column_vals = list(c_freq.keys())

                matrix = np.array(cost_matrix)
                row_ind, col_ind = linear_sum_assignment(matrix, maximize=False)
                rscore_success = 0
                vscore_success = 0

                for i in range(len(row_ind)):
                    if flag == 'N':
                        print('row: ', row_ind[i], '  col: ', col_ind[i], '  value: ', matrix[i, col_ind[i]])
                        print(row_vals[row_ind[i]], ", ", column_vals[col_ind[i]])
                    if row_vals[row_ind[i]] == column_vals[col_ind[i]]:  # compare if names are the same
                        rscore_success += cipher_freqs[i] * 1000
                        vscore_success += 1
                print("\nColumn:", columns_aux[l], "-", columns_ciph[l], "LAA:Lp-optimization, p =", p)

                # R-score
                print("\nR-score: ", rscore_success * 100 / len(c_data), "%")
                values_r.append(rscore_success * 100 / len(c_data))

                # V-score
                num_elements = len(set(c_data))
                print("\nV-score: ", vscore_success * 100 / num_elements, "%")
                values_v.append(vscore_success * 100 / num_elements)

            writerf.writerow(values_r)
            writerv.writerow(values_v)
            values_r.clear()
            values_v.clear()
