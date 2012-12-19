import pygame, os, sys, math, random
from math import cos, sin

# global vars
BLACK = 0, 0, 0
WHITE = 255,255,255
#SIZE = WIDTH, HEIGHT = 1280, 800
SIZE = WIDTH, HEIGHT = 800,600

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

	def checkCollision(self, other):
		if other != self and isinstance(other, Player):
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			dist -= 2*5 #5 is the player shield radius
			if dist <= 0:
				other.vel, other.dir, self.vel, self.dir = self.vel, self.dir, other.vel, other.dir
				self.update()
				other.update()

	def reset(self):
		self.x = self.orig['x']
		self.y = self.orig['y']
		self.rot = self.orig['rot']
		self.vel = 0

	def update(self, others=None):
		Movable.update(self)
		# TODO check collisions with others

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
		rad = math.radians(self.rot)
		x = self.x + math.cos(rad) * 7
		y = self.y + math.sin(rad) * 7
		b = Bullet(x, y, self.vel, self.dir, self.color)
		b.applyForce(3, self.rot)
		return b

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

	def checkCollision(self, player):
		if isinstance(player, Player):
			dx = self.x - player.x
			dy = self.y - player.y
			hyp = math.hypot(dx, dy)
			if hyp <= self.rad:
				player.reset()


	def display(self, surface):
		pygame.draw.circle(surface, (255,255,255,255), (self.x, self.y), self.rad, 1)
		pygame.draw.circle(surface, (255,255,255,200), (self.x, self.y), self.rad + 1, 1)
		pygame.draw.circle(surface, (255,255,255,150), (self.x, self.y), self.rad + 2, 1)
		pygame.draw.circle(surface, (255,255,255,100), (self.x, self.y), self.rad + 3, 1)
		pygame.draw.circle(surface, (255,255,255,55), (self.x, self.y), self.rad + 4, 1)
		pygame.draw.circle(surface, (255,255,255,25), (self.x, self.y), self.rad + 5, 1)

class Bullet(Movable):
	def __init__(self, x, y, vel, dir, color):
		Movable.__init__(self, x, y, vel, dir)
		self.color = color
		self.ttl = 250

	def display(self, surface):
		color = self.color
		pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 1)
		pygame.draw.circle(surface, (color[0], color[1], color[2], 125), (int(self.x), int(self.y)), 2)

	def update(self, others):
		Movable.update(self)
		self.ttl -= 1
		if self.ttl < 0:
			others.remove(self)

	def checkCollision(self, other):
		if isinstance(other, GravityWell):
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			if dist <= other.rad:
				self.ttl = 0
		elif isinstance(other, Player):
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			if dist <= 5: # shield radius
				other.applyForce(self.vel, self.dir)
				self.ttl = 0
		
def keyboardInput(player1, player2, mobs):
	# quit on window close or escape key
	for event in pygame.event.get():
		if event.type == pygame.QUIT \
		   or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
			pygame.quit()
			sys.exit()

	# player 1
	keys = pygame.key.get_pressed()
	if keys[pygame.K_d]:
		player1.rotate(+5)
	if keys[pygame.K_a]:
		player1.rotate(-5)
	if keys[pygame.K_w]:
		player1.accellerate(+0.25)
	if keys[pygame.K_s]:
		player1.accellerate(-0.1)
	if keys[pygame.K_LSHIFT]:
		mobs.append(player1.shoot())

	# player 2
	if keys[pygame.K_RIGHT]:
		player2.rotate(+5)
	if keys[pygame.K_LEFT]:
		player2.rotate(-5)
	if keys[pygame.K_UP]:
		player2.accellerate(+0.25)
	if keys[pygame.K_DOWN]:
		player2.accellerate(-0.1)
	if keys[pygame.K_RSHIFT]:
		mobs.append(player2.shoot())
	

def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	screen = pygame.display.set_mode(SIZE)
	buff = pygame.Surface(SIZE, flags=pygame.SRCALPHA, depth=32)
	clock = pygame.time.Clock()

	player1 = Player((255,100,100, 250), x=WIDTH/2 - WIDTH/4, y=HEIGHT/2, rot=180)
	player2 = Player((100,100,255, 250), x=WIDTH/2 + WIDTH/4, y=HEIGHT/2, rot=0)
	blackhole = GravityWell(WIDTH/2, HEIGHT/2, 15, 5.5)

	# list of game objects
	things = [player1, player2, blackhole]

	# game loop
	while True:
		keyboardInput(player1, player2, things)

		# do game state updates
		for thing in things:
			thing.update(things)
			thing.checkCollision(player1)
			thing.checkCollision(player2)
			thing.checkCollision(blackhole)

		#draw screen
		screen.fill(BLACK)
		buff.fill(BLACK)

		for thing in things:
			thing.display(buff)

		screen.blit(buff, (0,0))
		pygame.display.flip()

		#do loop at 40 fps
		clock.tick(40)

if __name__ == '__main__': main()
