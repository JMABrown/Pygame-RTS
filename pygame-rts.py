import pygame
import numpy as np
import time
from pygame.locals import *

WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
CYAN = (0, 255, 255)
GREEN = (0, 255, 0)

SELECTION_COLOR = GREEN
#ATTACK_COLOR = CYAN

SHOW_HEALTH = True

LMB = 1
MMB = 2
RMB = 3
SCROLL_UP = 4
SCROLL_DOWN = 5

UNIT_MAX_HP = 100
UNIT_RANGE = 30
UNIT_ATTACK_PERIOD = 1.0 #seconds

class AttackLine(object):
    
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        
    def draw(self, displaySurf):
        pygame.draw.line(displaySurf, RED, (self.x1, self.y1), (self.x2, self.y2), 3)
        pygame.draw.line(displaySurf, CYAN, (self.x1, self.y1), (self.x2, self.y2), 1)
        

class Unit(object):
    
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.selected = False
        self.x_dest = 0
        self.y_dest = 0
        self.moving = False
        self.hp = UNIT_MAX_HP
        self.target = None
        self.time_last_attack = 0
        
    def setSelected(self, b):
        self.selected = b
        
    def setDestination(self, goto_x, goto_y):
        self.x_dest = goto_x
        self.y_dest = goto_y
        self.moving = True
        
    def updateTravel(self):
        if (self.moving):
            x_dist = self.x_dest - self.x
            y_dist = self.y_dest - self.y
            dist = (x_dist**2 + y_dist**2)**0.5
            if (dist < 10):
                self.moving = False
                return
            x_dist /= dist
            y_dist /= dist
            self.x += x_dist * 2
            self.y += y_dist * 2
            
    def setTarget(self, new_target):
        self.target = new_target
            
    def updateAttack(self, attacks):
        if (self.target is not None):
            if (time.clock() >= self.time_last_attack + UNIT_ATTACK_PERIOD):
                x_dist = self.target.x - self.x
                y_dist = self.target.y - self.y
                total_dist = (x_dist**2 + y_dist**2)**0.5
                if (total_dist <= UNIT_RANGE):
                    self.target.inflictDamage(self, 10)
                    attacks.append(AttackLine(self.x, self.y, self.target.x, self.target.y))
                    self.time_last_attack = time.clock()
                
            
    def inflictDamage(self, attacker, damage):
        self.hp -= damage
        self.setTarget(attacker)
        if (self.hp < 0):
            self.hp = 0
            
    def updateAvoidOthers(self, units):
        for unit in units:
            if (unit is not self):      #is instead of == to check references not the same thing
                x_dist = unit.x - self.x
                y_dist = unit.y - self.y
                total_dist = (x_dist**2 + y_dist**2)**0.5
                if (total_dist < 5 and total_dist > 0):
                    if (abs(x_dist) < 5 and abs(x_dist) > 0):
                        self.x -= x_dist / abs(x_dist)
                    if (abs(y_dist) < 5 and abs(y_dist) > 0):
                        self.y -= y_dist / abs(y_dist)
        
    def draw(self, displaySurf):
        pygame.draw.circle(displaySurf, self.color, (int(self.x), int(self.y)), 2, 0)
        if (self.selected):
            pygame.draw.rect(displaySurf, SELECTION_COLOR, (int(self.x) - 4, int(self.y) - 4, 8, 8), 1)
            if (SHOW_HEALTH):
                bar_width = 24
                pygame.draw.rect(displaySurf, RED, ((int(self.x)) - 12, (int(self.y)) - 8, bar_width, 3), 0)
                health_fraction = float(self.hp) / float(UNIT_MAX_HP)
                health_fraction *= bar_width
                pygame.draw.rect(displaySurf, GREEN, ((int(self.x)) - 12, (int(self.y)) - 8, health_fraction, 3), 0)

pygame.init()

FPS = 30 # frames per second setting
fpsClock = pygame.time.Clock()

worldx = 400
worldy = 300

DISPLAYSURF = pygame.display.set_mode((worldx, worldy), 0, 32)
pygame.display.set_caption('Window Title')

box_being_dragged = False

attacks = [AttackLine(0, 0, 100, 100)]
units = [Unit(100, 100, RED)]
units.append(Unit(200, 100, BLUE))
units.append(Unit(100, 150, BLUE))
units.append(Unit(110, 150, BLUE))
units.append(Unit(120, 150, BLUE))
units.append(Unit(130, 150, BLUE))
units.append(Unit(140, 150, BLUE))
units.append(Unit(100, 160, BLUE))
units.append(Unit(110, 160, BLUE))
units.append(Unit(120, 160, BLUE))
units.append(Unit(130, 160, BLUE))
units.append(Unit(140, 160, BLUE))
units.append(Unit(20, 20, RED))
units.append(Unit(20, 30, RED))
units.append(Unit(20, 40, RED))
units.append(Unit(20, 50, RED))
units.append(Unit(20, 60, RED))
units.append(Unit(30, 20, RED))
units.append(Unit(30, 30, RED))
units.append(Unit(30, 40, RED))
units.append(Unit(30, 50, RED))
units.append(Unit(30, 60, RED))

def AnySelectedUnits(us):
    for u in us:
        if u.selected == True:
            return True
    return False

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
                for unit in units:
                    if (unit.selected):
                        unit.setDestination(mouse_pos[0], mouse_pos[1])
                        for target_unit in units:
                            dist_from_mouse = ((target_unit.x - mouse_pos[0])**2 + (target_unit.y - mouse_pos[1])**2)**0.5
                            if (dist_from_mouse < 8):
                                if (target_unit is not unit):
                                    unit.setTarget(target_unit)
                        
                #else:
                    #units.append(Unit(mouse_pos[0], mouse_pos[1], RED))
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
        unit.updateTravel()
        unit.updateAvoidOthers(units)
        unit.updateAttack(attacks)
        if (unit.hp == 0):
            for attacking_unit in units:
                if (attacking_unit.target is unit):
                    attacking_unit.setTarget(None)
            units.remove(unit)
        unit.draw(DISPLAYSURF)
        
    for al in attacks:
        al.draw(DISPLAYSURF)
        
    keys = pygame.key.get_pressed()

    pygame.display.update()
    
    for al in attacks:
        attacks.remove(al)
    
    fpsClock.tick(FPS)