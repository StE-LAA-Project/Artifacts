import math
from scipy.optimize import linear_sum_assignment as lsap
import random
import pandas as pd
import numpy as np
import csv

inf = 9999999999999

def log(x):
    if x < 0:
        return -inf * inf
    elif x == 0:
        return -inf
    else:
        return math.log(x)

def get_frequencies(l, cip_fulllist):
    d = {}
    for i in l:
      try: d[i] += 1
      except: d[i] = 1
    for cip in cip_fulllist:
      if cip not in l: d[cip] = 0
    cip_list = [[a, b] for [a, b] in d.items()]
    return sorted(cip_list)

def find_commoncip(C, D):
    C_new = [C[i] for i in range(len(C)) if (C[i][1] != 0 and D[i][1] != 0)]
    D_new = [D[i] for i in range(len(C)) if (C[i][1] != 0 and D[i][1] != 0)]
    return C_new, D_new

# p is the percentage error to be introduced
def gen_auxiliary(dist, p):
    aux_dist = [random.uniform(x * (100 - p), x * (100 + p)) for x in dist]
    tot = sum(aux_dist)
    aux_dist = [x / tot for x in aux_dist]

    return [[f"ciphertext{i}", x] for (i, x) in enumerate(aux_dist)]

def find_constants(A, C, D, C_new, D_new):
    n = len(A)
    m = len(C_new)
    c0 = sum([pair[1] for pair in C]) - sum(pair[1] for pair in C_new)
    d0 = sum([pair[1] for pair in D]) - sum(pair[1] for pair in D_new)
    return n, m, c0, d0
    print(f'n = {n} \nm = {m} \nc0 = {c0} \nd0 = {d0}')

#define uniform distribution
def uniform_dist(n,m):
    return [1/(n-m) for i in range(n-m)]

#define linear distribution
def linear_dist(n,m):
    intm_list = [i for i in range(1, n-m+1)]
    return [i/sum(intm_list) for i in intm_list]

#define zipfian distribution
def harmonic(a, b):
    l = [(n + 1) ** (-b) for n in range(a)]
    return sum(l)

def zipf(a, b, r):
    return r ** (-b) / harmonic(a, b)

def zipf_dist(n,m):
    a = n-m
    b = 1
    intm_list = [zipf(a, b, r + 1) for r in range(n-m)]
    return [i/sum(intm_list) for i in intm_list]

#running distribution functions based on the distribution types
def choose_dist(dist_type_split, dists_cip, n, m):
    if dist_type_split in dists_cip:
      if dist_type_split == dists_cip[0]: return uniform_dist(n,m)
      elif dist_type_split == dists_cip[1]: return linear_dist(n,m)
      elif dist_type_split == dists_cip[2]: return zipf_dist(n,m)

#define partitioning optimisation algorithm
def partition(A, B, c, d):
    '''
    A, B are lists of integers of length n
    c, d are integers
    Returns a partition R, S of [0, n-1] that maximises sum(A_i, i in R)^c * sum(B_i, i in S)^d
    '''
    big_no = 1000000
    A, B = [round(i * big_no) for i in A], [round(j * big_no) for j in B]

    n = len(A)
    L = max(sum(A), sum(B))

    best, path = [-inf * inf] * (L + 1), [0] * (L + 1)
    best[0] = 0

    for i in range(n):
        new_best, new_path = [-inf * inf] * (L + 1), [0] * (L + 1)
        for a_sum in range(L + 1):
            old_a, old_b = a_sum, best[a_sum]
            new_a, new_b = a_sum + A[i], old_b + B[i]
            if new_a <= L: new_best[new_a], new_path[new_a] = old_b, path[old_a] * 2
            if new_b > new_best[old_a]: new_best[old_a], new_path[old_a] = new_b, path[old_a] * 2 + 1

        best, path = new_best, new_path

    max_val, max_path = log(0), -1
    for i in range(L + 1):
        val = c * log(i) + d * log(best[i])
        if val > max_val: max_val, max_path = val, path[i]

    R, S = [], []
    for i in range(n - 1, -1, -1):
        if max_path % 2 == 1:
            S.append(i)
        else:
            R.append(i)
        max_path //= 2

    return R, S
  
def split_into_newcip(dist_list, c0, d0, n, m):
    R, S = partition(dist_list, dist_list, c0, d0)
    p = len(R)
    c0_list = [round((c0 + d0) * dist_list[i]) for i in R] + [0 for _ in range(n-m-p)]
    d0_list = [0 for _ in range(p)] + [round((c0 + d0) * dist_list[j]) for j in S]
    assert len(c0_list) == len(d0_list)
    return c0_list, d0_list, p

