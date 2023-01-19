import math
import os
import random

df_stat_file = "v2_df_overall_stats.txt"
di_stat_file = "v2_di_overall_stats.txt"

# each tuple (a,b) is an instance with a rows in each column and b distinct values in either column
instances_set = [(10000, 10), (10000, 50), (10000, 100), (1000000, 10), (1000000, 50), (1000000, 100), (1000000, 200),
                 (1000000, 500)]
# repeat each instance how many times
num_reps = 10
# in DI case, set this percentage (rounded) of the ciphertext values to negligibly small
di_fraction = 0.1
replace_flag = False


# generate ciphertexts
def gen_ciphs(num_ciph):
    s = []
    for i in range(num_ciph):
        s.append("ciphertext" + str(i))
        # s.append(''.join(random.choice(string.ascii_lowercase) for _ in range(16)))
    return s


# scale distri so it adds up to 1
def scale_distri(distri):
    s = sum(distri)
    out = [float(x) / float(s) for x in distri]
    return out


# y=x
def linear_distri(num_ciph):
    s = (num_ciph * (num_ciph + 1)) / 2
    return [(float(i + 1) / float(s)) for i in range(num_ciph)]


# y=.5x+.25
def s_linear_distri(num_ciph):
    s = (num_ciph * (num_ciph + 1)) / 2
    return [0.5 / float(num_ciph) + (float(i + 1) / float(2 * s)) for i in range(num_ciph)]


def harmonic(a, b):
    l = [(n + 1) ** (-b) for n in range(a)]
    return sum(l)


def zipf_r(a, b, r):
    return r ** (-b) / harmonic(a, b)


# zipfian distri with b=1
def zipf(num_ciph):
    b = 1
    a = num_ciph
    return [zipf_r(a, b, r + 1) for r in range(num_ciph)]


def gen_tuples(distri, ciphs, num_rows, num_ciph, filename):
    # l = []
    c_distri = []
    last = 0
    for i in range(num_ciph):
        c_distri.append(last)
        last = last + distri[i]
    c_distri.append(last)
    # print("cumulative distribution:" + str(c_distri))
    count = [0] * num_ciph
    for i in range(num_rows):
        val1 = random.random()
        ctr = 0
        for i in c_distri:
            if i <= val1:
                ctr = ctr + 1
            else:
                break
        ctr = ctr - 1
        count[ctr] = count[ctr] + 1
        with open(filename, "a") as file:
            file.write(ciphs[ctr])
            file.write("\n")
    return count


def df_one_case(distri, ciphs, num_rows, num_ciph, name):
    filename = "DF_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv"
    writename = "v2_df_datasets/" + filename
    c_distri = distri[:]
    c_distri = scale_distri(c_distri)
    if os.path.exists(writename) and not replace_flag:
        return 2
    with open(writename, "w") as file:
        file.write("distribution:" + str(c_distri) + "\n\n")
    outcome = (gen_tuples(c_distri, ciphs, num_rows, num_ciph, writename))
    rep = num_ciph
    for i in range(num_ciph):
        if outcome[i] == 0:
            rep = rep - 1
    if rep != num_ciph:
        os.remove(writename)
        return 0
    else:
        with open(df_stat_file, "a") as file:
            file.write(filename + " distribution: " + str(c_distri) + "\n")
            file.write(filename + " frequencies: " + str(outcome) + "\n\n")
            # file.write(filename + " represented ciphertexts: " + str(rep) + "/" + str(num_ciph) + "\n\n")
        return 1


def di_one_case(distri, ciphs, num_rows, num_ciph, name):
    filename = "DI_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv"
    writename = "v2_di_datasets/" + filename
    if os.path.exists(writename) and not replace_flag:
        return 2
    low_prob = float(1) / float(10 * num_rows)
    num_samp = math.ceil(di_fraction * num_ciph)
    sampled = random.sample(range(0, num_ciph - 1), num_samp)
    c_distri = distri[:]
    for i in sampled:
        c_distri[i] = low_prob
    c_distri = scale_distri(c_distri)
    with open(writename, "w") as file:
        file.write("distribution:" + str(c_distri) + "\n\n")
    outcome = (gen_tuples(c_distri, ciphs, num_rows, num_ciph, writename))
    rep = num_ciph
    for i in range(num_ciph):
        if outcome[i] == 0:
            rep = rep - 1
    if rep == num_ciph:
        os.remove(writename)
        return 0
    else:
        with open(di_stat_file, "a") as file:
            file.write(filename + " distribution: " + str(c_distri) + "\n")
            file.write(filename + " frequencies: " + str(outcome) + "\n")
            file.write(filename + " represented ciphertexts: " + str(rep) + "/" + str(num_ciph) + "\n\n")
        return 1


