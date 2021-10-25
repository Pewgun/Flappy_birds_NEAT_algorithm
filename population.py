from genome import Genome
from species import Species
import math
import matplotlib.pyplot as plt
import numpy as np
from constants import *

class Population():

	def __init__(self, fileName=""):
		self.pop_size = POP_SIZE
		self.inputCount = INPUT_COUNT
		self.outputCount = OUTPUT_COUNT
		self.generation = 0
		self.data = {"species":[],"fitness":[]}

		self.inovHist = {}
		self.genomes = []
		if fileName != "":
			loadedGenome = Genome.loadFromFile(fileName)
		for _ in range(self.pop_size):
			if fileName == "":
				g = Genome(self.inputCount, self.outputCount, self.inovHist)	
			else:
				g = loadedGenome.clone()
			g.mutate()
			self.genomes.append(g)

		self.species = []
		
		self.bestGenome = self.genomes[0]#let the best genome be the first genome in the list cause it doesn't matter at this stage anyways
		self.bestScore  = 0.0

		self.nextSpecies = 0
		self.COMPATIBILITY_THRES = 3.0
		self.speciate()

	def naturalSelection(self):
		while len(self.data["species"]) < self.nextSpecies:
				self.data["species"].append([])
		for s in self.species:
			info = [self.generation, len(s.members)]
			self.data["species"][s.number].append(info)
		#Genomes already are speciated 
		#and have pre-calculated fitnesses or just calculate them here
		self.sortSpecies()
		self.cullSpecies()

		self.species.sort(key=lambda x:x.members[0].fitness, reverse=True)
		self.data["fitness"].append([self.generation, self.species[0].members[0].fitness])
		self.setBestGenome()
		self.species.sort(key=lambda x:x.averageFitness, reverse=True)

		self.setBestGenome()
		self.killStaleSpecies()
		self.killBadSpecies()

		averageSum = self.getAverageFitnessSum()
		children = []
		print('-------------------------------------')
		print(f'Number of species: {len(self.species)}')
		for s in self.species:
			s.age += 1
			spawn_num = max(ELITISM ,math.floor((s.averageFitness*self.pop_size)/averageSum))

			if (len(children) + spawn_num) > self.pop_size:
				spawn_num = self.pop_size-len(children)

			if spawn_num > 0:
				best = s.members[0].clone()
				best.fitness = 0.0
				best.adjustedFitness = 0.0
				children.append(best)
				spawn_num -= 1

			for _ in range(spawn_num):
				children.append(s.giveMeBaby())
			print(f'ID: {s.number}, avg_fitness: {s.averageFitness}, member_num: {len(s.members)} spawn_num: {spawn_num+1}')
		print('bestScore: ',self.bestScore)

		if len(children) < self.pop_size:
			new = self.species[0].members[0].clone()
			new.fitness = 0.0
			new.adjustedFitness = 0.0
			children.append(new)

		#If next generation is not completely filled fill with off-spring from the best-performing species
		while len(children) < self.pop_size:
			children.append(self.species[0].giveMeBaby())
        
		self.genomes = children

		self.speciate()
		#Adjust comatibiltiy threshold in order to maintain a target amount of species
		if len(self.species) < TARGET_SPECIES:
			self.COMPATIBILITY_THRES *= ALPHA_LOWER
		elif len(self.species) > TARGET_SPECIES:
			self.COMPATIBILITY_THRES *= ALPHA_HIGHER
		self.generation += 1

	def speciate(self):
		for s in self.species:
			s.members = []
		for g in self.genomes:
			found = False
			for s in self.species:
				if s.sameSpecies(g, self.COMPATIBILITY_THRES):
					s.add(g)
					found = True
					break

			if not found:
				self.species.append(Species(g, self.nextSpecies))
				self.nextSpecies += 1

		#Remove extinct species
		newSpecies = []
		for s in self.species:
			if len(s.members)>0:
				newSpecies.append(s)
		self.species = newSpecies[:]

	def sortSpecies(self):
		for s in self.species:
			s.sortSpecies()

	def cullSpecies(self):
		for s in self.species:
			s.fitnessSharing()
			s.setAverage()
			s.cull()

	def setBestGenome(self):
		if self.species[0].members[0].fitness > self.bestScore:
			self.bestScore  = self.species[0].members[0].fitness
			self.bestGenome = self.species[0].members[0].clone()

	def killStaleSpecies(self):
		newSpecies = []
		for s in self.species:
			if s.staleness <= STAGNATION_LIMIT:
				newSpecies.append(s)

		self.species = newSpecies

	def killBadSpecies(self):
		averageSum = self.getAverageFitnessSum()

		newSpecies = []
		for s in self.species:
			if s.averageFitness*self.pop_size/averageSum > 0:
				newSpecies.append(s)

		self.species = newSpecies

	def getAverageFitnessSum(self):
		summ = 0.0
		for s in self.species:
			summ += s.averageFitness
		return summ

	def showSpeciesMemNum(self):
		data = self.data["species"]
		n_species = len(data)
		n_generations = self.generation

		min_max_gen = np.zeros([n_species,2])

		sizes = np.zeros([n_generations,n_species])
		fitness = np.zeros([n_generations,n_species])
		for i in range(n_species):
			s = np.array(data[i])
		    #print(s)
			min_gen = int(s[0,0])
			max_gen = int(s[-1,0])
			min_max_gen[i,:] = np.array([min_gen, max_gen])
			sizes[min_gen:max_gen+1,i] = s[:,1]

		#plt.figure()
		xmin = np.min(min_max_gen)
		xmax = np.max(min_max_gen)

		plt.stackplot(np.arange(n_generations),sizes.T, alpha=0.4)
		plt.xlim(xmin, xmax)
		plt.ylabel('Population/Species Size')
		plt.xlabel('Generation')

		plt.show()

	def showBestGenomeOuputMap(self):
		#Works only when genome has only two inputs
		self.bestGenome.showOutputMap()

	def showBestGenomeNeuralNet(self):
		self.bestGenome.showNeuralNet()

	def showFitnessGrowth(self):
		data = self.data["fitness"]
		n_generations = self.generation

		gens = []
		fits = []
		for i in range(len(data)):
			gen = data[i][0]
			fit = data[i][1]
			gens.append(gen)
			fits.append(fit)
		plt.plot(gens, fits)
		plt.xlim(0,n_generations)
		plt.ylabel('Highest Fitness')
		plt.xlabel('Generation')
		plt.show()
