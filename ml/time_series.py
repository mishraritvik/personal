from stat_funcs import *
from pprint import pprint
import csv
import json
import random
import math

gap = 1
lam = 1
ind = 1
memoizer = {}

Zerror = .002

LETTERS = {0 : 'a', 1 : 'b', 2 : 'c', 3 : 'd', 4 : 'e', 5 : 'f', 6 : 'g', 7 : 'h', 8 : 'i', 9 : 'j', 10 : 'k'}
NUMBERS = {'a' : 0, 'b' : 1, 'c' : 2, 'd' : 3, 'e' : 4, 'f' : 5, 'g' : 6, 'h' : 7, 'i' : 8, 'j' : 9, 'k' : 10}

#p values for z scores in Z
P = []
f = open('pvals.txt')
for line in f:
	P += [int(i) for i in line.split(' ')]
f.close()

Z = range(-349, 350)
for i in range(len(Z)):
	Z[i] = float(Z[i]) / 100.0

#returns true if difference between val1 and val2 is less than error
def closeEnough(val1, val2, error):
	if abs(val1 - val2) <= error:
		return True
	return False

def time_dif(time1, time2):
	return time1 - time2

#given a lst, a value that is being searched for, and the error allowed, returns index of lst where val is located ([lst(numbers), number, number] -> int)
def binarySearch(lst, val, error):
	assert(val >= lst[0] - error)
	assert(val <= lst[len(lst) - 1] + error)
	midpoint = len(lst) / 2
	if closeEnough(lst[midpoint], val, error) or len(lst) == 1:
		return midpoint
	elif val > lst[midpoint]:
		return midpoint + binarySearch(lst[midpoint :], val, .02)
	else:
		return binarySearch(lst[: midpoint], val, error)

#creates z score borders for a SAX alphabet given the alphabet size (int -> lst(float))
def setAlphabet(alpha):
	borders = []
	gapSize = 1.0 / float(alpha)
	for i in range(alpha):
		nextp = gapSize * (i + 1)
		zindex = binarySearch(P, nextp, Zerror)
		borders.append(Z[zindex])
	return borders

#given a z score and the borders that result from setAlphabet, returns the letter ([float, lst(float)] -> int)
def alphabet(z, borders):
	length = len(borders)
	for i in range(length):
		if z < borders[i]:
			return i
	return length

#SAX compression, div length w and alphabet size a ([lst(numbers), int, int, ~/lst(float)] -> lst(numbers))
def SAX(seq, w, a, borders=None):
	left = False
	if borders == None:
		borders = setAlphabet(a)
	lenseq = len(seq) / w
	if len(seq) % w != 0:
		left = True
	seq = normalize(seq)
	comp = []
	for i in range(lenseq):
		comp.append(avg(seq[i * w : (i + 1) * w]))
	if left:
		comp.append(avg(seq[w * lenseq :]))
	for i in range(len(comp)):
		comp[i] = alphabet(comp[i], borders)
	return comp

#turns number compression to letters (lst(int) -> lst(char))
def compTOlet(lst):
	ret = ''
	for i in range(len(lst)):
		ret += LETTERS[lst[i]]
	return ret

#turns letter compression to numbers (lst(char) -> lst(int))
def letTOcomp(lst):
	ret = []
	for i in range(len(lst)):
		ret.append(NUMBERS[lst[i]])
	return ret

#use SAX compression and euclidian time series distance ([lst(number), lst(number), int, int] -> number)
def distance(seqA, seqB, w, a):
	compA = SAX(seqA, w, a)
	compB = SAX(seqB, w, a)
	for i in range(len(compA)):
		score += (compA[i] - compB[i]) ** 2
	return score

#returns distance for TWED calculation - must initialize lam
def dist(a, b):
	return abs(a[ind] - b[ind]) + lam * abs(time_dif(a[0], b[0]))

#runs TWED on two sequences ([lst(number), lst(number)] -> number)
def fullTWED(a, b):
	memoizer = {}
	return TWED(a, b, len(a) - 1, len(b) - 1)

#called by fullTWED, should not be called directly
#a: one sequence
#b: other sequence
#i: index for a
#j: index for b
def TWED(a, b, i, j):
	rep = i * 10 ** (math.log(i) + 1) + j
	if rep in memoizer:
		return memoizer[rep]
	if i == 0 and j == 0:
		ret = 0
	elif i == 0:
		ret = TWED(a, b, i, j - 1) + dist(b[j], b[j - 1]) + gap
	elif j == 0:
		ret = TWED(a, b, i - 1, j) + dist(a[i], a[i - 1]) + gap
	else:
		ret = min([TWED(a, b, i - 1, j - 1) + dist(a[i], b[j]), \
			TWED(a, b, i - 1, j) + dist(a[i], a[i - 1]) + gap, \
			TWED(a, b, i, j - 1) + dist(b[j], b[j - 1]) + gap])
	memoizer[rep] = ret
	return ret

