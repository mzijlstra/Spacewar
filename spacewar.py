import pygame, os, sys, math
import ConfigParser 
import classes as c
import games as g
import menus as m 

def singleton(cls):
	instances = {}
	def getinstance():
		if cls not in instances:
			instances[cls] = cls()
		return instances[cls]
	return getinstance

@singleton
class State:
	def __init__(self):
		self.mainMenu = None
		self.current = None
		self.game = None
		self.screen = None

		self.fullscreen = 0
		self.ratio = '4x3'
		self.readSettings()
		self.setSizeWidthHeight()

	def setSizeWidthHeight(self):
		self.width = 1024
		self.height = 768
		if self.ratio == '16x9':
			self.width = 1280
			self.height = 720
		elif self.ratio == '16x10':
			self.width = 1200
			self.height = 800
		self.size = (self.width, self.height)

	
	def readSettings(self):
		parser = ConfigParser.SafeConfigParser()
		try:
			parser.read('settings.ini')
			if parser.has_option('video', 'fullscreen') and \
				parser.get('video', 'fullscreen') in ['on', 'yes', '1']:
				self.fullscreen = pygame.FULLSCREEN
			else:
				self.fullscreen = 0

			if parser.has_option('video', 'ratio'):
				self.ratio = parser.get('video', 'ratio')
		except Exception as e:
			print(e)
			self.writeSettings()

	def writeSettings(self):
		parser = ConfigParser.SafeConfigParser()
		try:
			parser.read('settings.ini')
			if not parser.has_section('video'):
				parser.add_section('video')
			parser.set('video', 'fullscreen', 'off' if self.fullscreen == 0 else 'on')
			parser.set('video', 'ratio', self.ratio)
			file = open('settings.ini', 'w')
			parser.write(file)
			file.close()
		except Exception as e:
			print(e)


def resume():
	State().current = State().game

def startClassic():
	state = State()
	game = g.Game(state)
	state.game = game
	state.current = game

	if state.mainMenu.items[0].text != 'Resume':
		state.mainMenu.items.insert(0, m.MenuItem('Resume', resume))

def startRandom():
	state = State()
	game = g.RandomGame(state)
	state.game = game
	state.current = game

	if state.mainMenu.items[0].text != 'Resume':
		state.mainMenu.items.insert(0, m.MenuItem('Resume', resume))

def backToMainMenu():
	State().current = State().mainMenu

def quit():
	pygame.quit()
	sys.exit()

def newGame():
	state = State()
	items = []
	items.append(m.MenuItem('Classic', startClassic))
	items.append(m.MenuItem('Random', startRandom))
	items.append(m.MenuItem('Main Menu', backToMainMenu))
	state.current = m.Menu(state, items)

def videoOptions():
	state = State()
	items = []

	fullint = 0
	if state.fullscreen != 0:
		fullint = 1
	fullscreenOption = m.MenuValues('Fullscreen', ['Off', 'On'], fullint)

	ratios = ['4x3', '16x9', '16x10']
	ratioint = ratios.index(state.ratio)
	ratioOption = m.MenuValues('Aspect Ratio', ratios, ratioint)

	def confirmOptions():
		if fullint != fullscreenOption.curval or ratioint != ratioOption.curval:

			# get fullscreen value
			setfull = state.fullscreen
			if fullscreenOption.curval == 0:
				setfull = 0
			elif fullscreenOption.curval == 1:
				setfull = pygame.FULLSCREEN

			# get aspect ratio value
			setsize = state.size
			if items[1].curval == 0:
				setsize = (1024,768)
			elif items[1].curval == 1:
				setsize = (1280,720)
			elif items[1].curval == 2:
				setsize = (1280,800)

			# apply changes
			state.screen = pygame.display.set_mode(setsize, setfull)
			state.fullscreen = setfull
			if ratioint != ratioOption.curval and state.game != None:
				state.game.resize(setsize[0], setsize[1])

			state.size = (state.width, state.height) = setsize
			state.writeSettings()

		backToMainMenu()
	
	items.append(fullscreenOption)
	items.append(ratioOption)
	items.append(m.MenuItem('OK', confirmOptions))
	items.append(m.MenuCancel('Cancel', backToMainMenu))
	state.current = m.Menu(state, items)

def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()
	pygame.font.init()

	# setup the screen, double buffer and game clock
	state = State()
	state.screen = pygame.display.set_mode(state.size, state.fullscreen)
	clock = pygame.time.Clock()

	# create main menu
	items = []
	items.append(m.MenuItem('New Game', newGame))
	items.append(m.MenuItem('Options', videoOptions))
	items.append(m.MenuItem('Quit', quit))
	options = ['New Game','Quit']

	# start in the main menu
	mainMenu = m.Menu(state, items)
	state.mainMenu = mainMenu
	state.current = mainMenu
	c.Movable.state = state


	# core game loop
	while True:
		# do the loop for the current state (passing in state)
		state.current.loop(state.screen)

		# show stuff on screen
		pygame.display.flip()

		#do loop at 60 fps
		clock.tick(60)

if __name__ == '__main__': main()
