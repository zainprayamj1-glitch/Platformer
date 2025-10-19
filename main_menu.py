import pygame, sys, threading, os, math, random
from os import listdir
from os.path import isfile, join
from pygame import *
from pygame.locals import *
import json

pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=8192 * 2)
pygame.init()
pygame.display.set_caption('Bismillah')
WIDTH, HEIGHT = (1280, 720)
screen = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)

mainClock = pygame.time.Clock()
FPS = 60

PLAYER_VEL = 5
scroll = 0

bg_mainmenu = pygame.image.load('BACKGROUND.png').convert_alpha()
MM_WIDTH, MM_HEIGHT = bg_mainmenu.get_width(), bg_mainmenu.get_height()

font = pygame.font.SysFont("arialblack", 80)
WORK = 10000000

click_sfx = pygame.mixer.Sound("click_sfx.wav")
click_sfx.set_volume(5)   
Main_Backsound = pygame.mixer.Sound("Whispering Leaves.wav")
Main_Backsound.set_volume(0.1)
quitgame_sfx = pygame.mixer.Sound("ClockTick.wav")
quitgame_sfx.set_volume(10)
forest_sfx = pygame.mixer.Sound("ForestSFX.wav")
forest_sfx.set_volume(10)

# ground
ground_image = pygame.image.load("ground.png").convert_alpha()
ground_width = ground_image.get_width()
ground_height = ground_image.get_height()
sapling = pygame.image.load("sapling.png").convert_alpha()

# background images - main area
bg_images1 = []
for i in range(1, 6):
    bg_image = transform.scale(pygame.image.load(f"BGMM{i}.png").convert_alpha(), (WIDTH, HEIGHT))
    bg_images1.append(bg_image)
bg1_width = bg_images1[0].get_width()

def draw_bgscenery():
    for x in range(6):
        speed = 1
        for i in bg_images1:
            screen.blit(i, ((x * bg1_width) - scroll * speed, 0))
            speed += 0.2

# forest backgrounds
bg_images2 = []
for i in range(1, 6):
    bg_image = transform.scale(pygame.image.load(f"plx-{i}.png").convert_alpha(), (WIDTH, HEIGHT))
    bg_images2.append(bg_image)
bg2_width = bg_images2[0].get_width()

def draw_bgforest():
    for x in range(6):
        speed = 1
        for i in bg_images2:
            screen.blit(i, ((x * bg2_width) - scroll * speed, 0))
            speed += 0.2

class Ground(pygame.sprite.Sprite):
    def __init__(self, width, height, tile_count=30):
        super().__init__()
        # create a tiled ground surface
        self.image = pygame.Surface((ground_width * tile_count, ground_height), pygame.SRCALPHA)
        for x in range(tile_count):
            self.image.blit(ground_image, (x * ground_width, 0))
        # position the ground at the bottom
        self.rect = self.image.get_rect(topleft=(0, HEIGHT - ground_height))
        # mask for pixel-perfect collisions
        self.mask = pygame.mask.from_surface(self.image)

    def draw_ground(self, screen, offset_x):
        # draw ground using camera offset so it follows the player
        screen.blit(self.image, (-offset_x, self.rect.y))

def get_font(size):
    return pygame.font.SysFont(None, size)

def resolve_ground_collision(player, ground_obj):

    if pygame.sprite.collide_mask(player, ground_obj):
        # player falling -> land on ground
        if player.y_vel >= 0:
            player.rect.bottom = ground_obj.rect.top
            player.landed()
        else:
            player.rect.top = ground_obj.rect.bottom
            player.hit_head()

# --- NEW: Sapling pickup / planting support ---
class Sapling(pygame.sprite.Sprite):
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        # use rect collision for simplicity
    def draw(self, surface, offset_x):
        surface.blit(self.image, (self.rect.x - offset_x, self.rect.y))

# helper: find nearest planting spot index if within radius
def find_near_spot(player, spots, radius=48):
    for i, s in enumerate(spots):
        if not s["planted"] and abs((player.rect.centerx) - s["x"]) <= radius:
            return i
    return None

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

def draw_text(text, fontobj, text_col, x, y):
    img = fontobj.render(text, True, text_col)
    screen.blit(img, (x, y))