def one_case(distri, ciphs, num_rows, num_ciph, name):
    print("Generating:" + "DF_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")
    i = 0
    while i == 0:
        i = df_one_case(distri, ciphs, num_rows, num_ciph, name)
        if i == 0:
            print("Repeating:" + "DF_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")
    if i == 1:
        print("completed:" + "DF_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")
    if i == 2:
        print("skipped: " + "DF_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")
    i = 0
    print("Generating:" + "DI_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")
    while i == 0:
        i = di_one_case(distri, ciphs, num_rows, num_ciph, name)
        if i == 0:
            print("Repeating:" + "DI_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")
    if i == 1:
        print("completed:" + "DI_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")
    if i == 2:
        print("skipped: " + "DI_" + str(num_rows) + "_" + str(num_ciph) + "_" + name + ".csv")


# c,d both lin, both zipf
def same_distri():
    for (k, j) in instances_set:
        distri = linear_distri(j)
        ciphs = gen_ciphs(j)
        for i in range(num_reps):
            one_case(distri, ciphs, k, j, "lin-lin" + str(i) + "_col0")
            one_case(distri, ciphs, k, j, "lin-lin" + str(i) + "_col1")
        distri = zipf(j)
        for i in range(num_reps):
            one_case(distri, ciphs, k, j, "zipf-zipf" + str(i) + "_col0")
            one_case(distri, ciphs, k, j, "zipf-zipf" + str(i) + "_col1")


# c,d are lin-slin, or lin-zipf
def correlated():
    for (k, j) in instances_set:
        distri1 = linear_distri(j)
        distri2 = s_linear_distri(j)
        ciphs = gen_ciphs(j)
        for i in range(num_reps):
            one_case(distri1, ciphs, k, j, "lin-slin" + str(i) + "_col0")
            one_case(distri2, ciphs, k, j, "lin-slin" + str(i) + "_col1")
        distri1 = linear_distri(j)
        distri2 = zipf(j)
        for i in range(num_reps):
            one_case(distri1, ciphs, k, j, "lin-zipf" + str(i) + "_col0")
            one_case(distri2, ciphs, k, j, "lin-zipf" + str(i) + "_col1")
        # distri1 = zipf(j)
        # distri2 = f_zipf(j)
        # for i in range(num_reps):
        #     one_case(distri1, ciphs, k, j, "zipf-fzipf" + str(i) + "_col0")
        #     one_case(distri2, ciphs, k, j, "zipf-fzipf" + str(i) + "_col1")


# c,d both lin or both zipf, but d distribution is reversed
def decorrelated():
    for (k, j) in instances_set:
        ciphs = gen_ciphs(j)
        distri1 = linear_distri(j)
        distri2 = linear_distri(j)
        distri2.reverse()
        for i in range(num_reps):
            one_case(distri1, ciphs, k, j, "lin-invlin" + str(i) + "_col0")
            one_case(distri2, ciphs, k, j, "lin-invlin" + str(i) + "_col1")
        distri1 = zipf(j)
        distri2 = zipf(j)
        distri2.reverse()
        for i in range(num_reps):
            one_case(distri1, ciphs, k, j, "zipf-invzipf" + str(i) + "_col0")
            one_case(distri2, ciphs, k, j, "zipf-invzipf" + str(i) + "_col1")

# c,d both lin or both zipf, but d distribution is randomly shuffled
def shuffled():
    for (k, j) in instances_set:
        ciphs = gen_ciphs(j)
        distri1 = linear_distri(j)
        distri2 = linear_distri(j)
        random.shuffle(distri2)
        for i in range(num_reps):
            one_case(distri1, ciphs, k, j, "lin-randlin" + str(i) + "_col0")
            one_case(distri2, ciphs, k, j, "lin-randlin" + str(i) + "_col1")
        distri1 = zipf(j)
        distri2 = zipf(j)
        random.shuffle(distri2)
        for i in range(num_reps):
            one_case(distri1, ciphs, k, j, "zipf-randzipf" + str(i) + "_col0")
            one_case(distri2, ciphs, k, j, "zipf-randzipf" + str(i) + "_col1")

# generates all files, if file already exists, will skip
if __name__ == '__main__':
    with open(df_stat_file, "w") as file:
        file.write("SUMMARY STATS:\n\n")
    with open(di_stat_file, "w") as file:
        file.write("SUMMARY STATS:\n\n")
    same_distri()
    correlated()
    decorrelated()
    shuffled()
