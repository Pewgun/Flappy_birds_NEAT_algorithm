import math

class Node():

	def __init__(self, nr):
		self.number = nr
		self.layer = 0
		self.inputSum = 0.0
		self.outputValue = 0.0
		self.outputConnections = []

	def __str__(self):
		return f"number: {self.number}, layer: {self.layer}"

	def engage(self):
		if self.layer != 0:
			self.activate()

		for con in self.outputConnections:
			if con.enabled:
				con.toNode.inputSum += con.weight*self.outputValue

	def activate(self):
		x = max(-60.0, min(60.0, -5.0 * self.inputSum))
		self.outputValue = 1/(1+math.exp(x))

	def clone(self):
		n = Node(self.number)
		n.layer = self.layer
		return n