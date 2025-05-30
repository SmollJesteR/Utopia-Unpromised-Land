import pygame
import json
from sprites import *
from config import *
from display_manager import DisplayManager
import sys
from camera_system import Camera
from handler import run_battle
import random

# Initialize pygame first
pygame.init()
pygame.mixer.init()

# ========== SCALING SYSTEM ==========
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080

# Now we can safely get display info
info = pygame.display.Info()
USER_WIDTH = info.current_w
USER_HEIGHT = info.current_h

SCALE_X = USER_WIDTH / DESIGN_WIDTH
SCALE_Y = USER_HEIGHT / DESIGN_HEIGHT
SCALE_FACTOR = min(SCALE_X, SCALE_Y)

SCREEN_WIDTH = int(DESIGN_WIDTH * SCALE_FACTOR)
SCREEN_HEIGHT = int(DESIGN_HEIGHT * SCALE_FACTOR)

OFFSET_X = (USER_WIDTH - SCREEN_WIDTH) // 2
OFFSET_Y = (USER_HEIGHT - SCREEN_HEIGHT) // 2

def scale_pos(x, y):
    return int(x * SCALE_FACTOR), int(y * SCALE_FACTOR)

def scale_size(width, height):
    return int(width * SCALE_FACTOR), int(height * SCALE_FACTOR)

def scale_rect(rect):
    x, y = scale_pos(rect.x, rect.y)
    w, h = scale_size(rect.width, rect.height)
    return pygame.Rect(x + OFFSET_X, y + OFFSET_Y, w, h)

def scale_surface(surface):
    width = int(surface.get_width() * SCALE_FACTOR)
    height = int(surface.get_height() * SCALE_FACTOR)
    return pygame.transform.scale(surface, (width, height))

# Screen setup
screen = pygame.display.set_mode((USER_WIDTH, USER_HEIGHT))

# Load and scale background
background_img = pygame.image.load('img/Background/Map.png').convert_alpha()
background_img = scale_surface(background_img)

# Scale UI elements
attack_icon_rect = scale_rect(pygame.Rect(350, 820, 64, 64))


