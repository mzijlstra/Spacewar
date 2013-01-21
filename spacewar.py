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
		self.width = 1024
		self.height = 768
		self.readSettings()
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
				if parser.get('video', 'ratio') == '16x9':
					self.width = 1280
					self.height = 720
				elif parser.get('video', 'ratio') == '16x10':
					self.width = 1200
					self.height = 800
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
			ratio = '4x3'
			if self.height == 768:
				ratio = '4x3'
			elif self.height == 720:
				ratio = '16x9'
			elif self.height == 800:
				ratio = '16x10'
			parser.set('video', 'ratio', ratio)

			file = open('settings.ini', 'w')
			parser.write(file)
			file.close()
		except Exception as e:
			print(e)

def resumeAction():
	State().current = State().game

def startAction():

	state = State()
	game = g.Game(state)
	state.game = game
	state.current = game

	if state.mainMenu.items[0].text != 'Resume':
		state.mainMenu.items.insert(0, m.MenuItem('Resume', resumeAction))

def backToMainMenu():
	State().current = State().mainMenu


def optionsAction():
	state = State()
	items = []

	fullint = 0
	if state.fullscreen != 0:
		fullint = 1
	fullscreenOption = m.MenuValues('Fullscreen', ['Off', 'On'], fullint)

	ratioint = 0
	if state.height ==  720:
		ratioint = 1
	elif state.height == 800:
		ratioint = 2
	ratioOption = m.MenuValues('Aspect Ratio', ['4x3', '16x9', '16x10'], ratioint)

	def confirmOptionsAction():
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
	items.append(m.MenuItem('OK', confirmOptionsAction))
	items.append(m.MenuCancel('Cancel', backToMainMenu))
	state.current = m.Menu(state, items)

def quit():
	pygame.quit()
	sys.exit()

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
	items.append(m.MenuItem('New Game', startAction))
	items.append(m.MenuItem('Options', optionsAction))
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
