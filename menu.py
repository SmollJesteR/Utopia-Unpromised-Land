import pygame
import sys
import subprocess
import time
import random
from button import Button  

# ========== KELAS UTILITAS ==========
class Scaler:
    """Kelas untuk menangani scaling antar resolusi"""
    def __init__(self, design_width=1920, design_height=1080):
        self.DESIGN_WIDTH = design_width
        self.DESIGN_HEIGHT = design_height
        
        # Dapatkan resolusi layar pengguna
        info = pygame.display.Info()
        self.USER_WIDTH = info.current_w
        self.USER_HEIGHT = info.current_h
        
        # Hitung scale factor
        self.SCALE_X = self.USER_WIDTH / self.DESIGN_WIDTH
        self.SCALE_Y = self.USER_HEIGHT / self.DESIGN_HEIGHT
        self.SCALE_FACTOR = min(self.SCALE_X, self.SCALE_Y)
        
        # Ukuran layar yang digunakan
        self.SCREEN_WIDTH = int(self.DESIGN_WIDTH * self.SCALE_FACTOR)
        self.SCREEN_HEIGHT = int(self.DESIGN_HEIGHT * self.SCALE_FACTOR)
        
        # Offset untuk centering
        self.OFFSET_X = (self.USER_WIDTH - self.SCREEN_WIDTH) // 2
        self.OFFSET_Y = (self.USER_HEIGHT - self.SCREEN_HEIGHT) // 2
    
    def scale_pos(self, x, y):
        """Scale koordinat dari design resolution ke screen resolution"""
        return int(x * self.SCALE_FACTOR), int(y * self.SCALE_FACTOR)
    
    def scale_size(self, width, height):
        """Scale ukuran dari design resolution ke screen resolution"""
        return int(width * self.SCALE_FACTOR), int(height * self.SCALE_FACTOR)
    
    def scale_rect(self, rect):
        """Scale pygame.Rect dari design resolution ke screen resolution"""
        x, y = self.scale_pos(rect.x, rect.y)
        w, h = self.scale_size(rect.width, rect.height)
        return pygame.Rect(x, y, w, h)
    
    def scale_surface(self, surface, target_width=None, target_height=None):
        """Scale surface dengan mempertahankan aspect ratio"""
        if target_width is None:
            target_width = int(surface.get_width() * self.SCALE_FACTOR)
        if target_height is None:
            target_height = int(surface.get_height() * self.SCALE_FACTOR)
        return pygame.transform.scale(surface, (target_width, target_height))

# ========== KELAS ENTITAS ==========
class Character:
    """Kelas untuk merepresentasikan karakter dalam game"""
    def __init__(self, name, image_path, color, description):
        self.name = name
        self.image = pygame.image.load(image_path)
        self.color = color
        self.description = description
        self.selected = False
    
    def scale_image(self, target_w, target_h, scaler):
        """Scale gambar karakter"""
        aspect = self.image.get_width() / self.image.get_height()
        target_aspect = target_w / target_h
        if aspect > target_aspect:
            new_w = target_w
            new_h = int(target_w / aspect)
        else:
            new_h = target_h
            new_w = int(target_h * aspect)
        return pygame.transform.scale(self.image, (new_w, new_h))

# ========== KELAS MANAJER ==========
class SoundManager:
    """Kelas untuk mengelola semua aspek suara dalam game"""
    def __init__(self):
        self.sound_enabled = True
        self.CLICK_SOUND = pygame.mixer.Sound("Assets/SFX/click_sound1.wav")
        pygame.mixer.music.load("Assets/Music/MainMenu/MM.wav")
    
    def play_click(self):
        """Mainkan suara klik jika suara diaktifkan"""
        if self.sound_enabled:
            self.CLICK_SOUND.play()
    
    def toggle_sound(self):
        """Toggle status suara"""
        self.sound_enabled = not self.sound_enabled
        pygame.mixer.music.set_volume(0.5 if self.sound_enabled else 0)
    
    def play_music(self):
        """Mainkan musik menu"""
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)

# ========== KELAS STATE ==========
class GameState:
    """Base class untuk semua state dalam game"""
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.scaler = game.scaler
        self.sound_manager = game.sound_manager
    
    def handle_events(self):
        pass
    
    def update(self):
        pass
    
    def draw(self):
        pass

