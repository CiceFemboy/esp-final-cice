import keyboard
import time
import pygame
import pynput
from pynput.mouse import Listener
import ctypes
#import mouse

process = True
initialized = False
#pressed = False

WHITE = (230, 230, 230)

ctypes.windll.user32.DisableProcessWindowsGhosting()

class Display :
	
	def update():
		pygame.display.update()

	def initialize() :
		screen = pygame.display.set_mode((1280, 720),pygame.RESIZABLE)
		screen.fill(WHITE)	
		pygame.display.update()
		initialized = True

Display.initialize()

def click(x, y, button, pressed):
	if pressed:
		coordinates = [x, y]
		print(coordinates)

listener = Listener(on_click=click)
listener.start()

coordinate_creature_list = []

while process :
	
	Display.update()

	if keyboard.is_pressed('esc'):
		listener.stop()
		coordinates_creature_list = []
		process = False
		print("exiting process")

# (x, y) = mouse.get_position()
#
#if mouse.is_pressed() and not pressed:
#		coordinates = [x, y]
#		print(coordinates)
#		pressed = True
#		print("...")
#
#	if not mouse.is_pressed() and pressed:
#		pressed = False