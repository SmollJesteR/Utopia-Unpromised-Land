import pygame
from sprites import *
from config import *
import sys

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.character_spritesheet = Spritesheet('BloodReaper/walk.png ')#image spritesheets char
        self.terrain_spritesheet = Spritesheet('BloodReaper/Ground_rocks.png')#image spritesheets env
    
    def create_map(self):
        for i, row in enumerate(tilemap):
            for j, tile in enumerate(row):
                Floor(self, j,i)
                if tile == 'B':
                    Block(self, j, i)
                if tile == 'P':
                    Player(self, j, i)

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.block = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attack = pygame.sprite.LayeredUpdates()

        self.create_map()

    def events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
        
    def update(self):
        self.all_sprites.update()
        
    def draw(self):
        self.screen.fill(BLACK)
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        pygame.display.update()
        
    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over(self):
        pass
    
    def intro_screen(self):
        pass

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()
pygame.quit()
sys.exit()
