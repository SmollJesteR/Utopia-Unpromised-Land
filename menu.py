import pygame, sys
from button import Button
import subprocess
import time
import random

pygame.init()
pygame.mixer.init()

# ========== SCALING SYSTEM ==========
# Design resolution (resolusi asset asli)
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080

# Dapatkan resolusi layar pengguna
info = pygame.display.Info()
USER_WIDTH = info.current_w
USER_HEIGHT = info.current_h

# Hitung scale factor (gunakan yang lebih kecil agar tidak terpotong)
SCALE_X = USER_WIDTH / DESIGN_WIDTH
SCALE_Y = USER_HEIGHT / DESIGN_HEIGHT
SCALE_FACTOR = min(SCALE_X, SCALE_Y)

# Ukuran layar yang akan digunakan (proporsional dengan design)
SCREEN_WIDTH = int(DESIGN_WIDTH * SCALE_FACTOR)
SCREEN_HEIGHT = int(DESIGN_HEIGHT * SCALE_FACTOR)

# Offset untuk centering jika ada letterbox/pillarbox
OFFSET_X = (USER_WIDTH - SCREEN_WIDTH) // 2
OFFSET_Y = (USER_HEIGHT - SCREEN_HEIGHT) // 2

# ========== UTILITY FUNCTIONS ==========
def scale_pos(x, y):
    """Scale koordinat dari design resolution ke screen resolution"""
    return int(x * SCALE_FACTOR), int(y * SCALE_FACTOR)

def scale_size(width, height):
    """Scale ukuran dari design resolution ke screen resolution"""
    return int(width * SCALE_FACTOR), int(height * SCALE_FACTOR)

def scale_rect(rect):
    """Scale pygame.Rect dari design resolution ke screen resolution"""
    x, y = scale_pos(rect.x, rect.y)
    w, h = scale_size(rect.width, rect.height)
    return pygame.Rect(x, y, w, h)

def scale_surface(surface, target_width=None, target_height=None):
    """Scale surface dengan mempertahankan aspect ratio"""
    if target_width is None:
        target_width = int(surface.get_width() * SCALE_FACTOR)
    if target_height is None:
        target_height = int(surface.get_height() * SCALE_FACTOR)
    return pygame.transform.scale(surface, (target_width, target_height))

# ========== SCREEN SETUP ==========
SCREEN = pygame.display.set_mode((USER_WIDTH, USER_HEIGHT))
pygame.display.set_caption("Menu")

# Load dan scale background
BG = pygame.image.load("Assets/Background.png")
BG = scale_surface(BG, SCREEN_WIDTH, SCREEN_HEIGHT)

def get_font(size):
    # Scale font size juga
    scaled_size = max(1, int(size * SCALE_FACTOR))
    return pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", scaled_size)

# ========== LOAD SOUND ==========
CLICK_SOUND = pygame.mixer.Sound("Assets/SFX/click_sound1.wav")  # Ganti path sesuai file Anda

sound_enabled = True

def play_click_sound():
    if sound_enabled:
        CLICK_SOUND.play()

# Tambahkan daftar background loading (gunakan gambar loading yang sama dengan main.py)
LOADING_BACKGROUNDS = [
    pygame.image.load('Assets/loading/1.png').convert_alpha(),
    pygame.image.load('Assets/loading/2.png').convert_alpha(),
    pygame.image.load('Assets/loading/3.png').convert_alpha()
]
LOADING_BACKGROUNDS = [scale_surface(img, SCREEN_WIDTH, SCREEN_HEIGHT) for img in LOADING_BACKGROUNDS]

