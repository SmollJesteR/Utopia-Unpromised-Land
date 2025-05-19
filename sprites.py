import pygame
from config import *
import math
import random

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

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(RED)

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

        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(CYAN)

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
