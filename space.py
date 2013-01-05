import pygame, os, sys, math, random
from math import cos, sin

# global vars
BLACK = 0, 0, 0
WHITE = 255,255,255
#SIZE = WIDTH, HEIGHT = 1280, 800
SIZE = WIDTH, HEIGHT = 1024,768
FONTSIZE = 25
menuSelection = 0
# FIXME the following variables should not be global!!!
state = None
things = []


def getDeg(dx, dy):
	hyp = math.hypot(dx, dy)
	if hyp == 0:
		return 0.0
	deg = math.degrees(math.acos(dx / hyp))
	if dy < 0:
		deg = 360 - deg
	return deg

class Movable:
	def __init__(self, x, y, vel, dir):
		self.x = x
		self.y = y
		self.vel = vel
		self.dir = dir

	def update(self):
		rad = math.radians(self.dir)
		dx = cos(rad) * self.vel
		dy = sin(rad) * self.vel
		self.x += dx
		self.y += dy
		if self.x > WIDTH:
			self.x = 0
		elif self.x < 0:
			self.x = WIDTH

		if self.y > HEIGHT:
			self.y = 0
		elif self.y < 0:
			self.y = HEIGHT
	
	def applyForce(self, val, direction):
		rad = math.radians(self.dir)
		cur_dx = cos(rad) * self.vel
		cur_dy = sin(rad) * self.vel
		
		rad = math.radians(direction)
		new_dx = cos(rad) * val
		new_dy = sin(rad) * val

		dx = cur_dx + new_dx
		dy = cur_dy + new_dy
		self.vel = math.hypot(dx, dy)
		self.dir = getDeg(dx, dy)
		
		if self.vel > 5:
			self.vel = 5
		if self.vel < 0:
			self.vel = 0

class Player(Movable):
	def __init__(self, color, x=640, y=400, rot=0):
		Movable.__init__(self, x, y, 0, 0)
		self.color = color
		self.rot = rot # angle we're facing
		self.orig = {}
		self.orig['x'] = x
		self.orig['y'] = y
		self.orig['rot'] = rot
		self.health = 100
		self.lives = 3
		self.shooting = 0

	def checkCollision(self, other):
		if other != self and isinstance(other, Player):
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			dist -= 2*5 #5 is the player shield radius
			if dist <= 0:
				# TODO damage based on collision speed
				self.health -= 25
				other.health -= 25
				other.vel, self.vel = self.vel, other.vel
				other.dir, self.dir = self.dir, other.dir
				self.update()
				other.update()

		if isinstance(other, GravityWell):
			dx = self.x - other.x
			dy = self.y - other.y
			hyp = math.hypot(dx, dy)
			if hyp <= other.rad:
				self.reset()

	def reset(self):
		self.lives -= 1
		self.health = 100
		self.x = self.orig['x']
		self.y = self.orig['y']
		self.rot = self.orig['rot']
		self.vel = 0

	def update(self, others=None):
		Movable.update(self)
		if self.shooting > 0:
			self.shooting -= 1
		if self.health <= 0:
			self.reset()

	def accellerate(self, val):
		self.applyForce(val, self.rot)

	def rotate(self, val):
		self.rot = self.rot + val
		if self.rot > 360:
			self.rot -= 360
		elif self.rot < -360:
			self.rot += 360

	def display(self, surface):
		points = []
		# first define the points relative to our x and y
		points.append([5, 0])
		points.append([-5, 5])
		points.append([-2, 0])
		points.append([-5, -5])

		# then rotate according to our rot
		rad = math.radians(self.rot)
		for point in points:
			x = point[0]
			y = point[1]
			point[0] = x*cos(rad) - y*sin(rad)
			point[1] = x*sin(rad) + y*cos(rad)

		# then update the points to become absolute screen positions
		for point in points:
			point[0] += self.x
			point[1] += self.y

		pygame.draw.polygon(surface, self.color, points)
		#pygame.draw.polygon(surface, (self.color[0],self.color[1],self.color[2],100), points, 1)

	def shoot(self):
		if self.shooting == 0:
			rad = math.radians(self.rot)
			x = self.x + math.cos(rad) * 7
			y = self.y + math.sin(rad) * 7
			b = Bullet(x, y, self.vel, self.dir, self.color)
			b.applyForce(3, self.rot)
			b.update()
			self.shooting = 2
			return b
		else:
			return False

