import random
from genome import Genome
import math
from constants import *

class Species():
	def __init__(self, leader, number):
		self.leader = leader.clone()
		self.members= []
		self.add(leader)
		self.averageFitness  = 0.0
		self.staleness = 0
		self.max_fitness = leader.fitness
		self.number = number
		self.age = 0

	def sameSpecies(self, g, THRES):
		matchingGenes = 0
		excessDisjointGenes = 0
		weightDifference = 0.0

		for gene in g.genes:
			matchingGene = self.leader.matchingGene(gene)
			if matchingGene:
				matchingGenes += 1
				weightDifference += abs(gene.weight-matchingGene.weight)

		excessDisjointGenes = len(g.genes) + len(self.leader.genes) - 2*matchingGenes

		largeGenomeNormaliser = len(g.genes) - LARGE_GENOME_THRES
		if largeGenomeNormaliser < 1:
			largeGenomeNormaliser = 1

		if matchingGenes == 0:
			matchingGenes = 1
			weightDifference = 0.0
			if len(g.genes) != 0 and len(self.leader.genes) != 0:
				weightDifference = 100

		diff = (EXCESS_DISJOINT_COEF*excessDisjointGenes/largeGenomeNormaliser) + (WEIGTH_DIFF_COEF*weightDifference/matchingGenes)
		return diff < THRES

	def add(self, g):
		self.members.append(g)

	def sortSpecies(self):
		self.members.sort(key=lambda x:x.fitness, reverse=True)

		self.representative = self.members[0].clone()#The representative of the next species is the best performing one in the current one
		if self.members[0].fitness > self.max_fitness:
			self.staleness = 0
			self.max_fitness = self.members[0].fitness
		else:
			self.staleness += 1

	def setAverage(self):
		fitnessSum = 0.0
		for m in self.members:
			fitnessSum += m.adjustedFitness

		self.averageFitness = fitnessSum / len(self.members)

	def giveMeBaby(self):
		if random.random() < PROB_CLONE_MEMBER:
			child = self.tournament_selection().clone()
			child.fitness = 0.0
			child.adjustedFitness = 0.0
		else:
			p1 = self.tournament_selection()
			p2 = self.tournament_selection()

			child = Genome.crossover(p1, p2)
		child.mutate()
		return child

	def wheel_selection(self):
		fitnessSum = 0.0
		for m in self.members:
			fitnessSum += m.fitness

		rand = random.random()*fitnessSum
		cummulativeSum = 0.0
		for m in self.members:
			cummulativeSum += m.fitness
			if cummulativeSum >= rand:
				return m

	def tournament_selection(self):
		best = None
		for _ in range(min(TRYS_IN_TOURNAMENT_SELECTION,len(self.members))):
			g = random.choice(self.members)
			if best == None or g.fitness > best.fitness:
				best = g
		return best.clone()

	def cull(self):
		k = max(MIN_AFTER_CUT_OFF, math.floor(len(self.members)*CUT_OFF))
		self.members[:] = self.members[:k]

	def fitnessSharing(self):
		for m in self.members:
			fitness = m.fitness
			if self.age < YOUNGE_AGE_THRESHHOLD:
				fitness *= YOUNGE_AGE_FITNESS_BONUSS
			if self.age > OLD_AGE_THRESHOLD:
				fitness *= OLD_AGE_FITNESS_PENALTY
			m.adjustedFitness = fitness/len(self.members)