#given list of sequences, framesize, length of compression frames, and alphabet size, runs BoPA ([lst(lst(anything)), int, int, int, ~/lst(float)] -> lst(string))
def BoPAm(lstofseqs, frame, w, a, borders=None):
	if borders == None:
		borders = setAlphabet(a)
	bags = {}
	for seq in lstofseqs:
		compression = SAX(seq, w, a, borders)
		for i in range(len(compression) - frame - 1):
			pattern = compression[i : i + frame]
			numpattern = 0
			for i in range(frame):
				numpattern += pattern[i] * 10 ** i
			if numpattern in bags:
				bags[numpattern] += 1
			else:
				bags[numpattern] = 1
	return bags

def BoPA(seq, frame, w, a, borders=None):
	if borders == None:
		borders = setAlphabet(a)
	bags = {}
	compression = SAX(seq, w, a, borders)
	for i in range(len(compression) - frame - 1):
		pattern = compression[i : i + frame]
		numpattern = 0
		for i in range(frame):
			numpattern += pattern[i] * 10 ** i
		if numpattern in bags:
			bags[numpattern] += 1
		else:
			bags[numpattern] = 1
	return bags

#returns euclidian sequence distance between two lists ([lst(number), lst(numbers)] -> number)
def euclidian(lst1, lst2):
	assert(len(lst1) == len(lst2))
	total = 0
	for i in range(len(lst1)):
		total += (lst1[i] - lst2[i]) ** 2
	return total

#given a matrix of data, returns the mahal distance for each row from the dataset as a whole
def mahal(data):
	#assume data is in the form that each row is a collection of observations
	ret = []
	X = numpy.array(data).T
	cov = numpy.cov(X)
	icov = numpy.linalg.inv(cov)
	mu = []
	for i in range(len(data[0])):
		arr = []
		for j in range(len(data)):
			arr.append(data[j][i])
		mu.append(avg(arr))
	npmu = numpy.array(mu)
	for row in data:
		row = numpy.array(row)
		ret.append(mahalanobis(row, npmu, icov))
	return ret

#the distance metric used by kmeans
def kmeansDist(A, B):
	return euclidean(A, B)

#k-means clustering algorithm that uses the distance metric specified by kmeansDist
def kmeans(data, k):
	changed = True
	dimension = len(data[0])
	dmin = []
	dmax = []
	centers = []
	clusters = []
	for i in range(k):
		clusters.append([])
	for i in range(dimension):
		minval = data[0][i]
		maxval = data[0][i]
		for j in range(len(data)):
			if data[j][i] < minval:
				minval = data[j][i]
			elif data[j][i] > maxval:
				maxval = data[j][i]
			else:
				pass
		dmin.append(minval)
		dmax.append(maxval)
	for i in range(k):
		newcenter = []
		for j in range(dimension):
			newcenter.append(rand(dmin[j], dmax[j]))
		centers.append(newcenter)
	assert(len(centers) == k)
	assert(len(centers[0]) == dimension)
	while changed:
		changed = False
		#assign all points to clusters
		clusters = []
		for i in range(len(centers)):
			clusters.append([])
		for point in data:
			distances = []
			for center in centers:
				distances.append(kmeansDist(point, center))
			index = mindex(distances)
			clusters[index].append(point)
		#redefine centers
		for i in range(len(centers)):
			newcenter = []
			for j in range(dimension):
				med = []
				for k in range(len(clusters[i])):
					med.append(clusters[i][k][j])
				newcenter.append(avg(med))
			if centers[i] != newcenter:
				changed = True
				centers[i] = newcenter
			else:
				pass
	return clusters

#clustering based on a non-euclidean distance metric that does not have a sense of "median"
def nonEuclideanCluster(data):
	pool = data
	clusters = []
	while len(pool) > 0:
		if len(pool) == 1:
			clusters.append(pool[0])
		else:
			alldists = []
			start = rand(0, len(pool) - 1)
			d = {}
			for i in range(len(pool)):
				if i != start:
					newdist = fullTWED(pool[start], pool[i])
					alldists[0].append(newdist)
					d[str(newdist)] = i
				else:
					pass
			clusters = kmeans(alldists[0], 2)
			newclust = [start]
			if avg(clusters[0]) < avg(clusters[1]):
				for val in clusters[0]:
					newclust.append(d[str(val)])
			else:
				for val in clusters[1]:
					newclust.append(d[str(val)])
			pool = []
			clustered = flatten(clusters)
			for i in range(len(data)):
				if i not in clustered:
					pool.append(data[i])
				else:
					pass
	return clusters