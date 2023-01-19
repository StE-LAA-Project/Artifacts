import math
import random
import numpy as np
import scipy as sp
import csv

from random import uniform
from helper import findpath

# Data format (.csv) should be [*empty row*], [L, M, N], [a1, ..., am], [b1, ..., bm], [c1, ..., cn], [d1, ..., dn],
# where each list indicates a row, L is the total number of database entries, M is the total number of classes, N is the number of revealed database classes,
# the a's and b's indicate actual frequencies and the c's and d's indicate auxiliary frequencies.

### PARAMETERS

epsilon = 10**-8  # can insert very small positive number here to avoid numerical inaccuracies messing with program
disc_factor = 100000  # discretization factor; how many buckets to partition into for DP
option = 1  # 0 for single-step, 1 for multi-step
zugzwang = 20  # terminate loop if no new indices involved in this number of swaps


def log(number):
    return np.log(number) if number > epsilon else -99999999999999999


def compute_edge_weights(nodes, M):
    edges = np.zeros((M, M))
    for i in range(M):
        for j in range(M):
            edges[i][j] = nodes[1][j][0] * (log(nodes[0][i][0])) + nodes[1][j][1] * (log(nodes[0][i][1]))
    return edges


# computes difference in score if we transpose the matchings (a_i, b_i) -> (c_x, d_x) with (a_j, b_j) -> (c_0, d_0)
def replacement_score(ab_j, ab_i, cd_ptn, sum_a_k, sum_b_k, c_0, d_0, cd_x):
    ud_a_k = [sum_a_k + ab_i[0] - (ab_j[0] * cd_ptn[0]), sum_a_k - (ab_j[0] * cd_ptn[0])]
    ud_b_k = [sum_b_k - (ab_j[1] * cd_ptn[1]), sum_b_k + ab_i[1] - (ab_j[1] * cd_ptn[1])]
    diff = [c_0 * (log(ud_a_k[i]) - log(sum_a_k)) + d_0 * (log(ud_b_k[i]) - log(sum_b_k)) + cd_x[0] * (
            log(ab_j[0]) - log(ab_i[0])) + cd_x[1] * (log(ab_j[1]) - log(ab_i[1])) for i in range(2)]
    pre = [c_0 * log(ud_a_k[i]) + d_0 * log(ud_b_k[i]) + cd_x[0] *
           log(ab_j[0]) + cd_x[1] * log(ab_j[1]) for i in range(2)]
    post = [c_0 * log(sum_a_k) + d_0 * log(sum_b_k) + cd_x[0] *
            log(ab_i[0]) + cd_x[1] * log(ab_i[1]) for i in range(2)]
    bkt = 1 if diff[0] < diff[1] else 0
    return diff[bkt], ud_a_k[bkt], ud_b_k[bkt], pre[bkt], post[bkt]