class GravityWell:
	def __init__(self, x, y, rad, force):
		self.x = x
		self.y = y
		self.rad = rad
		self.force = force

	def update(self, others):
		for other in others:
			force = self.force
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			if dist != 0:
				force = force / (dist/2)
			angle = getDeg(dx, dy)
			other.applyForce(force, angle)

	def applyForce(self, vel, dir):
		pass

	def checkCollision(self, other):
		pass

	def display(self, surface):
		pygame.draw.circle(surface, (255,255,255,255), (self.x, self.y), self.rad, 1)
		pygame.draw.circle(surface, (255,255,255,200), (self.x, self.y), self.rad + 1, 1)
		pygame.draw.circle(surface, (255,255,255,150), (self.x, self.y), self.rad + 2, 1)
		pygame.draw.circle(surface, (255,255,255,100), (self.x, self.y), self.rad + 3, 1)
		pygame.draw.circle(surface, (255,255,255,55), (self.x, self.y), self.rad + 4, 1)
		pygame.draw.circle(surface, (255,255,255,25), (self.x, self.y), self.rad + 5, 1)

class Bullet(Movable):
	# not super happy with these explosion colors, but they'll have to do for now
	n1 = [(192,122,0,192),(128,128,0,192), (128,128,0,128),(0,0,0,0),(0,0,0,0)]
	n2 = [(192,122,0,192),(192,122,0,192),(128,128,0,192), (128,128,0,128),(0,0,0,0)]
	n3 = [(192,128,0,128),(192,122,0,192),(192,122,0,192),(128,128,0,192), (128,128,0,128)]
	n4 = [(128,64,0,192),(192,128,0,128),(192,122,0,192),(192,192,100,192),(192,192,192,192)]
	n5 = [(128,64,0,192),(192,128,0,50),(192,122,0,128),(192,192,192,128),(192,192,192,128)]
	exp = [n5,n4,n3,n2,n1] # going to be using negative indexes into this

	def __init__(self, x, y, vel, dir, color):
		Movable.__init__(self, x, y, vel, dir)
		self.color = color
		self.ttl = 255

	def display(self, surface):
		color = self.color
		if self.ttl >= 0:
			pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 1)
			pygame.draw.circle(surface, (color[0], color[1], color[2], 125), (int(self.x), int(self.y)), 2)
		if self.ttl < 0:
			pygame.draw.circle(surface, Bullet.exp[self.ttl][0], (int(self.x), int(self.y)), 1, 1)
			pygame.draw.circle(surface, Bullet.exp[self.ttl][1], (int(self.x), int(self.y)), 2, 1)
			pygame.draw.circle(surface, Bullet.exp[self.ttl][2], (int(self.x), int(self.y)), 3, 1)
			pygame.draw.circle(surface, Bullet.exp[self.ttl][3], (int(self.x), int(self.y)), 4, 1)
			#pygame.draw.circle(surface, Bullet.exp[self.ttl][4], (int(self.x), int(self.y)), 5, 1)

	def update(self, others=None):
		Movable.update(self)
		self.ttl -= 1
		if self.ttl < -5:
			others.remove(self)

	def checkCollision(self, other):
		if isinstance(other, GravityWell):
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			if dist <= other.rad and self.ttl > 0:
				self.ttl = 0
		elif isinstance(other, Player):
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			if dist <= 5: # shield radius
				other.applyForce(self.vel / 5, self.dir)
				other.health -= 25
				if self.ttl > 0:
					self.ttl = 0
		
def quit():
	pygame.quit()
	sys.exit()

