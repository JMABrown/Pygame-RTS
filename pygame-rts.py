import pygame
import numpy as np
from pygame.locals import *

WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

SELECTION_COLOR = GREEN

LMB = 1
MMB = 2
RMB = 3
SCROLL_UP = 4
SCROLL_DOWN = 5

class Unit(object):
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        
    def setSelected(self, b):
        self.selected = b
        
    def draw(self, displaySurf):
        pygame.draw.circle(displaySurf, self.color, (self.x, self.y), 2, 0)
        if (self.selected):
            pygame.draw.rect(displaySurf, SELECTION_COLOR, (self.x - 4, self.y - 4, 8, 8), 1)

pygame.init()

FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()

worldx = 400
worldy = 300

DISPLAYSURF = pygame.display.set_mode((worldx, worldy), 0, 32)
pygame.display.set_caption('Window Title')

box_being_dragged = False

units = [Unit(100, 100, RED)]
units.append(Unit(200, 100, BLUE))
units.append(Unit(100, 150, BLUE))
units.append(Unit(20, 20, RED))

while (True): # the main game loop
    DISPLAYSURF.fill(WHITE)
    
    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if (event.button == LMB):
                click_pos = pygame.mouse.get_pos()
                box_being_dragged = True
            if (event.button == RMB):
                units.append(Unit(mouse_pos[0], mouse_pos[1], RED))
        if event.type == pygame.MOUSEBUTTONUP:
            if (event.button == LMB):
                box_being_dragged = False
                for unit in units:
                    if (unit.x < mouse_pos[0] and unit.x > click_pos[0] and unit.y < mouse_pos[1] and unit.y > click_pos[1]):
                        unit.setSelected(True)
                    else:
                        unit.setSelected(False)
    
    if (box_being_dragged):
        pygame.draw.rect(DISPLAYSURF, RED, (click_pos[0], click_pos[1], mouse_pos[0] - click_pos[0], mouse_pos[1] - click_pos[1]), 1)
        
    for unit in units:
        unit.draw(DISPLAYSURF)        
        
    keys = pygame.key.get_pressed()

    pygame.display.update()
    
    fpsClock.tick(FPS)