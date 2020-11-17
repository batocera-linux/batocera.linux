#!/usr/bin/python

import pygame

def bsod(screen, message):
    background_color = (0, 0, 170)
    
    # background
    screen.fill(background_color)

    # title
    font = pygame.font.SysFont("Lucida Console", 24, bold=True)

    text = font.render(" Windows ", True, background_color, (166, 166, 166))
    title_x = screen.get_width()  // 2 - text.get_width()  // 2
    title_y = screen.get_height() // 3 - text.get_height() // 2
    screen.blit(text, (title_x, title_y))

    # text
    n = 0
    for line in message.splitlines():
        text = font.render(line, True, (255, 255, 255))
        text_x = screen.get_width()  // 10
        text_y = screen.get_height() // 3 + text.get_height()*(2+n)
        screen.blit(text, (text_x, text_y))
        n += 1

# init
pygame.init()

# screen
infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h))

# bsod
bsod(screen, "No error has occured.\n\nWine is just generating the C: drive structure.\n\nPlease wait a few minutes.\n\nAddress dword Dll base\n80125800 kernel32.dll\nCode: 0E : 016F : BBF")
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            running = False
