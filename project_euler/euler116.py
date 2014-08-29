# generally, given the number of tiles and size of each cover
def num_ways(tile_size, num_tiles):
    ways = [1] * tile_size + [0] * (num_tiles - tile_size + 1)
    for j in range(tile_size, num_tiles + 1):
        ways[j] += ways[j - 1] + ways[j - tile_size]
    return ways[num_tiles] - 1

def solution(sizes, num_tiles):
	return sum([num_ways(size, num_tiles) for size in sizes])

solution([2, 3, 4], 50)