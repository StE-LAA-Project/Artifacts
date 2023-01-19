#libraries
import random
import scipy.optimize as sco
import numpy as np

#functions
def reading_csv(csv): #csv is directions to csv file
    file = open(csv)
    db = [] #full dataset
    for line in file:
        try:
            db.append(line[:-1])
        except:
            db.append(line)
    #reading in probability distributions in the first line, removing "distribution:"
    dist = db[0]
    thing = dist.split(":")[1]
    pd = thing.split(",")
    pd[0] = pd[0][1:]
    pd[len(pd) - 1] = pd[len(pd) - 1][:-1]
    for i in range(len(pd)):
        pd[i] = float(pd[i])
    ct = db[2:]
    return ct, pd

def find_freq(list_of_column_entries):
    #this function counts the frequency of each key in the input, inputs are an array of first names from ohio db. the output of this function will be a dictionary consisting of the first names as the keys and the frequencies as the values
    dictionary_with_freq_of_items_in_columns = {}
    for x in list_of_column_entries:
        if x in dictionary_with_freq_of_items_in_columns:
            dictionary_with_freq_of_items_in_columns[x] += 1
        else:
            dictionary_with_freq_of_items_in_columns[x] = 1
    return dictionary_with_freq_of_items_in_columns

def rand_in_range(a, b):
    y = random.uniform(a, b)
    return y

def percent_of(p, c):
    x = float(p)/100
    a = float(c*(1-x))
    b = float(c*(1+x))
    return a, b

def scale_down(tuple_of_entries):
    new_tuple = [0] * len(tuple_of_entries)
    for i in range(len(tuple_of_entries)):
        y = float(sum(list(tuple_of_entries)))
        new_tuple[i] = tuple_of_entries[i]/y
    return new_tuple

#generates auxiliary data, y introducing errors (percentage) into probability distribution by changing the values by a certain percentage
def gen_aux(prob_dist, percentage):
    b = [[0] * len(prob_dist) for i in range(2)] #len(ciphertext) columns and 2 rows, 2xlen(ciphertext) matrix
    for i in range(2):
        for j in range(len(prob_dist)):
            b[0][j], b[1][j] = percent_of(percentage, prob_dist[j])
    y = [0]*len(prob_dist)
    for i in range(len(prob_dist)):
        y[i] = rand_in_range(b[0][i], b[1][i])
    output = scale_down(y)
    return output

def sort(dictionary): #this function sorts the keys alphabetically, while returning a list with key and value together
    sorted_dict_list = sorted(dictionary.items())
    return sorted_dict_list

#this function forms a new list consisting of only values, no keys i.e. only frequency of names, no names; input should
def find_values(list1):
    l2 = []
    for i in range(len(list1)):
        tpl = (list1[i][1])
        l2.append(tpl)
    return l2

#tracks the indices of items in a list, returns dictionary with index as key and list item as value, eg [cat, dog] --> {0: cat, 1: dog}
def track(sorted_list):
    d1 = {}
    for x in range(len(sorted_list)):
        d1[x] = sorted_list[x]
    return d1

#makes keys of dictionary into a list
def key_list(dict):
    y = list(dict.keys())
    return y

#generates cost matrix that is used in the function "matching"
def gen_matrix(aux_freq1, aux_freq2, ct_num1, ct_num2):
    y = [[0]*len(aux_freq1) for i in range(len(ct_num1))]
    for i in range(len(ct_num1)):
        for j in range(len(aux_freq1)):
            y[i][j]= -ct_num1[j]*np.log(aux_freq1[i])-ct_num2[j]*np.log(aux_freq2[i])
    return y

#function returns mapping, can return maximum weight if required
def matching(costs):
    row_ind, col_ind = sco.linear_sum_assignment(costs)
    n = len(row_ind)
    list_of_matchings = [0] * n
    #max_weight = 0
    for i in range(n):
        list_of_matchings[i] = row_ind[i], col_ind[i]
        #max_weight += -costs[row_ind[i]][col_ind[i]]
    return list_of_matchings

