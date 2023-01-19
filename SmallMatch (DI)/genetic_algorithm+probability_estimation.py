import math
import random

import tqdm
from scipy.optimize import linear_sum_assignment
from random import uniform, randint, randrange, choice

inf = 9999999999999


def log(x):
    if x < 0:
        return -inf * inf
    elif x == 0:
        return -inf
    else:
        return math.log(x)


# A, B are lists of integers of length n
# c, d are integers
# Returns a partition R, S of [0, n-1] that maximises sum(A_i, i in R)^c * sum(B_i, i in S)^d
def partition(A, B, c, d):
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


def step_1(A, B, C, D):
    assert (len(A) == len(B))
    assert (len(C) == len(D))
    n, m = len(A) - 1, len(C) - 1
    assert (n > m)

    # Step 1: Split X+Y+Z into (X, Y+Z)
    totC, totD = sum(C), sum(D)
    P = [(i, (1 - A[i]) ** totC + (1 - B[i]) ** totD - (1 - A[i]) ** totC * (1 - B[i]) ** totD) for i in
         range(1, n + 1)]
    P = sorted(P, key=lambda x: -x[1])
    X, YZ = [x[0] for x in P[n - m:]], [x[0] for x in P[:n - m]]
    return X, YZ


# A = [<dummy>, aux_prob of pt_i in col1], A[1] to A[n]
# B = [<dummy>, aux_prob of pt_i in col2], B[1] to B[n]
# C[0] = num of ct that we don't know if got matching ct in col1, C[i] = number of ct_i in col1 that matches to ct_i in col2, C[0] to C[m]
# D[0] = num of ct that we don't know if got matching ct in col2, D[i] = number of ct_i in col2 that matches to ct_i in col1, D[0] to D[m]
# num_d = number of digits to round A[i], B[i] to
def DI(A, B, C, D, num_d):
    assert (len(A) == len(B))
    assert (len(C) == len(D))
    n, m = len(A) - 1, len(C) - 1
    assert (n > m)

    X, YZ = step_1(A, B, C, D)
    return step_2_3(A, B, C, D, X, YZ, num_d, n, m)


def DI_genetic(A, B, C, D, num_d):
    assert (len(A) == len(B))
    assert (len(C) == len(D))
    n, m = len(A) - 1, len(C) - 1
    assert (n > m)

    def random_chromosome():
        X = set(range(1, len(A)))
        YZ = set(randint(1, n) for x in range(n - m))
        return list(X.difference(YZ)), list(YZ)

    def fitness(x):
        f = step_2_3(A, B, C, D, x[0], x[1], num_d, n, m)
        return probability(A, B, C, D, f)

    def mutate(x):
        x = (x[0][:], x[1][:])
        for j in range(randint(1, 5)):
            if len(x[0]) == 0: break
            idx = randrange(len(x[0]))
            idx2 = randrange(len(x[1]))
            x[0][idx], x[1][idx2] = x[1][idx2], x[0][idx]

        return x

    def tournament_selection(fitnesses, k=3):
        return fitnesses[max([randrange(len(fitnesses)) for _ in range(k)])][0]

    POPULATION_SIZE = 15 * n
    MAX_GENERATIONS = 15
    best = None
    time_since_new_best = 0
    population = [random_chromosome() for x in range(POPULATION_SIZE - 1)] + [step_1(A, B, C, D)]
    for _ in tqdm.tqdm(range(MAX_GENERATIONS)):

        fitnesses = sorted(map(lambda x: (x, fitness(x)), population), key=lambda x: x[1])

        # Storing the best
        if best is None or best[1] < fitnesses[-1][1]: best = fitnesses[-1]
        else: time_since_new_best += 1

        if time_since_new_best > 4: break

        # Generating new popoulation
        population = []
        random_chromosome()
        for x in range(len(fitnesses) // 10):
            population.append(random_chromosome())
            population.append(fitnesses[-x-1][0])

        for i in range(8 * len(fitnesses) // 10):
            population.append(mutate(tournament_selection(fitnesses, k=6)))

    return step_2_3(A, B, C, D, best[0][0], best[0][1], num_d, n, m)


def step_2_3(A, B, C, D, X, YZ, num_d, n, m):
    f = [0] * (n + 1)

    # Step 2: Apply graph matching to X
    cost_matrix = [[-C[ct] * log(A[pt]) - D[ct] * log(B[pt]) for ct in range(1, m + 1)] for pt in X]
    _, matching = linear_sum_assignment(cost_matrix)
    for idx, ct in enumerate(matching): f[X[idx]] = ct + 1

    # Step 3: Split Y+Z into Y, Z
    AA, BB = [round(A[i] * 10 ** num_d) for i in YZ], [round(B[i] * 10 ** num_d) for i in YZ]
    Y, Z = partition(AA, BB, C[0], D[0])
    Y, Z = [YZ[i] for i in Y], [YZ[i] for i in Z]
    for i in Y: f[i] = m + 1
    for i in Z: f[i] = m + 2

    return f


def probability(A, B, C, D, f):
    p = 0
    m = len(C) - 1
    for i in range(1, len(f)):
        if f[i] <= m:
            p += C[f[i]] * log(A[i]) + D[f[i]] * log(B[i])

    p += log(sum([A[i] for i in range(len(f)) if f[i] == m + 1])) * C[0]
    p += log(sum([B[i] for i in range(len(f)) if f[i] == m + 2])) * D[0]
    return p


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
    dists = ["lin-lin", "lin-slin", "lin-invlin", "lin-randlin", "lin-zipf", "zipf-zipf", "zipf-randzipf", "zipf-invzipf"]
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
                    with open(col1_path, "r") as f: data0 = f.read().split('\n')[:-1]
                    with open(col2_path, "r") as f: data1 = f.read().split('\n')[:-1]

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

                    f = DI([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D], 5)
                    p = probability([x[1] for x in A], [x[1] for x in B], [x[1] for x in C], [x[1] for x in D], f)
                    print(f, p, len(A) - 1, len(C) - 1)

                    n, m = len(A) - 1, len(C) - 1
                    v, r, numr = 0, 0, 0
                    for pt_idx in range(1, n + 1):
                        if f[pt_idx] > m: continue  # mapped this pt to either W, Y or Z
                        pt, ct = A[pt_idx][0], C[f[pt_idx]][0]
                        col0_occ, col1_occ = C[f[pt_idx]][1], D[f[pt_idx]][1]
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


for e in [5]:
    print("run_all with error =", e)
    run_all(e, f"DI_e={e}.csv")
    print("\n\n\n\n\n")
