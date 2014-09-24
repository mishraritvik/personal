# given a user object and location, find list of ordered posts

class quad_tree(object):
	def __init__(self, bl, ur, points, bucket_size):
		self.world_size = world_size
		self.bucket_size = bucket_size
		self.bl = bl
		self.ur = ur
		self.points = points
		self.children = []

	def add_post(self, x, y):
		if not self.children:
			if len(self.points) < self.bucket_size - 1:
				self.points.append([x, y])
			else:
				nw_child = quad_tree([], [], [], self.bucket_size)
				ne_child = quad_tree([], [], [], self.bucket_size)
				sw_child = quad_tree([], [], [], self.bucket_size)
				se_child = quad_tree([], [], [], self.bucket_size)
		else:
			# do add_post for child that this one should be in

class user(object):
	def __init__(self, age, gender):
		self.age = age
		self.gender = gender

	def find_posts(self, tree, x, y):
