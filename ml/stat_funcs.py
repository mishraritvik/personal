import math
import random
import pickle

#this file does not do anything, but all the functions are used in many places

#pickles given object into given file
def pickleObj(obj, filename):
    f = open(filename, 'w')
    pickle.dump(obj, f)
    f.close()

#returns object pickled in given file
def unpickleObj(filename):
    f = open(filename, 'r')
    ret = pickle.load(f)
    f.close()
    return ret

#returns true if all characters in string are the same, false otherwise
def allsame(string):
    for i in range(len(string) - 1):
        if string[i] != string[i + 1]:
            return False
    return True

#returns true if input is a number, false otherwise
def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

#returns a random number between a and b
def rand(a, b):
    return a + (b - a) * random.random()

#returns average of lst
def avg(lst):
    if len(lst) == 0:
        return 0
    total = 0
    for i in range(len(lst)):
        total += lst[i]
    return float(total) / float(len(lst)) 

#returns standard deviation of lst
def std(lst):
    if len(lst) == 0:
        return 0
    average = avg(lst)
    squared_devs = []
    total = 0
    for val in lst:
        squared_devs.append((val - average) ** 2)
    avg_squared_devs = avg(squared_devs)
    return math.sqrt(avg_squared_devs)

#returns max of lst
def max(lst):
    maxval = lst[0]
    for i in range(1, len(lst)):
        if lst[i] > maxval:
            maxval = lst[i]
    return maxval

#returns min of lst
def min(lst):
    minval = lst[0]
    for i in range(1, len(lst)):
        if lst[i] < minval:
            minval = lst[i]
    return minval

#returns index of min in lst
def mindex(lst):
    minval = lst[0]
    index = 0
    for i in range(1, len(lst)):
        if lst[i] < minval:
            minval = lst[i]
            index = i
    return index

#returns the index of max in lst
def maxdex(lst):
    maxval = lst[0]
    index = 0
    for i in range(1, len(lst)):
        if lst[i] > maxval:
            maxval = lst[i]
            index = i
    return index

#returns the indices of the n largest values in lst (in no order)
def nMax(lst, n):
    if len(lst) <= n:
        return range(len(lst))
    ret = []
    for i in range(n):
        nextval = maxdex(lst)
        ret.append(nextval)
        del lst[nextval]
    return ret

#flattens a lstoflsts into a lst
def flatten(lstoflsts):
    ret = []
    for lst in lstoflsts:
        for val in lst:
            ret.append(val)
    return ret

#appends each element of a small lst to a big lst
def appendeach(biglst, smalllst):
    biglst += smalllst

#normalizes a lst
def normalize(lst):
    stddev = std(lst)
    average = avg(lst)
    ret = []
    if stddev == 0:
        for i in range(len(lst)):
            ret.append(0)
    else:
        for val in lst:
            ret.append((val - average) / stddev)
    return ret

#returns the mode of a lst
def mode(lst):
    lst = sorted(lst)
    current = 1
    currentnum = lst[0]
    highest = 0
    num = 0
    for i in range(2, len(lst)):
        if lst[i] == currentnum:
            current += 1
        else:
            if current > highest:
                num = currentnum
                highest = current
            currentnum = lst[i]
            current = 1
    return num

#returns the reverse of a lst
def reverse(lst):
    ret = []
    for i in range(len(lst) - 1, -1, -1):
        ret.append(lst[i])
    return ret

#selects a column from a lst
def selectColumn(lstoflsts, col):
    ret = []
    for lst in lstoflsts:
        ret.append(lst[col])
    return ret

#selects a subcolumn from a lst
def selectSubColumn(lstoflstoflsts, col):
    ret = []
    for lstoflsts in lstoflstoflsts:
        newsub = []
        for lst in lstoflsts:
            newsub.append(lst[col])
        ret.append(newsub)

#normalizes lst (deltas) in sections based on input days
def normalizeInSections(deltas, dt, days):
    if len(deltas) == 0:
        return deltas
    ret = []
    beginning = 0
    current = 0
    minutes = days * 24 * 60
    for i in range(len(deltas)):
        if dt[i] < 1:
            continue
        current += dt[i]
        if (current >= minutes) or (i == len(deltas) - 1):
            current = 0
            toappend = normalize(normalize(deltas[beginning : i + 1]))
            for val in toappend:
                ret.append(val)
            beginning = i + 1
        else:
            pass
    return ret
