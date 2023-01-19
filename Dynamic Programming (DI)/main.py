from SI import si_dp, get_p, sort_by_second
import math
import sys
import random
import copy
import subprocess
from random import uniform

sys.setrecursionlimit(50000)

def round_nearest(x, a):
	return round(x / a) * a

def heur_dp(nn, mm, ddelta1, ddelta2, mmapping, aa, bb, cc, dd, mm_size):
	memo = {}
	def get_highest_prob(n, m, delta1, delta2, mapping, a, b, c, d, m_size):
		if (n, m, delta1, delta2) in memo:
			return memo[n, m, delta1, delta2]
		mapping = list(mapping)
		if m == 0:
			sendarr0 = []
			sendarr1 = []
			str1 = ''
			str2 = ''
			indexes = []
			for i in range(n+1): 
				sendarr0.append(int(round(a[i], 5) * (10 ** 5)))
				sendarr1.append(int(round(b[i], 5) * (10 ** 5)))
				indexes.append(i)
			for i in range(len(sendarr0)): str1 += str(sendarr0[i]) + ','
			for i in range(len(sendarr1)): str2 += str(sendarr1[i]) + ','

			str1 += f"{round(delta1*10**5)},0"
			str2 += f"0,{round(delta2*10**5)}"

			subprocess.call(["./POAA.exe", str1, str2, str(c[0]), str(d[0])])
			partition_ans = open("di_ans.txt", 'r')
			counter = 0
			m1_sum = 0
			m2_sum = 0
			for line in partition_ans:
				# print(line)
				line = line[:-1]
				temp = line.split(',')
				if temp[0] == '0': 
					try:
						mapping[indexes[counter]] = m_size+2
						m2_sum += sendarr1[counter] / (10 ** 5)
					except: m2_sum = delta2
				else: 
					try:
						mapping[indexes[counter]] = m_size+1
						m1_sum += sendarr0[counter] / (10 ** 5)
					except: m1_sum = delta1
				counter += 1

			p = get_p(m1_sum, c[0]) + get_p(m2_sum, d[0])
			mapping = tuple(mapping)
			memo[n,m,delta1,delta2] = (mapping, p)
		elif m-1 > n:
			memo[n, m, delta1, delta2] = ((), -999999999999999999999999999999999999)
		else:
			m3 = copy.copy(mapping)
			m3[n] = m
			m3 = tuple(m3)
			(m_3, p_3) = get_highest_prob(n-1, m-1, delta1, delta2, m3, a, b, c, d, m_size)
			p_3 += get_p(b[n], d[m])
			p_3 += get_p(a[n], c[m])

			m1 = copy.copy(mapping)
			m1[n] = m_size + 1 # m + 1
			m1 = tuple(m1)
			x = delta1+round_nearest(a[n], 0.01)
			(m_1, p_1) = get_highest_prob(n-1, m, x, delta2, m1, a, b, c, d, m_size)

			m2 = copy.copy(mapping)
			m2[n] = m_size + 2 # m + 2
			m2 = tuple(m2)
			x = delta2+round_nearest(b[n], 0.01)
			(m_2, p_2) = get_highest_prob(n-1, m, delta1, x, m2, a, b, c, d, m_size)

			if p_2 > p_1 and p_2 > p_3:
				mapping = list(m_2)
				try: 
					mapping[n] = m_size + 2
					p = p_2
				except: 
					mapping = ()
					p = -999999999999999999999999999999999999
			elif p_1 > p_3:
				mapping = list(m_1)
				try:
					mapping[n] = m_size + 1
					p = p_1
				except:
					mapping = ()
					p = -999999999999999999999999999999999999
			else:
				mapping = list(m_3)
				try:
					mapping[n] = m
					p = p_3
				except:
					mapping = ()
					p = -999999999999999999999999999999999999
			mapping = tuple(mapping)
			memo[n, m, delta1, delta2] = (mapping, p)
		return memo[n, m, delta1, delta2]
	x = get_highest_prob(nn, mm, ddelta1, ddelta2, mmapping, aa, bb, cc, dd, mm_size)
	return x

def get_frequencies(l):
	d = {}
	for i in l:
		try: d[i] += 1
		except: d[i] = 1
	return [(a, b) for (a, b) in d.items()]

