import pygame, math
from math import cos, sin
import spacewar
from spacewar import SIZE, WIDTH, HEIGHT

def getDeg(dx, dy):
	'Helper function that returns degree based on slope'
	hyp = math.hypot(dx, dy)
	if hyp == 0:
		return 0.0
	deg = math.degrees(math.acos(dx / hyp))
	if dy < 0:
		deg = 360 - deg
	return deg

class Movable:
	'Super class for movable game objects'

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
	'Player class that extends Movable'

	def __init__(self, color, x, y, rot, healthLoc, livesLoc):
		Movable.__init__(self, x, y, 0, 0)
		self.color = color
		self.rot = rot # angle we're facing

		# player attributes
		self.health = 100
		self.lives = 3
		self.shooting = 0

		# each new live needs to start atoriginal x/y/rot
		self.orig = {}
		self.orig['x'] = x
		self.orig['y'] = y
		self.orig['rot'] = rot

		# UI elements for this player
		self.healthLoc = healthLoc
		self.livesLoc = livesLoc

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

	@staticmethod
	def renderShip(surface, (x,y), rot, color):
		'static helper method to draw a ship at a specific location'

		points = []
		# first define the points relative to our x and y
		points.append([5, 0])
		points.append([-5, 5])
		points.append([-2, 0])
		points.append([-5, -5])

		# then rotate according to our rot
		rad = math.radians(rot)
		for point in points:
			curx = point[0]
			cury = point[1]
			point[0] = curx*cos(rad) - cury*sin(rad)
			point[1] = curx*sin(rad) + cury*cos(rad)

		# then update the points to become absolute screen positions
		for point in points:
			point[0] += x
			point[1] += y

		# draw player at current location
		pygame.draw.polygon(surface, color, points)


	def display(self, surface):
		# draw player ship at current location
		if self.lives >= 0:
			Player.renderShip(surface, (self.x,self.y), self.rot, self.color)

		# draw health bar for this player
		uicolor = self.color[0], self.color[1], self.color[2], 128
		healthx = self.healthLoc[0]
		healthy = self.healthLoc[1]

		# first draw containing rectangle
		rect = pygame.Rect(healthx, healthy, 100, 10) 
		pygame.draw.rect(surface, uicolor, rect, 1)

		# then the actual health bar
		health = pygame.Rect(healthx, healthy, self.health, 10) 
		pygame.draw.rect(surface, uicolor, health)

		# draw extra lives for this player
		livesx = self.livesLoc[0]
		livesy = self.livesLoc[1]
		livesdx = 10
		if livesx < healthx:
			livesdx = -10
		
		# draw one ship for each extra live
		for i in range(self.lives):
			Player.renderShip(surface, (livesx, livesy), 270, uicolor)
			livesx += livesdx

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
		
