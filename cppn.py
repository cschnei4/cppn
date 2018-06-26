
class Connection:

	def __init__(self, i_num, start_node, end_node, weight):
		self.i_num = i_num
		self.start_node = start_node
		self.end_node = end_node
		self.weight = weight

	def __repr__(self):
		return ';'.join([str(self.i_num), str(self.start_node), str(self.end_node), str(self.weight)])

class Node:

	def __init__(self, i_num, func, out_conns=None, layer=0):
		self.i_num = i_num
		self.activate = func
		if out_conns == None:
			self.out_conns = []
		self.out_conns = out_conns
		self.layer = layer

	def __repr__(self):
		return ';'.join([str(self.i_num), self.activate.__name__, str([conn.i_num for conn in self.out_conns]), str(self.layer)])

class CPPN:

	def __init__(self, nodes=nodes, conns=conns):
		self.nodes = nodes
		self.conns = conns

	def get_node(self, num):
		for node in self.nodes:
			if node.i_num == num:
				return node

	def get_conn(self, num):
		for conn in self.conns:
			if conn.i_num == num:
				return conn

	def update_conns(self):
		for conn in self.conns:
			start = self.get_node(conn.start_node)

	def update(self):
		for conn in self.conns:
			start = self.get_node(conn.start_node)
			if 
