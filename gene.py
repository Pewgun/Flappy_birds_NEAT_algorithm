import random
from constants import *

class Gene():
	def __init__(self, fromNode, toNode, inno):
		self.fromNode  = fromNode
		self.toNode    = toNode
		if USE_GAUSS:
			self.weight = random.gauss(0.0,WEIGHT_CHANGE_POWER)
			self.clamp()
		else:
			self.weight = random.random()*abs(LOWER_WEIGHT_BOUND-UPPER_WEIGHT_BOUND)+LOWER_WEIGHT_BOUND
		
		self.enabled   = True
		self.inno      = inno

	def clamp(self):
		self.weight = min(max(LOWER_WEIGHT_BOUND, self.weight), UPPER_WEIGHT_BOUND)

	def mutateWeight(self):
		if random.random() < PROB_CHANGE_WEIGHT:
			if USE_GAUSS:
				self.weight = random.gauss(0.0,WEIGHT_CHANGE_POWER)
				self.clamp()
			else:
				self.weight = random.random()*abs(LOWER_WEIGHT_BOUND-UPPER_WEIGHT_BOUND)+LOWER_WEIGHT_BOUND
		else:
			self.weight += random.gauss(0.0,WEIGHT_CHANGE_POWER)
			self.clamp()

	def clone(self):
		g = Gene(self.fromNode, self.toNode, self.inno)
		g.weight = self.weight
		g.enabled = self.enabled
		return g