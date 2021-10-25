import pygame
import sys
import random
from population import Population

HEIGHT = 600
WIDTH  = 400

class Bird():
	def __init__(self, display, brain):
		self.display = display

		self.image = pygame.image.load("assets/up.png")
		self.upImg = pygame.image.load("assets/up.png")
		self.downImg = pygame.image.load("assets/down.png")

		self.width = 40
		self.height = 29
		self.x = 90
		self.y = (HEIGHT + self.height)//2
		self.speed = 0
		self.lift = -12
		self.gravity = 0.7

		self.alive = True
		self.hitBottom = False

		self.brain = brain
		self.brain.prepareNetwork()

	def draw(self):
		if self.speed < 0: 
			self.image = self.upImg
		else:
			self.image = self.downImg

		self.display.blit(self.image, (self.x, self.y))

	def update(self):
		self.speed += self.gravity
		self.speed *= 0.9
		self.y += self.speed
		if self.y+self.height > HEIGHT or self.y < 0:
			self.hitBottom = True

	def jump(self):
		self.speed = self.lift

class Pipe(object):
	def __init__(self, display):
		self.display = display
		self.bottomPart = pygame.image.load("assets/bottom.png")
		self.topPart = pygame.image.load("assets/top.png")
		self.gap = 150
		self.speed = -2.0
		self.width = self.bottomPart.get_width()
		self.height = self.topPart.get_height()
		self.x = WIDTH
		self.y = random.randint(70, HEIGHT-self.gap-70)
		self.isMoving = False
		if random.random() < 0.5:
			self.isMoving = True
			self.ySpeed = 1.0 + random.random()*2.0
			DIFF = 70
			self.upperLimit = max(self.y - DIFF, 70)
			if self.upperLimit == 70:
				self.lowerLimit = self.upperLimit + self.gap + 2*DIFF
			else:
				self.lowerLimit = min(self.upperLimit + self.gap + 2*DIFF, HEIGHT-70)
				if self.lowerLimit == HEIGHT-70:
					self.upperLimit = self.lowerLimit - self.gap - 2*DIFF
			self.y = self.upperLimit

	def show(self):
		self.display.blit(self.topPart, (self.x, self.y-self.height))
		self.display.blit(self.bottomPart, (self.x, self.y+self.gap))

	def update(self):
		self.x += self.speed
		if self.isMoving:
			self.y += self.ySpeed
			if self.y+self.gap >= self.lowerLimit or self.y <= self.upperLimit:
				self.ySpeed *= -1

	def hits(self, bird):
		margin = 0
		if(self.x < (bird.x+bird.width-margin)) and ((self.x+self.width) > bird.x+margin):
			if bird.y+margin < self.y or (bird.y + bird.height-margin)> (self.y+self.gap):
				return True
		return False


class flappyBird:
	def __init__(self, genomes):
		#Initializing sreen
		pygame.init()
		self.clock = pygame.time.Clock()
		pygame.display.set_caption("Flappy birds")
		self.display = pygame.display.set_mode((WIDTH, HEIGHT))#Width and hieght of display
		#Initializing background
		self.background = pygame.image.load("assets/background.png")
		#Creating a bird object
		self.birds = []
		for g in genomes:
			b = Bird(self.display, g)
			self.birds.append(b)

		#Creating pipes
		self.pipes = [Pipe(self.display)]
		self.score = 0

		#saved
		self.saved = []

	def update_screen(self):
		self.display.blit(self.background, (0, 0))
		for pipe in self.pipes:
			pipe.show()
		for bird in self.birds:
			bird.draw()
		self.update_score()
		pygame.display.update()

	def update_score(self):
		white = pygame.Color(255,255,255)
		black = pygame.Color(0,0,0)
		def draw_text(x, y, string, col, size):
			font = pygame.font.SysFont("Impact", size)
			text = font.render(string, True, col)
			textbox = text.get_rect()
			textbox.center = (x, y)
			self.display.blit(text, textbox)
		x = 50
		y = 60
		offset = 3
		draw_text(x + offset, y-offset , str(self.score), white, 64)
		draw_text(x +offset, y+offset ,str(self.score), white, 64)
		draw_text(x -offset, y +offset , str(self.score), white, 64)
		draw_text(x-offset, y -offset , str(self.score), white, 64) 
		draw_text(x, y , str(self.score), black, 64)

	def run_game(self, show=True, limit=300):	
		frame = 0
		prevClosest = None
		closestPipe = None
		while len(self.birds) != 0:
			pygame.event.get()
			if frame == 120:
				newPipe = Pipe(self.display)
				self.pipes.append(newPipe)
				frame = 0
			#Looping through all the current events
			for pipe in self.pipes:
				if self.birds[0].x < (pipe.x+pipe.width):
					prevClosest = closestPipe
					closestPipe = pipe
					break
			for bird in self.birds:
				if bird.alive:
					out = bird.brain.feedForward([abs(closestPipe.y-bird.y)/HEIGHT, abs(closestPipe.y+closestPipe.gap-bird.y)/HEIGHT])
					if out[0] > 0.6:
						bird.jump()
					bird.brain.fitness += 0.1#lifespan

			for bird in self.birds:
				bird.update()

			for pipe in self.pipes:
				pipe.update()
				if (pipe.x+pipe.width) < 0:
					self.pipes.remove(pipe)

			#Update the coordinates of the pipes
			for bird in self.birds:
				if closestPipe.hits(bird):
					bird.alive = False

			newBirds = []
			for bird in self.birds:
				if bird.alive and not bird.hitBottom:
					newBirds.append(bird)
			self.birds = newBirds

			#Check for a passed pipe
			passed = False
			for bird in self.birds:
				if closestPipe and prevClosest:
					if closestPipe.x != prevClosest.x:
						bird.brain.fitness += 10.0
						passed = True

			if passed:
				self.score += 1
				if self.score == limit:
					return True
			if show:
				self.update_screen()
				self.clock.tick()
			frame += 1
		print(self.score)
		return False

if __name__ == "__main__":
	#pop = Population(fileName="genome1.json")
	pop = Population()
	i = 0
	flag = False

	while not flag:#Make a key press
		print(f'Generation: {i+1}')
		flag = flappyBird(pop.genomes).run_game(show=True, limit=10000)
		pop.naturalSelection()
		i += 1
		if i == 100:
			flag = True
	print("Evolution has been executed!!!")
	pop.bestGenome.saveToFile("genome10000_lift-12")
	successful = 0
	total = 20
	for _ in range(total):
		res = flappyBird(pop.genomes).run_game(show=False, limit=100)
		if res: print('Successful run!!!')
		else: print('Failure occured!!!')
		successful += int(res)
	print(f"Success rate of the final genome is: {successful/total}")

	flappyBird([pop.bestGenome]).run_game(show=True, limit=50)
	"""from genome import Genome
	g = Genome.loadFromFile("genome1.json")
	flappyBird([g]).run_game(show=True, limit=100)"""

	pop.showSpeciesMemNum()
	pop.showFitnessGrowth()
	pop.showBestGenomeOuputMap()
	pop.showBestGenomeNeuralNet()