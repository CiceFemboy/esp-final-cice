import keyboard
import time
import pygame
import mouse

process = True
initialized = False

WHITE = (230, 230, 230)

ES_CONTINUOUS = 0x80000000

class Display :
	
	def update():
		pygame.display.update()

	def initialize() :
		screen = pygame.display.set_mode((1280, 720),pygame.RESIZABLE)
		screen.fill(WHITE)	
		pygame.display.update()
		initialized = True

Display.initialize()

while process :

	time.sleep(0.1)

	x, y = mouse.get_position()
		
	if mouse.is_pressed() :
		coordinates = [x, y]
		print(coordinates)

	if keyboard.is_pressed('esc'):
		process = False
		print("exiting process")

	Display.update()