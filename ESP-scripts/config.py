import keyboard
import time
import pygame

process = True
initialize = True

mode = "600p"

BG = (15,  14,  20)

class Update :
	def display_settings(mode) :
		if mode == "480p" :
			screen = pygame.display.set_mode((640, 480),pygame.RESIZABLE)
		if mode == "600p" :
			screen = pygame.display.set_mode((960, 600),pygame.RESIZABLE)
		if mode == "720p" :
			screen = pygame.display.set_mode((1280, 720),pygame.RESIZABLE)
		if mode == "1080p" :
			screen = pygame.display.set_mode((1920, 1080),pygame.RESIZABLE)
		screen.fill(BG)
		pygame.display.update()

def initialize_display(mode) :	
	Update.display_settings(mode)
	initialize = False

Update.display_settings(mode)

while process :
	
	clock  = pygame.time.Clock()
	mx, my = pygame.mouse.get_pos()

	time.sleep(0.1)
	press = False
		
#	if initialize :
#		initialize_display(mode)

	if keyboard.is_pressed('1') and mode != "480p":
		press = True
		mode = "480p"
		print(f"{mode} resolution set")
		Update.display_settings(mode)
		press = False

	if keyboard.is_pressed('2') and mode != "600p" :
		press = True
		mode = "600p"
		print(f"{mode} resolution set")
		Update.display_settings(mode)
		press = False

	if keyboard.is_pressed('3') and mode != "720p" :
		press = True
		mode = "720p"
		print(f"{mode} resolution set")
		Update.display_settings(mode)
		press = False

	if keyboard.is_pressed('esc'):
		process = False
		print("exiting process")
	
	pygame.display.update()