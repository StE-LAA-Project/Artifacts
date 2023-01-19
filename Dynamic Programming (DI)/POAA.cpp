//***************************************************************
// This file solves the following problem:
// Given a list V of pairs (a_i, b_i) and two numbers d and e,
// where each a_i and b_i are nonnegative integers and d and
// e are nonnegative, choose c_i, where each c_i is either
// (1, 0) or (0, 1) to form a tuple:
//
//   (x, y) = sum[c_i ** (a_i, b_i)]
//
// such that d log x + e log y is maximized among all possible
// choices of c_i.
//
// conMaxProb gives the maximum value of d log x + e log y along
// with a set of c_i that achieves it. In particular, this
// function has a time complexity of O(NC), where N is the size
// of the list and C is the sum of the a_i's, and a memory
// complexity of O(C).
//
// This algorithm can logically be divided into two parts:
//
// Firstly, we use a knapsack-style DP to compute all maximal
// pairs among choices of c_i (maximal pairs are pairs such
// that no other nonequal tuple is strictly greater than it in
// both coordinates) and then iterate over all such pairs to
// determine (x, y).
//
// The DP to find maximal pairs is implemented in getMaxPairs.
//
// After getting (x, y), we will construct the c_i's in
// the function conMaxPair. conMaxPair utilizes a divide and
// conquer strategy: We divide V into two lists of roughly equal
// sizes, V1 and V2. We then construct the maximal pairs for
// each list using getMaxPairs, find a maximal pair from each
// result, recursively call conMaxPair on each sublist, before
// combining the results.
//
// The recurrence for the time complexity of conMaxPair is:
//
// T(N, C) = O(NC + N) + T(N/2, C1) + T(N/2, C2), where C1 + C2 = C.
//***************************************************************

#include <bits/stdc++.h>

using namespace std;

int getMaxA(vector<pair<int, int>> const& V){
	int maxA = 0;
	for (auto [a, _] : V){
		maxA += a;
	}	
	return maxA;
}

// V is a list of pairs of nonnegative integers
// returns a vector M
// M[i] is the largest value - of tuples <i, -> as described in the introduction
// M[i] is -1 if not applicable
vector<int> getMaxPairs(vector<pair<int, int>> const& V){
	int N = V.size();
	int maxA = getMaxA(V);
	
	vector<int> M(maxA + 1, -1); // M[i] is the current maximal pair of form (i, -)
	M[0] = 0;
	
	// At the end of each iteration (the i-loop), M[x] is the maximal pair
	// of form (x, -) resulting from the partial sum of the first (i+1) elements
	for (int i = 0; i < N; i++){
		for (int j = maxA; j >= 0; j--) if (M[j] >= 0){
			auto [a, b] = V[i];
			M[j + a] = max(M[j + a], M[j]);
			M[j] += b;
		}
	}
	
	return M;
}

// returns the pair with maximum d * log x + e * log y
pair<int, int> getMaxPair(vector<pair<int, int>> const& V, int c, int d){
	double maxi = 0;
	pair<int, int> ans = {-1, -1};
	vector<int> M = getMaxPairs(V);
	for (int i = 1; i < M.size(); i++){
		if (M[i] <= 0) continue;
		double tmp = c * log(i) + d * log(M[i]);
		if (tmp > maxi){
			maxi = tmp;
			ans = {i, M[i]};
		}
	}
	return ans;
}

// Given a maximal pair "sol", constructs it as a sum of c_i ** V[i]
// Time Complexity: O(NC + N lg N)
// Space Complexity: O(N + C)
vector<bool> conMaxPair(vector<pair<int, int>> const& V, pair<int, int> sol){
	int n = V.size();
	if (n == 1){
		if (sol.first == 0){
			// assert(sol.second == V[0].second);
			return {1};
		} else{
			// assert (sol.first == V[0].first);
			return {0};
		}
	}
	int halfN = n / 2;
	auto const V1 = vector<pair<int, int>>(V.begin(), V.begin() + halfN);
	auto const V2 = vector<pair<int, int>>(V.begin() + halfN, V.begin() + n);
	
	vector<int> M1 = getMaxPairs(V1), M2 = getMaxPairs(V2);
	pair<int, int> sol1 = {-1, -1}, sol2 = {-1, -1};
	for (int i = 0; i < M1.size(); i++){
		int j = sol.first - i;
		if ((j >= 0) && (j < M2.size())){
			if (M1[i] + M2[j] == sol.second){
				sol1 = {i, M1[i]}, sol2 = {j, M2[j]};
				break;
			}
		}
	}
	// assert(sol1 != make_pair(-1, -1));
	
	vector<bool> ret1 = conMaxPair(V1, sol1), ret2 = conMaxPair(V2, sol2);
	ret1.insert(ret1.end(), ret2.begin(), ret2.end());
	return ret1;
	
}

// Time Complexity: O(NC + N lg N)
// Space Complexity: O(N + C)

pair<double, vector<bool>> conMaxProb(vector<pair<int, int>> const& V, int c, int d){
	pair<int, int> p = getMaxPair(V, c, d);
	double ans = c * log(p.first) + d * log(p.second);
	return {ans, conMaxPair(V, p)};
}

int main(int argc, char **argv){
	string a = argv[1];
	string b = argv[2];
	vector<int>aarr;
	vector<int>barr;

	size_t pos = 0;
	string token;
	while ((pos = a.find(',')) != std::string::npos) {
	    token = a.substr(0, pos);
	    aarr.push_back(stoi(token));
	    a.erase(0, pos + 1);
	} aarr.push_back(stoi(a));
	// std::cout << s << std::endl;

	// size_t pos = 0;
	// string token;
	while ((pos = b.find(',')) != std::string::npos) {
	    token = b.substr(0, pos);
	    barr.push_back(stoi(token));
	    b.erase(0, pos + 1);
	} barr.push_back(stoi(b));

	vector<pair<int, int> > V;
	for (int i=0; i<aarr.size(); i++) {
		V.push_back(make_pair(aarr[i], barr[i]));
	}

	// vector<pair<int, int>> V = {{1, 4}, {2, 3}, {3, 2}, {4, 1}};
	auto ans = conMaxProb(V, stoi(argv[3]), stoi(argv[4]));

	ofstream myfile;
	myfile.open("di_ans.txt");
	
	// cout << ans.first << endl;
	auto& A = ans.second;
	for (int i = 0; i < V.size(); i++){
		if (A[i] == 0) myfile << V[i].first << ",0" << endl;
		else myfile << "0," << V[i].second << endl;
	}
}