def gen_auxiliary(dist, p):
	aux_dist = [(uniform(x * (100 - p), x * (100 + p)), f"ciphertext{i}") for i, x in enumerate(dist)]
	tot = 0
	for i in aux_dist:
		tot += i[0]
	for i, val in enumerate(aux_dist):
		aux_dist[i] = (val[0]/tot, val[1])
	# aux_dist = [x / tot for x in aux_dist]
	aux_dist.sort()

	return aux_dist

def makecd(col0, col1, length):
	names_all = [f"ciphertext{e}" for e in range(length)]
	names0 = [e[0] for e in col0]
	names1 = [e[0] for e in col1]
	col0.sort()
	col1.sort()

	col0_all = []
	col1_all = []
	counter0 = 0
	counter1 = 0
	for i, e in enumerate(names_all):
		if e in names0:
			col0_all.append(col0[i-counter0][1])
		else:
			counter0 += 1
			col0_all.append(0)
		if e in names1:
			col1_all.append(col1[i-counter1][1])
		else:
			counter1 += 1
			col1_all.append(0)

	c = []
	d = []
	c0 = 0
	d0 = 0
	mapped_to_d0 = []
	mapped_to_c0 = []
	c_names = []
	d_names = []

	for i, val in enumerate(col0_all):
		if col1_all[i] == 0 or val == 0: # not in join
			if col1_all[i] != 0:
				d0 += col1_all[i]
				mapped_to_d0.append(names_all[i])
			if val != 0:
				c0 += val
				mapped_to_c0.append(names_all[i])
			continue
		# is in join
		c.append((val, names_all[i]))
		d.append((col1_all[i], names_all[i]))

	c.sort()
	d.sort()

	for i, val in enumerate(c):
		c_names.append(val[1])
		c[i] = val[0]


	for i, val in enumerate(d):
		d_names.append(val[1])
		d[i] = val[0]

	c.insert(0, c0)
	d.insert(0, d0)

	return c, d, c_names, d_names, col0_all, col1_all, names_all

def sort_by_indexes(a, b, ttype):
	a_indexes = [i[1] for i in a]
	b_indexes = [i[1] for i in b]
	if ttype == 1: # sort b based on a
		newb = []
		a.sort()
		for i, val in enumerate(a):
			new_index = b_indexes.index(val[1])
			newb.append(b[new_index])
		return a, newb
	if ttype == 2:
		newa = []
		b.sort()
		for i, val in enumerate(b):
			new_index = a_indexes.index(val[1])
			newa.append(a[new_index])
		return newa, b

def sort_by_sum(a, b):
	# (prob, ciphertextnum)
	a_indexes = [i[1] for i in a]
	b_indexes = [i[1] for i in b]
	# print(a_indexes)
	sums = [(a[a_indexes.index(f"{i}")][0]+b[b_indexes.index(f"{i}")][0], f"{i}") for i in a_indexes]
	sums.sort()
	newa, newb = [], []
	for i in sums:
		newa.append(a[a_indexes.index(i[1])])
		newb.append(b[b_indexes.index(i[1])])
	return newa, newb