# NEW: show a centered message that fades out
def show_fade_message(message, duration_ms=900, font_size=40):
    fontobj = get_font(font_size)
    text_surf = fontobj.render(message, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    start = pygame.time.get_ticks()
    while True:
        elapsed = pygame.time.get_ticks() - start
        if elapsed >= duration_ms:
            break
        # events so window stays responsive
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        # redraw current frame behind the message
        # caller should have already drawn background/buttons before calling this.
        # darken background slightly
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 120))
        screen.blit(overlay, (0, 0))
        # fade alpha
        alpha = 255 - int((elapsed / duration_ms) * 255)
        tmp = text_surf.copy()
        tmp.set_alpha(alpha)
        screen.blit(tmp, text_rect)
        pygame.display.update()
        mainClock.tick(FPS)

def fade_to_black(surface):
    fade_Surface = pygame.Surface((WIDTH, HEIGHT))
    fade_Surface.fill((0, 0, 0))
    for alpha in range(0, 255, 5):
        fade_Surface.set_alpha(alpha)
        surface.blit(screen, (0, 0))
        surface.blit(fade_Surface, (0, 0))
        pygame.display.flip()
        mainClock.tick(FPS)

def fade_from_black(surface):
    fade_surface = pygame.Surface((WIDTH, HEIGHT))
    fade_surface.fill((0, 0, 0))
    for alpha in range(255, 0, -5):
        fade_surface.set_alpha(alpha)
        surface.blit(fade_surface, (0, 0))
        pygame.display.flip()
        mainClock.tick(FPS)

def slide_out_left(surface, screen_width, clock, speed=15):
    slide_surface = pygame.Surface((WIDTH, screen.get_height()))
    slide_surface.fill((0, 0, 0))
    slide_rect = slide_surface.get_rect(topright=(0, 0))
    while slide_rect.left < screen_width:
        surface.blit(slide_surface, slide_rect)
        slide_rect.x += speed
        pygame.display.flip()
        clock.tick(180)

mypath = os.path.dirname(os.path.realpath(__file__))

# persistent save file
SAVE_FILE = os.path.join(mypath, "save_game.json")
SAVED_STATE = {"has_sapling": False, "planting_spots": None}

def load_state():
    global SAVED_STATE
    try:
        with open(SAVE_FILE, "r") as f:
            SAVED_STATE = json.load(f)
    except Exception:
        SAVED_STATE = {"has_sapling": False, "planting_spots": None}

def save_state():
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(SAVED_STATE, f)
    except Exception:
        pass

# load saved state once at startup
load_state()

def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]

def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join(mypath, "assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        # extract frames
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            #Character scale
            sprites.append(pygame.transform.scale(surface, (width * 4, height * 4)))

        name = image.replace(".png", "")
        if direction:
            all_sprites[name + "_right"] = sprites
            all_sprites[name + "_left"] = flip(sprites)
        else:
            all_sprites[name] = sprites

    return all_sprites

class Player():
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        # inventory flag: whether player carries a sapling (picked up in forest)
        self.has_sapling = False
        default_key = "idle_left" if "idle_left" in self.SPRITES else next(iter(self.SPRITES))
        self.sprite = self.SPRITES[default_key][0]
        self.update()

    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        if sprite_sheet_name not in self.SPRITES:
            sprite_sheet_name = next(iter(self.SPRITES))  # fallback
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        # update rect to sprite size (keep topleft)
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))

def handle_player_input(player):
    """
    Read keyboard state and set player velocity. Clearing player.x_vel at start
    ensures the character stops when keys are released.
    """
    keys = pygame.key.get_pressed()

    # Reset horizontal velocity each frame — prevents continuous movement after key release
    player.x_vel = 0

    if keys[K_a] or keys[K_LEFT]:
        player.move_left(PLAYER_VEL)
    elif keys[K_d] or keys[K_RIGHT]:
        player.move_right(PLAYER_VEL)

    if keys[K_SPACE] and getattr(player, "jump_count", 0) < 2:
        player.jump()

