import keyboard
import json
import sys
import pygame
import math
import pynput
from pynput.mouse import Listener
import ctypes
#import mouse

process = True
#pressed = False

not_pressed1 = False
not_pressed2 = False
not_pressed3 = False
not_pressed4 = False

WHITE = (230, 230, 230)

FPS = 60

pygame.time.Clock()

coord_list = []
draw_coord_list = []
bodytypes_list = []
color_torso = ( 245, 10 , 10 )
color_leg = ( 10, 245 , 10 )
color_dot = ( 10 , 10 , 10 )
creature = { "bodies" : {}, "joints" : {} }
body_type_selected = "leg"

ctypes.windll.user32.DisableProcessWindowsGhosting()

class Display :

	def initialize() :
		screen = pygame.display.set_mode([1280, 720], pygame.RESIZABLE)
		clock  = pygame.time.Clock()
		pygame.display.update()
		screen.fill(WHITE)

	def update():
		pygame.display.update()

	def unload():
		pygame.display.quit()

Display.initialize()

def click(x, y, button, pressed):
	if pressed :
		wx, wy = pygame.display.get_window_position()
		mx, my = (x, y)
		tx = mx - wx
		ty = my - wy
		length, width = pygame.display.get_window_size()
		global body_type_selected
		
		if 0 < tx < length and 0 < ty < width :
			draw_coordinates = [tx , ty]
			coordinates = [tx - length // 2, ty - width // 2]
			global coord_list
			global draw_coord_list
			global bodytypes_list
			print(f"type de section selectioner : {body_type_selected}")
			if len(coord_list) <= 6 :
				coord_list.append(coordinates)
				draw_coord_list.append(draw_coordinates)
				if 1 < len(coord_list) :
					bodytypes_list.append(body_type_selected)
			else:
				print("nombre de noeud maximal atteint, veuillez rafra\u00EEchir la liste en pressant sur 'backspace' ou 'delete'")
			print(coord_list)
			print(bodytypes_list)
			print(draw_coord_list)

listener = Listener(on_click=click)
listener.start()

print("Warning! Body type per default is leg and you must have at least 1 body part that is a torso which is the red lines")
while process :
	
	Display.update()
	screen.fill(WHITE)

	if keyboard.is_pressed('esc'):
		pygame.event.post(pygame.event.Event(pygame.QUIT))

	if (keyboard.is_pressed('delete') or keyboard.is_pressed('backspace')) and not_pressed1 :
		coord_list = []
		bodytypes_list = []
		draw_coord_list = []
		print("liste effac\u00E9")
		not_pressed1 = False
	if not (keyboard.is_pressed('delete') or keyboard.is_pressed('backspace')) :
		not_pressed1 = True
	if keyboard.is_pressed('enter') and not_pressed2 :
		if 2 < len(coord_list):
			process = False
			listener.stop()
			creature = { "bodies" : {}, "joints" : {} }
			temp_list = []
			window_length, width = pygame.display.get_window_size()
			for i in range(0,len(coord_list) - 1):
				body_length = math.ceil(math.sqrt( (coord_list[i + 1][0] - coord_list[i][0])**2 + (coord_list[i + 1][1] - coord_list[i][1])**2 ))
				body_width = 30
				body_pos = [(coord_list[i + 1][0] - coord_list[i][0]) // 2 + coord_list[i][0] , (coord_list[i + 1][1] - coord_list[i][1]) // 2 + coord_list[i][1] ]
				if bodytypes_list[i] == "torso" :
					temp_list.append({"name":f"torso{i}","type":"torso","size":[body_length,body_width],"position":body_pos})
				if bodytypes_list[i] == "leg" :
					temp_list.append({"name":f"leg{i}","type":"leg","size":[body_width,body_length],"position":body_pos})
			creature["bodies"] = temp_list
			temp_list = []
			for i in range(1,len(coord_list) - 1):
					temp_list.append({"body_a":creature["bodies"][i-1]["name"],"body_b":creature["bodies"][i]["name"],"anchor":coord_list[i], "actuated":True})
			creature["joints"] = temp_list
			print(creature)
			files_saved_counter = 1
			with open(f"creatures\\creature{files_saved_counter}.json", "w") as file:
    				json.dump(creature, file)
			exec(open("ESP-scripts\\menu.py").read())
	
	if keyboard.is_pressed('1') and not_pressed3:
		body_type_selected = "leg"
		print("leg body type selected")
		not_pressed3 = False
	if not keyboard.is_pressed('1'):
		not_pressed3 = True

	if keyboard.is_pressed('2') and not_pressed4:
		body_type_selected = "torso"
		print("torso body type selected")
		not_pressed4 = False
	if not keyboard.is_pressed('2'):
		not_pressed4 = True
	
		not_pressed2 = False
	if not keyboard.is_pressed('enter') :
		not_pressed2 = True

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			coord_list = []
			draw_coord_list = []
			bodytypes_list = []
			listener.stop()
			Display.unload
			process = False
			print("exiting process")
			pygame.quit(); sys.exit()
	if 0 < len(coord_list) :
		for i in range(0,len(coord_list)):
			if 1 < len(coord_list) :
				if bodytypes_list[i - 1] == "leg" :
					pygame.draw.lines(screen,color_leg,False,draw_coord_list,2)
				else:
					pygame.draw.lines(screen,color_torso,False,draw_coord_list,2)
			pygame.draw.circle(screen,color_dot,draw_coord_list[i],5)
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