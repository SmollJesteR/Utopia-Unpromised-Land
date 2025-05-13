import pygame

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 1920
screen_height = 1080

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle Sequence")


background_img = pygame.image.load('img/Background/Map.png').convert_alpha()

panel_img = pygame.image.load('img/Background/Panel.png').convert_alpha()

def draw_background():
    screen.blit(background_img, (0, 0))

def draw_panel():
    screen.blit(panel_img, (0, 0))


class Character():
    def __init__(self, x, y, max_hp, strength, potion, name):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potion = potion
        self.alive = True
        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        tempt_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Idle/{i+1}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            tempt_list.append(img)
        self.animation_list.append(tempt_list)

        tempt_list = []
        for i in range(6):
            img = pygame.image.load(f'img/{self.name}/Attack/{i+1}.png')
            img = pygame.transform.scale(img, (img.get_width() * 4.5, img.get_height() * 4.5))
            tempt_list.append(img)
        self.animation_list.append(tempt_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def draw(self):
        screen.blit(self.image, self.rect)

class Mob():
    def __init__(self, x, y, max_hp, strength, potion, name):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potion = potion
        self.alive = True
        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        tempt_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Idle/{i+1}.png')
            img = pygame.transform.scale(img, (img.get_width() * 4.5, img.get_height() * 4.5))
            tempt_list.append(img)
        self.animation_list.append(tempt_list)

        tempt_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Attack/{i+1}.png')
            img = pygame.transform.scale(img, (img.get_width() * 4.5, img.get_height() * 4.5))
            tempt_list.append(img)
        self.animation_list.append(tempt_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


    def update(self):
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

    def draw(self):
        screen.blit(self.image, self.rect)

# Create a character and mobs
BloodReaper = Character(501, 500, 100, 10, 3, "BloodReaper")
DoomCultist = Mob(1086, 350, 100, 10, 3, "DoomCultist")
Medusa = Mob(1520, 350, 100, 10, 3, "Medusa") 
Cyclops = Mob(1086, 350, 100, 10, 3, "Cyclops")

run = True
while run:

    clock.tick(fps)

    draw_background()

    draw_panel()

    BloodReaper.update()
    BloodReaper.draw()

    DoomCultist.update()
    DoomCultist.draw()

    Medusa.update()
    Medusa.draw()

    Cyclops.update()
    Cyclops.draw()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
    
pygame.quit()