class MainMenuState(GameState):
    """State untuk menu utama"""
    def __init__(self, game, replay_music=True):
        super().__init__(game)
        self.replay_music = replay_music
        self.selected_menu = 0
        self.setup_buttons()
        
        if replay_music:
            self.sound_manager.play_music()
    
    def setup_buttons(self):
        """Setup tombol-tombol di menu utama"""
        # Load dan scale button images
        play_img = pygame.image.load("Assets/Play Rect.png")
        options_img = pygame.image.load("Assets/Options Rect.png")
        quit_img = pygame.image.load("Assets/Quit Rect.png")
        
        play_img = self.scaler.scale_surface(play_img)
        options_img = self.scaler.scale_surface(options_img)
        quit_img = self.scaler.scale_surface(quit_img)
        
        # Scale button positions
        play_x, play_y = self.scaler.scale_pos(960, 425)
        opt_x, opt_y = self.scaler.scale_pos(960, 625)
        quit_x, quit_y = self.scaler.scale_pos(960, 825)
        
        self.buttons = [
            Button(
                image=play_img,
                pos=(play_x + self.scaler.OFFSET_X, play_y + self.scaler.OFFSET_Y),
                text_input="PLAY",
                font=self.game.get_font(75),
                base_color="#d7fcd4" if self.selected_menu != 0 else "White",
                hovering_color="White"
            ),
            Button(
                image=options_img,
                pos=(opt_x + self.scaler.OFFSET_X, opt_y + self.scaler.OFFSET_Y),
                text_input="OPTIONS",
                font=self.game.get_font(75),
                base_color="#d7fcd4" if self.selected_menu != 1 else "White",
                hovering_color="White"
            ),
            Button(
                image=quit_img,
                pos=(quit_x + self.scaler.OFFSET_X, quit_y + self.scaler.OFFSET_Y),
                text_input="QUIT",
                font=self.game.get_font(75),
                base_color="#d7fcd4" if self.selected_menu != 2 else "White",
                hovering_color="White"
            )
        ]
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_menu = (self.selected_menu - 1) % 3
                elif event.key == pygame.K_DOWN:
                    self.selected_menu = (self.selected_menu + 1) % 3
                elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    self.sound_manager.play_click()
                    if self.selected_menu == 0:
                        self.game.change_state(PlayState(self.game))
                    elif self.selected_menu == 1:
                        self.game.change_state(OptionsState(self.game))
                    elif self.selected_menu == 2:
                        pygame.quit()
                        sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for i, button in enumerate(self.buttons):
                    if button.checkForInput(mouse_pos):
                        self.sound_manager.play_click()
                        if i == 0:
                            self.game.change_state(PlayState(self.game))
                        elif i == 1:
                            self.game.change_state(OptionsState(self.game))
                        elif i == 2:
                            pygame.quit()
                            sys.exit()
    
    def update(self):
        # Update warna tombol berdasarkan mouse
        mouse_pos = pygame.mouse.get_pos()
        for i, button in enumerate(self.buttons):
            button.changeColor(mouse_pos)
            # Update warna berdasarkan keyboard selection
            if i == self.selected_menu:
                button.base_color = "White"
            else:
                button.base_color = "#d7fcd4"
    
    def draw(self):
        # Fill dengan warna hitam untuk letterbox/pillarbox
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game.BG, (self.scaler.OFFSET_X, self.scaler.OFFSET_Y))
        
        # Render judul menu
        MENU_TEXT = self.game.get_font(100).render("", True, "#b68f40")
        menu_x, menu_y = self.scaler.scale_pos(960, 230)
        MENU_RECT = MENU_TEXT.get_rect(center=(menu_x + self.scaler.OFFSET_X, menu_y + self.scaler.OFFSET_Y))
        self.screen.blit(MENU_TEXT, MENU_RECT)
        
        # Render tombol
        for button in self.buttons:
            button.update(self.screen)

