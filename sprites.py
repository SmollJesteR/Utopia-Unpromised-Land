import pygame
from config import *
import math
import random

class Spritesheet:
    def __init__(self,file):
        self.sheet = pygame.image.load(file).convert()
        
    def get_sprite(self,x,y,width,height):
        sprite = pygame.Surface([width,height])
        sprite.blit(self.sheet, (0,0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return sprite
    
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites 
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width =  TILESIZE
        self.height = TILESIZE

        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'

        #image_load = pygame.game.load("img/1.png")
        self.image = self.game.character_spritesheet.get_sprite(15 , 12 , self.width,self.height) #need variable like x,y, width, height of assets
        #self.image = pygame.Surface([self.width, self.height])
        #self.image.set_colorkey(BLACK)
        #self.image.blit(image_load,(0,0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
    
    def update(self):
        self.movement()

        # Gerak horizontal dulu
        self.rect.x += self.x_change
        self.collide_blocks('x')

        # Lalu gerak vertikal
        self.rect.y += self.y_change
        self.collide_blocks('y')

        # Reset perubahan
        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_change = -PLAYER_SPEED
            self.facing = 'left'
        if keys[pygame.K_RIGHT]:
            self.x_change = PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_UP]:
            self.y_change = -PLAYER_SPEED
            self.facing = 'up'
        if keys[pygame.K_DOWN]:
            self.y_change = PLAYER_SPEED
            self.facing = 'down'

    def collide_blocks(self, direction):
        hits = pygame.sprite.spritecollide(self, self.game.block, False)
        if hits:
            if direction == 'x':
                if self.x_change > 0:  # ke kanan
                    self.rect.right = hits[0].rect.left
                if self.x_change < 0:  # ke kiri
                    self.rect.left = hits[0].rect.right
            elif direction == 'y':
                if self.y_change > 0:  # ke bawah
                    self.rect.bottom = hits[0].rect.top
                if self.y_change < 0:  # ke atas
                    self.rect.top = hits[0].rect.bottom


class Block(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        
        self.game = game
        self._layer = BLOCK_LAYER
        self.groups = self.game.block, self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE

        self.image = self.game.terrain_spritesheet.get_sprite(11,7,self.width,self.height)#need variable like width, height,x,y of assets
        #self.image = pygame.Surface([self.width, self.height])
        #self.image.fill(CYAN)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

class Floor(pygame.sprite.Sprite):
    def __init__ (self, game ,x ,y):
        self.game = game
        self._layer = GROUND_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__ (self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.image = self.game.terrain_spritesheet.get_sprite(64, 352, self.width, self.height)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
