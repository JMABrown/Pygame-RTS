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
BLACK = (0, 0, 0)

SELECTION_COLOR = GREEN
#ATTACK_COLOR = CYAN

SHOW_HEALTH = True

LMB = 1
MMB = 2
RMB = 3
SCROLL_UP = 4
SCROLL_DOWN = 5

UNIT_MAX_HP = 100
UNIT_RANGE = 50
UNIT_ATTACK_PERIOD = 1.0 #seconds
UNIT_RADIUS = 2
BULLET_RADIUS = 0
BULLET_DAMAGE = 10
AVOID_RADIUS = 5
WAYPOINT_THRESHOLD = 10

class AttackLine(object):
    
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        
    def draw(self, displaySurf):
        pygame.draw.line(displaySurf, RED, (self.x1, self.y1), (self.x2, self.y2), 3)
        pygame.draw.line(displaySurf, CYAN, (self.x1, self.y1), (self.x2, self.y2), 1)
        
class Bullet(object):
    def __init__(self, source, color, x, y, x_vel, y_vel):
        self.source = source        
        self.color = color
        self.x = x
        self.y = y
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.colided = False
        
    def updatePos(self):
        self.x += self.x_vel
        self.y += self.y_vel
        
    def checkColisions(self, units):
        for unit in units:
            if (unit is not self.source):
                total_dist = ((self.x - unit.x)**2 + (self.y - unit.y)**2)**0.5
                if (total_dist <= UNIT_RADIUS + BULLET_RADIUS):
                    unit.inflictDamage(self.source, BULLET_DAMAGE)
                    self.colided = True
        
    def draw(self, displaySurf):
        pygame.draw.circle(displaySurf, self.color, (int(self.x), int(self.y)), BULLET_RADIUS, 0)
        

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
            if (dist < WAYPOINT_THRESHOLD):
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
                    self.target.inflictDamage(self, BULLET_DAMAGE)
                    attacks.append(AttackLine(self.x, self.y, self.target.x, self.target.y))
                    self.time_last_attack = time.clock()
                    
    def updateShots(self, bullets):
        if (self.target is not None):
            if (time.clock() >= self.time_last_attack + UNIT_ATTACK_PERIOD):
                x_dist = self.target.x - self.x
                y_dist = self.target.y - self.y
                total_dist = (x_dist**2 + y_dist**2)**0.5
                if (total_dist <= UNIT_RANGE):
                    bullets.append(Bullet(self, self.color, self.x, self.y, x_dist/total_dist*3, y_dist/total_dist*3))
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
                    if (abs(x_dist) < AVOID_RADIUS and abs(x_dist) > 0):
                        self.x -= x_dist / abs(x_dist)
                    if (abs(y_dist) < AVOID_RADIUS and abs(y_dist) > 0):
                        self.y -= y_dist / abs(y_dist)
                        
    def updateTargetAggressors(self, units, radius):
        if (self.target is None):   #dont retarget wildly
            for unit in units:
                if (unit is not self):
                    #if (unit.target is not None):   #target those who have targets (should really be those who fired but yaknow)
                    if (unit.color != self.color):  #making the units only shoot on enemies
                        x_dist = unit.x - self.x
                        y_dist = unit.y - self.y
                        total_dist = (x_dist**2 + y_dist**2)**0.5
                        if (total_dist < radius):
                            if (total_dist < UNIT_RANGE):
                                self.x_dest = unit.x
                                self.y_dest = unit.y
                            self.setTarget(unit)
                            
    def untargetDeadUnits(self, units):
        found_target = False
        for unit in units:
            if (self.target is unit):
                found_target = True
        if (not found_target):
            self.target = None
        
    def draw(self, displaySurf):
        pygame.draw.circle(displaySurf, self.color, (int(self.x), int(self.y)), UNIT_RADIUS, 0)
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

bullets = []
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
units.append(Unit(300, 200, BLACK))
units.append(Unit(300, 210, BLACK))
units.append(Unit(300, 220, BLACK))
units.append(Unit(300, 230, BLACK))
units.append(Unit(310, 200, BLACK))
units.append(Unit(310, 210, BLACK))
units.append(Unit(310, 220, BLACK))
units.append(Unit(310, 230, BLACK))
units.append(Unit(310, 240, BLACK))

while (True): # the main game loop
    DISPLAYSURF.fill(WHITE)
    
    keys = pygame.key.get_pressed()
    mouse_pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if keys[pygame.K_1]:
            units.append(Unit(mouse_pos[0], mouse_pos[1], BLUE))
        if keys[pygame.K_2]:
            units.append(Unit(mouse_pos[0], mouse_pos[1], RED))
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
        unit.updateShots(bullets)
        unit.updateTargetAggressors(units, UNIT_RANGE)
        if (unit.hp == 0):
            units.remove(unit)
            continue
        unit.untargetDeadUnits(units)
        unit.draw(DISPLAYSURF)
        
    for al in attacks:
        al.draw(DISPLAYSURF)
        
    for bullet in bullets:
        bullet.updatePos()
        bullet.checkColisions(units)
        if (bullet.colided == True):
            bullets.remove(bullet)
            continue
        bullet.draw(DISPLAYSURF)

    pygame.display.update()
    
    for al in attacks:
        attacks.remove(al)
    
    fpsClock.tick(FPS)