class PlayState(GameState):
    """State untuk memilih karakter"""
    def __init__(self, game):
        super().__init__(game)
        self.selected_character = 1
        self.characters = [
            Character("Ashen Warrior", "Assets/SplashArt/AW.png", (120, 200, 255), 
                     "Ashen Warrior is a Warden from Le Beaux Family,\n His Vigor is unmatched througout the Land."),
            Character("Blood Reaper", "Assets/SplashArt/BR.png", (255, 100, 100), 
                     "Blood Reaper is an Ex-Mercenary Head from Hound Dogs Corps,\nHis Vicious Grit are Relentless in The Battlefield.")
        ]
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk state ini"""
        # Scale target size
        self.TARGET_WIDTH, self.TARGET_HEIGHT = self.scaler.scale_size(240, 420)
        
        # Scale karakter images
        for char in self.characters:
            char.scaled_image = char.scale_image(
                self.TARGET_WIDTH, self.TARGET_HEIGHT, self.scaler
            )
        
        # Setup tombol back
        back_x, back_y = self.scaler.scale_pos(960, 900)
        self.BACK_BTN = Button(
            image=None, 
            pos=(back_x + self.scaler.OFFSET_X, back_y + self.scaler.OFFSET_Y), 
            text_input="BACK", 
            font=self.game.get_font(28), 
            base_color="White", 
            hovering_color="Green"
        )
    
    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.selected_character = 1
                elif event.key == pygame.K_RIGHT:
                    self.selected_character = 2
                elif event.key in [pygame.K_RETURN, pygame.K_KP_ENTER]:
                    self.sound_manager.play_click()
                    self.game.change_state(CharacterStoryState(self.game, self.selected_character))
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.BACK_BTN.checkForInput(mouse_pos):
                    self.sound_manager.play_click()
                    self.game.change_state(MainMenuState(self.game, replay_music=False))
                
                # Handle karakter selection
                if self.left_rect.collidepoint(mouse_pos) or self.left_name_box.collidepoint(mouse_pos):
                    self.sound_manager.play_click()
                    self.game.change_state(CharacterStoryState(self.game, 1))
                if self.right_rect.collidepoint(mouse_pos) or self.right_name_box.collidepoint(mouse_pos):
                    self.sound_manager.play_click()
                    self.game.change_state(CharacterStoryState(self.game, 2))
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.BACK_BTN.changeColor(mouse_pos)
        
        # Update character boxes positions
        left_rect_scaled = self.scaler.scale_rect(pygame.Rect(560, 300, 240, 420))
        right_rect_scaled = self.scaler.scale_rect(pygame.Rect(1120, 300, 240, 420))
        
        self.left_rect = pygame.Rect(
            left_rect_scaled.x + self.scaler.OFFSET_X, 
            left_rect_scaled.y + self.scaler.OFFSET_Y, 
            left_rect_scaled.width, 
            left_rect_scaled.height
        )
        self.right_rect = pygame.Rect(
            right_rect_scaled.x + self.scaler.OFFSET_X, 
            right_rect_scaled.y + self.scaler.OFFSET_Y, 
            right_rect_scaled.width, 
            right_rect_scaled.height
        )
        
        # Update name boxes
        name_box_height = int(60 * self.scaler.SCALE_FACTOR)
        name_box_gap = int(60 * self.scaler.SCALE_FACTOR)
        name_box_width = int(320 * self.scaler.SCALE_FACTOR)
        
        self.left_name_box = pygame.Rect(
            self.left_rect.centerx - name_box_width // 2, 
            self.left_rect.bottom + name_box_gap, 
            name_box_width, 
            name_box_height
        )
        self.right_name_box = pygame.Rect(
            self.right_rect.centerx - name_box_width // 2, 
            self.right_rect.bottom + name_box_gap, 
            name_box_width, 
            name_box_height
        )
    
    def draw(self):
        # Fill dengan warna hitam untuk letterbox/pillarbox
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game.BG, (self.scaler.OFFSET_X, self.scaler.OFFSET_Y))
        
        # Render judul
        PLAY_TEXT = self.game.get_font(45).render("Select Your Character", True, "White")
        title_x, title_y = self.scaler.scale_pos(960, 250)
        PLAY_RECT = PLAY_TEXT.get_rect(center=(title_x + self.scaler.OFFSET_X, title_y + self.scaler.OFFSET_Y))
        self.screen.blit(PLAY_TEXT, PLAY_RECT)
        
        # Draw character boxes
        pygame.draw.rect(self.screen, (50, 50, 50), self.left_rect, border_radius=10)
        pygame.draw.rect(self.screen, (50, 50, 50), self.right_rect, border_radius=10)
        
        # Draw character images
        self.screen.blit(self.characters[0].scaled_image, 
                        (self.left_rect.centerx - self.characters[0].scaled_image.get_width()//2, 
                         self.left_rect.centery - self.characters[0].scaled_image.get_height()//2))
        
        self.screen.blit(self.characters[1].scaled_image, 
                        (self.right_rect.centerx - self.characters[1].scaled_image.get_width()//2, 
                         self.right_rect.centery - self.characters[1].scaled_image.get_height()//2))
        
        # Draw name boxes
        char_font = self.game.get_font(32)
        char1_color = "Green" if self.selected_character == 1 else "White"
        char2_color = "Green" if self.selected_character == 2 else "White"
        
        char1_text = char_font.render("Ashen Warrior", True, char1_color)
        char2_text = char_font.render("Blood Reaper", True, char2_color)
        
        self.screen.blit(char1_text, (self.left_name_box.centerx - char1_text.get_width()//2, 
                                     self.left_name_box.centery - char1_text.get_height()//2))
        self.screen.blit(char2_text, (self.right_name_box.centerx - char2_text.get_width()//2, 
                                     self.right_name_box.centery - char2_text.get_height()//2))
        
        # Draw back button
        self.BACK_BTN.update(self.screen)

class CharacterStoryState(GameState):
    """State untuk menampilkan cerita karakter"""
    def __init__(self, game, selected_character):
        super().__init__(game)
        self.selected_character = selected_character
        self.character = self.game.characters[selected_character - 1]
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk state ini"""
        # Scale karakter image
        TARGET_WIDTH, TARGET_HEIGHT = self.scaler.scale_size(280, 540)
        self.char_img = self.character.scale_image(TARGET_WIDTH, TARGET_HEIGHT, self.scaler)
        
        # Setup tombol
        back_btn_x = self.scaler.OFFSET_X + int(180 * self.scaler.SCALE_FACTOR)
        back_btn_y = self.scaler.SCREEN_HEIGHT + self.scaler.OFFSET_Y - int(80 * self.scaler.SCALE_FACTOR)
        
        start_btn_x = self.scaler.SCREEN_WIDTH + self.scaler.OFFSET_X - int(180 * self.scaler.SCALE_FACTOR)
        start_btn_y = self.scaler.SCREEN_HEIGHT + self.scaler.OFFSET_Y - int(80 * self.scaler.SCALE_FACTOR)
        
        self.BACK_BTN = Button(
            image=None,
            pos=(back_btn_x, back_btn_y),
            text_input="BACK",
            font=self.game.get_font(28),
            base_color="White",
            hovering_color="Green"
        )
        
        self.START_BTN = Button(
            image=None,
            pos=(start_btn_x, start_btn_y),
            text_input="START",
            font=self.game.get_font(28),
            base_color="White",
            hovering_color="Green"
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.BACK_BTN.checkForInput(mouse_pos):
                    self.sound_manager.play_click()
                    self.game.change_state(PlayState(self.game))
                
                if self.START_BTN.checkForInput(mouse_pos):
                    self.start_game()
    
    def start_game(self):
        """Mulai permainan utama"""
        self.sound_manager.play_click()
        self.smooth_transition_to_main()
        import main
        main.main(self.selected_character)
        sys.exit()
    
    def smooth_transition_to_main(self):
        """Animasi transisi ke permainan utama"""
        LOADING_BACKGROUNDS = [
            pygame.image.load('Assets/loading/1.png').convert_alpha(),
            pygame.image.load('Assets/loading/2.png').convert_alpha(),
            pygame.image.load('Assets/loading/3.png').convert_alpha()
        ]
        LOADING_BACKGROUNDS = [self.scaler.scale_surface(img, self.scaler.SCREEN_WIDTH, self.scaler.SCREEN_HEIGHT) 
                              for img in LOADING_BACKGROUNDS]
        
        bg_img = random.choice(LOADING_BACKGROUNDS)
        fade_surface = pygame.Surface((self.scaler.USER_WIDTH, self.scaler.USER_HEIGHT))
        fade_surface.fill((0, 0, 0))
        
        steps = 50
        for i in range(steps + 1):
            alpha = int(255 * i / steps)
            blur_amount = 1 + (4 * (alpha / 255))
            
            # Blur background loading
            blurred_bg = pygame.transform.smoothscale(
                pygame.transform.smoothscale(bg_img, 
                                          (int(self.scaler.SCREEN_WIDTH / blur_amount), 
                                           int(self.scaler.SCREEN_HEIGHT / blur_amount))),
                (self.scaler.SCREEN_WIDTH, self.scaler.SCREEN_HEIGHT)
            )
            
            self.screen.fill((0, 0, 0))
            self.screen.blit(blurred_bg, (self.scaler.OFFSET_X, self.scaler.OFFSET_Y))
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.update()
            pygame.time.wait(10)
        
        # Tampilkan loading screen penuh 1 detik
        self.screen.blit(bg_img, (self.scaler.OFFSET_X, self.scaler.OFFSET_Y))
        pygame.display.update()
        pygame.time.wait(1000)
    
    def draw(self):
        # Fill dengan warna hitam untuk letterbox/pillarbox
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.game.BG, (self.scaler.OFFSET_X, self.scaler.OFFSET_Y))
        
        # Center character box
        char_rect_w, char_rect_h = self.scaler.scale_size(280, 540)
        char_rect_x = (self.scaler.SCREEN_WIDTH - char_rect_w) // 3
        char_rect_y = int(320 * self.scaler.SCALE_FACTOR)
        char_rect = pygame.Rect(char_rect_x + self.scaler.OFFSET_X, 
                               char_rect_y + self.scaler.OFFSET_Y, 
                               char_rect_w, char_rect_h)
        
        # Render nama karakter
        name_font = self.game.get_font(48)
        gap = int(80 * self.scaler.SCALE_FACTOR)
        title_text = name_font.render(self.character.name, True, "White")
        title_rect = title_text.get_rect(center=(char_rect.centerx, char_rect.top - gap))
        self.screen.blit(title_text, title_rect)
        
        # Render gambar karakter
        self.screen.blit(self.char_img, (char_rect.x, char_rect.y))
        
        # Render deskripsi karakter
        desc_width = int(600 * self.scaler.SCALE_FACTOR)
        desc_font = self.game.get_font(18)
        desc_lines = []
        
        for paragraph in self.character.description.split('\n'):
            words = paragraph.split(' ')
            line = ""
            for word in words:
                test_line = line + word + " "
                test_surface = desc_font.render(test_line, True, "White")
                if test_surface.get_width() > desc_width:
                    desc_lines.append(line)
                    line = word + " "
                else:
                    line = test_line
            desc_lines.append(line)
        
        line_spacing = int(38 * self.scaler.SCALE_FACTOR)
        desc_title_gap = int(10 * self.scaler.SCALE_FACTOR)
        desc_y = char_rect.top 
        
        # Position deskripsi
        desc_spacing = int(140 * self.scaler.SCALE_FACTOR)
        desc_x = char_rect.right + desc_spacing
        
        for i, line in enumerate(desc_lines):
            desc_text = desc_font.render(line.strip(), True, "White")
            desc_rect = desc_text.get_rect()
            desc_rect.topleft = (desc_x, desc_y + i * line_spacing)
            self.screen.blit(desc_text, desc_rect)
        
        # Render perk rect
        rect_gap = int(40 * self.scaler.SCALE_FACTOR)
        perk_rect_y = desc_y + len(desc_lines) * line_spacing + rect_gap
        perk_rect_width = min(int(500 * self.scaler.SCALE_FACTOR), 
                             (self.scaler.SCREEN_WIDTH + self.scaler.OFFSET_X) - desc_x - int(20 * self.scaler.SCALE_FACTOR))
        
        perk_rect = pygame.Rect(
            desc_x,
            perk_rect_y,
            perk_rect_width,
            int(50 * self.scaler.SCALE_FACTOR)
        )
        border_radius = int(18 * self.scaler.SCALE_FACTOR)
        pygame.draw.rect(self.screen, (200, 200, 80), perk_rect, border_radius=border_radius)
        
        # Update dan render tombol
        self.BACK_BTN.changeColor(pygame.mouse.get_pos())
        self.START_BTN.changeColor(pygame.mouse.get_pos())
        self.BACK_BTN.update(self.screen)
        self.START_BTN.update(self.screen)

