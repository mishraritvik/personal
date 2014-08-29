def factorial(n):
    if n <= 1:
        return n
    return n * factorial(n - 1)

def solution(n):
    r = (n-1) / 2
    p = [1] + [0] * r
    for k in range(n + 1):
        for i in range(r, 0, -1):
            p[i] += k * p[i - 1]
    return factorial(n + 1) / sum(p)

solution(15)