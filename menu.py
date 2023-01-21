import mediapipe as mp
import cv2
import numpy as np
import uuid
import os
import calcul
from math import *
import sign
import settings
import pygame

BLACK = (0, 0, 0)
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)
mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands


pygame.init()

hands = mp_hands.Hands(max_num_hands=settings.nb_max_hands,
                       min_detection_confidence=0.8, min_tracking_confidence=0.5)


# an image that can be selected
class ClickableIcon(pygame.sprite.Sprite):
    def __init__(self, screen, pos, path, rawtext, size=(80, 80),rotate=0):
        self.rawtext = rawtext
        self.pos = pos
        print(path)
        self.size = size
        image = pygame.image.load(path).convert_alpha()
        image = pygame.transform.scale(image, size)
        image = pygame.transform.rotate(image, rotate)
        self.rect = image.get_rect()
        # set position of self.rect
        self.rect.x = self.pos[0]
        self.rect.y = self.pos[1]
        self.image = image
        self.selected = False
        self.screen = screen
        self.screen.blit(self.image, self.pos)
        # add the text text under the image
        self.font = pygame.font.SysFont(None, 20)
        self.text = self.font.render(rawtext, True, settings.BLACK)
        text_rect = self.text.get_rect()
        self.text_pos = (
            self.pos[0]+(self.size[0]-text_rect[2])/2, self.pos[1]+self.size[1]+10)
        self.screen.blit(self.text, self.text_pos)
        self.screen.blit(self.image, self.pos)

    # when the image is selected, change the text color to red and draw it and change the boolean selected to True
    def update(self):
        if not self.selected:
            print("up")
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.rawtext, True, settings.pygame_RED)
            self.screen.blit(text, self.text_pos)
            self.selected = True
            print("done")
        else:
            self.text = self.font.render(self.rawtext, True, settings.BLACK)
            self.screen.blit(self.text, self.text_pos)
            self.selected = False

    def who(self):
        print("Size : "+str(self.size) + "\nPosition : " + str(self.pos))

# a class that represents a text that can be clicked on, inherits from pygame.sprite.Sprite


class ClickableText(pygame.sprite.Sprite):
    def __init__(self, text, pos, color, screen, size=40, bg_color=False, centered=False, funcupdate=False):
        super().__init__()
        self.bg_color = bg_color
        self.color = color
        font = pygame.font.SysFont(None, size)
        self.text = font.render(text, True, self.color)
        self.rect = self.text.get_rect()
        if funcupdate!=False:
            self.funcupdate = funcupdate
        if centered:
            self.rect.centerx = pos[0]
            self.rect.y = pos[1]
            self.pos = (int(pos[0]-self.rect.width/2), pos[1])
        else:
            self.pos = pos
            self.rect.x = pos[0]
            self.rect.y = pos[1]
        self.screen = screen
        self.draw()
        print(self.rect)
        
    def update(self):
        self.funcupdate()
    # draws the text on the screen
    def draw(self):
        if self.bg_color:
            pygame.draw.rect(self.screen, self.bg_color, self.rect)
        self.screen.blit(self.text, self.pos)


def checkpos(square, x, y):
    #print("Checking if {},{} is between {},{} and {},{}".format(x,y,square.pos[0],square.pos[0]+square.size[0],square.pos[1],square.pos[1]+square.size[1]))
    return x >= square.pos[0] and x <= square.pos[0]+square.size[0] and y >= square.pos[1] and y <= square.pos[1]+square.size[1]

# center text horizontally with given y setting


