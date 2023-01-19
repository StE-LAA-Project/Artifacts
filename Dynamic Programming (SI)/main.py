import math
import sys
import random
import time
import copy

# change these variables
prefix = "100firstname"
run = "0"

random.seed(time.time())
sys.setrecursionlimit(50000)

def sort_by_second(elem):
	return elem[1]

def calc_sums_weighted(l):
	# skips over -1 (queried) values
	ssums = []
	cur = 0
	for val in l:
		if val[1] == -1:
			continue
		ssums.append(cur+val[1])
		cur += val[1]
	return ssums

def retrieve_vals(csv, is_ciph=True):
	# is_ciph=False means retrieving aux values
	csv_file = open(csv, 'r')
	vals = []
	for line in csv_file:
		try:
			val = line.split(',')
			if is_ciph:
				try:
					vals.append([val[0], int(val[1])])
				except:
					vals.append([val[0], int(val[1][:-1])]) # remove \n
			else: 
				try:
					vals.append([val[0], float(val[1])])
				except:
					vals.append([val[0], float(val[1][:-1])]) # remove \n
		except:
			continue
	csv_file.close()
	vals.sort(key=sort_by_second)
	return vals

def write_csv_file(csv, vals):
	csv_file = open(csv, 'a')
	for val in vals:
		csv_file.write(f"{val[0]},{val[1]}\n")

def save_corr_ans(ans, ciphs, newd):
	corr_ans = []
	for i in range(len(ciphs)):
		try:
			query_pos = newd.index(i)
			corr_ans.append(query_pos+1)
		except:
			# not queried
			corr_ans.append(0)

	ans_file = open(ans, 'w')
	ans_file.write(','.join(str(i) for i in corr_ans))
	ans_file.close()
	return corr_ans

def build_d(o_ciphs, corr_ans):
	d = []
	total = 0
	for i in range(len(o_ciphs)):
		if corr_ans[i]:
			# queried
			d.append(o_ciphs[i][1])
		else:
			total += o_ciphs[i][1]
	d.insert(0, total)
	return d

def weighted_query(csv, percentage, ans, sort_csv=""):
	ciphs = retrieve_vals(csv)

	if sort_csv: write_csv_file(sort_csv, ciphs)

	newd = []
	queries = math.ceil(int(percentage)/100*len(ciphs))
	for i in range(queries):
		sums = calc_sums_weighted(ciphs)
		queried = random.randint(1, sums[len(sums)-1]-1) # query val

		# find index in sums array
		index = -1
		for j in sums:
			if j >= queried:
				index = sums.index(j)
				break

		# find index in original array
		real_index = -1
		counter = 0
		for j in ciphs:
			if j[1] == -1:
				continue
			if counter == index:
				real_index = ciphs.index(j)
				break
			counter += 1

		newd.append(real_index)
		ciphs[real_index][1] = -1

	newd.sort()
	o_ciphs = retrieve_vals(csv)

	# save "correct answer"
	corr_ans = save_corr_ans(ans, o_ciphs, newd)

	return build_d(o_ciphs, corr_ans)

def unweighted_query(csv, percentage, ans, sort_csv=""):
	ciphs = retrieve_vals(csv)
	if sort_csv: write_csv_file(sort_csv, ciphs)

	queries = math.ceil(int(percentage)/100*len(ciphs))
	queried_vals = random.sample(ciphs, k=queries)

	newd = [] # saves indexes of queried values
	for i in queried_vals:
		newd.append(ciphs.index(i))
	newd.sort()

	corr_ans = save_corr_ans(ans, ciphs, newd)

	return build_d(ciphs, corr_ans)

def topx_query(csv, percentage, ans, sort_csv=""):
	ciphs = retrieve_vals(csv)
	if sort_csv: write_csv_file(sort_csv, ciphs)

	queries = math.ceil(int(percentage)/100*len(ciphs))
	newd = [len(ciphs)-1-_ for _ in range(queries)] # indexes of queried values
	newd.sort()
	corr_ans = save_corr_ans(ans, ciphs, newd)

	return build_d(ciphs, corr_ans)

def retrieve_aux(csv, sort_csv=""):
	aux = retrieve_vals(csv, False)
	if sort_csv: write_csv_file(sort_csv, aux)
	b = [i[1] for i in aux]
	return b

def get_p(dec, d):
	try:
		return math.log(dec, 10) * d
	except:
		# should not occur
		return -d

