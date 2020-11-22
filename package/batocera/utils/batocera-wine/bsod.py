#!/usr/bin/python

import pygame
import psutil

def get_fs_type(mypath):
    root_type = ""
    for part in psutil.disk_partitions():
        if part.mountpoint == '/':
            root_type = part.fstype
            continue
        if mypath.startswith(part.mountpoint):
            return part.fstype
    return root_type

def bsod(screen, message, error_msg):
    background_color = (0, 0, 170)
    
    # background
    screen.fill(background_color)

    # title
    font = pygame.font.SysFont("Lucida Console", 24, bold=True)

    text = font.render(" Windows ", True, background_color, (166, 166, 166))
    title_x = screen.get_width()  // 2 - text.get_width()  // 2
    title_y = screen.get_height() // 3 - text.get_height() // 2
    screen.blit(text, (title_x, title_y))

    n = 0
    if error_msg:
        for line in error_msg.splitlines():
            text = font.render(line, True, (255, 255, 255), (170, 0, 0))
            text_x = screen.get_width()  // 10
            text_y = screen.get_height() // 3 + text.get_height()*(2+n)
            screen.blit(text, (text_x, text_y))
            n += 1

    # text
    for line in message.splitlines():
        text = font.render(line, True, (255, 255, 255), background_color)
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
fs_userdata = get_fs_type("/userdata")
if fs_userdata not in [ 'ext4', 'btrfs' ]:
    bsod(screen, "\nHowever, Wine is still generating the C: drive structure.\n\nPlease wait a few minutes, it might still work.\n\nAddress dword Dll base\n80125800 kernel32.dll\nCode: 0E : 016F : BBF", "WARNING: Your /userdata partition is formatted as "+fs_userdata+", which might not be fully supported.")
else:
    bsod(screen, "No error has occured.\n\nWine is just generating the C: drive structure.\n\nPlease wait a few minutes.\n\nAddress dword Dll base\n80125800 kernel32.dll\nCode: 0E : 016F : BBF", False)
pygame.display.flip()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
            running = False
