import pygame
import random
import sys
import math

pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=4096)
pygame.init()

SCREEN_WIDTH = 500
SCREEN_HEIGHT = 760
FPS = 60
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_icon(pygame.image.load('img/icon.png'))

# Load images
background = pygame.image.load("img/bg.bmp").convert()
BG_WIDTH = background.get_width()
BG_HEIGHT = background.get_height()
tiles = math.ceil(SCREEN_WIDTH/BG_WIDTH)+1
button = pygame.image.load("img/restart.png").convert_alpha()

#Load Bird
class Bird(pygame.sprite.Sprite):
    def __init__(self,x,y):
        pygame.sprite.Sprite.__init__(self)
        self.index = 0
        self.images = []
        self.count = 0
        for i in range(1,3):
            self.images.append(pygame.image.load(f"img/{i}.png"))
            self.images[i-1] = pygame.transform.smoothscale(
                self.images[i-1], (68.8,73.1))
        self.image = self.images[self.index]
        self.rect = pygame.rect.Rect((0, 0), (40,50))
        self.rect.center = [x, y]
        self.speed = 0
        self.clicked = False
    def update(self):
        #gravity
        if start:
            self.speed += 0.5
            if self.rect.bottom < SCREEN_HEIGHT-25:
                self.rect.y += self.speed
            if self.speed > 7:
                self.speed = 7
        if game_over == False:
            #jump
            if (pygame.key.get_pressed()[pygame.K_SPACE] or pygame.mouse.get_pressed()[0]) and self.clicked == False:
                wing_sound.play()
                self.speed = -8
                self.clicked = True
            if pygame.key.get_pressed()[pygame.K_SPACE] == False and pygame.mouse.get_pressed()[0] == False:
                self.clicked = False
            #flap
            self.count += 1
            if self.count % 14 == 0:
                self.index +=1
                self.index %= 2
            self.image = self.images[self.index]
            #rotate
            self.image = pygame.transform.rotate(self.images[self.index],-self.speed*1.2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -135)
class Pipe(pygame.sprite.Sprite):
    def __init__(self,x,y,position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("img/pipe.png")
        self.image = pygame.transform.smoothscale(self.image, (100,600))
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y]
        else:
            self.rect.topleft = [x, y]
    def update(self):
        self.rect.x -= game_speed
        if self.rect.right <0:
            self.kill()
class Button():
    def __init__(self,x,y,image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = [x,y]
        self.images = []
        self.images.append(pygame.image.load("img/abe.png"))
        self.images[0] = pygame.transform.smoothscale(self.images[0], (270,215))
        self.images.append(pygame.image.load("img/over.png"))
        self.images[1] = pygame.transform.smoothscale(self.images[1], (420,137))

    def draw(self):
        action = False
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0]:
                end_sound.stop()
                action = True
        screen.blit(self.images[0], (115,150))
        screen.blit(self.images[1], (50,400))
        screen.blit(self.image, self.rect)
        return action
bird_group = pygame.sprite.Group()
bird = Bird(50,300)
bird_group.add(bird)
pipe_group = pygame.sprite.Group()
pipe_frequency = 2000
last_pipe = pygame.time.get_ticks()+pipe_frequency/2
score = 0
font = pygame.font.SysFont("comicsansms", 60)
#functions
def draw_score(text,font,text_color,x,y):
    image = font.render(text, True, text_color)
    screen.blit(image, (x,y))
def reset():
    pipe_group.empty()
    bird.rect.x = 50
    bird.rect.y = 300
    score = 0
    return score
#game variables
run = True
start = False
clock = pygame.time.Clock()
game_over = False
pass_pipe = False
scrolling = 0
game_speed = 3
end_sound = pygame.mixer.Sound("sfx/laugh.mp3")
hit_sound = pygame.mixer.Sound("sfx/hit.wav")
score_sound = pygame.mixer.Sound("sfx/score.wav")
wing_sound  = pygame.mixer.Sound("sfx/wing.wav")
restart = Button(SCREEN_WIDTH/2,SCREEN_HEIGHT/2,button)
is_hit = True 
while run:
    clock.tick(FPS)
    #look for collisions
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
        if is_hit:
            hit_sound.play()
            end_sound.play()
            is_hit = False
        game_over = True
        start = False
    #scrolling background
    if game_over==False:
        if start:
        #generate pipes
            time_now = pygame.time.get_ticks()
            if time_now - last_pipe > pipe_frequency:
                pipe_height = random.randint(-100,150)
                top_pipe = Pipe(SCREEN_WIDTH,SCREEN_HEIGHT/2+pipe_height-160,1)
                btm_pipe = Pipe(SCREEN_WIDTH,SCREEN_HEIGHT/2+pipe_height,-1)
                pipe_group.add(top_pipe)
                pipe_group.add(btm_pipe)
                last_pipe = time_now

        for i in range(tiles):
            screen.blit(background, (i*BG_WIDTH-scrolling, 0))
        scrolling += game_speed
        if scrolling >= BG_WIDTH:
            scrolling = 0
        pipe_group.update()
        pipe_group.draw(screen)
        bird_group.draw(screen)
        bird_group.update()
    else:
        if restart.draw():
            game_over = False
            is_hit = True
            score = reset()
    #check scores
    if len(pipe_group) >0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left\
            and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right\
            and pass_pipe==False:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score_sound.play()
                score += 1
                pass_pipe = False             
    draw_score(f"{score:02d}",font,(255,255,255),SCREEN_WIDTH/2-30,20)
    #check if game is over
    if bird.rect.bottom >= SCREEN_HEIGHT-25 or bird.rect.top <= -25:
        if is_hit:
            hit_sound.play()
            end_sound.play()
            is_hit = False
        game_over = True              
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN)  and start==False and game_over== False:
            start = True
    pygame.display.update()
pygame.quit()

