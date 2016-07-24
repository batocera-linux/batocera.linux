#!/usr/bin/python

import sys
import pygame
import re
from   sys           import exit
from   pygame.locals import QUIT

class Upgrader:

    def __init__(self, screen):
        self.screen = screen
        self.width  = screen.get_width()
        self.height = screen.get_height()
        self.font   = pygame.font.SysFont("arial", 72)
        self.txt    = self.font.render("", True, (255, 255, 255))
        self.percent_margin = 10
        self.percent_height = 30
        self.setTitle("")
        self.percentage = 0

    def setTitle(self, title):
        self.txt = self.font.render(title, True, (255, 255, 255))

    def setPercentage(self, percentage):
        self.percentage = percentage

    def doAction(self, action):
        m = re.match("^([^ ]+) (.*)$", line)
        if not m:
            return

        # percentage
        if m.group(1) == "percent":
            upg.setPercentage(int(m.group(2)))

        # title
        elif m.group(1) == "title":
            upg.setTitle(m.group(2))

    def render(self):
        percent_width = (self.width-self.percent_margin*2)*self.percentage/100
        percent_txt   = self.font.render(str(self.percentage) + "%", True, (255, 255, 255))
        screen.fill([0,0,0])
        screen.blit(self.txt, (self.width/2-self.txt.get_width()/2, self.height/2-self.txt.get_height()-self.percent_height/2))
        pygame.draw.rect(self.screen, (255, 255, 255), [self.percent_margin, self.height/2-self.percent_height/2, percent_width, self.percent_height])
        screen.blit(percent_txt, (self.width/2-percent_txt.get_width()/2, self.height/2+self.percent_height/2))
        pygame.display.update()

pygame.init()
pygame.mouse.set_visible(False)
screen = pygame.display.set_mode()

upg = Upgrader(screen)
upg.render()

line = sys.stdin.readline()
while line != "":
    upg.doAction(line)
    upg.render()
    line = sys.stdin.readline()