def smooth_transition_to_main():
    # Pilih background random
    bg_img = random.choice(LOADING_BACKGROUNDS)
    fade_surface = pygame.Surface((USER_WIDTH, USER_HEIGHT))
    fade_surface.fill((0, 0, 0))
    steps = 50
    for i in range(steps + 1):
        alpha = int(255 * i / steps)
        blur_amount = 1 + (4 * (alpha / 255))
        # Blur background loading
        blurred_bg = pygame.transform.smoothscale(
            pygame.transform.smoothscale(bg_img, (int(SCREEN_WIDTH / blur_amount), int(SCREEN_HEIGHT / blur_amount))),
            (SCREEN_WIDTH, SCREEN_HEIGHT)
        )
        SCREEN.fill((0, 0, 0))
        SCREEN.blit(blurred_bg, (OFFSET_X, OFFSET_Y))
        fade_surface.set_alpha(alpha)
        SCREEN.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.wait(10)
    # Tampilkan loading screen penuh 1 detik
    SCREEN.blit(bg_img, (OFFSET_X, OFFSET_Y))
    pygame.display.update()
    pygame.time.wait(1000)

def start(selected_character):
    play_click_sound()
    smooth_transition_to_main()
    # Import main and run main.main(selected_character) for seamless transition
    import main
    main.main(selected_character)
    sys.exit()

def character_story(selected_character):
    running = True
    
    # Load dan scale karakter images
    ashen_img = pygame.image.load("Assets/SplashArt/AW.png")
    blood_img = pygame.image.load("Assets/SplashArt/BR.png")
    
    # Scale images untuk character story (ukuran sesuai dengan rect)
    TARGET_WIDTH, TARGET_HEIGHT = scale_size(280, 540)
    
    def scale_image(img, target_w, target_h):
        aspect = img.get_width() / img.get_height()
        target_aspect = target_w / target_h
        if aspect > target_aspect:
            new_w = target_w
            new_h = int(target_w / aspect)
        else:
            new_h = target_h
            new_w = int(target_h * aspect)
        return pygame.transform.scale(img, (new_w, new_h))
    
    ashen_img = scale_image(ashen_img, TARGET_WIDTH, TARGET_HEIGHT)
    blood_img = scale_image(blood_img, TARGET_WIDTH, TARGET_HEIGHT)

    if selected_character == 1:
        title = "Ashen Warrior"
        desc = "Ashen Warrior adalah penjaga biru yang setia,\nberjuang demi keadilan dan kedamaian di Utopia."
        char_color = (120, 200, 255)
        char_img = ashen_img
    else:
        title = "Blood Reaper"
        desc = "Blood Reaper adalah pendekar merah yang kejam,\nmenebar teror demi ambisi dan kekuatan."
        char_color = (255, 100, 100)
        char_img = blood_img

    while running:
        # Fill dengan warna hitam untuk letterbox/pillarbox
        SCREEN.fill((0, 0, 0))
        
        # Blit background dengan offset
        SCREEN.blit(BG, (OFFSET_X, OFFSET_Y))

        # Center character box di tengah layar
        char_rect_w, char_rect_h = scale_size(280, 540)
        char_rect_x = (SCREEN_WIDTH - char_rect_w) // 3  # Center horizontal
        char_rect_y = int(320 * SCALE_FACTOR)  # Scale vertical position
        char_rect = pygame.Rect(char_rect_x + OFFSET_X, char_rect_y + OFFSET_Y, char_rect_w, char_rect_h)

        name_font = get_font(48)
        gap = int(80 * SCALE_FACTOR)
        title_text = name_font.render(title, True, "White")
        title_rect = title_text.get_rect(center=(char_rect.centerx, char_rect.top - gap))
        SCREEN.blit(title_text, title_rect)
        
        SCREEN.blit(char_img, (char_rect.x, char_rect.y))

        desc_width = int(600 * SCALE_FACTOR)
        desc_font = get_font(18)
        desc_lines = []
        for paragraph in desc.split('\n'):
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
        
        line_spacing = int(38 * SCALE_FACTOR)
        desc_title_gap = int(10 * SCALE_FACTOR)
        desc_y = char_rect.top 
        
        # Center deskripsi di sebelah kanan character, dengan spacing yang proporsional
        desc_spacing = int(140 * SCALE_FACTOR)  # Jarak antara char dan deskripsi
        desc_x = char_rect.right + desc_spacing

        for i, line in enumerate(desc_lines):
            desc_text = desc_font.render(line.strip(), True, "White")
            desc_rect = desc_text.get_rect()
            desc_rect.topleft = (desc_x, desc_y + i * line_spacing)
            SCREEN.blit(desc_text, desc_rect)

        rect_gap = int(40 * SCALE_FACTOR)
        perk_rect_y = desc_y + len(desc_lines) * line_spacing + rect_gap
        perk_rect_width = int(500 * SCALE_FACTOR)
        
        # Pastikan perk rect tidak keluar dari layar
        max_perk_width = (SCREEN_WIDTH + OFFSET_X) - desc_x - int(20 * SCALE_FACTOR)  # 20px margin
        perk_rect_width = min(perk_rect_width, max_perk_width)
        
        perk_rect = pygame.Rect(
            desc_x,
            perk_rect_y,
            perk_rect_width,
            int(50 * SCALE_FACTOR)
        )
        border_radius = int(18 * SCALE_FACTOR)
        pygame.draw.rect(SCREEN, (200, 200, 80), perk_rect, border_radius=border_radius)

        # Tombol BACK di pojok kiri bawah
        back_btn_x = OFFSET_X + int(180 * SCALE_FACTOR)  # Margin dari kiri
        back_btn_y = SCREEN_HEIGHT + OFFSET_Y - int(80 * SCALE_FACTOR)  # Sejajar dengan tombol START di kanan bawah
        BACK_BTN = Button(
            image=None,
            pos=(back_btn_x, back_btn_y),
            text_input="BACK",
            font=get_font(28),
            base_color="White",
            hovering_color="Green"
        )
        BACK_BTN.changeColor(pygame.mouse.get_pos())
        BACK_BTN.update(SCREEN)

        # Tombol START di pojok kanan bawah (tetap)
        start_btn_x = SCREEN_WIDTH + OFFSET_X - int(180 * SCALE_FACTOR)
        start_btn_y = SCREEN_HEIGHT + OFFSET_Y - int(80 * SCALE_FACTOR)
        START_BTN = Button(
            image=None,
            pos=(start_btn_x, start_btn_y),
            text_input="START",
            font=get_font(28),
            base_color="White",
            hovering_color="Green"
        )
        START_BTN.changeColor(pygame.mouse.get_pos())
        START_BTN.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BTN.checkForInput(pygame.mouse.get_pos()):
                    play_click_sound()
                    running = False
                if START_BTN.checkForInput(pygame.mouse.get_pos()):
                    start(selected_character)  # Panggil main.py

        pygame.display.update()

