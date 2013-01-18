import pygame
import spacewar as sw

class MenuItem:
	def __init__(self, text, action):
		self.text = text
		self.action = action

	def doAction(self):
		self.action()

	def nextValue(self, num):
		pass

	def display(self, surface, pos, color):
		img = Menu.font.render(self.text, 1, color)
		surface.blit(img, pos)


class MenuValues:
	def __init__(self, text, values, current):
		self.text = text
		self.values = values
		self.curval = current

	def doAction(self):
		pass

	def nextValue(self, num):
		self.curval = (self.curval + num) % len(self.values)

	def display(self, surface, pos, color):
		disp = '{:20} {:>6}'.format(self.text, self.values[self.curval])
		img = Menu.font.render(disp, 1, color)
		surface.blit(img, pos)
		

class MenuCancel(MenuItem):
	def __init__(self, text, values):
		MenuItem.__init__(self, text, values)
		
	def display(self, surface, (x, y), color):
		img = Menu.font.render(self.text, 1, color)
		surface.blit(img, (x + 300, y - 2 * Menu.fontsize))
		

class Menu:
	fontsize = 25
	textcolor = (255,255,255)
	highlight = (255,255,0)

	def __init__(self, items):
		Menu.font = pygame.font.SysFont('monospace', Menu.fontsize)
		self.font.set_bold(True)
		self.items = items
		self.selected = 0
	
	def loop(self, screen):
		# event driven menu navigation
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				a.quit()
			if event.type == pygame.KEYDOWN:
				if event.key in (pygame.K_UP, pygame.K_w):
					self.selected = \
						(self.selected - 1) % len(self.items)
				elif event.key in (pygame.K_DOWN, pygame.K_s):
					self.selected = \
						(self.selected + 1) % len(self.items)
				elif event.key in (pygame.K_LEFT, pygame.K_a):
					self.items[self.selected].nextValue(-1)
				elif event.key in (pygame.K_RIGHT, pygame.K_d):
					self.items[self.selected].nextValue(1)
				elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
					self.items[self.selected].doAction()
		
		# render menu items	
		x = sw.WIDTH * 0.25
		y = sw.HEIGHT * 0.25
		for i in range(len(self.items)):
			color = Menu.textcolor
			if i == self.selected:
				color = Menu.highlight
			item = self.items[i]
			item.display(screen, (x, y), color)
			y += Menu.fontsize * 2
