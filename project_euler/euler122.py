from pprint import pprint

def solution(n):
	memo = {}
	vals = {}
	for i in range(1, n + 1):
		if i == 1:
			memo[i] = 0
		else:
			pass
		if i in vals:
			vals[i].append(i)
		else:
			vals[i] = [i]
		vals[i] = sorted(list(set(vals[i])))
		for val in vals[i]:
			if val + i in memo:
				if memo[i] + 1 < memo[val + i]:
					memo[val + i] = memo[i] + 1
					vals[val + i] = vals[i] + [val + i]
				else:
					pass
			else:
				memo[val + i] = memo[i] + 1
				vals[val + i] = vals[i] + [val + i]
	ret = 0
	for i in range(1, n + 1):
		ret += memo[i]
	return ret

print(solution(200))