def Main_menu():
    while True:
        Main_Backsound.play()
        quitgame_sfx.stop()
        screen.blit(bg_mainmenu,(0,0))
        
        MENU_MOUSE_POS = pygame.mouse.get_pos()

        PLAY_BUTTON = Button(image=pygame.image.load("PLAY.png"), pos=(250, 600),
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("OPTIONS.png"), pos=(650, 600), 
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("QUIT.png"), pos=(1050, 600), 
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_sfx.play()
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Levels()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    Options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()
        mainClock.tick(FPS)

def Levels():
    running = True
    while running:
        screen.blit(pygame.image.load("LevelsBG.png").convert_alpha(), (0, 0))
        screen.blit(pygame.image.load('PlayFrame2.png').convert_alpha(), (340, 55))
        draw_text('Level - 1', font, (0, 0, 0), 890, 70)

        Levels_MOUSE_POS = pygame.mouse.get_pos()

        PLAYLEVEL_BUTTON = Button(image=pygame.image.load('PlayButton.png'), pos=(640, 350),
                      text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        LARROW_BUTTON = Button(image=transform.scale(pygame.image.load('LARROW.png'), (200, 200)), pos=(140, 350),
                      text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        RARROW_BUTTON = Button(image=transform.scale(pygame.image.load('RARROW.png'), (200, 200)), pos=(1150, 350),
                      text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=pygame.image.load('exit_btn.png'), pos=(640, 600), 
                      text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
       
        for button in [PLAYLEVEL_BUTTON, LARROW_BUTTON, RARROW_BUTTON, BACK_BUTTON]:
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_sfx.play()
                if PLAYLEVEL_BUTTON.checkForInput(Levels_MOUSE_POS):
                    slide_out_left(screen, WIDTH, mainClock)
                    Game()
                if LARROW_BUTTON.checkForInput(Levels_MOUSE_POS):
                    # show fade message when level not available
                    show_fade_message("Level isn't available yet.", duration_ms=1000)
                if RARROW_BUTTON.checkForInput(Levels_MOUSE_POS):
                    show_fade_message("Level isn't available yet.", duration_ms=1000)
                if BACK_BUTTON.checkForInput(Levels_MOUSE_POS):
                    running = False

        pygame.display.update()
        mainClock.tick(FPS)

def Game():
    InGame = True
    global scroll, SAVED_STATE
    max_scroll = 3000
    min_scroll = 0

    Main_Backsound.stop()
    quitgame_sfx.stop()
    forest_sfx.stop()

    # create player using sprite-based Player
    player = Player(scroll, HEIGHT - ground_height - 160, 32, 32)
    # restore inventory from saved state
    player.has_sapling = bool(SAVED_STATE.get("has_sapling", False))

    # create a Ground instance used for collisions and drawing
    ground_sprite = Ground(ground_width, ground_height, tile_count=60)

    # restore or create planting spots
    world_w = ground_sprite.rect.width
    # ensure planting spots are generated inside the world area reachable BEFORE camera clamps
    # i.e. keep spots <= max_scroll - margin so camera will still pan to them
    spawn_margin = 200
    spawn_limit = max(spawn_margin + 200, min(world_w - 200, max_scroll - spawn_margin))
    if SAVED_STATE.get("planting_spots"):
         planting_spots = SAVED_STATE["planting_spots"]
         # ensure spots are within world bounds
         for s in planting_spots:
             s["x"] = max(0, min(s["x"], world_w - 1))
    else:
        plant_count = 5
        # generate planting spots only up to spawn_limit so camera doesn't clamp before player can reach them
        raw_positions = random.sample(range(spawn_margin, max(spawn_margin + 1, spawn_limit)), k=plant_count)
        planting_spots = [{"x": px, "y": HEIGHT - ground_height - sapling.get_height(), "planted": False} for px in raw_positions]
        SAVED_STATE["planting_spots"] = planting_spots
        save_state()

    planted_total = sum(1 for s in planting_spots if s.get("planted"))

    # show "you did it" briefly after planting
    last_planted_time = 0
    last_planted_index = None
    YOU_DID_MS = 1500  # milliseconds to show the message

    while InGame:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()
                # planting action: press E to plant when near a spot and carrying a sapling
                if event.key == K_e:
                    idx = find_near_spot(player, planting_spots, radius=48)
                    if idx is not None and player.has_sapling and not planting_spots[idx]["planted"]:
                        planting_spots[idx]["planted"] = True
                        player.has_sapling = False
                        planted_total += 1
                        # persist change
                        SAVED_STATE["has_sapling"] = False
                        SAVED_STATE["planting_spots"] = planting_spots
                        save_state()
                        click_sfx.play()
                        # record last planted for short feedback
                        last_planted_time = pygame.time.get_ticks()
                        last_planted_index = idx

        # scene draw
        draw_bgscenery()
        # draw ground via ground_sprite (keeps parity with collision rect/mask)
        ground_sprite.draw_ground(screen, scroll)

        # draw planting spots (unplanted show faint marker, planted show sapling image)
        # compute nearest unplanted spot once (world coordinates)
        near_idx = find_near_spot(player, planting_spots, radius=48)
        for i, spot in enumerate(planting_spots):
            screen_x = spot["x"] - scroll
            # only render spots that are (roughly) on screen
            if -100 < screen_x < WIDTH + 100:
                # planted -> draw sapling sprite
                if spot.get("planted"):
                    screen.blit(sapling, (screen_x, spot["y"]))
                    # if this was just planted, show "You did it!" above the planted spot briefly
                    if last_planted_index == i:
                        elapsed = pygame.time.get_ticks() - last_planted_time
                        if elapsed < YOU_DID_MS:
                            msg_font = get_font(36)
                            msg_surf = msg_font.render("You did it!", True, (240, 220, 60))
                            msg_rect = msg_surf.get_rect(center=(screen_x + sapling.get_width() // 2, spot["y"] - 28))
                            bg = pygame.Surface((msg_rect.width + 12, msg_rect.height + 8), pygame.SRCALPHA)
                            bg.fill((0, 0, 0, 160))
                            bg_rect = bg.get_rect(center=msg_rect.center)
                            screen.blit(bg, bg_rect)
                            screen.blit(msg_surf, msg_rect)
                        else:
                            last_planted_index = None
                else:
                    # unplanted -> draw faint ground marker
                    marker_w = sapling.get_width() // 2
                    marker_h = sapling.get_height() // 2
                    marker = pygame.Surface((marker_w, marker_h), pygame.SRCALPHA)
                    is_near = (near_idx == i)
                    color = (180, 140, 60, 160) if is_near else (120, 80, 30, 120)
                    marker.fill(color)
                    marker_x = screen_x + sapling.get_width() // 4
                    marker_y = spot["y"] + sapling.get_height() // 2
                    screen.blit(marker, (marker_x, marker_y))
                    # outline if player is near
                    if is_near:
                        outline_color = (255, 255, 200)
                        pygame.draw.rect(screen, outline_color, (marker_x - 2, marker_y - 2, marker_w + 4, marker_h + 4), 2)
                        # show contextual hint
                        if player.has_sapling:
                            hint = "Press E to plant"
                        else:
                            hint = "No sapling — go to forest"
                        hint_surf = get_font(22).render(hint, True, (240, 240, 240))
                        hint_rect = hint_surf.get_rect(midbottom=(marker_x + marker_w // 2, marker_y - 8))
                        # shadow for readability
                        screen.blit(pygame.Surface((hint_rect.width, hint_rect.height), pygame.SRCALPHA), hint_rect.topleft)

        # input & physics
        handle_player_input(player)
        player.loop(FPS)

        # resolve collision with ground after movement
        resolve_ground_collision(player, ground_sprite)

        # camera follow: keep player on-screen and clamp to world edges
        margin = 200
        left_edge = scroll + margin
        right_edge = scroll + WIDTH - margin

        if player.rect.x < left_edge and scroll > min_scroll:
            scroll = max(min_scroll, player.rect.x - margin)
        elif player.rect.x > right_edge and scroll < max_scroll:
            scroll = min(max_scroll, player.rect.x - (WIDTH - margin))

        scroll = max(min_scroll, min(scroll, max_scroll))

        # draw player with scroll offset
        player.draw(screen, scroll)

        # show indicator if player has a sapling
        if player.has_sapling:
            draw_text("Sapling: in inventory (press E to plant)", get_font(24), (255,255,255), 10, 10)

        # transition trigger
        if scroll >= max_scroll:
            fade_to_black(screen)
            fade_from_black(screen)
            scroll = 300
            Forest()

        pygame.display.update()
        mainClock.tick(FPS)

def Forest():
    InGame = True
    global scroll, SAVED_STATE
    max_scroll = 2000
    min_scroll = 0

    forest_sfx.play()
    quitgame_sfx.stop()

    # create player for forest scene
    player = Player(scroll, HEIGHT - ground_height - 160, 32, 32)

    # create ground used in forest scene (tile_count can be tuned)
    ground_sprite = Ground(ground_width, ground_height, tile_count=60)

    # spawn a few saplings in the forest at random positions (player must pick these up)
    forest_saplings = pygame.sprite.Group()
    sapling_count = 4
    # keep forest saplings inside the navigable region before camera clamps
    forest_spawn_margin = 200
    forest_spawn_limit = max(forest_spawn_margin + 100, min(ground_sprite.rect.width - 200, max_scroll - forest_spawn_margin))
    spawn_xs = random.sample(range(forest_spawn_margin, forest_spawn_limit), k=sapling_count)
    for sx in spawn_xs:
        s = Sapling(sx, HEIGHT - ground_height - sapling.get_height(), sapling)
        forest_saplings.add(s)

    while InGame:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == K_ESCAPE:
                    quitgame()

        draw_bgforest()
        ground_sprite.draw_ground(screen, scroll)

        handle_player_input(player)
        player.loop(FPS)

        # resolve collision with ground after movement
        resolve_ground_collision(player, ground_sprite)

        # check for sapling pickups
        for s in list(forest_saplings):
            if player.rect.colliderect(s.rect):
                forest_saplings.remove(s)
                player.has_sapling = True
                # persist pickup so Game will restore inventory
                SAVED_STATE["has_sapling"] = True
                save_state()
                click_sfx.play()

        # draw saplings
        for s in forest_saplings:
            s.draw(screen, scroll)

        # camera follow with clamp
        margin = 200
        left_edge = scroll + margin
        right_edge = scroll + WIDTH - margin

        if player.rect.x < left_edge and scroll > min_scroll:
            scroll = max(min_scroll, player.rect.x - margin)
        elif player.rect.x > right_edge and scroll < max_scroll:
            scroll = min(max_scroll, player.rect.x - (WIDTH - margin))

        scroll = max(min_scroll, min(scroll, max_scroll))

        # transition back to main when reaching left end
        if scroll <= min_scroll:
            fade_to_black(screen)
            fade_from_black(screen)
            scroll = 1200
            Game()

        player.draw(screen, scroll)

        # show pickup hint
        if not player.has_sapling and len(forest_saplings) > 0:
            draw_text("Find and walk over a sapling to pick it up", get_font(20), (255,255,255), 10, 10)
        elif player.has_sapling:
            draw_text("Sapling picked up! Return to main area to plant (press E to plant)", get_font(20), (255,255,255), 10, 10)

        pygame.display.update()
        mainClock.tick(FPS)

def quitgame():
    running = True
    while running:

        forest_sfx.stop()
        quitgame_sfx.play()
        screen.blit(pygame.image.load("ime.png").convert_alpha(), (0, 0))
        quitgame_MOUSE_POS = pygame.mouse.get_pos()

        CONTINUE_BUTTON = Button(image=pygame.image.load("CONTINUE.png"), pos=(640, 200),
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("OPTIONS.png"), pos=(640, 350), 
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        MAIN_MENU_BUTTON = Button(image=pygame.image.load("MAIN MENU.png"), pos=(640, 500), 
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        for button in [CONTINUE_BUTTON, OPTIONS_BUTTON, MAIN_MENU_BUTTON]:
            button.changeColor(quitgame_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                click_sfx.play()
                if CONTINUE_BUTTON.checkForInput(quitgame_MOUSE_POS):
                    quitgame_sfx.stop()
                    running = False
                if OPTIONS_BUTTON.checkForInput(quitgame_MOUSE_POS):
                    Options()
                if MAIN_MENU_BUTTON.checkForInput(quitgame_MOUSE_POS):
                    Main_menu()

        pygame.display.update()
        mainClock.tick(FPS)

def Options():  
    running = True
    while running:
        quitgame_sfx.stop()
        screen.fill('Black')
        Options_MOUSE_POS = pygame.mouse.get_pos()

        VIDEO_BUTTON = Button(image=pygame.image.load("button_video.png"), pos=(640, 200),
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        AUDIO_BUTTON = Button(image=pygame.image.load("button_audio.png"), pos=(640, 350), 
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        KEYS_BUTTON = Button(image=pygame.image.load("button_keys.png"), pos=(640, 500), 
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        BACK_BUTTON = Button(image=pygame.image.load("button_back.png"), pos=(640, 650), 
                            text_input="", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        
        for button in [VIDEO_BUTTON, AUDIO_BUTTON, KEYS_BUTTON, BACK_BUTTON]:
            button.changeColor(Options_MOUSE_POS)
            button.update(screen)

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == MOUSEBUTTONDOWN:
                click_sfx.play()
                if VIDEO_BUTTON.checkForInput(Options_MOUSE_POS):
                    print('Video Resolution')
                if AUDIO_BUTTON.checkForInput(Options_MOUSE_POS):
                    print('Audio SFX Setting')
                if KEYS_BUTTON.checkForInput(Options_MOUSE_POS):
                    print('Keys Output Change')
                if BACK_BUTTON.checkForInput(Options_MOUSE_POS):
                    running = False

        pygame.display.update()
        mainClock.tick(FPS)

# loading screen
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
    loading_bar_scaled = pygame.transform.scale(loading_bar, (int(loading_bar_width), 150))
    loading_bar_rect = loading_bar_scaled.get_rect(midleft=(280, 360))
    screen.blit(LOADING_BG, LOADING_BG_RECT)
    screen.blit(loading_bar_scaled, loading_bar_rect)

    pygame.display.update()
    mainClock.tick(FPS)

    if loading_finished:
        break

Main_menu()