def main():
	global state
	global things

	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	# initialize  fonts and stuff for menus
	pygame.font.init()
	font = pygame.font.SysFont('monospace', FONTSIZE)
	textColor = (255,255,255)
	selected  = (255,255,0)

	# setup the screen, double buffer and game clock
	screen = pygame.display.set_mode(SIZE)
	buff = pygame.Surface(SIZE, flags=pygame.SRCALPHA, depth=32)
	clock = pygame.time.Clock()

	# Game objects (players and black hole)
	c1 = (255,100,100, 250)
	c2 = (100,100,255, 250)
	player1 = Player(c1, x=WIDTH/2 - WIDTH/4, y=HEIGHT/2, rot=180)
	player2 = Player(c2, x=WIDTH/2 + WIDTH/4, y=HEIGHT/2, rot=0)
	blackhole = GravityWell(WIDTH/2, HEIGHT/2, 15, 5.5)

	# Interface needs Player objects to draw remaining 'lives'
	c1 = c1[0], c1[1], c1[2], 128
	c2 = c2[0], c2[1], c2[2], 128
	l1 = Player(c1, 140, 25, 270)
	l2 = Player(c2, WIDTH-140, 25, 270)

	# list of game objects
	things = [player1, player2, blackhole]

	def gameLoop():
		global state
		global things

		# quit on window close 
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()

		# player 1 input
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			state = mainMenuLoop

		if keys[pygame.K_d]:
			player1.rotate(+5)
		if keys[pygame.K_a]:
			player1.rotate(-5)
		if keys[pygame.K_w]:
			player1.accellerate(+0.25)
		if keys[pygame.K_s]:
			player1.accellerate(-0.1)
		if keys[pygame.K_LSHIFT]:
			b = player1.shoot()
			if b != False:
				things.append(b)

		# player 2 input
		if keys[pygame.K_RIGHT]:
			player2.rotate(+5)
		if keys[pygame.K_LEFT]:
			player2.rotate(-5)
		if keys[pygame.K_UP]:
			player2.accellerate(+0.25)
		if keys[pygame.K_DOWN]:
			player2.accellerate(-0.1)
		if keys[pygame.K_RSHIFT]:
			b = player2.shoot()
			if b != False:
				things.append(b)

		# do game state updates
		for thing in things:
			thing.checkCollision(player1)
			thing.checkCollision(player2)
			thing.checkCollision(blackhole)
			thing.update(things)

		# initialize buffer
		buff.fill(BLACK)

		# draw the things
		for thing in things:
			thing.display(buff)

		# draw health bars
		c1 = player1.color
		r1 = pygame.Rect(20, 20, 100, 10)
		h1 = pygame.Rect(20, 20, player1.health, 10)
		pygame.draw.rect(buff, (c1[0], c1[1], c1[2], 128), h1)
		pygame.draw.rect(buff, (c1[0], c1[1], c1[2], 128), r1, 1)

		c2 = player2.color
		r2 = pygame.Rect(WIDTH - 120, 20, 100, 10)
		h2 = pygame.Rect(WIDTH - 120, 20, player2.health, 10)
		pygame.draw.rect(buff, (c2[0], c2[1], c2[2], 128), h2)
		pygame.draw.rect(buff, (c2[0], c2[1], c2[2], 128), r2, 1)

		# draw lives
		l1.x = 140
		for i in range(player1.lives):
			l1.display(buff)
			l1.x += 10

		l2.x = WIDTH-140
		for i in range(player2.lives):
			l2.display(buff)
			l2.x -= 10

		# draw buffer onto the screen (alpha blending)
		screen.blit(buff, (0,0))
		
	def mainMenuLoop():
		global menuSelection
		options = [ 
			'Game', \
			'Quit']
		def startAction():
			global state
			state = gameLoop
		def quitAction():
			quit()

		actions = [startAction, quitAction]

		# event driven menu navigation
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
			if event.type == pygame.KEYDOWN and event.key in \
					(pygame.K_UP, pygame.K_a):
				menuSelection = (menuSelection + 1) % len(options)
			if event.type == pygame.KEYDOWN and event.key in \
					(pygame.K_DOWN, pygame.K_s):
				menuSelection = (menuSelection - 1) % len(options)
			if event.type == pygame.KEYDOWN and event.key in \
					(pygame.K_SPACE, pygame.K_RETURN):
				actions[menuSelection]()
		
		# render menu items	
		for i in range(len(options)):
			color = textColor
			if i == menuSelection:
				color = selected

			text = font.render(options[i], 1, color)
			screen.blit(text, (WIDTH*0.25, HEIGHT*0.25 + FONTSIZE*2*i)) #TODO test me!

	state = mainMenuLoop
		
	# game loop
	while True:
		# initialize screen
		screen.fill(BLACK)

		# do the loop for the current state
		state()

		# show stuff on screen
		pygame.display.flip()

		#do loop at 60 fps
		clock.tick(60)

if __name__ == '__main__': main()
