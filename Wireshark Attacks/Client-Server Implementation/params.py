case = 0

if case == 0:
    tables = 1
    table_files = ["col0.csv"]
    select_cols = [True]
    join_cols = {}
elif case == 1:
    tables = 2
    table_files = ["col0.csv", "col1.csv"]
    select_cols = [True, True]
    join_cols = {(0, 1): True}

# Leave select_cols[i] as True for select_cols to be all possible columns for table i
# Change join_cols[(i, j)] to True if all possible pairs of (column in table i, column in table j) are joinable


K_S_M_file = "K_S_M"
K_S_N_file = "K_S_N"
K_F_M_file = "K_F_M"
K_F_N_file = "K_F_N"

with open(K_S_M_file, "rb") as f: K_S_M = f.read()
with open(K_S_N_file, "rb") as f: K_S_N = f.read()
with open(K_F_M_file, "rb") as f: K_F_M = f.read()
with open(K_F_N_file, "rb") as f: K_F_N = f.read()