def si_dp(nn, mm, ddelta, mmapping, bb, dd):
	memo = {}
	def get_highest_prob(n, m, delta, mapping, b, d):
		if (n, m, delta) in memo:
			return memo[n, m, delta]
		mapping = list(mapping)

		if m == 0:
			mapping = []
			final_delta = delta
			for i in range(n+1):
				mapping.append(0)
				final_delta += b[i]
			p = get_p(final_delta, d[0])
			for i in range(n+1, len(b)):
				mapping.append(-1)
			mapping = tuple(mapping)
			memo[n, m, delta] = (mapping, p)

		elif m-1 > n:
			memo[n, m, delta] = ((), -999999999999999999999999999999999999)

		else:
			m1 = copy.copy(mapping)
			m1[n] = 0
			m1 = tuple(m1)
			newdelta = delta+round(b[n], 3)
			(m_1, p_1) = get_highest_prob(n-1, m, newdelta, m1, b, d)
			
			m2 = copy.copy(mapping)
			m2[n] = m
			m2 = tuple(m2)
			(m_2, p_2) = get_highest_prob(n-1, m-1, delta, m2, b, d)
			p_2 += get_p(b[n], d[m])
			
			if p_2 > p_1:
				mapping = list(m_2)
				mapping[n] = m
				p = p_2
			else:
				mapping = list(m_1)
				mapping[n] = 0
				p = p_1

			mapping = tuple(mapping)
			memo[n, m, delta] = (mapping, p)
		
		return memo[n, m, delta]

	final_mapping = get_highest_prob(nn, mm, ddelta, mmapping, bb, dd)
	return final_mapping

def calc_scores(ciph_csv, aux_csv, ans, mmapping, d):
	ciph_vals = retrieve_vals(ciph_csv)
	aux_vals = retrieve_vals(aux_csv, False)
	aux_names = [i[0] for i in aux_vals]
	corr_arr = open(ans, 'r').read().split(',')
	mapping = mmapping[0]
	for i, val in enumerate(corr_arr): corr_arr[i] = int(val)

	corr_rows = 0
	corr_vals = 0
	tot_rows = sum(d[1:])

	for i, name in enumerate(ciph_vals):
		try:
			# check if value exists in both vectors
			aux_index = aux_names.index(name[0])
		except:
			continue

		if mapping[i] == corr_arr[aux_index]:
			if mapping[i] != 0:
				corr_vals += 1
				corr_rows += name[1]

	return (corr_vals/(len(d)-1), corr_rows/tot_rows)

if __name__ == "__main__":
	b = retrieve_aux(f"{prefix}_aux.csv", f"{prefix}_aux_sorted.csv")

	print("TOP 10: ", end="")
	d = topx_query(f"{prefix}_cipher.csv", 10, f"ans{run}.txt", f"{prefix}_cipher_sort.csv")
	mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
	print(calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d))

	print("TOP 50: ", end="")
	d = topx_query(f"{prefix}_cipher.csv", 50, f"ans{run}.txt")
	mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
	print(calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d))

	print("TOP 90: ", end="")
	d = topx_query(f"{prefix}_cipher.csv", 90, f"ans{run}.txt")
	mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
	print(calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d))

	tot_v, tot_r = 0, 0
	print("WEIGHTED 10: ", end="")
	for i in range(10):
		d = weighted_query(f"{prefix}_cipher.csv", 10, f"ans{run}.txt")
		mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
		v_score, r_score = calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d)
		tot_v += v_score
		tot_r += r_score
	print(f"({tot_v/10}, {tot_r/10})")

	tot_v, tot_r = 0, 0
	print("WEIGHTED 50: ", end="")
	for i in range(10):
		d = weighted_query(f"{prefix}_cipher.csv", 50, f"ans{run}.txt")
		mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
		v_score, r_score = calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d)
		tot_v += v_score
		tot_r += r_score
	print(f"({tot_v/10}, {tot_r/10})")

	tot_v, tot_r = 0, 0
	print("WEIGHTED 90: ", end="")
	for i in range(10):
		d = weighted_query(f"{prefix}_cipher.csv", 90, f"ans{run}.txt")
		mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
		v_score, r_score = calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d)
		tot_v += v_score
		tot_r += r_score
	print(f"({tot_v/10}, {tot_r/10})")

	tot_v, tot_r = 0, 0
	print("UNWEIGHTED 10: ", end="")
	for i in range(10):
		d = unweighted_query(f"{prefix}_cipher.csv", 10, f"ans{run}.txt")
		mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
		v_score, r_score = calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d)
		tot_v += v_score
		tot_r += r_score
	print(f"({tot_v/10}, {tot_r/10})")

	tot_v, tot_r = 0, 0
	print("UNWEIGHTED 50: ", end="")
	for i in range(10):
		d = unweighted_query(f"{prefix}_cipher.csv", 50, f"ans{run}.txt")
		mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
		v_score, r_score = calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d)
		tot_v += v_score
		tot_r += r_score
	print(f"({tot_v/10}, {tot_r/10})")

	tot_v, tot_r = 0, 0
	print("UNWEIGHTED 90: ", end="")
	for i in range(10):
		d = unweighted_query(f"{prefix}_cipher.csv", 90, f"ans{run}.txt")
		mapping = si_dp(len(b)-1, len(d)-1, 0, (-1 for _ in b), b, d)
		v_score, r_score = calc_scores(f"{prefix}_cipher_sort.csv", f"{prefix}_aux_sorted.csv", f"ans{run}.txt", mapping, d)
		tot_v += v_score
		tot_r += r_score
	print(f"({tot_v/10}, {tot_r/10})")