def main(A, B, C, D):
    K = sum(C)
    L = sum(D)
    M = len(A) - 1
    N = len(C) - 1
    # print(L, M, N)
    U = M - N  # number of unattributed classes
    c_0 = K
    d_0 = L

    # initializing allocation; first assume c_0 / d_0 distributed uniformly across all unobserved labels, then perform LSAP on that.
    nodes = np.zeros((2, M, 2))
    edges = np.zeros((M, M))
    discauxnodes = np.zeros((M, 2))  # discretized auxiliary nodes

    for i in range(M):
        nodes[0][i][0] = A[i + 1]  # float(datalist[2][i])
        nodes[0][i][1] = B[i + 1]  # float(datalist[3][i])
    max_pd = np.amax(nodes[0])  # pre-discretized max value between all a's and b's, used in max_sum for DP
    max_sum = U * (round(max_pd * disc_factor) + 1)

    discauxnodes = [[round(disc_factor * i), round(disc_factor * j)] for i, j in nodes[0]]

    for i in range(N):
        nodes[1][i][0] = C[i + 1]  # int(datalist[4][i])
        nodes[1][i][1] = D[i + 1]  # int(datalist[5][i])
        c_0 = c_0 - nodes[1][i][0]
        d_0 = d_0 - nodes[1][i][1]

    c_dist = 0 if U == 0 else float(float(c_0) / float(U))
    d_dist = 0 if U == 0 else float(float(d_0) / float(U))

    for i in range(U):
        nodes[1][N + i][0] = c_dist
        nodes[1][N + i][1] = d_dist

    edges = compute_edge_weights(nodes, M)
    min_edge = edges.min()  # for normalization during LSAP on partial matrix
    n_edges = edges - min_edge + 1  # normalized positive edge weights
    row_ind, col_ind = sp.optimize.linear_sum_assignment(edges, maximize=True)

    if U == 0:
        return row_ind, col_ind, edges[row_ind, col_ind].sum()

    # Can choose single-step (slower but more accurate) or multi-step (faster but possibly suboptimal) descent.
    if option == 0:
        # Single-Step
        no_of_trans = 1  # number of transpositions in current iteration
        cost_diff = 1
        sum_a_k = 0
        sum_b_k = 0
        col_to_row = np.zeros(N).astype(int)
        inactive_rows = []
        drow_ptn = []

        prev_cost = edges[row_ind, col_ind].sum() + (c_0 * log(sum_a_k)) + (d_0 * log(sum_b_k))

        for i in range(M):
            if col_ind[i] < N:
                col_to_row[col_ind[i]] = i
            else:
                sum_a_k = sum_a_k + nodes[0][i][0]
                sum_b_k = sum_b_k + nodes[0][i][1]
                inactive_rows.append(i)
                drow_ptn.append([1, 1])

        m_vind = set()
        mdoom_ctr = 0

        while no_of_trans > 0 and cost_diff > epsilon:  # perform until local minima attained across all 3-steps (no more transitions between known and unknown buckets after optimization within each bucket)
            # print("No. of trans = %d\n\n" % no_of_trans)
            rest_graph = np.zeros((M, N))
            no_of_trans = -1
            best_diff = 1
            vind = set()
            doom_ctr = 0

            while True:  # perform transpositions until no further transpositions between buckets will improve score; does not optimize within buckets
                no_of_trans = no_of_trans + 1
                best_diff = 0
                score_diff = []
                for i in range(U):
                    for j in range(N):
                        # print(col_to_row[i])
                        curr_diff, ud_a_k, ud_b_k, pre, post = replacement_score(nodes[0][inactive_rows[i]],
                                                                                 nodes[0][col_to_row[j]],
                                                                                 drow_ptn[i], sum_a_k, sum_b_k, c_0,
                                                                                 d_0,
                                                                                 nodes[1][j])  # bkt: [c, d] -> [0, 1]
                        septuple = [curr_diff, inactive_rows[i], col_to_row[j], ud_a_k,
                                    ud_b_k, pre,
                                    post]  # extend to sextuple with cd_bucket (do c/d partition here) if only want to run dp once, at the end of the entire process.
                        score_diff.append(septuple)

                score_diff.sort(key=lambda x: float(x[0]), reverse=True)
                best_diff = score_diff[0][0]
                if best_diff <= epsilon:
                    break
                inactive_rows.remove(score_diff[0][1])
                inactive_rows.append(score_diff[0][2])
                tmp = col_ind[score_diff[0][2]]
                col_ind[score_diff[0][2]] = col_ind[score_diff[0][1]]
                col_ind[score_diff[0][1]] = tmp
                col_to_row[tmp] = score_diff[0][1]
                # print(best_diff, score_diff[0][5], score_diff[0][6], score_diff[0][1], score_diff[0][2], tmp, col_ind[[score_diff[0][2]]])
                # print("\n\n\n")
                # print(inactive_rows, col_to_row)
                # print("\n\n\n")
                sum_a_k = score_diff[0][3]
                sum_b_k = score_diff[0][4]
                if set([score_diff[0][1], score_diff[0][2]]).issubset(vind):
                    doom_ctr = doom_ctr + 1
                    if doom_ctr > zugzwang:
                        print("Premature termination at inner loop! Repeat rows:")
                        print(vind)
                        print("\n")
                        break
                vind.add(score_diff[0][1])
                vind.add(score_diff[0][2])

            if vind.issubset(m_vind):
                mdoom_ctr = mdoom_ctr + 1
                if mdoom_ctr > zugzwang:
                    print("Premature termination at outer loop! Repeat rows:")
                    print(m_vind)
                    print("\n")
                    break
            m_vind = vind.union(m_vind)

            # perform steps 2 and 3 (optimization within buckets) here.
            # LSAP
            for i in range(N):
                rest_graph[col_to_row[i], :N] = n_edges[col_to_row[i], :N]

            row_ind, col_ind = sp.optimize.linear_sum_assignment(rest_graph, maximize=True)
            for i in range(N):
                col_to_row[col_ind[i]] = row_ind[i]

            calc_col_ind = col_ind
            tmp_col_ind = np.full(M, N, dtype=int)
            for i in range(N):
                tmp_col_ind[row_ind[i]] = col_ind[i]
            col_ind = tmp_col_ind

            # DP for c_0 and d_0 buckets; variables: sum_a_k, sum_b_k, drow_ptn
            '''
            #Insert DP code here
            '''
            input_list = [[discauxnodes[row][0], discauxnodes[row][1]] for row in inactive_rows]
            best_val, path = findpath(input_list, c_0, d_0, max_sum)
            for i in range(U):
                drow_ptn[U - 1 - i][path & 1] = 1
                drow_ptn[U - 1 - i][1 - (path & 1)] = 0
                path = path >> 1

            sum_a_k = 0
            sum_b_k = 0
            for i in range(U):
                sum_a_k = sum_a_k + (nodes[0][inactive_rows[i]][0] * drow_ptn[i][0])
                sum_b_k = sum_b_k + (nodes[0][inactive_rows[i]][1] * drow_ptn[i][1])

            cost = edges[row_ind, calc_col_ind].sum() + (c_0 * log(sum_a_k)) + (d_0 * log(sum_b_k))
            cost_diff = cost - prev_cost
            prev_cost = cost
            # print("cost_diff = %f" % cost_diff)

        allocmat = np.zeros((M, N + 2))
        f = np.zeros((M,), dtype=int)
        for i in range(N):
            allocmat[col_to_row[i], i] = edges[col_to_row[i], i]
            f[col_to_row[i]] = i

        i = 0
        for row in inactive_rows:
            allocmat[row, N] = drow_ptn[i][0] * (c_0 * log(sum_a_k))
            allocmat[row, N + 1] = drow_ptn[i][1] * (d_0 * log(sum_b_k))
            f[row] = N + drow_ptn[i][1]
            i = i + 1

        # print(cost)
        # print(allocmat)
        # print(f)
        return cost, allocmat, f

    # End Single-Step

    ###############################################################################

    else:
        # Multi-Step
        no_of_trans = 1  # number of transpositions in current iteration
        cost_diff = 1
        sum_a_k = 0
        sum_b_k = 0
        col_to_row = np.zeros(N).astype(int)
        inactive_rows = []
        drow_ptn = []

        prev_cost = edges[row_ind, col_ind].sum() + (c_0 * log(sum_a_k)) + (d_0 * log(sum_b_k))

        for i in range(M):
            if col_ind[i] < N:
                col_to_row[col_ind[i]] = i
            else:
                sum_a_k = sum_a_k + nodes[0][i][0]
                sum_b_k = sum_b_k + nodes[0][i][1]
                inactive_rows.append(i)
                drow_ptn.append([1, 1])

        m_vind = set()
        mdoom_ctr = 0

        while no_of_trans > 0 and cost_diff > epsilon:  # perform until local minima attained across all 3-steps (no more transitions between known and unknown buckets after optimization within each bucket)
            rest_graph = np.zeros((M, M))
            lsap_graph = np.zeros((M, N))
            no_of_trans = 0

            kn_graph = [[0 if i == col_to_row[j] else -99999999999999999 for j in range(N)] for i in range(M)]
            fix_graph = [[0 if j == i else -99999999999999999 for j in range(U)] for i in range(U)]
            val_graph = [
                [replacement_score(nodes[0][inactive_rows[i]], nodes[0][col_to_row[j]], drow_ptn[i], sum_a_k, sum_b_k,
                                   c_0, d_0, nodes[1][j])[0] for j in range(N)] for i in range(U)]
            rest_graph[0:M, 0:N] = kn_graph

            for i in range(U):
                tmp_wb = val_graph[i]
                tmp_wb.extend(fix_graph[i])
                rest_graph[inactive_rows[i]] = tmp_wb

            '''
            #generate and run LSAP on a matrix of the following form
            #[	kn_graph	|	0	  ]
            #[-------------------------]
            #[	val_graph	|fix_graph]	,

            #where kn_graph and fix_graph are matrices that are a very negative number everywhere except 0 at its diagonal,
            #and val_graph is a graph with replacement scores in its entries (rows correspond to nodes in c_0 and d_0 buckets that are to be replaced by nodes in columns)

            '''
            row_ind, col_ind = sp.optimize.linear_sum_assignment(rest_graph, maximize=True)
            tps = []
            bpt = 0
            for row in inactive_rows:
                if col_ind[row] < N:
                    if set([row, col_to_row[col_ind[row]]]).issubset(m_vind):
                        mdoom_ctr = mdoom_ctr + 1
                        if mdoom_ctr > zugzwang:
                            bpt = 1
                            break
                    m_vind.add(row)
                    m_vind.add(col_to_row[col_ind[row]])
                    no_of_trans = no_of_trans + 1
                    tps.append([row, col_ind[row]])

            if bpt == 1:
                print("Premature termination! Repeat rows:")
                print(m_vind)
                print("\n")
                break

            for pairs in tps:
                inactive_rows.remove(pairs[0])
                inactive_rows.append(col_to_row[pairs[1]])
                col_to_row[pairs[1]] = pairs[0]

            # perform steps 2 and 3 (optimization within buckets) here.
            # LSAP
            for i in range(N):
                lsap_graph[col_to_row[i], :N] = n_edges[col_to_row[i], :N]
            row_ind, col_ind = sp.optimize.linear_sum_assignment(lsap_graph, maximize=True)
            for i in range(N):
                # print (col_to_row, col_ind, row_ind)
                col_to_row[col_ind[i]] = row_ind[i]

            # DP for c_0 and d_0 buckets; variables: sum_a_k, sum_b_k, drow_ptn

            '''
            #Insert DP code here
            '''
            input_list = [[discauxnodes[row][0], discauxnodes[row][1]] for row in inactive_rows]
            best_val, path = findpath(input_list, c_0, d_0, max_sum)
            for i in range(U):
                drow_ptn[U - 1 - i][path & 1] = 1
                drow_ptn[U - 1 - i][1 - (path & 1)] = 0
                path = path >> 1

            sum_a_k = 0
            sum_b_k = 0
            for i in range(U):
                sum_a_k = sum_a_k + (nodes[0][inactive_rows[i]][0] * drow_ptn[i][0])
                sum_b_k = sum_b_k + (nodes[0][inactive_rows[i]][1] * drow_ptn[i][1])

            cost = edges[row_ind, col_ind].sum() + (c_0 * log(sum_a_k)) + (d_0 * log(sum_b_k))
            cost_diff = cost - prev_cost
            prev_cost = cost
            # print("cost_diff = %f" % cost_diff)

        allocmat = np.zeros((M, N + 2))
        f = np.zeros((M,), dtype=int)
        for i in range(N):
            allocmat[col_to_row[i], i] = edges[col_to_row[i], i]
            f[col_to_row[i]] = i

        i = 0
        for row in inactive_rows:
            allocmat[row, N] = drow_ptn[i][0] * (c_0 * log(sum_a_k))
            allocmat[row, N + 1] = drow_ptn[i][1] * (d_0 * log(sum_b_k))
            f[row] = N + drow_ptn[i][1]
            i = i + 1

        # print(cost)
        # print(allocmat)
        # print(f)
        return cost, allocmat, f


