import pygame
from config import *
import math
import random

class Spritesheet:
    def __init__(self,file):
        self.sheet = pygame.image.load(file).convert()
        
    def get_sprite(self, x, y, width, height):
        sprite = pygame.Surface([width, height])
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        sprite.set_colorkey(BLACK)
        return pygame.transform.scale(sprite, (TILESIZE, TILESIZE))

    
class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y,tipe):

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
        self.animation_loop = 1

        #image_load = pygame.game.load("img/1.png")
        self.image = self.game.character_spritesheet.get_sprite(15 , 12 , self.width,self.height) #need variable like x,y, width, height of assets
        #self.image = pygame.Surface([self.width, self.height])
        #self.image.set_colorkey(BLACK)
        #self.image.blit(image_load,(0,0))

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
        self.tipe = tipe
    
    def update(self):
        self.movement()
        self.animate()

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
    
    def animate(self):
            up_animations = [self.game.character_spritesheet.get_sprite(15,12,47,51),
                               self.game.character_spritesheet.get_sprite(79,12,43,50),
                               self.game.character_spritesheet.get_sprite(143,12,42,51),
                               self.game.character_spritesheet.get_sprite(207,13,43,51),
                               self.game.character_spritesheet.get_sprite(271,12,46,52),
                               self.game.character_spritesheet.get_sprite(335,12,47,50),
                               self.game.character_spritesheet.get_sprite(399,12,47,51),
                               self.game.character_spritesheet.get_sprite(463,12,47,51),
                               self.game.character_spritesheet.get_sprite(527,12,47,52)
                               ]
            left_animations = [self.game.character_spritesheet.get_sprite(7,76,38,51),
                             self.game.character_spritesheet.get_sprite(78,77,32,50),
                             self.game.character_spritesheet.get_sprite(138,76,37,50),
                             self.game.character_spritesheet.get_sprite(201,76,37,50),
                             self.game.character_spritesheet.get_sprite(262,76,41,50),
                             self.game.character_spritesheet.get_sprite(324,77,44,49),
                             self.game.character_spritesheet.get_sprite(390,76,41,51),
                             self.game.character_spritesheet.get_sprite(457,76,37,51),
                             self.game.character_spritesheet.get_sprite(522,76,37,51)
                             ]
            down_animations = [self.game.character_spritesheet.get_sprite(15,140,47,51),
                               self.game.character_spritesheet.get_sprite(79,140,43,51),
                               self.game.character_spritesheet.get_sprite(143,140,42,51),
                               self.game.character_spritesheet.get_sprite(207,141,43,51),
                               self.game.character_spritesheet.get_sprite(271,140,46,52),
                               self.game.character_spritesheet.get_sprite(335,140,47,51),
                               self.game.character_spritesheet.get_sprite(399,140,47,51),
                               self.game.character_spritesheet.get_sprite(463,141,46,51),
                               self.game.character_spritesheet.get_sprite(527,140,47,52)
                               ]
            right_animations = [self.game.character_spritesheet.get_sprite(19,204,38,51),
                                self.game.character_spritesheet.get_sprite(82,205,32,50),
                                self.game.character_spritesheet.get_sprite(145,204,37,50),
                                self.game.character_spritesheet.get_sprite(210,204,37,50),
                                self.game.character_spritesheet.get_sprite(273,204,41,50),
                                self.game.character_spritesheet.get_sprite(336,205,44,49),
                                self.game.character_spritesheet.get_sprite(401,204,41,51),
                                self.game.character_spritesheet.get_sprite(466,204,37,51),
                                self.game.character_spritesheet.get_sprite(529,204,37,51)
                                ]
            
            if self.facing == "down":
                if self.y_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(15,140,47,51)
                else:
                    self.image = down_animations[math.floor(self.animation_loop)]
                    self.animation_loop += 0.1
                    if self.animation_loop >= 9:
                        self.animation_loop = 1
                        
            if self.facing == "up":
                if self.y_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(15,12,47,51)
                else:
                    self.image = up_animations[math.floor(self.animation_loop)]
                    self.animation_loop += 0.1
                    if self.animation_loop >= 9:
                        self.animation_loop = 1
                    
            if self.facing == "left":
                if self.x_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(7,76,38,51)
                else:
                    self.image = left_animations[math.floor(self.animation_loop)]
                    self.animation_loop += 0.1
                    if self.animation_loop >= 9:
                        self.animation_loop = 1
                        
            if self.facing == "right":
                if self.x_change == 0:
                    self.image = self.game.character_spritesheet.get_sprite(19,204,38,51)
                else:
                    self.image = right_animations[math.floor(self.animation_loop)]
                    self.animation_loop += 0.1
                    if self.animation_loop >= 9:
                        self.animation_loop = 1
                        
class Enemy(pygame.sprite.Sprite):
    def __init__(self, game, x, y,tipe):
        self.game = game
        self._layer = ENEMY_LAYER
        self.groups = self.game.enemies ,self.game.all_sprites
        pygame.sprite.Sprite.__init__ (self, self.groups)
        
        self.x = x * TILESIZE
        self.y = y * TILESIZE
        self.width = TILESIZE
        self.height = TILESIZE
        
        self.image = self.game.tile_spritesheet.get_sprite(0,0,self.width, self.height)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

        self.tipe = tipe
        self.alive = True


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
        
        self.image = self.game.tile_spritesheet.get_sprite(0,0,self.width, self.height)
        
        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y