def DP1(A, B, C, D, ciphs):
	c, d, c_names, d_names, col0, col1, col_names = makecd(C, D, ciphs)
	a = [i[0] for i in A]
	b = [i[0] for i in B]
	g0 = si_dp(len(a)-1, len(c)-1, 0, (-1 for i in a), a, c)
	mapping0 = g0[0] # mapping [0,0,1,2,3] eg
	c0 = 0
	d0 = 0
	unmapped_a = []
	unmapped_b = []

	for index, val in enumerate(mapping0):
		if val != 0:
			continue
		c0 += col0[index]
		d0 += col1[index]
		try: unmapped_a.append(int(round(a[index], 5) * (10 ** 5)))
		except: pass
		try: unmapped_b.append(int(round(b[index], 5) * (10 ** 5)))
		except: pass

	astring = ','.join(str(e) for e in unmapped_a)
	bstring = ','.join(str(e) for e in unmapped_b)
	subprocess.call(["./POAA.exe", astring, bstring, str(c0), str(d0)])
	ansfile = open("di_ans.txt", 'r')
	mapc0 = 0
	mapd0 = 0

	uunknown_col0 = []
	uunknown_col1 = []
	for line in ansfile:
		vals = line.split(",")
		if int(vals[0]) != 0:
			mapc0 += int(vals[0])/ (10 ** 5) 
			uunknown_col0.append(int(vals[0]))
		else:
			mapd0 += int(vals[1])/ (10 ** 5) 
			uunknown_col1.append(int(vals[1]))

	p0 = 0.0

	for index, val in enumerate(mapping0):
		if val == 0:
			continue
		try: p0 += c[val] * math.log(a[index], 10)
		except: pass
		try: p0 += d[val] * math.log(b[index], 10) 
		except: pass

	try: p0 += c0 * math.log(mapc0, 10)
	except: pass
	try: p0 += d0 * math.log(mapd0, 10)
	except: pass

	g1 = si_dp(len(b)-1, len(d)-1, 0, (-1 for i in b), b, d)
	mapping1 = g1[0] # mapping [0,0,1,2,3] eg
	c1 = 0
	d1 = 0
	unmapped_a = []
	unmapped_b = []
	for index, val in enumerate(mapping1):
		if val != 0:
			continue
		c1 += col0[index]
		d1 += col1[index]
		try: unmapped_a.append(int(round(a[index], 5) * (10 ** 5)))
		except: pass
		try: unmapped_b.append(int(round(b[index], 5) * (10 ** 5)))
		except: pass

	astring = ','.join(str(e) for e in unmapped_a)
	bstring = ','.join(str(e) for e in unmapped_b)
	subprocess.call(["./POAA.exe", astring, bstring, str(c1), str(d1)])
	ansfile = open("di_ans.txt", 'r')
	mapc1 = 0
	mapd1 = 0

	unknown_col0 = []
	unknown_col1 = []
	for line in ansfile:
		vals = line.split(",")
		if int(vals[0]) != 0:
			mapc1 += int(vals[0])/ (10 ** 5) 
			unknown_col0.append(int(vals[0]))
		else:
			mapd1 += int(vals[1])/ (10 ** 5) 
			unknown_col1.append(int(vals[1]))

	p1 = 0.0

	for index, val in enumerate(mapping1):
		if val == 0:
			continue
		try: p1 += c[val] * math.log(a[index], 10)
		except: pass
		try: p1 += d[val] * math.log(b[index], 10)
		except: pass

	try: p1 += c1 * math.log(mapc1)
	except: pass
	try: p1 += d1 * math.log(mapd1)
	except: pass

	final_mapping = []
	corr_names = []
	corr_mapping = []

	if p0 > p1:
		for i, x in enumerate(mapping0):
			if x == 0:
				continue
			final_mapping.append(i)
		final_mapping.append(uunknown_col0)
		final_mapping.append(uunknown_col1)
		corr_names = tuple(c_names)
		corr_mapping = tuple(mapping0)
		aux_names = [i[1] for i in B]

	else:
		for i, x in enumerate(mapping1):
			if x == 0:
				continue
			final_mapping.append(i)
		final_mapping.append(unknown_col0)
		final_mapping.append(unknown_col1)
		corr_names = tuple(d_names)
		corr_mapping = tuple(mapping1)
		aux_names = [i[1] for i in D]

	tot_vals = 0
	tot_rows = 0
	corr_vals = 0
	corr_rows = 0

	for index, val in enumerate(col0):
		if val == 0 or col1[index] == 0:
			continue 
		# joined
		tot_vals += 1
		tot_rows += max(val, col1[index])
		name = col_names[index] 
		ind = corr_mapping.index(corr_names.index(name)+1)
		try:
			if aux_names[final_mapping[final_mapping.index(ind)]] == name:
				corr_vals += 1
				corr_rows += max(val, col1[index])
		except:
			continue

	print(f"{corr_vals/tot_vals} {corr_rows/tot_rows}", end=" ")

