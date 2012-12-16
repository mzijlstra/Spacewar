import pygame, os, sys, math, random
from math import cos, sin

# global vars
BLACK = 0, 0, 0
WHITE = 255,255,255
SIZE = WIDTH, HEIGHT = 1280, 800

class Player:
	
	def __init__(self, x=640, y=400, rot=0):
		self.x = x
		self.y = y
		self.rot = rot # angle we're facing
		self.vel = 0   # speed we're going
		self.dir = 0   # direction we're going

	def update(self):
		rad = math.radians(self.rot)
		dx = cos(rad) * self.vel
		dy = sin(rad) * self.vel
		self.x += dx
		self.y += dy

	def accellerate(self, val):
		self.vel += val
		if self.vel > 5:
			self.vel = 5
		if self.vel < 0:
			self.vel = 0

	def rotate(self, val):
		self.rot = self.rot + val
		if self.rot > 360:
			self.rot -= 360
		elif self.rot < -360:
			self.rot += 360

	def display(self, surface):
		points = []
		# first define the points relative to our x and y
		points.append([10, 0])
		points.append([-10, 10])
		points.append([-5, 0])
		points.append([-10, -10])

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

		pygame.draw.polygon(surface, (255,255,255,250), points)

def main():
	# basic init
	os.environ['SDL_VIDEO_CENTERED'] = '1'
	pygame.init()

	screen = pygame.display.set_mode(SIZE)
	buff = pygame.Surface(SIZE, flags=pygame.SRCALPHA, depth=32)
	clock = pygame.time.Clock()

	player = Player()


	# game loop
	while True:

		# quit on window close or escape key
		for event in pygame.event.get():
			if event.type == pygame.QUIT \
			   or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
				pygame.quit()
				sys.exit()


		# move paddle based on left and right arrows
		keys = pygame.key.get_pressed()
		if keys[pygame.K_e]:
			player.rotate(+1)
		if keys[pygame.K_q]:
			player.rotate(-1)
		if keys[pygame.K_w]:
			player.accellerate(+0.25)
		if keys[pygame.K_s]:
			player.accellerate(-0.1)

		# do game state updates
		player.update()

		#draw screen
		screen.fill(BLACK)
		buff.fill(BLACK)
		player.display(buff)
		screen.blit(buff, (0,0))
		pygame.display.flip()


		#do all this at 40 fps
		clock.tick(40)

if __name__ == '__main__': main()
