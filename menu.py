import pygame, sys
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1920, 1080))  
pygame.display.set_caption("Menu")

BG = pygame.image.load("Assets/Background.png")
BG = pygame.transform.scale(BG, (1920, 1080))

def get_font(size):
    return pygame.font.Font("Assets/font.ttf", size)

def character_story(selected_character):
    running = True

    if selected_character == 1:
        title = "Ashen Warrior"
        desc = "Ashen Warrior adalah penjaga biru yang setia,\nberjuang demi keadilan dan kedamaian di Utopia."
        char_color = (120, 200, 255)
    else:
        title = "Blood Ripper"
        desc = "Blood Ripper adalah pendekar merah yang kejam,\nmenebar teror demi ambisi dan kekuatan."
        char_color = (255, 100, 100)

    while running:
        SCREEN.blit(BG, (0, 0))

        screen_center_x = SCREEN.get_width() // 2

        char_rect = pygame.Rect(screen_center_x - 470, 320, 280, 540)

        name_font = get_font(48)
        gap = 80  
        title_text = name_font.render(title, True, "White")
        title_rect = title_text.get_rect(center=(char_rect.centerx, char_rect.top - gap))
        SCREEN.blit(title_text, title_rect)
        pygame.draw.rect(SCREEN, char_color, char_rect, border_radius=50)

        
        desc_width = 600
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
        line_spacing = 38

        desc_title_gap = 10 
        desc_y = char_rect.top 
        desc_x = char_rect.right + 180  

        for i, line in enumerate(desc_lines):
            desc_text = desc_font.render(line.strip(), True, "White")
            desc_rect = desc_text.get_rect()
            desc_rect.topleft = (desc_x, desc_y + i * line_spacing)
            SCREEN.blit(desc_text, desc_rect)

        rect_gap = 40
        perk_rect_y = desc_y + len(desc_lines) * line_spacing + rect_gap
        perk_rect_width = 500
        perk_rect = pygame.Rect(
            desc_x,  # sejajar dengan deskripsi
            perk_rect_y,
            perk_rect_width,
            50
        )
        pygame.draw.rect(SCREEN, (200, 200, 80), perk_rect, border_radius=18)
        # ...bisa tambahkan isi perk di sini jika ingin...


        BACK_BTN = Button(image=None, pos=(960, 900), 
                          text_input="BACK", font=get_font(28), base_color="White", hovering_color="Green")
        BACK_BTN.changeColor(pygame.mouse.get_pos())
        BACK_BTN.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if BACK_BTN.checkForInput(pygame.mouse.get_pos()):
                    running = False

        pygame.display.update()

def play():
    selected_character = 1  
    last_click_time = 0
    click_interval = 400 
    blink = True
    blink_timer = 0
    blink_interval = 500  

    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()

        SCREEN.blit(BG, (0, 0))

        PLAY_TEXT = get_font(45).render("Select Your Character", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(960, 200)) 
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        left_rect = pygame.Rect(560, 300, 240, 420)
        right_rect = pygame.Rect(1120, 300, 240, 420)
        pygame.draw.rect(SCREEN, (120, 200, 255) if selected_character == 1 else (180, 180, 180), left_rect, border_radius=30)
        pygame.draw.rect(SCREEN, (255, 200, 120) if selected_character == 2 else (180, 180, 180), right_rect, border_radius=30)

        name_box_height = 60
        name_box_gap = 60
        name_box_width = 320
        left_name_box = pygame.Rect(left_rect.centerx - name_box_width // 2, left_rect.bottom + name_box_gap, name_box_width, name_box_height)
        right_name_box = pygame.Rect(right_rect.centerx - name_box_width // 2, right_rect.bottom + name_box_gap, name_box_width, name_box_height)

        char_font = get_font(32)
        char1_text = char_font.render("Ashen Warrior", True, "White")
        char2_text = char_font.render("Blood Ripper", True, "White")
        SCREEN.blit(char1_text, (left_name_box.centerx - char1_text.get_width() // 2, left_name_box.centery - char1_text.get_height() // 2))
        SCREEN.blit(char2_text, (right_name_box.centerx - char2_text.get_width() // 2, right_name_box.centery - char2_text.get_height() // 2))


        PLAY_BACK = Button(image=None, pos=(960, 900), 
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
                    character_story(selected_character)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                if left_rect.collidepoint(PLAY_MOUSE_POS) or left_name_box.collidepoint(PLAY_MOUSE_POS):
                    if selected_character == 1 and now - last_click_time < click_interval:
                        character_story(1)
                        last_click_time = 0
                    else:
                        selected_character = 1
                        last_click_time = now
                if right_rect.collidepoint(PLAY_MOUSE_POS) or right_name_box.collidepoint(PLAY_MOUSE_POS):
                    if selected_character == 2 and now - last_click_time < click_interval:
                        character_story(2)
                        last_click_time = 0
                    else:
                        selected_character = 2
                        last_click_time = now

        pygame.display.update()
    
def options():
    while True:
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("white")

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(960, 390))
        SCREEN.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = Button(image=None, pos=(960, 825), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.changeColor(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    main_menu()

        pygame.display.update()

def main_menu():
    selected_menu = 0 
    menu_buttons = ["PLAY", "OPTIONS", "QUIT"]
    button_positions = [425, 625, 825]
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(960, 230))  
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        PLAY_BUTTON = Button(
            image=pygame.image.load("Assets/Play Rect.png"),
            pos=(960, 425),
            text_input="PLAY",
            font=get_font(75),
            base_color="#d7fcd4" if selected_menu != 0 else "White",
            hovering_color="White"
        )
        OPTIONS_BUTTON = Button(
            image=pygame.image.load("Assets/Options Rect.png"),
            pos=(960, 625),
            text_input="OPTIONS",
            font=get_font(75),
            base_color="#d7fcd4" if selected_menu != 1 else "White",
            hovering_color="White"
        )
        QUIT_BUTTON = Button(
            image=pygame.image.load("Assets/Quit Rect.png"),
            pos=(960, 825),
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
                    if selected_menu == 0:
                        play()
                    elif selected_menu == 1:
                        options()
                    elif selected_menu == 2:
                        pygame.quit()
                        sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if OPTIONS_BUTTON.checkForInput(MENU_MOUSE_POS):
                    options()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

main_menu()
