import sys, math, pickle
from scipy.optimize import linear_sum_assignment
from random import uniform, seed


def gen_aux(dist, e):
    seed(123)
    aux_dist = [uniform(x * (100-e), x * (100+e)) for x in dist]
    tot = sum(aux_dist)
    aux_dist = [x / tot for x in aux_dist]
    return [(f"ciphertext{i}", x) for (i, x) in enumerate(aux_dist)]


# bipartite graph LAA (for JOIN queries)
# a, c are lists of ciphertexts
# b, d are lists of auxiliary data
def bipartite_graph_matching(A, B, C, D):
    try:  # Sieve out DI cases
        assert (len(A) == len(C))
        for i in range(len(A)): assert (A[i][0] == C[i][0])
    except:
        return -1, -1

    assert (len(B) == len(D))
    assert (len(A) <= len(B))
    if len(A) < len(B):
        A.extend([('0', 0)] * (len(B) - len(A)))
        C.extend([('0', 0)] * (len(B) - len(C)))

    cost_matrix = [[-A[y][1] * math.log(B[x][1]) - C[y][1] * math.log(D[x][1]) for y in range(len(A))]
                   for x in range(len(B))]  # negate value because scipy.optimize.lsa calculates minimum
    _, matching = linear_sum_assignment(cost_matrix)

    return matching

def load():
    ciphs_FP_file = sys.argv[1]
    col0_aux_file = sys.argv[2]
    col1_aux_file = sys.argv[3]
    e = int(sys.argv[4])

    with open(ciphs_FP_file, "rb") as f: ciphs_FP = pickle.loads(f.read())
    A, C = ciphs_FP
    A, C = sorted(A), sorted(C)

    with open(col0_aux_file, "r") as f: col0_aux = f.readlines()[0].replace("distribution:[", "").replace("]", "").split(', ')
    with open(col1_aux_file, "r") as f: col1_aux = f.readlines()[0].replace("distribution:[", "").replace("]", "").split(', ')
    col0_aux, col1_aux = [float(i) for i in col0_aux], [float(i) for i in col1_aux]
    B, D = gen_aux(col0_aux, e), gen_aux(col1_aux, e)

    with open("join_pt", "rb") as f: join_pt = pickle.loads(f.read())

    return A, B, C, D, join_pt


if __name__ == "__main__":
    A, B, C, D, join_pt = load()
    matching = bipartite_graph_matching(A, B, C, D) # pt i mapped to ct matching[i]
    for i in matching: print(B[i][0], '=', join_pt[A[matching[i]][0]])
    print("\n\n")

    v, r, totv, totr = 0, 0, 0, 0
    for i in range(len(A)):
        if B[i][0] == join_pt[A[matching[i]][0]]: v, r = v + 1, r + A[matching[i]][1] * C[matching[i]][1]
        totv, totr = totv + 1, totr + A[i][1] * C[i][1]

    print(f"(v_score, r_score) = ({v/totv}, {r/totr})")
