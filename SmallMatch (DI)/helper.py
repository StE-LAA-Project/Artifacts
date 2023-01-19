import os, sys
from math import log
from random import randint


def findpath(input_list, c, d, max_sum):
    N = len(input_list)
    curr_grid = [[-1, -1] for _ in range(
        max_sum + 1)]  # curr_grid[x] represents largest value of (x,-) and its associated path (e.g. ABAA -> 0100)

    # Start with first (a,b)
    first = input_list[0]
    curr_grid[first[0]] = [0, 0]  # Pick A
    curr_grid[0] = [first[1], 1]  # Pick B

    for i in range(1, len(input_list)):
        a, b = input_list[i]
        for j in range(max_sum, -1, -1):
            if curr_grid[j][0] >= 0:  # Valid (j,-)
                curr_path = curr_grid[j][1]
                if curr_grid[j][0] > curr_grid[j + a][0]:
                    curr_grid[j + a][0] = curr_grid[j][0]
                    curr_grid[j + a][1] = curr_path * 2
                curr_grid[j][0] = curr_grid[j][0] + b
                curr_grid[j][1] = curr_path * 2 + 1

    best_res = 0
    best_i = 0
    for i in range(1, max_sum):
        if curr_grid[i][0] <= 0: continue
        res = c * log(i) + d * log(curr_grid[i][0])
        if res > best_res:
            best_res = res
            best_i = i

    return best_res, curr_grid[best_i][1]


def findpath_slow(input_list, c, d, max_sum):
    N = len(input_list)
    curr_grid = [[-1, -1] for _ in range(
        max_sum + 1)]  # curr_grid[x] represents largest value of (x,-) and its associated path (e.g. ABAA -> 0100)

    # Start with first (a,b)
    first = input_list[0]
    curr_grid[first[0]] = [0, 0]  # Pick A
    curr_grid[0] = [first[1], 1]  # Pick B

    for i in range(1, len(input_list)):
        a, b = input_list[i]
        new_grid = [[-1, -1] for _ in range(max_sum + 1)]
        for j in range(0, max_sum + 1):
            if curr_grid[j][0] != -1:
                if curr_grid[j][0] > new_grid[j + a][0]:
                    new_grid[j + a][0] = curr_grid[j][0]
                    new_grid[j + a][1] = curr_grid[j][1] * 2
                if curr_grid[j][0] + b > new_grid[j][0]:
                    new_grid[j][0] = curr_grid[j][0] + b
                    new_grid[j][1] = curr_grid[j][1] * 2 + 1
        curr_grid = new_grid

    best_res = 0
    best_i = 0
    for i in range(1, max_sum):
        if curr_grid[i][0] <= 0: continue
        res = c * log(i) + d * log(curr_grid[i][0])
        if res > best_res:
            best_res = res
            best_i = i

    return best_res, curr_grid[best_i][1]


def gen_vectors(N, maxA, maxB):
    V = [[0, 0] for _ in range(N)]
    for i in range(maxA):
        V[randint(0, N - 1)][0] += 1
    for i in range(maxB):
        V[randint(0, N - 1)][1] += 1
    return V


if __name__ == "__main__":
    max_sum = 100000
    # input_list = [(5,4),(3,2),(2,1),(0,3),(5,4),(3,2),(2,1),(0,3)]
    input_list = gen_vectors(500, max_sum, max_sum)
    N = len(input_list)
    c, d = 3, 4

    print("Finding path")
    best_val, best_path = findpath(input_list, c, d, max_sum)
    x = bin(best_path)[2:]
    path = (N - len(x)) * '0' + x
    print(best_val, path)

# 18 seconds, 30MB for max_sum = 100000
# 3 minutes, 220MB for max_sum = 1000000