# End Multi-Step


def get_frequencies(l):
    d = {}
    for i in l:
        try:
            d[i] += 1
        except:
            d[i] = 1
    return [(a, b) for (a, b) in d.items()]


# p is the percentage error to be introduced
def gen_auxiliary(dist, p):
    random.seed(123)
    aux_dist = [uniform(x * (100 - p), x * (100 + p)) for x in dist]
    tot = sum(aux_dist)
    aux_dist = [x / tot for x in aux_dist]

    return [(f"ciphertext{i}", x) for (i, x) in enumerate(aux_dist)]


def run_all(error, write_file=""):
    rows = [1000000]
    dists = ["lin-lin", "lin-slin", "lin-invlin", "lin-randlin", "lin-zipf", "zipf-zipf", "zipf-randzipf",
             "zipf-invzipf"]
    ciphs_s, ciphs_l = [10, 50, 100], [10, 50, 100, 200, 500]
    res = []

    for row in rows:
        for dist in dists:
            prefix = f"../../Datasets/DI_{row}_{dist}/"
            for ciphs in ciphs_s if row == 10000 else ciphs_l:
                print(f"{row} {ciphs} {dist}: ", end="")
                totv, totr, p, num = 0, 0, 0, 0
                for run in range(10):
                    col1_path = prefix + f"DI_{row}_{ciphs}_{dist}{run}_col0.csv"
                    col2_path = prefix + f"DI_{row}_{ciphs}_{dist}{run}_col1.csv"
                    with open(col1_path, "r") as f:
                        data0 = f.read().split('\n')[:-1]
                    with open(col2_path, "r") as f:
                        data1 = f.read().split('\n')[:-1]

                    dist0, dist1 = data0[0][14:-1], data1[0][14:-1]  # Remove "distribution:[" and "]"
                    dist0, dist1 = [float(i) for i in dist0.split(", ")], [float(i) for i in dist1.split(", ")]
                    col0, col1 = data0[2:], data1[2:]

                    col0_freq, col1_freq = dict(sorted(get_frequencies(col0))), dict(sorted(get_frequencies(col1)))
                    A, B = gen_auxiliary(dist0, error), gen_auxiliary(dist1, error)
                    A.insert(0, ('', 0))
                    B.insert(0, ('', 0))

                    C, D = [0], [0]
                    for key, val in col0_freq.items():
                        if key not in col1_freq.keys():
                            C[0] += val
                        else:
                            C.append((key, val))
                    for key, val in col1_freq.items():
                        if key not in col0_freq.keys():
                            D[0] += val
                        else:
                            D.append((key, val))
                    C[0], D[0] = ('', C[0]), ('', D[0])
                    assert (len(C) == len(D))
                    for i in range(1, len(C)): assert (C[i][0] == D[i][0])

                    # print([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D])
                    _, _, f = main([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D])
                    print(f)

                    # try:
                    # f = DI([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D], 5)
                    # p = probability([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D], f)
                    # print(f, p)
                    # print()

                    # f = DI_genetic([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D], 5)
                    # p = probability([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D], f)
                    # print(f, p)
                    # print()
                    # except Exception as e:
                    #     print(e)
                    #     continue

                    n, m = len(A) - 1, len(C) - 1
                    v, r, numr = 0, 0, 0
                    for pt_idx in range(1, n + 1):
                        if (f[
                                pt_idx - 1] + 1) > m: continue  # if f[pt_idx] > m: continue  # mapped this pt to either W, Y or Z
                        pt, ct = A[pt_idx][0], C[f[pt_idx - 1] + 1][0]  # pt, ct = A[pt_idx][0], C[f[pt_idx]][0]
                        col0_occ, col1_occ = C[f[pt_idx - 1] + 1][1], D[f[pt_idx - 1] + 1][
                            1]  # col0_occ, col1_occ = C[f[pt_idx - 1]][1], D[f[pt_idx - 1]][1]
                        if pt == ct: v, r = v + 1, r + col0_occ * col1_occ
                        numr += col0_occ * col1_occ

                    totv, totr, num = totv + v / m, totr + r / numr, num + 1

                if num != 0:
                    res.append((f"{row}_{ciphs}_{dist},{totv / num},{totr / num},{num}", totv / num, totr / num))
                    print(totv / num, totr / num)

    to_write = "rows_ciphs_distribution,v-score,r-score,num of good files\n"
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"
    res = sorted(res, key=lambda x: -x[1])
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"
    res = sorted(res, key=lambda x: -x[2])
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"
    res = sorted(res, key=lambda x: -x[1] - x[2])
    to_write += "\n".join([i[0] for i in res]) + "\n\n\n\n\n"

    if write_file == "":
        print("\n\n\n\n\n\n\n", to_write, sep="")
    else:
        with open(write_file, "w") as f:
            f.write(to_write)


for e in [5, 10, 20]:
    print("run_all with error =", e)
    run_all(e, f"DI_e={e}.csv")
    print("\n\n\n\n\n")