def play():
    # Load character images
    ashen_img = pygame.image.load("Assets/SplashArt/AW.png")
    blood_img = pygame.image.load("Assets/SplashArt/BR.png")
    
    # Target size for character images - scale dari design resolution
    TARGET_WIDTH, TARGET_HEIGHT = scale_size(240, 420)
    
    # Scale images while maintaining aspect ratio
    def scale_image(img, target_w, target_h):
        aspect = img.get_width() / img.get_height()
        target_aspect = target_w / target_h
        if aspect > target_aspect:
            new_w = target_w
            new_h = int(target_w / aspect)
        else:
            new_h = target_h
            new_w = int(target_h * aspect)
        return pygame.transform.scale(img, (new_w, new_h))
    
    ashen_img = scale_image(ashen_img, TARGET_WIDTH, TARGET_HEIGHT)
    blood_img = scale_image(blood_img, TARGET_WIDTH, TARGET_HEIGHT)
    
    selected_character = 1

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        # Fill dengan warna hitam untuk letterbox/pillarbox
        SCREEN.fill((0, 0, 0))
        SCREEN.blit(BG, (OFFSET_X, OFFSET_Y))

        PLAY_TEXT = get_font(45).render("Select Your Character", True, "White")
        title_x, title_y = scale_pos(960, 250)
        PLAY_RECT = PLAY_TEXT.get_rect(center=(title_x + OFFSET_X, title_y + OFFSET_Y))
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        # Draw character boxes - scale koordinat dan ukuran
        left_rect_scaled = scale_rect(pygame.Rect(560, 300, 240, 420))
        right_rect_scaled = scale_rect(pygame.Rect(1120, 300, 240, 420))
        
        # Offset untuk centering
        left_rect = pygame.Rect(left_rect_scaled.x + OFFSET_X, left_rect_scaled.y + OFFSET_Y, 
                               left_rect_scaled.width, left_rect_scaled.height)
        right_rect = pygame.Rect(right_rect_scaled.x + OFFSET_X, right_rect_scaled.y + OFFSET_Y, 
                                right_rect_scaled.width, right_rect_scaled.height)

        # Draw character images centered in rectangles
        SCREEN.blit(ashen_img, (left_rect.centerx - ashen_img.get_width()//2, 
                               left_rect.centery - ashen_img.get_height()//2))
        SCREEN.blit(blood_img, (right_rect.centerx - blood_img.get_width()//2, 
                               right_rect.centery - blood_img.get_height()//2))

        # Scale name boxes
        name_box_height = int(60 * SCALE_FACTOR)
        name_box_gap = int(60 * SCALE_FACTOR)
        name_box_width = int(320 * SCALE_FACTOR)
        
        left_name_box = pygame.Rect(left_rect.centerx - name_box_width // 2, 
                                   left_rect.bottom + name_box_gap, name_box_width, name_box_height)
        right_name_box = pygame.Rect(right_rect.centerx - name_box_width // 2, 
                                    right_rect.bottom + name_box_gap, name_box_width, name_box_height)

        char_font = get_font(32)
        # Indikator: nama karakter yang terpilih berwarna hijau, yang lain putih
        char1_color = "Green" if selected_character == 1 else "White"
        char2_color = "Green" if selected_character == 2 else "White"
        char1_text = char_font.render("Ashen Warrior", True, char1_color)
        char2_text = char_font.render("Blood Reaper", True, char2_color)
        SCREEN.blit(char1_text, (left_name_box.centerx - char1_text.get_width() // 2, 
                                left_name_box.centery - char1_text.get_height() // 2))
        SCREEN.blit(char2_text, (right_name_box.centerx - char2_text.get_width() // 2, 
                                right_name_box.centery - char2_text.get_height() // 2))

        back_x, back_y = scale_pos(960, 900)
        PLAY_BACK = Button(image=None, pos=(back_x + OFFSET_X, back_y + OFFSET_Y), 
                          text_input="BACK", font=get_font(28), base_color="White", hovering_color="Green")
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    selected_character = 1
                elif event.key == pygame.K_RIGHT:
                    selected_character = 2
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    play_click_sound()
                    character_story(selected_character)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    play_click_sound()
                    main_menu()
                # --- Sekali klik langsung masuk ke character_story ---
                if left_rect.collidepoint(PLAY_MOUSE_POS) or left_name_box.collidepoint(PLAY_MOUSE_POS):
                    play_click_sound()
                    character_story(1)
                if right_rect.collidepoint(PLAY_MOUSE_POS) or right_name_box.collidepoint(PLAY_MOUSE_POS):
                    play_click_sound()
                    character_story(2)
        pygame.display.update()

def options():
    global sound_enabled
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("Settings", True, "Black")
        opt_x, opt_y = scale_pos(960, 390)
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(opt_x + OFFSET_X, opt_y + OFFSET_Y))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        # BACK di pojok kiri bawah
        back_x, back_y = scale_pos(130, 1020)  # 60, 1020 agar tidak terlalu mepet sudut
        OPTIONS_BACK = Button(
            image=None,
            pos=(back_x, back_y),  # Jangan tambahkan OFFSET_X/OFFSET_Y di sini
            text_input="BACK",
            font=get_font(50),
            base_color="Black",
            hovering_color="Green"
        )

        # Tombol toggle sound
        sound_status = "ON" if sound_enabled else "OFF"
        sound_btn_x, sound_btn_y = scale_pos(960, 600)
        SOUND_BTN = Button(
            image=None,
            pos=(sound_btn_x + OFFSET_X, sound_btn_y + OFFSET_Y),
            text_input=f"SOUND: {sound_status}",
            font=get_font(50),
            base_color="Black",
            hovering_color="Green"
        )

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)
        SOUND_BTN.changeColor(OPTIONS_MOUSE_POS)
        SOUND_BTN.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    play_click_sound()
                    main_menu(replay_music=False)
                if SOUND_BTN.checkForInput(OPTIONS_MOUSE_POS):
                    sound_enabled = not sound_enabled
                    pygame.mixer.music.set_volume(0.5 if sound_enabled else 0)
                    play_click_sound()

        pygame.display.update()

def main_menu(replay_music=True):
    if replay_music:
        pygame.mixer.music.load("Assets/Music/MainMenu/MM.wav")
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(0.5)

    selected_menu = 0 
    menu_buttons = ["PLAY", "OPTIONS", "QUIT"]
    button_positions = [425, 625, 825]
    
    while True:
        # Fill dengan warna hitam untuk letterbox/pillarbox
        SCREEN.fill((0, 0, 0))
        SCREEN.blit(BG, (OFFSET_X, OFFSET_Y))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("", True, "#b68f40")
        menu_x, menu_y = scale_pos(960, 230)
        MENU_RECT = MENU_TEXT.get_rect(center=(menu_x + OFFSET_X, menu_y + OFFSET_Y))
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        # Scale button images
        play_img = pygame.image.load("Assets/Play Rect.png")
        options_img = pygame.image.load("Assets/Options Rect.png")
        quit_img = pygame.image.load("Assets/Quit Rect.png")
        
        play_img = scale_surface(play_img)
        options_img = scale_surface(options_img)
        quit_img = scale_surface(quit_img)

        # Scale button positions
        play_x, play_y = scale_pos(960, 425)
        opt_x, opt_y = scale_pos(960, 625)
        quit_x, quit_y = scale_pos(960, 825)

        PLAY_BUTTON = Button(
            image=play_img,
            pos=(play_x + OFFSET_X, play_y + OFFSET_Y),
            text_input="PLAY",
            font=get_font(75),
            base_color="#d7fcd4" if selected_menu != 0 else "White",
            hovering_color="White"
        )
        OPTIONS_BUTTON = Button(
            image=options_img,
            pos=(opt_x + OFFSET_X, opt_y + OFFSET_Y),
            text_input="OPTIONS",
            font=get_font(75),
            base_color="#d7fcd4" if selected_menu != 1 else "White",
            hovering_color="White"
        )
        QUIT_BUTTON = Button(
            image=quit_img,
            pos=(quit_x + OFFSET_X, quit_y + OFFSET_Y),
            text_input="QUIT",
            font=get_font(75),
            base_color="#d7fcd4" if selected_menu != 2 else "White",
            hovering_color="White"
        )

        buttons = [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]

        for button in buttons:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_menu = (selected_menu - 1) % 3
                elif event.key == pygame.K_DOWN:
                    selected_menu = (selected_menu + 1) % 3
                elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                    play_click_sound()
                    if selected_menu == 0:
                        play()
                    elif selected_menu == 1:
                        options()
                    elif selected_menu == 2:
                        pygame.quit()
                        sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_click_sound()
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_click_sound()
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play_click_sound()
                    pygame.quit()
                    sys.exit()

        pygame.display.update()


main_menu()
