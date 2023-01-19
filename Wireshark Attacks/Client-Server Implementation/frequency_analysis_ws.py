import sys, pickle

# frequency analysis LAA (for SELECT queries)
# a is (ciph, num_occ), b is (aux, num_occ)
def frequency_analysis(a, b):
    if len(a) < len(b): b = b[:len(a)] # remove excess plaintexts
    else: b.extend([('0', 0)] * (len(a) - len(b))) # pad 0 to end of plaintexts    
    a, b = sorted(a, key=lambda x: x[1]), sorted(b, key=lambda x: x[1])
    return [(a[x][0], b[x][0]) for x in range(len(a))]


def load():
    ciph_file = sys.argv[1]
    aux_file = sys.argv[2]
    col_name = sys.argv[3]

    with open(ciph_file, "rb") as f: ciph_freq = pickle.loads(f.read())

    from pandas import read_csv
    aux_col = read_csv(aux_file, dtype=str, keep_default_na=False, usecols=[col_name])[col_name]
    aux_col = list(aux_col)
    d = {}
    for i in aux_col:
        try: d[i] += 1
        except: d[i] = 1
    aux_freq = list(d.items())

    with open("select_pt", "rb") as f: select_pt = pickle.loads(f.read())

    return ciph_freq, aux_freq, select_pt

if __name__ == "__main__":
    ciph_freq, aux_freq, select_pt = load()
    matching = frequency_analysis(ciph_freq, aux_freq)
    for a, b in matching: print(b, '=', select_pt[a])
    print("\n\n")

    new_l = [(select_pt[a], b) for a, b in ciph_freq]

    dict_ciph = dict(ciph_freq)

    vscore, rscore, totv, totrows = 0, 0, 0, 0
    for ciph, pt in matching:
        num_occ = dict_ciph[ciph]
        if select_pt[ciph].upper() == pt.upper(): vscore, rscore = vscore + 1, rscore + num_occ
        totv, totrows = totv + 1, totrows + num_occ

    print(f"(v_score, r_score) = ({vscore / totv}, {rscore / totrows})")
