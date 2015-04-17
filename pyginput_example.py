#!/usr/bin/env python
# coding: utf
'''
Пример использования pyginput
'''

import pygame
from pyginput import Input

size = 760, 540

pygame.init()
scr=pygame.display.set_mode(size)

# создадим поле ввода, явно зададим шрифт и преобразоваине типа
inp=Input("Input a color code as #RRGGBB:","#FFAAFF",FontID="Vera.ttf",SetType=pygame.Color)
color=pygame.Color("blue")
n=0
while True:
    ev=pygame.event.wait()
    if ev.type is pygame.QUIT:
        break
    # нарисуем что-нибудь отвлекающее :)
    if ev.type is pygame.MOUSEMOTION:
        pygame.draw.circle(scr, color, ev.pos, 3)
    # нажата кнопка на клавиатуре
    elif ev.type is pygame.KEYDOWN:
        # Если окно ввода активно, все события от кнопок направляются ему
        if inp.is_active():
            inp.edit(ev)
            n=0
        # А если неактивно, обрабатываются как-то ещё
        else:
            if ev.key == pygame.K_ESCAPE:
                break
    # Пользователь долго не вводил цвет, пусть введёт
    if n>100:
        inp.activate()
    # Если ввод окончен
    if inp.is_done():
        # …и успешен,
        if inp.is_success():
            # …будем рисовать введённым цветом
            color=inp.value()
        inp.deactivate()
    # здесь можно что-то нарисовать на экране
    # если поле ввода активно, покажем его поверх экрана…
    if inp.is_active(): inp.draw(scr,(100,100))
    pygame.display.flip()
    # …а потом тут же уберём (восстановится то, что было под полем ввода)
    if inp.is_active(): inp.undraw()
    n+=1
