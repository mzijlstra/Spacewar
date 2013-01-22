import pygame, math, random
import classes as c
import menus as m
import spacewar as sw

class Game:
	color1 = (255,100,100, 250) # TODO would be nice to have player colors in settings
	color2 = (100,100,255, 250)

	def __init__(self, state):
		self.state = state
		SIZE = WIDTH, HEIGHT = state.size

		self.buff = pygame.Surface(SIZE, flags=pygame.SRCALPHA, depth=32)
		self.buff = self.buff.convert_alpha()

		self.font = pygame.font.SysFont('monospace', m.Menu.fontsize)
		self.font.set_bold(True)
		self.textcolor = (255,255,255)
		self.winner = False
		self.initThings()
		self.createBackGround(WIDTH, HEIGHT)

	def initThings(self):
		WIDTH, HEIGHT = self.state.size
		self.player1 = c.Player(Game.color1, WIDTH/2 - WIDTH/4, HEIGHT/2, 180, 'left')
		self.player2 = c.Player(Game.color2, WIDTH/2 + WIDTH/4, HEIGHT/2, 0, 'right')
		self.blackhole = c.GravityWell(WIDTH/2, HEIGHT/2, 15, 5.5)
		self.things = [self.player1, self.player2, self.blackhole]

	def createBackGround(self, width, height):
		self.bg = pygame.Surface((width, height), flags=pygame.SRCALPHA, depth=32)
		self.bg.fill((0,0,0))

		# draw stars
		pxarray = pygame.PixelArray(self.bg)
		for i in range(3000):
			x = random.randrange(width)	
			y = random.randrange(height)
			c = random.randrange(256)
			pxarray[x][y] = (c, c, c)
		del pxarray

		# draw elements that don't change
		for thing in self.things:
			thing.drawBg(self.bg)

		self.bg = self.bg.convert()

	def resize(self, width, height): 
		for thing in self.things:
			thing.resize(width, height)
		
		self.buff = pygame.Surface((width, height), flags=pygame.SRCALPHA, depth=32)
		self.buff = self.buff.convert_alpha()
		self.createBackGround(width, height)
		
	def loop(self, screen):
		'Main game loop checks input, does state updates, draws game to screen'

		# quit on window close 
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				sw.quit()

			elif event.type == pygame.KEYDOWN:
				# player 1 system selection
				if event.key == pygame.K_TAB:
					self.player1.nextsystem(1)
				elif event.key == pygame.K_BACKQUOTE:
					self.player1.nextsystem(-1)
				# player 2 system selection
				elif event.key == pygame.K_BACKSLASH:
					self.player2.nextsystem(1)
				elif event.key == pygame.K_BACKSPACE:
					self.player2.nextsystem(-1)
					

		# general input
		keys = pygame.key.get_pressed()
		if keys[pygame.K_ESCAPE]:
			self.state.current = self.state.mainMenu

		# while we haven't lost / won
		if self.winner == False:
			# player 1 input - movement
			if keys[pygame.K_d]:
				self.player1.rotate(+5)
			if keys[pygame.K_a]:
				self.player1.rotate(-5)
			if keys[pygame.K_w]:
				self.player1.accellerate(+0.25)
			if keys[pygame.K_s]:
				self.player1.accellerate(-0.1)

			# actions: shoot, jump, shield
			if keys[pygame.K_LSHIFT]:
				b = self.player1.shoot()
				if b != False:
					self.things.append(b)
			if keys[pygame.K_z]:
				self.player1.hyperjump()
			if keys[pygame.K_LCTRL]:
				self.player1.shield()
			
			# energy management:
			if keys[pygame.K_q]:
				self.player1.energy(-1)
			if keys[pygame.K_e]:
				self.player1.energy(+1)


			# player 2 input - movement
			if keys[pygame.K_RIGHT]:
				self.player2.rotate(+5)
			if keys[pygame.K_LEFT]:
				self.player2.rotate(-5)
			if keys[pygame.K_UP]:
				self.player2.accellerate(+0.25)
			if keys[pygame.K_DOWN]:
				self.player2.accellerate(-0.1)

			# actions: shoot, jump, shield
			if keys[pygame.K_RSHIFT]:
				b = self.player2.shoot()
				if b != False:
					self.things.append(b)
			if keys[pygame.K_SLASH]:
				self.player2.hyperjump()
			if keys[pygame.K_PERIOD]:
				self.player2.shield()

			# energy management:
			if keys[pygame.K_LEFTBRACKET]:
				self.player2.energy(-1)
			if keys[pygame.K_RIGHTBRACKET]:
				self.player2.energy(+1)

			# do updates and check collisions
			for thing in self.things:
				for thing2 in self.things:
					if isinstance(thing2, c.Bullet):
						break
					thing.checkCollision(thing2)
				thing.update(self.things)
				#thing.checkCollision(self.player2)
				#thing.checkCollision(self.blackhole)
			
			# check win condition
			if self.player1.lives < 0 and self.player2.lives < 0:
				self.winner = "It's a Tie!"
			elif self.player1.lives < 0:
				self.winner = 'Player 2 has won!'
				self.textcolor = self.player2.color
			elif self.player2.lives < 0:
				self.winner = 'Player 1 has won!'
				self.textcolor = self.player1.color

			# remove resume if game is over
			if self.player1.lives < 0 or self.player2.lives < 0:
				self.state.mainMenu.items.pop(0)

		# initialize screen
		screen.blit(self.bg, (0,0))

		# clear buffer
		self.buff.fill((0,0,0,0))

		# draw the things
		for thing in self.things:
			thing.display(self.buff)

		# display who has won
		if self.winner != False:
			text = self.font.render(self.winner, 1, self.textcolor)
			rect = text.get_rect()
			WIDTH, HEIGHT = self.state.size
			self.buff.blit(text, (WIDTH/2 - rect.w / 2, HEIGHT/4))

		# draw buffer onto the screen (alpha blending)
		screen.blit(self.buff, (0,0))

class RandomGame(Game):
	def initThings(self):
		WIDTH, HEIGHT = self.state.size
		self.things = []
		holes = random.randrange(1, 4)
		for i in range(holes + 1):
			(x,y) = self.getLocation()
			rad = random.randrange(0, 30)
			pow = random.uniform(2.5, 7.5)
			self.things.append(c.GravityWell(x, y, rad, pow))

		(x,y) = self.getLocation()
		rot = random.randrange(0, 360)
		self.player1 = c.Player(Game.color1, x, y, rot, 'left')
		self.things.append(self.player1)

		(x,y) = self.getLocation()
		rot = random.randrange(0, 360)
		self.player2 = c.Player(Game.color2, x, y, rot, 'right')
		self.things.append(self.player2)

	def getLocation(self):
		WIDTH, HEIGHT = self.state.size
		close = True
		while close:
			close = False
			x = random.randrange(0, WIDTH)
			y = random.randrange(0, HEIGHT)
			for thing in self.things:
				dx = thing.x - x
				dy = thing.y - y
				hyp = math.hypot(dx, dy)
				if hyp < 40:
					close = True
		return (x,y)
		
