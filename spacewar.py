import pygame, os, sys, math
import classes as c
import games as g
import menus as m 

# global vars
#SIZE = WIDTH, HEIGHT = 1280, 800
SIZE = WIDTH, HEIGHT = 1024,768

# game state global variables
#STATE = None
#GAME = None
#MAINMENU = None

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

def resumeAction():
	State().current = State().game

def startAction():
	game = g.Game()
	State().game = game
	State().current = game

	if State().mainMenu.items[0].text != 'Resume':
		State().mainMenu.items.insert(0, MenuItem('Resume', resumeAction))

def backToMainMenu():
	State().current = State().mainMenu

def confirmOptionsAction():
	backToMainMenu()

def optionsAction():
	items = []
	items.append(m.MenuValues('Fullscreen', ['Off', 'On'], 0))
	items.append(m.MenuItem('OK', confirmOptionsAction))
	items.append(m.MenuCancel('Cancel', backToMainMenu))
	State().current = m.Menu(items)

def quit():
	pygame.quit()
	sys.exit()

def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()
	pygame.font.init()

	# setup the screen, double buffer and game clock
	screen = pygame.display.set_mode(SIZE)
	clock = pygame.time.Clock()

	# create main menu
	items = []
	items.append(m.MenuItem('New Game', startAction))
	items.append(m.MenuItem('Options', optionsAction))
	items.append(m.MenuItem('Quit', quit))
	options = ['New Game','Quit']

	# start in the main menu
	mainMenu = m.Menu(items)
	State().mainMenu = mainMenu
	State().current = mainMenu


	# core game loop
	while True:
		# initialize screen
		screen.fill((0,0,0))

		# do the loop for the current state (passing in state)
		State().current.loop(screen)

		# show stuff on screen
		pygame.display.flip()

		#do loop at 60 fps
		clock.tick(60)

if __name__ == '__main__': main()