class OptionsState(GameState):
    """State untuk menu pengaturan"""
    def __init__(self, game):
        super().__init__(game)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup UI untuk state ini"""
        # Setup tombol back
        back_x, back_y = self.scaler.scale_pos(130, 1020)
        self.OPTIONS_BACK = Button(
            image=None,
            pos=(back_x, back_y),
            text_input="BACK",
            font=self.game.get_font(50),
            base_color="Black",
            hovering_color="Green"
        )
        
        # Setup tombol sound toggle
        sound_btn_x, sound_btn_y = self.scaler.scale_pos(960, 600)
        self.SOUND_BTN = Button(
            image=None,
            pos=(sound_btn_x + self.scaler.OFFSET_X, sound_btn_y + self.scaler.OFFSET_Y),
            text_input=f"SOUND: {'ON' if self.sound_manager.sound_enabled else 'OFF'}",
            font=self.game.get_font(50),
            base_color="Black",
            hovering_color="Green"
        )
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                if self.OPTIONS_BACK.checkForInput(mouse_pos):
                    self.sound_manager.play_click()
                    self.game.change_state(MainMenuState(self.game, replay_music=False))
                
                if self.SOUND_BTN.checkForInput(mouse_pos):
                    self.sound_manager.toggle_sound()
                    self.sound_manager.play_click()
                    # Update teks tombol
                    self.SOUND_BTN.text_input = f"SOUND: {'ON' if self.sound_manager.sound_enabled else 'OFF'}"
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        self.OPTIONS_BACK.changeColor(mouse_pos)
        self.SOUND_BTN.changeColor(mouse_pos)
    
    def draw(self):
        self.screen.fill("white")
        
        # Render judul
        OPTIONS_TEXT = self.game.get_font(45).render("Settings", True, "Black")
        opt_x, opt_y = self.scaler.scale_pos(960, 390)
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(opt_x + self.scaler.OFFSET_X, opt_y + self.scaler.OFFSET_Y))
        self.screen.blit(OPTIONS_TEXT, OPTIONS_RECT)
        
        # Render tombol
        self.OPTIONS_BACK.update(self.screen)
        self.SOUND_BTN.update(self.screen)

# ========== KELAS GAME UTAMA ==========
class Game:
    """Kelas utama untuk mengelola game"""
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        # Inisialisasi komponen
        self.scaler = Scaler()
        self.sound_manager = SoundManager()
        
        # Setup screen
        self.screen = pygame.display.set_mode((self.scaler.USER_WIDTH, self.scaler.USER_HEIGHT))
        pygame.display.set_caption("Menu")
        
        # Load background
        self.BG = pygame.image.load("Assets/Background.png")
        self.BG = self.scaler.scale_surface(self.BG, self.scaler.SCREEN_WIDTH, self.scaler.SCREEN_HEIGHT)
        
        # Inisialisasi karakter
        self.characters = [
            Character("Ashen Warrior", "Assets/SplashArt/AW.png", (120, 200, 255), 
                     "Ashen Warrior adalah penjaga biru yang setia,\nberjuang demi keadilan dan kedamaian di Utopia."),
            Character("Blood Reaper", "Assets/SplashArt/BR.png", (255, 100, 100), 
                     "Blood Reaper adalah pendekar merah yang kejam,\nmenebar teror demi ambisi dan kekuatan.")
        ]
        
        # Setup state awal
        self.current_state = MainMenuState(self)
    
    def get_font(self, size):
        """Dapatkan font yang sudah di-scale"""
        scaled_size = max(1, int(size * self.scaler.SCALE_FACTOR))
        return pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", scaled_size)
    
    def change_state(self, new_state):
        """Ganti state game saat ini"""
        self.current_state = new_state
    
    def run(self):
        """Main game loop"""
        while True:
            self.current_state.handle_events()
            self.current_state.update()
            self.current_state.draw()
            pygame.display.update()

# ========== RUN GAME ==========
if __name__ == "__main__":
    game = Game()
    game.run()