from node import Node
from gene import Gene
import random
from constants import *

class Genome():

	def __init__(self, inputs, outputs, inovHist):
		self.genes = []
		self.nodes = []
		self.inputs = inputs
		self.outputs = outputs
		self.nextNode = 0
		self.inputNodes  = []
		self.outputNodes = []
		self.inovHist = inovHist
		
		self.fitness = 0.0
		self.adjustedFitness = 0.0

		#Creating input nodes
		for i in range(self.inputs):
			inputNode = Node(self.nextNode)
			inputNode.layer = 0
			self.inputNodes.append(inputNode)
			self.nodes.append(inputNode)
			self.nextNode += 1

		#Creating output nodes
		for i in range(self.outputs):
			outputNode = Node(self.nextNode)
			outputNode.layer = 1
			self.outputNodes.append(outputNode)
			self.nodes.append(outputNode)
			self.nextNode += 1
		#Creating a bias node
		self.biasNode = Node(self.nextNode)
		self.biasNode.layer = 0
		self.nodes.append(self.biasNode)
		self.nextNode += 1
		#Creating all bias-output genes
		for i in range(self.inputs, self.inputs + self.outputs):
			self.createGene(self.biasNode, self.nodes[i])

		self.levels = {}

	def __str__(self):
		out = 'Nodes:\n'
		for node in self.nodes:
			out += 'ID: ' + str(node.number) + ', layer: ' + str(node.layer) + '\n'
		out += 'Genes:\n'
		for gene in self.genes:
			out += f'inNode:{gene.fromNode.number}, outNode:{gene.toNode.number}, weight:{gene.weight}, enabled:{gene.enabled}, innovationNumber:{gene.inno}\n'
		out += f'fitness: {self.fitness}\n'
		return out

	def createGene(self,inNode, outNode):
		#short-cut for adding a new gene to this genome
		#returns just created gene
		gene = Gene(inNode, outNode, self.getInnovation(inNode, outNode))
		self.genes.append(gene)
		return gene

	def mutate(self):
		if random.random() < PROB_MUTATE_GENE:
			for gene in self.genes:
				gene.mutateWeight()

		if random.random() < PROB_ADD_NODE:
			self.addNode()

		if random.random() < PROB_ADD_GENE:
			self.addConnection()	

	def geneExists(self, node1, node2):
		for gene in self.genes:
			if gene.fromNode.number == node1.number and gene.toNode.number == node2.number:
				return [gene.enabled, gene]
			if gene.fromNode.number == node2.number and gene.toNode.number == node1.number:
				return [gene.enabled, gene]
		return [False, None]

	def getInnovation(self, node1, node2):
		for key, innovation in self.inovHist.items():
			if (node1.number, node2.number) == key:
				return innovation
		nextInnovation = len(self.inovHist.keys())
		self.inovHist[node1.number, node2.number] = nextInnovation
		return nextInnovation

	def addConnection(self):
		if self.fullyConnected():
			self.addNode()
			return
		node1 = None
		node2 = None
		flag = False
		for _ in range(CREATE_CON_TRIES):
			node1 = random.choice(self.nodes)
			node2 = random.choice(self.nodes)
			decision, gene = self.geneExists(node1, node2)
			if gene is not None and not decision:
				#if this gene already exists but it's disabled then enable it
				gene.enabled = True
				return
			if node1.layer == node2.layer or decision:
				continue
			flag = True
			break	
		if not flag:
			#Failed to create a new conncection
			return
		if node1.layer > node2.layer:
			tmp = node2
			node2 = node1
			node1 = tmp
		self.createGene(node1, node2)

	def fullyConnected(self):
		maxConnections = 0
		nodesInLayer = {}
		for node in self.nodes:
			if node.layer not in nodesInLayer.keys():
				nodesInLayer[node.layer] = 1
			else:
				nodesInLayer[node.layer] += 1
		i = 1
		numberOfNodeBefore = nodesInLayer[0]
		while i in nodesInLayer.keys():
			currentNumber = nodesInLayer[i]
			maxConnections += currentNumber*numberOfNodeBefore
			numberOfNodeBefore += currentNumber
			i += 1
		return maxConnections == len(self.genes)

	def addNode(self):
		if len(self.genes) == self.outputs:
			#If there are only bias genes then try creating a new connection
			self.addConnection()
			return
		flag = False
		for _ in range(ADD_NODE_TRIES):
			randomGene = random.choice(self.genes)
			while randomGene.fromNode.number == self.biasNode.number:
				#Repeat while randomGene is a bias gene
				randomGene = random.choice(self.genes)
			if randomGene.fromNode.layer + 1 == randomGene.toNode.layer and not self.fullyConnected():
				#If adding node in this gene would cause creation of a new layer it should only
				#Happen when it is also not fully connected
				continue
			flag = True
			break
		if not flag:
			#Failed to add a new node
			return

		randomGene.enabled = False

		newNode = Node(self.nextNode)
		self.nodes.append(newNode)
		self.nextNode += 1

		gene1 = self.createGene(randomGene.fromNode, newNode) 
		gene1.weight = 1.0

		gene2 = self.createGene(newNode, randomGene.toNode)
		gene1.weight = randomGene.weight

		biasGene = self.createGene(self.biasNode, newNode)

		#Upadate layer values of nodes
		if randomGene.fromNode.layer + 1 == randomGene.toNode.layer:
			for node in self.nodes:
				if node.layer >= randomGene.fromNode.layer + 1:
					node.layer += 1
		newNode.layer = randomGene.fromNode.layer + 1

	def matchingGene(self, gene1):
		for gene in self.genes:
			if gene.inno == gene1.inno:
				return gene
		return False

	def getNode(self, nr):
		for node in self.nodes:
			if node.number == nr:
				return node
		raise Exeption('Node does not exist')
		return False

	@staticmethod
	def crossover(p1, p2):
		if p1.fitness > p2.fitness:
			parent1, parent2 = p1, p2
		else:
			parent1, parent2 = p2, p1

		child = Genome(p1.inputs, p1.outputs, p1.inovHist)
		child.nodes = []
		child.genes = []
		child.inputNodes = []
		child.outputNodes = []
		child.nextNode = parent1.nextNode

		for node in parent1.nodes:
			child.nodes.append(node.clone())

		child.biasNode = child.getNode(parent1.biasNode.number)

		for inNode in parent1.inputNodes:
			child.inputNodes.append(child.getNode(inNode.number))

		for outNode in parent1.outputNodes:
			child.outputNodes.append(child.getNode(outNode.number))
		for gene in parent1.genes:
			parent2gene = parent2.matchingGene(gene)
			if parent2gene:
				enabled = True
				if not parent2gene.enabled or not gene.enabled:
					if random.random() < DISABLE_AFTER_CROSS:
						enabled = False

				if random.random() < 0.5:
					clonedGene = child.createGene(child.getNode(parent2gene.fromNode.number), child.getNode(parent2gene.toNode.number))
					clonedGene.weight = parent2gene.weight
				else:
					clonedGene = child.createGene(child.getNode(gene.fromNode.number), child.getNode(gene.toNode.number))
					clonedGene.weight = gene.weight
				clonedGene.enabled = enabled
			else:
				clonedGene = child.createGene(child.getNode(gene.fromNode.number), child.getNode(gene.toNode.number))
				clonedGene.weight = gene.weight
				clonedGene.enabled = gene.enabled
		return child

	def prepareNetwork(self):
		if self.levels: return
		for gene in self.genes:
			if gene.enabled:
				gene.fromNode.outputConnections.append(gene)

		for node in self.nodes:
			if node.layer not in self.levels:
				self.levels[node.layer] = [node]
			else:
				self.levels[node.layer].append(node)

	def feedForward(self, ins):
		for i, node in enumerate(self.inputNodes):
			node.outputValue = ins[i]

		self.biasNode.outputValue = 1.0

		level = 0
		while level <= max(self.levels.keys()):
			nodes = self.levels[level]
			for node in nodes:
				node.engage()
			level += 1

		outs = []
		for i, node in enumerate(self.outputNodes):
			outs.append(node.outputValue)

		for node in self.nodes:
			node.inputSum = 0.0
			node.outputValue = 0.0

		return outs

	def clone(self):
		newGenome = Genome(self.inputs, self.outputs, self.inovHist)
		newGenome.genes = []
		newGenome.nodes = []
		newGenome.inputNodes = []
		newGenome.outputNodes = []
		newGenome.nextNode = self.nextNode
		newGenome.fitness = self.fitness
		newGenome.adjustedFitness = self.adjustedFitness

		for node in self.nodes:
			newGenome.nodes.append(node.clone())

		newGenome.biasNode = newGenome.getNode(self.biasNode.number)
		for gene in self.genes:
			clonedGene = newGenome.createGene(newGenome.getNode(gene.fromNode.number), newGenome.getNode(gene.toNode.number))
			clonedGene.weight = gene.weight
			clonedGene.enabled = gene.enabled
		for inNode in self.inputNodes:
			newGenome.inputNodes.append(newGenome.getNode(inNode.number))

		for outNode in self.outputNodes:
			newGenome.outputNodes.append(newGenome.getNode(outNode.number))
		
		return newGenome

	def showOutputMap(self):
		import matplotlib.pyplot as plt
		import numpy as np
		self.prepareNetwork()

		resol = 150
		matrix = np.zeros([resol+1,resol+1])
		for y in range(resol+1):
			for x in range(resol+1):
				value = self.feedForward([x/resol,y/resol])
				matrix[resol-y,x] = value[0]
		plt.figure(figsize=(7, 7), dpi=70)
		plt.imshow(matrix)
		plt.ylabel('Distance From Bottom Pipe')
		plt.xlabel('Distance From Upper Pipe')
		ax = plt.gca()
		ax.xaxis.set_ticks([x*150/10 for x in range(0,11)])
		ax.set_xticklabels([str(x/10) for x in range(0, 11)])
		ax.yaxis.set_ticks([x*150/10 for x in range(10,-1,-1)])
		ax.set_yticklabels([str(x/10) for x in range(0, 11)])
		plt.clim(0.0, 1.0)
		plt.colorbar()
		plt.show()

	def showNeuralNet(self):
		import networkx as nx
		import matplotlib.pyplot as plt
		import matplotlib
		import random
		G = nx.DiGraph()

		net = self
		net.prepareNetwork()

		level = 0
		while level <= max(net.levels.keys()):
			nodes = net.levels[level]
			for i, node in enumerate(nodes):
				if i in [node.number for node in net.inputNodes] or i in [node.number for node in net.outputNodes]:
					G.add_node(node.number, pos=(level, float(i) + random.random()*0.3-0.15))
				else:
					G.add_node(node.number, pos=(level, i))
			level += 1

		edge_weights=[]
		widths = []
		MAX_WIDTH = 3
		MIN_WIDTH = 1
		for gene in net.genes:
			G.add_edge(gene.fromNode.number, gene.toNode.number)
			if gene.enabled:
				if gene.weight > 0.0:
					edge_weights.append(gene.weight)
					widths.append(MIN_WIDTH + gene.weight*(MAX_WIDTH-MIN_WIDTH)/UPPER_WEIGHT_BOUND)
				elif gene.weight < 0.0:
					edge_weights.append(gene.weight)
					widths.append(MIN_WIDTH + gene.weight*(MAX_WIDTH-MIN_WIDTH)/LOWER_WEIGHT_BOUND)
			else:
				edge_weights.append(0.0)
				widths.append(0)

		node_color_map = []
		for node in G:
			if node == net.biasNode.number:
				node_color_map.append('green')
			elif node in [node.number for node in net.inputNodes]:
				node_color_map.append('darkblue')
			elif node in [node.number for node in net.outputNodes]:
				node_color_map.append('brown')
			else:
				node_color_map.append('gray')
		pos=nx.get_node_attributes(G,'pos')
		cmap = matplotlib.colors.LinearSegmentedColormap.from_list("", ["red","white","blue"])
		nx.draw(G,pos, 	node_color=node_color_map, font_color='white',edge_cmap=cmap, edge_color=edge_weights,
						node_size=[1000 for _ in range(len(net.nodes))], vmin=LOWER_WEIGHT_BOUND,vmax=UPPER_WEIGHT_BOUND,
						width=widths, with_labels = True)
		plt.show()

	def saveToFile(self, fileName):
		import json
		out = {}
		out["nodes"] = []
		for node in self.nodes:
			#number, layer
			out["nodes"].append({"number":node.number, "layer": node.layer})
		out["biasNode"] = self.biasNode.number
		out["genes"] = []
		for gene in self.genes:
			out["genes"].append({"fromNode":gene.fromNode.number, "toNode": gene.toNode.number, 
								"weight": gene.weight, "enabled": gene.enabled})
		out["inputs"] = self.inputs
		out["outputs"] = self.outputs
		out["nextNode"] = self.nextNode
		out["inputNodes"] = [node.number for node in self.inputNodes]
		out["outputNodes"] = [node.number for node in self.outputNodes]
		out["inovHist"] = []
		for key, val in self.inovHist.items():
			out["inovHist"].append({"n1": key[0], "n2": key[1], "val": val})

		with open(fileName+".json",'w') as f:
			json.dump(out, f)

	def loadFromFile(fileName):
		import json
		
		with open(fileName) as f:
			data = json.load(f)

		inputs = data["inputs"]
		outputs = data["outputs"]
		inovHist = {}
		for hist in data["inovHist"]:
			inovHist[hist["n1"],hist["n2"]] = hist["val"]
		newGenome = Genome(inputs, outputs, inovHist)
		newGenome.genes = []
		newGenome.nodes = []
		newGenome.inputNodes = []
		newGenome.outputNodes = []
		newGenome.nextNode = data["nextNode"]
		for node in data["nodes"]:
			newNode = Node(node["number"])
			newNode.layer = node["layer"]
			newGenome.nodes.append(newNode)

		newGenome.biasNode = newGenome.getNode(data["biasNode"])

		for gene in data["genes"]:
			clonedGene = newGenome.createGene(newGenome.getNode(gene["fromNode"]), newGenome.getNode(gene["toNode"]))
			clonedGene.weight = gene["weight"]
			clonedGene.enabled = gene["enabled"]

		for inNodeNr in data["inputNodes"]:
			newGenome.inputNodes.append(newGenome.getNode(inNodeNr))
		for outNodeNr in data["outputNodes"]:
			newGenome.outputNodes.append(newGenome.getNode(outNodeNr))

		return newGenome

