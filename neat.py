import random
import numpy as np
from label_image import classify
import cppn
from subprocess import call
import os

class Population:

	def __init__(self, size, goal):
		self.size = size
		self.goal = goal
		self.generation = 1
		self.generate_pop()
		self.conn_num = 10
		self.node_num = 7

	def generate_pop(self):
		self.population = {}
		for i in range(1, self.size + 1):
			self.population["population/" + str(self.generation) + "_" + str(i) + ".png"] = cppn.build_radial_cppn()

	def draw_population(self):
		for indiv in self.population.keys():
			cppn.make_radial_image(128, 128, self.population[indiv], indiv)

	def eval_gen(self):
		self.fits = {}
		for indiv in self.population.keys():
			self.fits[indiv] = classify(indiv)[self.goal]

	def get_best_indiv(self):
		max_fit = 0
		max_indiv = ""
		for indiv in self.population.keys():
			if self.fits[indiv] > max_fit:
				max_fit = self.fits[indiv]
				max_indiv = indiv
		return max_indiv, max_fit

	def pick_winners(self):
		self.winners = []
		for indiv in self.fits.keys():
			if random.random() < self.fits[indiv]:
				self.winners.append(indiv)
			if len(self.winners) >= self.size / 2:
				return
		while len(self.winners) < self.size / 2:
			random_winner = list(self.fits.keys())[random.randint(0, self.size - 1)]
			if random_winner not in self.winners:
				self.winners.append(random_winner)

	def crossover(self, i1, i2):
		i1_genome = str(self.population[i1])
		i2_genome = str(self.population[i2])
		i1_nodes = i1_genome.split("|")[0].split(":")
		i2_nodes = i2_genome.split("|")[0].split(":")
		node_genes = list(set(i1_nodes + i2_nodes))
		node_gene = ':'.join(node_genes)

		i1_conns = i1_genome.split("|")[1].split(":")
		i2_conns = i2_genome.split("|")[1].split(":")
		i1_conns = dict(zip([int(conn.split(";")[0]) for conn in i1_conns], i1_conns))
		i2_conns = dict(zip([int(conn.split(";")[0]) for conn in i2_conns], i2_conns))

		i1_hist = list(i1_conns.keys())
		i2_hist = list(i2_conns.keys())

		if self.fits[i1] > self.fits[i2]:
			sup_dict = i1_conns
			sup_hist = i1_hist
		elif self.fits[i2] > self.fits[i1]:
			sup_dict = i2_conns
			sup_hist = i2_hist
		else:
			sup_dict = None
			sup_hist = None

		shared = [num for num in i1_hist for num_2 in i2_hist if num == num_2]
		gene = []
		for share in shared:
			if random.random() < .5:
				gene.append(i1_conns[share])
			else:
				gene.append(i2_conns[share])

		if sup_dict == None:
			for num in i1_hist:
				if num not in shared:
					gene.append(i1_conns[num])
			for num in i2_hist:
				if num not in shared:
					gene.append(i2_conns[num])
		else:
			for num in sup_hist:
				if num not in shared:
					gene.append(sup_dict[num])

		conn_gene = ':'.join(gene)
		return node_gene + "|" + conn_gene

	def mutate(self):
		for indiv in self.next_gen:
			if random.random() < .8:
				for conn in indiv.conns:
					if random.random() < .9:
						conn.weight += np.random.normal(scale=.25)
						if conn.weight < -1:
							conn.weight = -1
						elif conn.weight > 1:
							conn.weight = 1
			if random.random() < .075:
				nodes = [node.i_num for node in indiv.nodes]
				success = False
				while not success:
					before = nodes[random.randint(0, len(nodes) - 1)]
					after = nodes[random.randint(0, len(nodes) - 1)]
					success = indiv.add_node(before, after, self.node_num, self.conn_num)
				self.node_num += 1
				self.conn_num += 2
			elif random.random() < .1:
				nodes = [node.i_num for node in indiv.nodes]
				success = False
				while not success:
					before = nodes[random.randint(0, len(nodes) - 1)]
					after = nodes[random.randint(0, len(nodes) - 1)]
					success = indiv.add_conn(before, after, self.conn_num)
				self.conn_num += 1

	def breed_winners(self):
		self.next_gen = []		
		for indiv in self.winners:
			mate = indiv
			while mate != indiv:
				mate = self.winners[random.randint(0, len(self.winners) - 1)]
			new_indiv = cppn.build_cppn_from_str(self.crossover(indiv, mate))
			self.next_gen.append(new_indiv)
			self.next_gen.append(self.population[indiv])
		self.mutate()

	def new_gen(self):
		best, best_fit = self.get_best_indiv()
		call(['mv', best, 'good_bois/' + best.split('/')[-1]])
		for filename in os.listdir("population"):
			call(['rm', 'population/' + filename])
		self.generation += 1
		self.population = {}
		for i in range(0, self.size):
			self.population["population/" + str(self.generation) + "_" + str(i + 1) + ".png"] = self.next_gen[i]
		return best, best_fit

def evolve(size, goal):
	p = Population(size, goal)

	best = ""
	best_fit = 0

	while best_fit < .99:

		p.draw_population()

		p.eval_gen()

		p.pick_winners()

		p.breed_winners()

		best, best_fit = p.new_gen()
	
	print(best + ": " + str(best_fit))

