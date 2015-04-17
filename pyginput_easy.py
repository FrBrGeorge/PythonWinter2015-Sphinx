#!/usr/bin/env python
# coding: utf
'''
Простой пример использования pyginput
'''

import pygame
from pyginput import Input, Print
pygame.init()
scr=pygame.display.set_mode((300,100))
pygame.draw.ellipse(scr,(255,200,123),(10,10,280,80))

inp=Input(u"Строчка:")
txt=inp.input(scr,(10,10))
Print(scr,txt)
while True:
    ev=pygame.event.wait()
    if ev.type in (pygame.QUIT, pygame.KEYDOWN):
        break
    pygame.display.flip()
