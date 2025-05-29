import pygame
from sprites import *
from config import *
import sys
from camera_system import Camera
from handler import run_battle



class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
                     
        self.screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.zoom = 1.3  # >1 = zoom in, <1 = zoom out
        self.camera_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))

        pygame.mixer.music.load('Assets/Music/Exploration/E1.ogg')  
        pygame.mixer.music.set_volume(0.5)         
        pygame.mixer.music.play(-1)   
        
        self.character_spritesheet = Spritesheet('img/BloodReaper/walk.png ')#image spritesheets char
        self.terrain_spritesheet = Spritesheet('img/Background/Ground_rocks.png')#image spritesheets env
        self.tile_spritesheet = Spritesheet('img/Background/Tile.png')#image spritesheets 

    def create_map(self):
        for i, row in enumerate(tilemap):
            for j, tile in enumerate(row):
                Floor(self, j,i)
                if tile == 'B':
                    Block(self, j, i)
                if tile == 'P':
                    Player(self, j, i)
                if tile == 'E':
                    Enemy(self, j, i,1)

    def new(self):
        self.playing = True
        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.block = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attack = pygame.sprite.LayeredUpdates()

        self.create_map()

        # Hitung ukuran total map berdasarkan tilemap
        map_width = len(tilemap[0]) * TILESIZE
        map_height = len(tilemap) * TILESIZE
        self.camera = Camera(map_width, map_height)

        # Temukan objek player untuk tracking kamera
        for sprite in self.all_sprites:
            if isinstance(sprite, Player):
                self.player = sprite

    def events(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def fade_out(self, color=(0, 0, 0), speed=5):
        fade_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        fade_surface.fill(color)
        for alpha in range(0, 256, speed):
            fade_surface.set_alpha(alpha)
            self.draw()  # Gambar game sebelum ditutup
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)

    def fade_in(self, color=(0, 0, 0), speed=5):
        fade_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        fade_surface.fill(color)
        for alpha in range(255, -1, -speed):
            fade_surface.set_alpha(alpha)
            self.draw()  # Gambar game yang muncul kembali
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            self.clock.tick(FPS)
            
    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)

         # Cek collision dengan enemy
        enemy_hit = pygame.sprite.spritecollideany(self.player, self.enemies)
        if enemy_hit and enemy_hit.alive:
            
            # Pause musik eksplorasi
            pygame.mixer.music.stop()
            run_battle(self.player.tipe,enemy_hit.tipe,tree_stats={
            'strength': 0,
            'energy': 0,
            'health': 0
        })
            # Jalankan mode battle dengan transisi
            #BUATIN REY FUNGSI MAIN BATTLENYA(NAMA FUNGSI ADALAH RUN_BATTLE)
            #run_battle(self.screen)

            # Setelah battle selesai, lanjutkan musik eksplorasi
            pygame.mixer.music.play(-1)

    def draw(self):
        self.camera_surface.fill(BLACK)
        for sprite in self.all_sprites:
            pos = self.camera.apply(sprite)
            self.camera_surface.blit(sprite.image, pos)

    # Zooming surface
        zoomed_width = int(WIN_WIDTH * self.zoom)
        zoomed_height = int(WIN_HEIGHT * self.zoom)
        zoomed_surface = pygame.transform.smoothscale(self.camera_surface, (zoomed_width, zoomed_height))

    # Centering the zoomed surface
        x_offset = (zoomed_width - WIN_WIDTH) // 2
        y_offset = (zoomed_height - WIN_HEIGHT) // 2
        self.screen.blit(zoomed_surface, (-x_offset, -y_offset))

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