def center(text, screen, y):
    screen_width = screen.get_size()[0]
    rect_size = text.get_rect()
    screen.blit(text, ((screen_width-rect_size[2])//2, y))

# create the main menu


class Menu():
    def __init__(self):
        self.screen=pygame.display.set_mode((settings.sw, settings.sh))
        self.initalize()
        self.running = True
        self.run()

    def initalize(self):
        
        font = pygame.font.Font(None, 50)
        self.screen.fill(settings.CYAN)
        text = font.render("PACMAIN", True, settings.pygame_BLUE)
        textpos = text.get_rect(centerx=settings.sw/2, centery=50)
        self.screen.blit(text, textpos)

        # Create the "Start Game" button
        start_game = ClickableText("Start Game", (settings.sw/2, 200),
                                   settings.pygame_BLUE, self.screen, 40, settings.WHITE, True, sign_selection_menu)

        # Create the "Quit" button
        quit_game = ClickableText("Quit", (settings.sw/2, 300),
                                  settings.pygame_BLUE, self.screen, 40, settings.WHITE, True, quit)
        
        self.sprites = [start_game, quit_game]
    
    def quit(self):
        self.running=False

    def run(self):
        while self.running:
            for event in pygame.event.get():
                x, y = pygame.mouse.get_pos()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for sprite in self.sprites:
                        if sprite.rect.collidepoint(x, y):
                            print("update")
                            sprite.update()

            pygame.display.flip()

# display a menu that enables sign selection among those possible


def sign_selection_menu():

    #global variable that will contain the list of selected signs
    global sign_list
    sign_list = []

    run = True
    # create pygame screen and set it to cyan
    screen = pygame.display.set_mode((settings.sw, settings.sh))
    screen.fill(settings.CYAN)

    # display main message "Selection des signes"
    font = pygame.font.SysFont(None, 50)
    maintext = font.render("Selection des signes", True, settings.BLACK)
    center(maintext, screen, 50)

    sprite_list = {}

    # create a text at the bottom right that display "Play" and that will be clickable
    playtext = ClickableText("Play", (settings.sw-100, settings.sh-50),settings.pygame_BLUE, screen, funcupdate=play)
    playtext.draw()
    sprite_list[0] = playtext

    #create a text a the bottom left that display quits and that calls the menu class
    quittext = ClickableText("Menu", (50, settings.sh-50),settings.pygame_BLUE, screen, funcupdate=Menu)
    quittext.draw()
    sprite_list[5] = quittext

    # create multiple squares that will each represent one sign
    pos = []
    icon1 = ClickableIcon(screen, pos=(150, 150),
                          rawtext="Extension du pouce", path="images/thumb.png",rotate=90)
    sprite_list[1] = icon1
    icon2 = ClickableIcon(screen, pos=(400, 150),
                          rawtext="Ouverture de la main", path="images/hand.png")
    sprite_list[2] = icon2
    icon3 = ClickableIcon(screen, pos=(150, 300),
                          rawtext="Arpèges", path="images/arpege.png")
    sprite_list[3] = icon3
    icon4 = ClickableIcon(screen, pos=(400, 300),
                          rawtext="Fermture du poing", path="images/fist.png")
    sprite_list[4] = icon4

    while run:
        for event in pygame.event.get():
            x, y = pygame.mouse.get_pos()
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                #updates sprites 0 and 5 (play and menu)
                for i in [0, 5]:
                    if sprite_list[i].rect.collidepoint(x, y):
                        sprite_list[i].update()
                #updates sprites 1 to 4 (signs)
                for i in range(1, 5):
                    if sprite_list[i].rect.collidepoint(x, y):
                        sprite_list[i].update()
                        if sprite_list[i].selected:
                            sign_list.append(sprite_list[i].rawtext)
                        else:
                            try:
                                sign_list.remove(sprite_list[i].rawtext)
                            except:
                                pass
        pygame.display.flip()

def play():
    #print the list of the selected signs
    print(sign_list)

    run = True
    # create pygame screen and set it to cyan
    screen = pygame.display.set_mode((settings.sw, settings.sh))
    screen.fill(settings.CYAN)

    #back to menu button
    back = ClickableText("Menu", (50, settings.sh-50),settings.pygame_BLUE, screen, funcupdate=Menu)
    back.draw()
    sprite_list = {}
    sprite_list[0] = back
    #capture the camera with cv2 and display it on pygame
    cap = cv2.VideoCapture(0)
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            x, y = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if sprite_list[0].rect.collidepoint(x, y):
                    sprite_list[0].update()
        ret, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = np.rot90(frame)
        frame = cv2.resize(frame, (settings.sh, settings.sw))
        frame = pygame.surfarray.make_surface(frame)
        screen.blit(frame, (0, 0))
        back.draw()
        pygame.display.flip()


    cap.release()

def instant_test_():
    screen = pygame.display.set_mode((settings.sw, settings.sh))
    screen.fill(settings.CYAN)
    path = "images/logo.png"
    image = pygame.image.load(path).convert_alpha()
    size = (100, 100)
    image = pygame.transform.scale(image, size)
    screen.blit(image, (100, 100))
    pygame.display.flip()
    input()


if __name__ == "__main__":
    # test()
    Menu()
    sign_selection_menu()
    # instant_test_()
