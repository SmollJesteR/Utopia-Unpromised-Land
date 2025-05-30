import pygame
from config import WIN_WIDTH, WIN_HEIGHT

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(WIN_WIDTH / 2)
        y = -target.rect.centery + int(WIN_HEIGHT / 2)

        # Batas kamera agar tidak keluar dari map
        x = min(0, x)
        y = min(0, y)
        x = max(-(self.width - WIN_WIDTH), x)
        y = max(-(self.height - WIN_HEIGHT), y)

        self.camera = pygame.Rect(x, y, self.width, self.height)