def DP2A(A, B, C, D, ciphs):
	a, b = sort_by_indexes(A, B, 1)
	c, d, c_names, d_names, col0, col1, col_names = makecd(C, D, ciphs)

	sub_a = [i[0] for i in a]
	sub_b = [i[0] for i in b]

	g0 = heur_dp(len(a)-1, len(c)-1, 0, 0, (-1 for i in a), sub_a, sub_b, c, d, len(c)-1)
	mapping0 = g0[0]
	p0 = g0[1]
	
	a, b = sort_by_indexes(A, B, 2)
	sub_a = [i[0] for i in a]
	sub_b = [i[0] for i in b]
	g1 = heur_dp(len(a)-1, len(c)-1, 0, 0, (-1 for i in a), sub_a, sub_b, c, d, len(c)-1)
	mapping1 = g1[0] # mapping [0,0,1,2,3] eg
	p1 = g1[1]

	final_mapping = []
	corr_names = []
	corr_mapping = []

	if p0 > p1:
		final_mapping = mapping0
		corr_names = c_names
		corr_index = [i[1] for i in A]
		fin_rows = c
	else:
		final_mapping = mapping1
		corr_names = d_names
		corr_index = [i[1] for i in B]
		fin_rows = d

	tot_vals = 0
	tot_rows = 0
	corr_vals = 0
	corr_rows = 0

	mapping_arr = final_mapping
	with_unknown = 0
	with_known = 0
	no_vals = 0
	for i, mapval in enumerate(mapping_arr):
		if mapval >= len(c): continue
		if corr_names[mapval-1] == corr_index[i]:
			with_known += fin_rows[mapval]
			no_vals += 1
	print(f"{no_vals/(len(fin_rows)-1)} {with_known/sum(fin_rows[1:])}", end=" ")

def DP2B(A, B, C, D, ciphs):
	a, b = sort_by_sum(A, B)
	c, d, c_names, d_names, col0, col1, col_names = makecd(C, D, ciphs)

	sub_a = [i[0] for i in a]
	sub_b = [i[0] for i in b]

	g0 = heur_dp(len(a)-1, len(c)-1, 0, 0, (-1 for i in a), sub_a, sub_b, c, d, len(c)-1)
	mapping0 = g0[0] # mapping [0,0,1,2,3] eg
	p0 = g0[1]
	
	tot_vals = 0
	tot_rows = 0
	corr_vals = 0
	corr_rows = 0

	with_unknown = 0
	with_known = 0
	no_vals = 0
	
	for i, mapval in enumerate(mapping0):
		if mapval >= len(c): continue
		if c_names[mapval-1] == a[i][1]:
			with_known += c[mapval]
			no_vals += 1
		if d_names[mapval-1] == b[i][1]:
			with_known += d[mapval]
			no_vals += 1
	print(f"{no_vals/(len(c)-1)/2} {with_known/(sum(c[1:])+sum(d[1:]))}")

def run_all(error):
	rows = [10000, 1000000]
	dists = ["lin-lin", "lin-slin", "lin-invlin", "lin-randlin", "lin-zipf", "zipf-zipf", "zipf-randzipf", "zipf-invzipf"]
	ciphs_s, ciphs_l = [10, 50, 100], [10, 50, 100, 200, 500]
	res = []

	for row in rows:
		for dist in dists:
			prefix = f"./data_v2/data_v2/DI/DI_{row}_{dist}/DI_{row}_{dist}/"
			for ciphs in ciphs_s if row == 10000 else ciphs_l:
				print(f"{row} {ciphs} {dist}")
				totv, totr, num = 0, 0, 0
				for run in range(10):
					file0_path = f"DI_{row}_{ciphs}_{dist}{run}_col0.csv"
					file1_path = f"DI_{row}_{ciphs}_{dist}{run}_col1.csv"

					with open(prefix + file0_path, "r") as f: data0 = f.read().split('\n')[:-1]
					with open(prefix + file1_path, "r") as f: data1 = f.read().split('\n')[:-1]

					dist0, dist1 = data0[0][15:-1], data1[0][15:-1]  # Remove "distribution:[" and "]"
					dist0, dist1 = [float(i) for i in dist0.split(", ")], [float(i) for i in dist1.split(", ")]
					col0, col1 = data0[2:], data1[2:]

					C, D = get_frequencies(col0), get_frequencies(col1)
					A, B = gen_auxiliary(dist0, error), gen_auxiliary(dist1, error)

					C.sort(key=sort_by_second)
					D.sort(key=sort_by_second)

					while C[0][0] == 0:
						A.pop(0)
						C.pop(0)
					while D[0][0] == 0:
						B.pop(0)
						D.pop(0)

					DP1(A, B, C, D, ciphs)
					DP2A(A, B, C, D, ciphs)
					DP2B(A, B, C, D, ciphs)

if __name__ == "__main__":
	print("-----------5----------")
	run_all(5)
	print("-----------10----------")
	run_all(10)
	print("-----------20----------")
	run_all(20)