def gen_new_cip(cip_fulllist, cip_new, bucket):
    cip_final = cip_new.copy()
    commoncip = [pair[0] for pair in cip_new]
    bucketcip_list = [cip for cip in cip_fulllist if cip not in commoncip]
    new_bucket_list = [[bucketcip_list[i], bucket[i]] for i in range(len(bucket))]
    cip_final.extend(new_bucket_list)
    return cip_final

def bipartite_graph_matching(A, B, C, D, C_common, D_common, m):
    '''
    bipartite graph LAA (for JOIN queries)
    a, b are lists of auxiliary data
    c, d are lists of ciphertexts
    '''
    C, D = sorted(C), sorted(D)  # sorted so that frequencies point to correct ct in both columns

    try:
        assert(len(A) == len(B))
        assert(len(C) == len(D))
    except:
        return -1, -1 # bad file
    cost_matrix = [[-C[y][1] * math.log(A[x][1]) - D[y][1] * math.log(B[x][1]) for y in range(len(C))]
                   for x in range(len(A))] # negate value because scipy.optimize.lsap calculates minimum
    _, matching = lsap(cost_matrix)

    v_score = sum([1 if (C[matching[i]][0] == A[i][0] and matching[i] <= m-1) else 0 for i in range(len(matching))]) / m * 100
    print(f'v_score = {v_score}')
    r_score = sum([C_common[matching[i]][1] * D_common[matching[i]][1] if (C[matching[i]][0] == A[i][0] and matching[i] <= m-1) else 0 for i in range(len(matching))]) / sum([C_common[i][1] * D_common[i][1] for i in range(len(C_common))]) * 100
    print(f'r_score = {r_score}')
    return v_score, r_score

def writetocsv(dist, csv_file, error, vscore, rscore, add_info):
    results = [csv_file + add_info, error, vscore, rscore]
    results_csv = f'results_file_({dist}).csv'
    with open(results_csv, 'a', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(results)

def run_all():
    row = 1000000
    dists = ["lin-lin", "lin-slin", "lin-invlin", "lin-randlin", "lin-zipf", "zipf-zipf", "zipf-randzipf", "zipf-invzipf"]
    ciphs = [10, 50, 100, 200, 500]
    errors = [5, 10, 20]
    dists_cip = ['uniform', 'linear', 'zipfian']
    runs = list(range(10))

    for dist in dists:
        prefix = f'Datasets/DI_{row}_{dist}/' 
        for ciph in ciphs:
            cip_fulllist = ["ciphertext"+str(i) for i in range(0,int(ciph))] 
            for run in runs:
                csv_file = f'DI_{row}_{ciph}_{dist}{run}'
                print(csv_file)
                file0_path = prefix + csv_file + '_col0.csv'
                file1_path = prefix + csv_file + '_col1.csv'
                with open(file0_path, "r") as f: data0 = f.read().split('\n')[:-1]
                with open(file1_path, "r") as f: data1 = f.read().split('\n')[:-1]

                dist0, dist1 = data0[0][15:-1], data1[0][15:-1]  # Remove "distribution:[" and "]"
                dist0, dist1 = [float(i) for i in dist0.split(", ")], [float(i) for i in dist1.split(", ")]
                col0, col1 = data0[2:], data1[2:]
                for error in errors:
                    C, D = get_frequencies(col0, cip_fulllist), get_frequencies(col1, cip_fulllist)
                    C_new, D_new = find_commoncip(C, D)
                    print(C_new)
                    A, B = gen_auxiliary(dist0, error), gen_auxiliary(dist1, error)

                    n, m, c0, d0 = find_constants(A, C, D, C_new, D_new)
                    print(f'n = {n}, m = {m}, c0 = {c0}, d0 = {d0}')

                    v_score_list = []
                    r_score_list = []                    

                    for dist_split in dists_cip:
                        dist_list = choose_dist(dist_split, dists_cip, n, m)
                        c0_list, d0_list, p = split_into_newcip(dist_list, c0, d0, n, m)
                        C_final = gen_new_cip(cip_fulllist, C_new, c0_list)           
                        D_final = gen_new_cip(cip_fulllist, D_new, d0_list)

                        v, r = bipartite_graph_matching(A, B, C_final, D_final, C_new, D_new, m)
                        v_score_list.append(v)
                        r_score_list.append(r)
                        writetocsv(dist, csv_file, error, v, r, f'({dist_split})')

                    r_score_index_list = list(enumerate(r_score_list))
                    r_score_best_index = [r_score_index_list[i][0] for i in range(len(r_score_list)) if r_score_list[i] == r_score_list[np.argmax(r_score_list)]]
                    
                    for i in r_score_best_index:
                        dist_split = dists_cip[i]
                        writetocsv(dist + '_bestpartition', csv_file, error, v_score_list[i], r_score_list[i], f'({dist_split})')

if __name__ == "__main__":
    run_all()