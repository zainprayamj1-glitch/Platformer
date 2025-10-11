import pygame, sys, threading
from pygame import *

mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('Bismillah')
WIDTH, HEIGHT = (1280, 720)
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
bg_mainmenu = pygame.image.load('BACKGROUND.png').convert_alpha()
MM_WIDTH, MM_HEIGHT = bg_mainmenu.get_width(), bg_mainmenu.get_height()

FONT = pygame.font.SysFont("arialblack", 100)
WORK = 10000000
FPS = 60
scroll = 0


#FOREST


ground_image = pygame.image.load("ground.png").convert_alpha()
ground_width = ground_image.get_width()
ground_height = ground_image.get_height()

bg_images1 = [] #MAIN AREA
for i in range(1, 6):
    bg_image = transform.scale(pygame.image.load(f"BGMM{i}.png").convert_alpha(), (WIDTH, HEIGHT))
    bg_images1.append(bg_image)
bg_width = bg_images1[0].get_width()

def draw_bgscenery():
    for x in range(6):
        speed = 1
        for i in bg_images1:
            screen.blit(i, ((x * bg_width) - scroll * speed, 0))
            speed += 0.2

bg_images2 = [] #FOREST AREA
for i in range(1, 6):
  bg_image = transform.scale(pygame.image.load(f"plx-{i}.png").convert_alpha(), (WIDTH, HEIGHT))
  bg_images2.append(bg_image)
bg_width = bg_images2[0].get_width()

def draw_bgforest():
  for x in range(6):
    speed = 1
    for i in bg_images2:
      screen.blit(i, ((x * bg_width) - scroll * speed, 0))
      speed += 0.2

def draw_ground():
  for x in range(30):
    screen.blit(ground_image, ((x * ground_width) - scroll * 2.5, HEIGHT - ground_height))

#OTHERS
def get_font(size):
    return pygame.font.SysFont("font.ttf", GL_RED_SIZE)

class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center = (self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center = (self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)
    
    def checkForInput(self, position):
        if position[0] in range (self.rect.left, self.rect.right) and position [1] in range (self.rect.top, self.rect.bottom):
            return True
        return False
    def changeColor(self, position):
        if position[0] in range (self.rect.left, self.rect.right) and position [1] in range (self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

def draw_text(text, font, color, surface, x ,y):
    textobj = font.render(text, 1, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)

def Main_menu():
    while True:

        screen.blit(bg_mainmenu,(0,0))
        menu_text = get_font(100).render('Main Menu', True, "#b68f40")
        menu_rect = menu_text.get_rect(center = (450, 300))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        PLAY_BUTTON = Button(image=pygame.image.load("PLAY.png"), pos=(200, 200),
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("OPTIONS.png"), pos=(200, 350), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("QUIT.png"), pos=(200, 500), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Early()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        mainClock.tick(FPS)

def Early():
    InGame = True
    while InGame:

        global scroll
        max_scroll = 1010
        fade_counter = 0

        draw_bgscenery()
        draw_ground()

        key = pygame.key.get_pressed()

        if scroll <= max_scroll:

            if key[pygame.K_a] and scroll > 0:
                scroll -= 5
            if key[pygame.K_d] and scroll <= max_scroll:
                scroll += 5

        else:
            if fade_counter < WIDTH:
                fade_counter += 50
                pygame.draw.rect(screen, "Black", (0, 0, fade_counter, HEIGHT))


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()

        pygame.display.update()
        mainClock.tick(FPS)

def Forest():
    while True:
        

        SCROLL = 20
        SCROLL_FOREST = 0
        SCROLL += SCROLL_FOREST
        fade_counter = 0
        draw_bgforest()
        draw_ground()
        key = pygame.key.get_pressed()

        if key[pygame.K_a] and SCROLL > 0:
            SCROLL_FOREST -= 5
        if key[pygame.K_d] and SCROLL < 1005:
            SCROLL_FOREST += 5

            if SCROLL < 10 and fade_counter < 100:
                fade_counter += 5
                pygame.draw.rect(screen, "Black", (0, 0, fade_counter, HEIGHT))
                if fade_counter == 100:
                    Early()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()

        pygame.display.update()
        mainClock.tick(FPS)


def quitgame():
    while True:

        screen.fill("White")
        quitgame_MOUSE_POS = pygame.mouse.get_pos()

        CONTINUE_BUTTON = Button(image=pygame.image.load("CONTINUE.png"), pos=(640, 200),
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("OPTIONS.png"), pos=(640, 350), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        MAIN_MENU_BUTTON = Button(image=pygame.image.load("MAIN MENU.png"), pos=(640, 500), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        for button in [CONTINUE_BUTTON, OPTIONS_BUTTON, MAIN_MENU_BUTTON]:
            button.changeColor(quitgame_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if CONTINUE_BUTTON.checkForInput(quitgame_MOUSE_POS):
                    Early()
                if OPTIONS_BUTTON.checkForInput(quitgame_MOUSE_POS):
                    Options()
                if MAIN_MENU_BUTTON.checkForInput(quitgame_MOUSE_POS):
                    Main_menu()

        pygame.display.update()
        mainClock.tick(FPS)

def Options():  
    running = True
    while running:
        
        screen.fill('Black')
        Options_MOUSE_POS = pygame.mouse.get_pos()

        VIDEO_BUTTON = Button(image=pygame.image.load("button_video.png"), pos=(640, 200),
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        AUDIO_BUTTON = Button(image=pygame.image.load("button_audio.png"), pos=(640, 350), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        KEYS_BUTTON = Button(image=pygame.image.load("button_keys.png"), pos=(640, 500), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=pygame.image.load("button_back.png"), pos=(640, 650), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        for button in [VIDEO_BUTTON, AUDIO_BUTTON, KEYS_BUTTON, BACK_BUTTON]:
            button.changeColor(Options_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                if VIDEO_BUTTON.checkForInput(Options_MOUSE_POS):
                    print('Video Resolution')
                if AUDIO_BUTTON.checkForInput(Options_MOUSE_POS):
                    print('Audio SFX Setting')
                if KEYS_BUTTON.checkForInput(Options_MOUSE_POS):
                    print('Keys Output Change')
                if BACK_BUTTON.checkForInput(Options_MOUSE_POS):
                    if running == True:
                        running = False

        pygame.display.update()
        mainClock.tick(FPS)


LOADING_BG = pygame.image.load("Loading Bar Background.png")
LOADING_BG_RECT = LOADING_BG.get_rect(center=(640, 360))

loading_bar = pygame.image.load("Loading Bar.png")
loading_bar_rect = loading_bar.get_rect(midleft=(280, 360))
loading_finished = False
loading_progress = 0
loading_bar_width = 10

def doWork():
    global loading_finished, loading_progress

    for i in range(WORK):
        math_equation = 912781 / 192837 * 19823
        loading_progress = i 

    loading_finished = True

threading.Thread(target=doWork).start()

while True:
    screen.fill("#0d0e2e")
    loading_bar_width = loading_progress / WORK * 720

    loading_bar = pygame.transform.scale(loading_bar, (int(loading_bar_width), 150))
    loading_bar_rect = loading_bar.get_rect(midleft=(280, 360))

    screen.blit(LOADING_BG, LOADING_BG_RECT)
    screen.blit(loading_bar, loading_bar_rect)

    pygame.display.update()
    mainClock.tick(FPS)

            
    if loading_finished == True:
        break
Main_menu()