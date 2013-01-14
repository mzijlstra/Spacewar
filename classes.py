import pygame, math, random
from math import cos, sin
import spacewar
from spacewar import SIZE, WIDTH, HEIGHT

def enum(*sequential, **named):
	enums = dict(zip(sequential, range(len(sequential))), **named)
	reverse = dict((value, key) for key, value in enums.iteritems())
	enums['reverse'] = reverse
	return type('Enum', (), enums)

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

	# default usage amounts (out of 100)
	use = {}
	use['ammo'] = 3
	use['shield'] = 2
	use['engine'] = 5
	use['jump'] = 75

	# default recharge rates (per frame)
	# these are considered to be at 50%
	rate = {}
	rate['hull']   = 0.05
	rate['ammo']   = 0.2
	rate['shield'] = 0.25
	rate['engine'] = 1.0
	rate['jump']   = 0.25
	rateColor = (0,255,0,128)
	selectedRateColor = (255, 255, 128, 200)

	# TODO if rate is too low some systems should degrade
	# Perhapse define a wear rate for each system as well? 

	system = enum('hull', 'ammo', 'shield', 'engine', 'jump')

	def __init__(self, color, x, y, rot, barLoc, livesLoc):
		Movable.__init__(self, x, y, 0, 0)
		self.color = color
		self.rot = rot # angle we're facing

		# player attributes
		self.lives = 4

		# each new live needs to start atoriginal x/y/rot
		self.orig = {}
		self.orig['x'] = x
		self.orig['y'] = y
		self.orig['rot'] = rot

		# reset removes a live, sets:
		# health, ammo, shield, engine, jump
		self.system = {}
		self.rate   = {}
		Player.reset(self)

		# state related attributes
		self.accelerating = 0
		self.shooting = 0
		self.shieldUp = 0
		self.cursysnum = 0

		# UI elements for this player
		font = pygame.font.SysFont('monospace', 12)
		self.uicolor = self.color[0], self.color[1], self.color[2], 128
		self.barLoc = barLoc
		self.livesLoc = livesLoc
		self.uitext = []
		self.uitext.append(font.render('H', 1, self.uicolor))
		self.uitext.append(font.render('A', 1, self.uicolor))
		self.uitext.append(font.render('S', 1, self.uicolor))
		self.uitext.append(font.render('E', 1, self.uicolor))
		self.uitext.append(font.render('J', 1, self.uicolor))

	def reset(self):
		self.lives -= 1
		self.x = self.orig['x']
		self.y = self.orig['y']
		self.rot = self.orig['rot']
		self.vel = 0

		self.system['hull']   = 100
		self.system['ammo']   = 100
		self.system['shield'] = 100
		self.system['engine'] = 100
		self.system['jump']   = 100

		self.rate['hull']   = Player.rate['hull']
		self.rate['ammo']   = Player.rate['ammo']
		self.rate['shield'] = Player.rate['shield']
		self.rate['engine'] = Player.rate['engine']
		self.rate['jump']   = Player.rate['jump']

	def update(self, others=None):
		Movable.update(self)

		# state related checks
		if self.shooting > 0:
			self.shooting -= 1
		if self.accelerating > 0:
			self.accelerating -= 1
		if self.shieldUp > 0:
			self.shieldUp -= 1
		if self.system['hull'] <= 0:
			self.reset()

		# energy management
		if self.system['hull'] < 100:
			self.system['hull'] += self.rate['hull']
		if self.system['ammo'] < 100:
			self.system['ammo'] += self.rate['ammo']
		if self.system['shield'] < 100:
			self.system['shield'] += self.rate['shield']
		if self.system['engine'] < 100:
			self.system['engine'] += self.rate['engine']
		if self.system['jump'] < 100:
			self.system['jump'] += self.rate['jump']

	def rotate(self, val):
		self.rot = self.rot + val
		if self.rot > 360:
			self.rot -= 360
		elif self.rot < -360:
			self.rot += 360

	def accellerate(self, val):
		if self.system['engine'] > 5:
			self.applyForce(val, self.rot)
			self.accelerating = 2
			self.system['engine'] -= Player.use['engine']

	def shoot(self):
		if self.shooting == 0 and self.system['ammo'] >= 2:
			rad = math.radians(self.rot)
			x = self.x + math.cos(rad) * 7
			y = self.y + math.sin(rad) * 7
			
			b = Bullet(x, y, self.vel, self.dir, self.color)
			b.applyForce(3, self.rot)
			b.update()

			self.shooting = 3
			self.system['ammo'] -= Player.use['ammo']
			return b
		else:
			return False

	def shield(self):
		if self.system['shield'] >= 2:
			self.shieldUp = 2 # will be reduced by 1 before display
			self.system['shield'] -= Player.use['shield']

	def hyperjump(self):
		# Question: should we maintain velocity after jumping?
		# Answer: not sure, we'll say yes for now
		if self.system['jump'] >= 75: 
			self.x = random.randrange(0, WIDTH)
			self.y = random.randrange(0, HEIGHT)
			self.system['jump'] -= Player.use['jump']

	def nextsystem(self, inc=1):
		self.cursysnum = (self.cursysnum + inc) % 5

	def __adjustenergy(self, systemnum, amount, test=False):
		'''private helper function takes system number, amount
		and whether it should just test or actually do it
		returns how much actually adjusted'''

		# get system name from system number
		system = Player.system.reverse[systemnum]

		# normalize the rate into range 0-100
		rate = self.rate[system] / (Player.rate[system] / 50)

		added = amount
		if rate + amount > 100:
			added = 100 - rate
			rate = 100
		elif rate + amount < 0:
			added = -rate
			rate = 0
		else:
			rate += amount

		# convert back and store
		if test != True:
			self.rate[system] = rate * (Player.rate[system] / 50)

		return added
	
	def energy(self, amount=1):
		# test how much we can add
		toadd = self.__adjustenergy(self.cursysnum, amount, test=True)
		
		# exit out if we're not doing anything anyway
		if toadd == 0:
			return

		# toadd needs to come from other systems' energy
		ignored = [self.cursysnum]
		removed = False

		while not removed:
			adjust = float(-toadd) / (5 - len(ignored))
			cando = True

			# find systems that can support adjustment
			for i in range(5):
				if i not in ignored:
					possible = self.__adjustenergy(i, adjust, test=True)
					if possible != adjust:
						ignored.append(i)
						cando = False
						break; # and try with less systems

			# actually do it
			if cando:
				for i in range(5):
					if i not in ignored:
						self.__adjustenergy(i, adjust)
				removed = True

		#for i in ignored:
		#	system = Player.system.reverse[i]
		#	print(i, self.rate[system] / (Player.rate[system] / 50), len(ignored))

		# now that it's removed from others actually add to self
		self.__adjustenergy(self.cursysnum, toadd)


	def checkCollision(self, other):
		if other != self and isinstance(other, Player):
			dx = self.x - other.x
			dy = self.y - other.y
			dist = math.hypot(dx, dy)
			dist -= 2*5 #5 is the player damage

			# shields up also makes collision sooner
			if self.shieldUp > 0:
				dist -= 5
			if other.shieldUp > 0:
				dist -= 5

			if dist <= 0:
				# the length of the collision vector 
				# is with how much force they hit
				dxa = cos(math.radians(self.dir)) * self.vel
				dya = sin(math.radians(self.dir)) * self.vel
				dxb = cos(math.radians(other.dir)) * other.vel
				dyb = sin(math.radians(other.dir)) * other.vel
				dx = dxa - dxb
				dy = dya - dyb
				length = math.hypot(dx, dy)

				# do damage based on the force mutiplied by 5
				# seems about right when no shield, maybe a bit low
				# when shields are up just bounce, no shield half bounce
				if self.shieldUp > 0 and other.shieldUp > 0:
					# bounce away from each other
					other.vel, self.vel = self.vel, other.vel
					other.dir, self.dir = self.dir, other.dir
				elif self.shieldUp	> 0 and other.shieldUp == 0:
					other.vel, self.vel = self.vel*0.5, other.vel
					other.dir, self.dir = self.dir, other.dir
					other.system['hull'] -= length * 5
				elif self.shieldUp == 0 and other.shieldUp > 0:
					other.vel, self.vel = self.vel, other.vel*0.5
					other.dir, self.dir = self.dir, other.dir
					self.system['hull'] -= length * 5 
				else: # self.shieldUp == 0 and other.shieldUp == 0
					other.vel, self.vel = self.vel*0.5, other.vel*0.5
					other.dir, self.dir = self.dir, other.dir
					self.system['hull'] -= length * 5 
					other.system['hull'] -= length * 5

				# make sure they're moved appart
				Movable.update(self)
				Movable.update(other)

		if isinstance(other, GravityWell):
			dx = self.x - other.x
			dy = self.y - other.y
			hyp = math.hypot(dx, dy)
			if hyp <= other.rad:
				self.reset()

	@staticmethod
	def rotateAndMove(points, rot, (x,y)):
		'Helper function to rotate list of points'
		# then rotate according to our rot
		rad = math.radians(rot)
		for point in points:
			curx = point[0]
			cury = point[1]
			point[0] = curx*cos(rad) - cury*sin(rad)
			point[1] = curx*sin(rad) + cury*cos(rad)

		for point in points:
			point[0] += x
			point[1] += y

	@staticmethod
	def renderShip(surface, (x,y), rot, color, accel=False):
		'static helper method to draw a ship at a specific location'

		points = []
		# first define the points relative to our x and y
		points.append([7, 0])
		points.append([-5, 5])
		points.append([-1, 0])
		points.append([-5, -5])

		# do rotation, and move to screen position
		Player.rotateAndMove(points, rot, (x,y)) 

		# draw player at current location
		pygame.draw.polygon(surface, color, points)

		# draw flame for acceleration
		if accel > 0:
			points = []
			points.append([-2,0])
			points.append([-4,-1])
			points.append([-6,0])
			points.append([-4,1])
			Player.rotateAndMove(points, rot, (x,y))
			pygame.draw.polygon(surface, (225,225,0), points)

	def drawShipSystem(self, surface, rect, sysnum, textx): 
		# get system name from number
		system = Player.system.reverse[sysnum]
		
		# draw containing rectangle
		pygame.draw.rect(surface, self.uicolor, rect, 1)
		
		# draw power level for this system
		power = pygame.Rect(rect.x, rect.y, self.system[system], 10) 
		pygame.draw.rect(surface, self.uicolor, power)
		
		# blit system letter
		texty = rect.y - 1
		surface.blit(self.uitext[sysnum], (textx, rect.y - 1))

		# draw the recharge rate line
		rate = 50 / Player.rate[system] * self.rate[system]
		color = Player.rateColor
		if sysnum == self.cursysnum:
			color = Player.selectedRateColor
		pygame.draw.line(surface, color, (rect.x, rect.y + 12), (rect.x + rate, rect.y + 12))
		

	def display(self, surface):
		# draw player ship at current location
		if self.lives >= 0:
			Player.renderShip(surface, (self.x,self.y), self.rot, self.color, self.accelerating)

		# draw shield around player if shield is on
		if self.shieldUp > 0:
			pygame.draw.circle(surface, (255,255,255), (int(self.x), int(self.y)), 12, 1)

		# health bar location for this player
		barx = self.barLoc[0]
		bary = self.barLoc[1]

		# draw extra lives for this player
		livesx = self.livesLoc[0]
		livesy = self.livesLoc[1]
		livesdx = 10
		if livesx < barx:
			livesdx = -10

		# draw one ship for each extra live
		for i in range(self.lives):
			# TODO check that this doesn't take too much computing
			# could make the default rotation up, might save some cycles
			Player.renderShip(surface, (livesx, livesy), 270, self.uicolor)
			livesx += livesdx

		# draw the power levels for the different ship systems
		rect = pygame.Rect(barx, bary, 100, 10) 
		textx = self.barLoc[0] - 10
		if livesx < barx:
			textx = self.barLoc[0] + 105

		for i in range(5):
			self.drawShipSystem(surface, rect, i, textx)
			rect.y += 15


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
		if self.ttl > 0:
			pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 1)
			pygame.draw.circle(surface, (color[0], color[1], color[2], 125), (int(self.x), int(self.y)), 2)
		elif self.ttl <= 0:
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
		if self.ttl > 0: # only bullets that are not exploding
			if isinstance(other, Player):
				dx = self.x - other.x
				dy = self.y - other.y
				dist = math.hypot(dx, dy)

				if other.shieldUp > 0:
					# 12 radius of shield?
					# this also means that own bullets (being shot)
					# can not go from inside to outside shield
					if dist <= 12:
						other.applyForce(self.vel / 5, self.dir)
						if self.ttl > 0:
							self.ttl = 0
				else: # noshield
					# 5 radius is ship damage?
					if dist <= 5: 
						other.applyForce(self.vel / 10, self.dir)
						other.system['hull'] -= 25
						if self.ttl > 0:
							self.ttl = 0

			if isinstance(other, GravityWell):
				dx = self.x - other.x
				dy = self.y - other.y
				dist = math.hypot(dx, dy)
				if dist <= other.rad and self.ttl > 0:
					self.ttl = 0
		