class Game:
    def __init__(self, player_choice):
        pygame.init()
        pygame.mixer.init()
        
        # Get user's display info
        display_info = pygame.display.Info()
        self.user_width = display_info.current_w
        self.user_height = display_info.current_h
        
        # Calculate scaling factors
        self.scale_x = self.user_width / WIN_WIDTH
        self.scale_y = self.user_height / WIN_HEIGHT
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        # Create window without fancy flags
        self.screen = pygame.display.set_mode((self.user_width, self.user_height))
        pygame.display.set_caption('Utopia')
        
        # Create surfaces for rendering
        self.game_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        self.camera_surface = pygame.Surface((WIN_WIDTH, WIN_HEIGHT))
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.zoom = 1.25  # >1 = zoom in, <1 = zoom out
        self.player_choice = player_choice  # Set dari argumen, bukan hardcoded
        # Load stat tree dari file jika ada, jika tidak default 0
        try:
            with open("tree_stats.json", "r") as f:
                self.tree_stats = json.load(f)
        except Exception:
            self.tree_stats = {'strength': 0, 'energy': 0, 'health': 0}  # <-- Tambah ini

        pygame.mixer.music.load('Assets/Music/Exploration/E1.ogg')  
        pygame.mixer.music.set_volume(0.5)         
        pygame.mixer.music.play(-1)   
        
        self.character_spritesheet = Spritesheet('img/AshenKnight/walk.png ')#image spritesheets char
        self.character_spritesheet2 = Spritesheet('img/BloodReaper/walk.png')#
        self.terrain_spritesheet = Spritesheet('img/Background/Ground_rocks.png')#image spritesheets env
        self.tile_spritesheet = Spritesheet('img/Background/grass.png')#image spritesheets
        self.stonewall_spritesheet = Spritesheet('img/Background/stonewall.png')#image spritesheets wall
        self.tree_spritesheet = Spritesheet('img/Background/darktree2.png')#image spritesheets tree
        self.tree2_spritesheet = Spritesheet('img/Background/Tree.png')#image spritesheets tree2 

        # Add loading screen images
        self.loading_screens = [
            pygame.image.load('Assets/loading/1.png').convert_alpha(),
            pygame.image.load('Assets/loading/2.png').convert_alpha(),
            pygame.image.load('Assets/loading/3.png').convert_alpha()
        ]
        # Scale loading screens
        self.loading_screens = [scale_surface(img) for img in self.loading_screens]
        
        # Add transition states
        self.state = "explore"  # States: explore, battle, loading
        self.next_state = None
        self.fade_alpha = 0
        self.fade_speed = 5
        self.loading_duration = 1000  # 1 second for loading screen
        self.loading_start = 0
        self.current_loading_screen = None  # Add this line
        self.in_battle = False  # Add this line
        self.last_check_time = 0  # Add timer for status check
        
    def create_map(self):
        for i, row in enumerate(tilemap):
            for j, tile in enumerate(row):
                Floor(self, j,i)
                if tile == 'B':
                    Block(self, j, i)
                if tile == 'P':
                    player = Player(self, j, i, self.player_choice)
                    player.tipe = self.player_choice  # Add tipe attribute matching player_choice
                if tile == 'W':
                    Wall(self, j, i)
                if tile == 'T':
                    Tree(self, j, i)
                if tile == 'D':
                    Tree2(self, j, i) 
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

    def apply_blur(self, surface, amount):
        """Apply gaussian blur effect to surface"""
        scaled = pygame.transform.scale(surface, 
                                      (int(surface.get_width() / amount),
                                       int(surface.get_height() / amount)))
        scaled = pygame.transform.scale(scaled, (surface.get_width(), surface.get_height()))
        return scaled

    def smooth_transition(self, start_alpha, end_alpha, steps=50):
        # Capture current screen
        current_screen = self.screen.copy()
        
        # Calculate blur amounts
        blur_steps = 5  # Number of blur stages
        
        for alpha in range(start_alpha, end_alpha, (end_alpha - start_alpha) // steps):
            # Calculate blur amount based on alpha
            blur_amount = 1 + (4 * (alpha / 255))  # Blur increases with alpha
            
            # Apply blur to current screen
            blurred = self.apply_blur(current_screen, blur_amount)
            
            # Apply fade
            fade = pygame.Surface((self.user_width, self.user_height))
            fade.fill((0, 0, 0))
            fade.set_alpha(alpha)
            
            # Draw blurred screen and fade
            self.screen.blit(blurred, (0, 0))
            self.screen.blit(fade, (0, 0))
            
            pygame.display.flip()
            pygame.time.wait(10)  # Slightly longer delay for smoother effect

    def show_loading_screen(self):
        # Choose a random loading screen if none selected
        if not self.current_loading_screen:
            self.current_loading_screen = random.choice(self.loading_screens)
        
        x = (USER_WIDTH - self.current_loading_screen.get_width()) // 2
        y = (USER_HEIGHT - self.current_loading_screen.get_height()) // 2
        
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.current_loading_screen, (x, y))
        pygame.display.flip()
        
    def handle_transition(self):
        if self.state == "explore" and self.next_state == "battle":
            # Fade out from explore
            if self.fade_alpha < 255:
                self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
            else:
                self.state = "loading"
                self.loading_start = pygame.time.get_ticks()
                self.fade_alpha = 0
                
        elif self.state == "loading":
            current_time = pygame.time.get_ticks()
            if current_time - self.loading_start >= self.loading_duration:
                if self.next_state == "battle":
                    self.state = "battle"
                elif self.next_state == "explore":
                    self.state = "explore"
                self.fade_alpha = 0
                
        elif self.state == "battle" and self.next_state == "explore":
            if self.fade_alpha < 255:
                self.fade_alpha = min(255, self.fade_alpha + self.fade_speed)
            else:
                self.state = "loading"
                self.loading_start = pygame.time.get_ticks()
                self.fade_alpha = 0

    def draw_transition(self):
        if self.fade_alpha > 0:
            fade_surface = pygame.Surface((self.user_width, self.user_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(self.fade_alpha)
            self.screen.blit(fade_surface, (0, 0))
            
        if self.state == "loading":
            loading_img = random.choice(self.loading_screens)
            x = (self.user_width - loading_img.get_width()) // 2
            y = (self.user_height - loading_img.get_height()) // 2
            self.screen.fill((0, 0, 0))
            self.screen.blit(loading_img, (x, y))

    def check_alive_status(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_check_time >= 500:  # Check every 500ms (0.5 seconds)
            self.last_check_time = current_time
            try:
                with open('alive_status.json', 'r') as f:
                    status = json.load(f)
                    print(f"Debug: Checking alive_status.json - Status: {status}")
                    if status.get('alive_status') == False:
                        print("Debug: alive_status is False - Exiting battle!")
                        # Reset battle state
                        self.in_battle = False
                        # Reset json status
                        with open('alive_status.json', 'w') as f:
                            json.dump({"alive_status": True}, f)
                            print("Debug: Reset alive_status to True")
                        # Resume exploration music
                        pygame.mixer.music.load('Assets/Music/Exploration/E1.ogg')
                        pygame.mixer.music.set_volume(0.5)
                        pygame.mixer.music.play(-1)
                        print("Debug: Resumed exploration music")
                        # Fade back to exploration
                        self.smooth_transition(255, 0)
                        self.current_loading_screen = None
                        return True
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Debug: Error reading alive_status.json - {e}")
        return False

    def update(self):
        if self.in_battle:
            if self.check_alive_status():
                return
        # ...existing code...

        self.all_sprites.update()
        self.camera.update(self.player)

        # Handle enemy collision
        enemy_hit = pygame.sprite.spritecollideany(self.player, self.enemies)
        if enemy_hit and enemy_hit.alive:
            enemy_hit.alive = False
            self.in_battle = True

            # Fade out to loading screen
            self.smooth_transition(0, 255)
            self.current_loading_screen = random.choice(self.loading_screens)
            self.show_loading_screen()
            pygame.time.wait(1000)
            pygame.mixer.music.stop()

            # Kirim stat tree yang sudah diupdate
            encounter_value = random.choice([5, 15, 20] + [i for i in range(1, 21) if i not in [5, 15, 20]])
            boss_type = 3 if encounter_value == 5 else 2 if encounter_value == 15 else 1 if encounter_value == 20 else random.choice([4, 5])

            # --- Kirim stat tree yang sudah diupdate ---
            battle_result = run_battle(self.player.tipe, boss_type, tree_stats=self.tree_stats)

            # Setelah battle, cek apakah ada file stat_increased.json dan update self.tree_stats
            try:
                with open("stat_increased.json", "r") as f:
                    data = json.load(f)
                    stat = data.get("stat")
                    amount = data.get("amount", 0)
                    if stat in self.tree_stats:
                        self.tree_stats[stat] += amount
                        if self.tree_stats[stat] < 0:
                            self.tree_stats[stat] = 0
                # Simpan stat tree ke file agar persistent
                with open("tree_stats.json", "w") as f:
                    json.dump(self.tree_stats, f)
                import os
                os.remove("stat_increased.json")
            except Exception:
                pass

            # ...existing code...
            self.smooth_transition(0, 255)
            self.current_loading_screen = random.choice(self.loading_screens)
            self.show_loading_screen()
            pygame.time.wait(1000)
            pygame.mixer.music.load('Assets/Music/Exploration/E1.ogg')
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)
            self.smooth_transition(255, 0)
            self.in_battle = False
            self.current_loading_screen = None

    def draw(self):
        # Draw to game surface first
        self.game_surface.fill(BLACK)
        for sprite in self.all_sprites:
            pos = self.camera.apply(sprite)
            self.game_surface.blit(sprite.image, pos)

        # Apply zoom
        zoomed_width = int(WIN_WIDTH * self.zoom)
        zoomed_height = int(WIN_HEIGHT * self.zoom)
        zoomed_surface = pygame.transform.smoothscale(self.game_surface, 
                                                    (zoomed_width, zoomed_height))

        # Scale to screen size directly
        scaled_surface = pygame.transform.smoothscale(zoomed_surface, 
                                                    (self.user_width, self.user_height))
        self.screen.blit(scaled_surface, (0, 0))
        
        self.draw_transition()
        pygame.display.update()
        self.clock.tick(FPS)

        
    def main(self):
        while self.playing:
            self.events()
            self.update()
            self.draw()
        self.running = False

    def game_over(self):
        pass
    
    def intro_screen(self):
        # Skip character selection since we're using hardcoded choice
        pass

def main(player_choice=1):
    g = Game(player_choice)
    g.intro_screen()
    g.new()
    while g.running:
        g.main()
    pygame.quit()
    sys.exit()

# Only run as script if called directly (not when imported from menu.py)
if __name__ == "__main__":
    import sys
    player_choice = 1
    if len(sys.argv) > 1:
        try:
            player_choice = int(sys.argv[1])
        except Exception:
            player_choice = 1
    main(player_choice)
