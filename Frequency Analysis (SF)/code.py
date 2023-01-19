# frequency analysis LAA (for SELECT queries)
# a is (ciph, num_occ), b is (aux, num_occ)
def frequency_analysis(a, b):
    if len(a) < len(b): b = b[:len(a)] # remove excess plaintexts
    else: b.extend([('0', 0)] * (len(a) - len(b))) # pad 0 to end of plaintexts    
    a, b = sorted(a, key=lambda x: x[1]), sorted(b, key=lambda x: x[1])
    return [(a[x], b[x]) for x in range(len(a))]


def load(ciph_file, aux_file, ciph_col, aux_col):
    from pandas import read_csv

    ciph_col = read_csv(ciph_file, dtype=str, keep_default_na=False, usecols=[ciph_col])[ciph_col]
    ciph_col = list(ciph_col)
    d = {}
    for i in ciph_col:
        try: d[i] += 1
        except: d[i] = 1
    ciph_freq = list(d.items())

    aux_col = read_csv(aux_file, dtype=str, keep_default_na=False, usecols=[aux_col])[aux_col]
    aux_col = list(aux_col)
    d = {}
    for i in aux_col:
        try: d[i] += 1
        except: d[i] = 1
    aux_freq = list(d.items())

    return ciph_freq, aux_freq


prefix = "../../Datasets/"
ciph_file = [''] + ["ohio_1000000.csv"] * 2 + ["NIS_2019_Core_1000000_cols.csv"] * 13
aux_file = [''] + ["flori_1000000_cols_caps.csv"] * 4 + ["NIS_2018_Core_1000000_cols.csv"] * 11
ciph_col = ['', "FIRST_NAME", "LAST_NAME", "Indicator of sex", "Race (uniform)", "Age in years at admission",
            "Neonatal age (first 28 days after birth) indicator", "Admission month", "Admission day is a weekend",
            "Died during hospitalization", "DRG in effect on discharge date", "MDC in effect on discharge date", "ICD-10-CM Diagnosis 1",
            "Number of days from admission to I10_PR1", "Indicator of sex", "Race (uniform)"]
aux_col = ciph_col[:3] + ["GENDER", "RACE"] + ciph_col[5:]

def equals(ciph, pt, num):
    if num == 3: return (ciph == '1' and pt == 'F') or (ciph == '0' and pt == 'M')
    elif (num == 4 or num == 15) and int(ciph) < 0: return False
    else: return ciph.upper() == pt.upper()

def counted(ciph, pt, num):
    if num == 3: return (ciph == '0' or ciph == '1')
    # elif num == 4: return 1
    elif (num == 4 or num == 15) and int(ciph) < 0: return False
    else: return True

for i in range(1, len(ciph_col)):
    ciph_freq, aux_freq = load(prefix + ciph_file[i], prefix + aux_file[i], ciph_col[i], aux_col[i])
    matching = frequency_analysis(ciph_freq, aux_freq)

    dict_ciph = dict(ciph_freq)

    vscore, rscore, totv, totrows = 0, 0, 0, 0
    for ciph, pt in matching:
        num_occ = dict_ciph[ciph]
        if equals(ciph, pt, i): vscore, rscore = vscore + 1, rscore + num_occ
        if counted(ciph, pt, i): totv, totrows = totv + 1, totrows + num_occ

    print(f"v-score = {'%s' % float('%.3g' % (vscore/totv))}, r-score = {'%s' % float('%.3g' % (rscore / totrows))}")