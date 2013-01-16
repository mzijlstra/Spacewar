import pygame, os, sys, math
from math import cos, sin
from classes import *
		
class MenuItem:
	def __init__(self, text, action):
		self.text = text
		self.action = action

	def getText(self):
		return self.text

	def doAction(self):
		self.action()

	def nextValue(self, num):
		pass


class MenuValues:
	def __init__(self, text, values):
		self.text = text
		self.values = values
		self.curval = 0

	def getText(self):
		return '{} {}'.format(self.text, self.values[self.curval])

	def doAction(self):
		pass

	def nextValue(self, num):
		self.curval = (self.curval + num) % len(self.values)
		

class Menu:
	fontsize = 25
	textcolor = (255,255,255)
	highlight = (255,255,0)

	def __init__(self, items):
		self.font = pygame.font.SysFont('monospace', Menu.fontsize)
		self.font.set_bold(True)
		self.items = items
		self.selected = 0
	
	def loop(self, screen):
		# event driven menu navigation
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()
			if event.type == pygame.KEYDOWN and event.key in \
					(pygame.K_UP, pygame.K_a):
				self.selected = (self.selected - 1) % len(self.items)
			if event.type == pygame.KEYDOWN and event.key in \
					(pygame.K_DOWN, pygame.K_s):
				self.selected = (self.selected + 1) % len(self.items)
			if event.type == pygame.KEYDOWN and event.key in \
					(pygame.K_SPACE, pygame.K_RETURN):
				self.items[self.selected].doAction()
		
		# render menu items	
		for i in range(len(self.items)):
			color = Menu.textcolor
			if i == self.selected:
				color = Menu.highlight

			text = self.font.render(self.items[i].getText(), 1, color)
			screen.blit(text, (WIDTH*0.25, HEIGHT*0.25 + Menu.fontsize*2*i))


class Game:
	def __init__(self):
		c1 = (255,100,100, 250) # would be nice to have player colors in settings
		c2 = (100,100,255, 250)
		self.player1 = Player(c1, WIDTH/2 - WIDTH/4, HEIGHT/2, 180, (20,20), (130,25))
		self.player2 = Player(c2, WIDTH/2 + WIDTH/4, HEIGHT/2, 0, (WIDTH - 120, 20), (WIDTH - 130, 25))
		self.blackhole = GravityWell(WIDTH/2, HEIGHT/2, 15, 5.5)

		self.things = [self.player1, self.player2, self.blackhole]
		self.buff = pygame.Surface(SIZE, flags=pygame.SRCALPHA, depth=32)

		self.winner = False
		self.font = pygame.font.SysFont('monospace', Menu.fontsize)
		self.font.set_bold(True)
		self.textcolor = (255,255,255)
		
	def loop(self, screen):
		'Main game loop checks input, does state updates, draws game to screen'

		global STATE
		global MAINMENU

		# quit on window close 
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				quit()

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
			STATE = MAINMENU

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
				thing.checkCollision(self.player1)
				thing.checkCollision(self.player2)
				thing.checkCollision(self.blackhole)
				thing.update(self.things)
			
			# check win condition
			if self.player1.lives < 0 and self.player2.lives < 0:
				self.winner = "It's a Tie!"
			elif self.player1.lives < 0:
				self.winner = 'Player 2 has won!'
				self.textcolor = self.player2.color
			elif self.player2.lives < 0:
				self.winner = 'Player 1 has won!'
				self.textcolor = self.player1.color
			if self.player1.lives < 0 or self.player2.lives < 0:
				MAINMENU.options.pop(0)
				MAINMENU.actions.pop(0)

		# clear buffer
		self.buff.fill((0,0,0))

		# draw the things
		for thing in self.things:
			thing.display(self.buff)

		# display who has won
		if self.winner != False:
			text = self.font.render(self.winner, 1, self.textcolor)
			rect = text.get_rect()
			self.buff.blit(text, (WIDTH/2 - rect.w / 2, HEIGHT/4))

		# draw buffer onto the screen (alpha blending)
		screen.blit(self.buff, (0,0))

# global vars
#SIZE = WIDTH, HEIGHT = 1280, 800
SIZE = WIDTH, HEIGHT = 1024,768

# game state global variables
STATE = None
GAME = None
MAINMENU = None

def quit():
	pygame.quit()
	sys.exit()

def main():
	global STATE
	global MAINMENU

	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()
	pygame.font.init()

	# setup the screen, double buffer and game clock
	screen = pygame.display.set_mode(SIZE)
	clock = pygame.time.Clock()

	# create main menu
	def startAction():
		global GAME
		global STATE

		GAME = Game()
		STATE = GAME

		def resumeAction():
			global STATE
			global GAME
			STATE = GAME

		if MAINMENU.items[0].text != 'Resume':
			MAINMENU.items.insert(0, MenuItem('Resume', resumeAction))

	items = []
	items.append(MenuItem('New Game', startAction))
	items.append(MenuItem('Quit', quit))
	options = ['New Game','Quit']
	MAINMENU = Menu(items)

	# start in the main menu
	STATE = MAINMENU

	# core game loop
	while True:
		# initialize screen
		screen.fill((0,0,0))

		# do the loop for the current state (passing in state)
		STATE.loop(screen)

		# show stuff on screen
		pygame.display.flip()

		#do loop at 60 fps
		clock.tick(60)

if __name__ == '__main__': main()
