import pygame, sys
from button import Button

pygame.init()

SCREEN = pygame.display.set_mode((1920, 1080))  
pygame.display.set_caption("Menu")

BG = pygame.image.load("Assets/Background.png")
BG = pygame.transform.scale(BG, (1920, 1080))

def get_font(size):
    return pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", size)

def play():
    while True:
        selected_character = 1
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.fill("black")

        PLAY_TEXT = get_font(45).render("This is the PLAY screen.", True, "White")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(960, 390)) 
        PLAY_RECT = PLAY_TEXT.get_rect(center=(960, 200)) 
        SCREEN.blit(PLAY_TEXT, PLAY_RECT)

        PLAY_BACK = Button(image=None, pos=(960, 825), 
                            text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")

        left_rect = pygame.Rect(560, 300, 240, 420)
        right_rect = pygame.Rect(1120, 300, 240, 420)
        pygame.draw.rect(SCREEN, (120, 200, 255) if selected_character == 1 else (180, 180, 180), left_rect, border_radius=30)
        pygame.draw.rect(SCREEN, (255, 200, 120) if selected_character == 2 else (180, 180, 180), right_rect, border_radius=30)

        name_box_height = 60
        name_box_gap = 60
        name_box_width = 320
        left_name_box = pygame.Rect(left_rect.centerx - name_box_width // 2, left_rect.bottom + name_box_gap, name_box_width, name_box_height)
        right_name_box = pygame.Rect(right_rect.centerx - name_box_width // 2, right_rect.bottom + name_box_gap, name_box_width, name_box_height)
        pygame.draw.rect(SCREEN, (120, 200, 255) if selected_character == 1 else (220, 220, 220), left_name_box, border_radius=14)
        pygame.draw.rect(SCREEN, (255, 200, 120) if selected_character == 2 else (220, 220, 220), right_name_box, border_radius=14)

        char_font = get_font(18)
        char1_text = char_font.render("Ashen Warrior", True, "Black")
        char2_text = char_font.render("Blood Ripper", True, "Black")
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                if left_rect.collidepoint(PLAY_MOUSE_POS) or left_name_box.collidepoint(PLAY_MOUSE_POS):
                    selected_character = 1
                if right_rect.collidepoint(PLAY_MOUSE_POS) or right_name_box.collidepoint(PLAY_MOUSE_POS):
                    selected_character = 2


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
    while True:
        SCREEN.blit(BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(960, 230))  

        PLAY_BUTTON = Button(image=pygame.image.load("Assets/Play Rect.png"), pos=(960, 425), 
                            text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        OPTIONS_BUTTON = Button(image=pygame.image.load("Assets/Options Rect.png"), pos=(960, 625), 
                            text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("Assets/Quit Rect.png"), pos=(960, 825), 
                            text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
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
