import math
import random
import numpy as np
import cv2

def SIG(x):
	return 1 / (1 + math.exp(-x))

def ABS(x):
	return abs(x)

def SIN(x):
	return math.sin(x)

def ID(x):
	return x

FUNCS = [SIG, ABS, SIN, ID]

class Connection:

	def __init__(self, i_num, start_node, end_node, weight=None, active=1):
		self.i_num = i_num
		self.start_node = start_node
		self.end_node = end_node
		if weight == None:
			self.weight = random.random() * 2 - 1
		else:
			self.weight = weight
		self.active = active

	def apply_weight(self, num):
		if self.active:
			return self.weight * num
		return 0

	def __repr__(self):
		return ';'.join([str(self.i_num), str(self.start_node), str(self.end_node), str(self.weight), str(self.active)])

class Node:

	def __init__(self, i_num, func=None, out_conns=None, layer=0):
		self.i_num = i_num
		if func == None:
			self.func = FUNCS[random.randint(0, len(FUNCS) - 1)]
		else:
			self.func = func
		if out_conns == None:
			self.out_conns = []
		else:
			self.out_conns = out_conns
		self.layer = layer
		self.total = 0

	def receive(self, num):
		self.total += num

	def activate(self):
		to_ret = self.func(self.total)
		self.total = 0
		return to_ret

	def __repr__(self):
		return ';'.join([str(self.i_num), self.func.__name__, str(self.layer)])

class InputNode(Node):

	def __init__(self, i_num, func=ID, out_conns=None, layer=1):
		Node.__init__(self, i_num, func=func, out_conns=out_conns, layer=layer)

class OutputNode(Node):

	def __init__(self, i_num, func=SIG, out_conns=None, layer=1):
		Node.__init__(self, i_num, func=func, out_conns=out_conns, layer=layer)

class CPPN:

	def __init__(self, in_nodes, out_nodes, conns=None, hidden_nodes=None):
		self.in_nodes = in_nodes
		self.out_nodes = out_nodes
		if hidden_nodes == None:
			self.hidden_nodes = []
		else:
			self.hidden_nodes = hidden_nodes
		self.nodes = self.in_nodes + self.out_nodes + self.hidden_nodes
		self.conns = conns
		self.update()

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
			if conn not in start.out_conns:
				start.out_conns.append(conn)

	def follow_node(self, node):
		for conn in node.out_conns:
			new_node = self.get_node(conn.end_node)
			if new_node.layer <= node.layer:
				new_node.layer = node.layer + 1
			self.follow_node(new_node)

	def get_layer(self, layer):
		return [node for node in self.nodes if node.layer == layer]

	def update_layers(self):
		for node in self.nodes:
			node.layer = 0
		for node in self.in_nodes:
			node.layer = 1
			self.follow_node(node)
		out_layer = max([node.layer for node in self.out_nodes])
		for node in self.out_nodes:
			node.layer = out_layer
		self.layers = [self.get_layer(layer) for layer in range(2, out_layer)]

	def update(self):
		self.update_conns()
		self.update_layers()

	def add_conn(self, conn):
		self.conns.append(conn)
		self.get_node(conn.start_node).out_conns.append(conn)
		self.update()

	def add_node(self, before, after, node_num, conn_num):
		before_node = self.get_node(before)
		for conn in before_node.out_conns:
			if conn.end_node == after:
				conn.active = False
		before_conn = Connection(conn_num, before, node_num)
		after_conn = Connection(conn_num + 1, node_num, after)
		new_node = Node(node_num, out_conns=[after_conn])
		self.conns.extend([before_conn, after_conn])
		self.hidden_nodes.append(new_node)
		self.nodes.append(new_node)
		self.update()

	def activate_node(self, node):
		signal = node.activate()
		for conn in node.out_conns:
			self.get_node(conn.end_node).receive(conn.apply_weight(signal))

	def get_point(self, x, y, scale):
		self.in_nodes[0].receive(x)
		self.in_nodes[1].receive(y)
		self.activate_node(self.in_nodes[0])
		self.activate_node(self.in_nodes[1])
		for layer in self.layers:
			for node in layer:
				self.activate_node(node)
		return tuple([node.activate() * scale for node in self.out_nodes])

	def __repr__(self):
		node_str = ""
		for node in self.nodes:
			node_str += str(node) + ":"
		conn_str = ""
		for conn in self.conns:
			conn_str += str(conn) + ":"
		return node_str[:-1] + "|" + conn_str[:-1]
		
def build_basic_cppn():
	in_nodes = [InputNode(i) for i in [1, 2]]
	out_nodes = [OutputNode(i) for i in [3, 4, 5]]
	c13 = Connection(1, 1, 3)
	c14 = Connection(2, 1, 4)
	c15 = Connection(3, 1, 5)

	c23 = Connection(4, 2, 3)
	c24 = Connection(5, 2, 4)
	c25 = Connection(6, 2, 5)

	conns = [c13, c14, c15, c23, c24, c25]

	return CPPN(in_nodes, out_nodes, conns=conns)

def make_image(size_x, size_y, net, filename):
	x_r = [(i * 2 / (size_x - 1)) - 1 for i in range(size_x)]
	y_r = [(i * 2 / (size_y - 1)) - 1 for i in range(size_y)]
	img = np.array([[net.get_point(x, y, 255) for x in x_r] for y in y_r])
	cv2.imwrite(filename, img)
	return img

def build_cppn_from_str(string):
	strs = string.split('|')
	nodes = strs[0].split(':')
	conns = strs[1].split(':')
	ns = []
	for node in nodes:
		node_parts = node.split(';')
		ns.append(Node(eval(node_parts[0]), func=eval(node_parts[1]), layer=eval(node_parts[2])))
	ins = ns[:2]
	outs = ns[2:5]
	hids = ns[5:]
	cs = []
	for conn in conns:
		conn_parts = conn.split(';')
		cs.append(Connection(eval(conn_parts[0]), eval(conn_parts[1]), eval(conn_parts[2]), weight=eval(conn_parts[3]), active=eval(conn_parts[4])))
	return CPPN(ins, outs, conns=cs, hidden_nodes=hids)