def v_score(matching, no_of_ciphertext,ciphertext, aux):
    correct_values = 0
    sum = no_of_ciphertext
    aux_track, ciph_track = track(key_list(aux)), track(key_list(ciphertext))
    for i in range(len(matching)):
        m1, m2 = matching[i][1], matching[i][0]
        if aux_track[m1] == ciph_track[m2]:
            correct_values += 1
        else:
            correct_values += 0
    score = (correct_values/sum)*100
    return score

def r_score(matching, no_of_ct, ct, ct2, aux): #changed, aux should be ct2 ie col1
    key_ct,  key_aux = track(key_list(ct)), track(key_list(aux))
    combined_ct = {}
    for i in list(ct.keys()):
        combined_ct[i] = ct[i] * ct2[i]
    total_rows = sum(combined_ct.values())
    correct_no_rows = 0
    for i in range(no_of_ct):
        line = matching[i]
        if(key_ct[line[0]] == key_aux[line[1]]):
            correct_no_rows += combined_ct[key_ct[line[0]]]
    score = (correct_no_rows/total_rows)*100
    return score

#read in everything from csv
def laa(ct_csv1, ct_csv2, e): #csvs need to be inputted as directions
    db1, pd1 = reading_csv(ct_csv1)
    db2, pd2 = reading_csv(ct_csv2)
    ct1i, ct2i = find_freq(db1), find_freq(db2)
    #sorting ciphertexts in order, according to the number
    d1, d2 = dict(sorted(ct1i.items(), key=lambda x: int(x[0][10:]))), dict(sorted(ct2i.items(), key=lambda x: int(x[0][10:])))
    ct_num1, ct_num2 = find_values(list(d1.items())), find_values(list(d2.items()))
    ct1_keys, ct2_keys = list(d1.keys()), list(d2.keys())
    aux_dist1, aux_dist2 = gen_aux(pd1, e), gen_aux(pd2, e)
    aux1, aux2 = dict(zip(ct1_keys, aux_dist1)), dict(zip(ct2_keys, aux_dist2))
    costs = gen_matrix(aux_dist1, aux_dist2, ct_num1, ct_num2)
    m = matching(costs)
    vscorei = v_score(m, len(ct_num1), d1, aux1)
    rscorei = r_score(m, len(ct_num1), d1, d2, aux1)
    return vscorei, rscorei

def run_all(error, write_file=""):
    rows = [10000, 1000000]
    dists = ["lin-lin", "lin-slin", "lin-invlin", "lin-randlin", "lin-zipf", "zipf-zipf", "zipf-randzipf", "zipf-invzipf"]
    ciphs_s, ciphs_l = [10, 50, 100], [10, 50, 100, 200, 500]
    res = []

    for row in rows:
        for dist in dists:
            prefix = f"data_v2\\DF\\DF_{row}_{dist}\\"
            for ciphs in ciphs_s if row == 10000 else ciphs_l:
                print(f"{row} {ciphs} {dist}: ", end="")
                v_ave, r_ave = 0, 0
                for run in range(10):
                    file0_path = prefix + f"DF_{row}_{ciphs}_{dist}{run}_col0.csv"
                    file1_path = prefix + f"DF_{row}_{ciphs}_{dist}{run}_col1.csv"
                    vi, ri = laa(file0_path, file1_path, error)
                    v_ave, r_ave = v_ave + vi, r_ave + ri
                v_ave, r_ave = v_ave / 10, r_ave / 10
                res.append((f"{row}_{ciphs}_{dist},{v_ave},{r_ave}", v_ave, r_ave))

                print(v_ave, r_ave)

    to_write = "rows_ciphs_distr,v,r\n"
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"
    res = sorted(res, key=lambda x: -x[1])
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"
    res = sorted(res, key=lambda x: -x[2])
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"
    res = sorted(res, key=lambda x: -x[1]-x[2])
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"

    if write_file == "":
        print(to_write)
    else:
        with open(write_file, "w") as f:
            f.write(to_write)


if __name__ == "__main__":
    for e in [5, 10, 20]:
        print(e)
        run_all(e, f"{e}_final.csv")
        print("\n\n\n\n\n")
