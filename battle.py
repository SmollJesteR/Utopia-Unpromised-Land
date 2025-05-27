import pygame
import random
from entity import Entity
from boss import Boss
from deathsentry import DeathSentry
from bloodreaper import BloodReaper
from game_data import (screen, scale_pos, font_ui, damage_numbers, 
                      DamageNumber, DESIGN_WIDTH, scale_factor, ComboText)
from baphomet import Baphomet

# Initialize pygame and mixer first
pygame.init()
pygame.mixer.init()

bgm_list = [
    'Assets/Music/Battle/B1.wav',
    'Assets/Music/Battle/B2.wav',
    'Assets/Music/Battle/B3.wav',
]

def play_random_bgm():
    track = random.choice(bgm_list)
    pygame.mixer.music.load(track)
    pygame.mixer.music.set_volume(0.2)  
    pygame.mixer.music.play(-1) 

play_random_bgm() 

attack_sfx = pygame.mixer.Sound('Assets/SFX/BA.wav')
monster_sfx = pygame.mixer.Sound('Assets/SFX/MA.wav')
boss1_sfx = pygame.mixer.Sound('Assets/SFX/BA_DS.wav')
deathboss1_sfx = pygame.mixer.Sound('Assets/SFX/Death_DS.wav')
skillboss1_sfx = pygame.mixer.Sound('Assets/SFX/Skill_DS.wav')
ultimateboss1_sfx = pygame.mixer.Sound('Assets/SFX/Ultimate_DS.wav')
deathsentryhit_sfx = pygame.mixer.Sound('Assets/SFX/MA_DS.wav')
deathsentryshieldhit_sfx = pygame.mixer.Sound('Assets/SFX/MA_SHIELD_DS.wav')
deathbloodreaper_sfx = pygame.mixer.Sound('Assets/SFX/Death_BR.wav')
basiccombo_sfx = pygame.mixer.Sound('Assets/SFX/combo2,3,.wav')
morecombo_sfx = pygame.mixer.Sound('Assets/SFX/combo4,-.wav')
idlebr_sfx = pygame.mixer.Sound('Assets/SFX/Idle_BR.wav')
idleds_sfx = pygame.mixer.Sound('Assets/SFX/Idle_DS.wav')

clock = pygame.time.Clock()
fps = 180

# Get the user's screen info
screen_info = pygame.display.Info()
DESIGN_WIDTH = 1920  # Original design width
DESIGN_HEIGHT = 1080  # Original design height

# Calculate scaling factors
scale_x = screen_info.current_w / DESIGN_WIDTH
scale_y = screen_info.current_h / DESIGN_HEIGHT
scale_factor = min(scale_x, scale_y)  # Use the smaller scale to maintain aspect ratio

# Calculate actual screen dimensions
screen_width = int(DESIGN_WIDTH * scale_factor)
screen_height = int(DESIGN_HEIGHT * scale_factor)

# Calculate padding to center the game
padding_x = (screen_info.current_w - screen_width) // 2
padding_y = (screen_info.current_h - screen_height) // 2

# Create the screen
screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h))
game_surface = pygame.Surface((DESIGN_WIDTH, DESIGN_HEIGHT))

def scale_pos(x, y):
    """Scale position from design coordinates to actual screen coordinates"""
    return (int(x * scale_factor) + padding_x, 
            int(y * scale_factor) + padding_y)

def scale_rect(rect):
    """Scale rectangle from design coordinates to actual screen coordinates"""
    scaled_rect = pygame.Rect(
        int(rect.x * scale_factor) + padding_x,
        int(rect.y * scale_factor) + padding_y,
        int(rect.width * scale_factor),
        int(rect.height * scale_factor)
    )
    return scaled_rect

# Load assets at original size (no scaling during load)
background_img = pygame.image.load('img/Background/Map.png').convert_alpha()
panel_img = pygame.image.load('img/Background/Panel.png').convert_alpha()
font_ui = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", int(20 * scale_factor))  # Scale font size

# Define UI elements in design coordinates (1920x1080 space)
attack_icon_rect = pygame.Rect(350, 820, 64, 64)  # Original coordinates and size

# Modify the draw functions to use scaling
def draw_background():
    # Draw to game surface first at original resolution
    game_surface.blit(background_img, (0, 0))
    # Scale and draw to main screen with proper positioning
    scaled_surface = pygame.transform.scale(game_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (padding_x, padding_y))

def draw_panel():
    # Draw panel to game surface first
    game_surface.blit(panel_img, (0, 0))
    # Scale and draw to main screen
    scaled_surface = pygame.transform.scale(game_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (padding_x, padding_y))

blood_reaper = BloodReaper(int(500 * scale_factor), int(500 * scale_factor), scale=4.2 * scale_factor)

# Add boss selection
BOSS_TYPE = 0  # 1 for DeathSentry, 0 for Baphomet

# Create appropriate boss based on selection
if BOSS_TYPE == 1:
    current_boss = DeathSentry(int(1400 * scale_factor), int(420 * scale_factor), 
                              scale=8.5 * scale_factor, player=blood_reaper)
else:
    current_boss = Baphomet(int(1400 * scale_factor), int(120 * scale_factor),  # Changed Y from 400 to 300
                           scale=7 * scale_factor, player=blood_reaper)

current_turn = "player"  # giliran "player" atau "enemy"
enemy_has_attacked = False

turn_switch_delay = 1500  # jeda milidetik antar giliran
turn_switch_time = 0
font_turn = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", 26)  # Change font size from 36 to 28

turn_notification_img = pygame.image.load('img/Background/TurnNotification.png').convert_alpha()
# Scale up the turn notification image by 1.5x
turn_notification_img = pygame.transform.scale(turn_notification_img, 
    (int(turn_notification_img.get_width() * 5), 
     int(turn_notification_img.get_height() * 5)))

turn_notification_duration = 5000  # durasi notifikasi tampil (ms)
turn_notification_start = 0  # waktu mulai notifikasi (ms)

player_turn_counter = 0
enemy_turn_counter = 0
round_counter = 0  # Add this line

# Add combo counter variables
combo_counter = 0
combo_text_duration = 1000  # 1 second
combo_text_start = 0

def start_turn_notification():
    global turn_notification_start
    turn_notification_start = pygame.time.get_ticks()

def draw_turn_text():
    now = pygame.time.get_ticks()
    if now - turn_notification_start < turn_notification_duration:
        # Use original design coordinates and scale them
        notif_pos = scale_pos(DESIGN_WIDTH // 2, 100)  # Position at top of screen
        
        # Draw notification background
        notif_rect = turn_notification_img.get_rect(center=notif_pos)
        screen.blit(turn_notification_img, notif_rect)

        # Change text based on game state
        if blood_reaper.is_dead:
            text = font_turn.render("You Lose!", True, (255, 0, 0))
        elif current_boss.is_dead:
            text = font_turn.render("You Win!", True, (0, 255, 0))
        elif current_turn == "player":
            text = font_turn.render("Your Turn!", True, (0, 255, 0))
        else:
            text = font_turn.render("Foe Turn!", True, (255, 0, 0))

        # Center text in notification
        text_rect = text.get_rect(center=(notif_pos[0], notif_pos[1] - 10))
        screen.blit(text, text_rect)

def switch_turns():
    global current_turn, enemy_has_attacked, turn_switch_time, player_turn_counter, enemy_turn_counter, round_counter
    
    # Handle combo logic when enemy turn ends
    if current_turn == "enemy":
        # Debug info before checking damage
        print("\nDamage Check Debug:")
        print("Current damage numbers:")
        for num in damage_numbers:
            if isinstance(num, DamageNumber):
                print(f"- Amount: {num.amount}")
        
        # Get the actual damage number from the most recent DamageNumber
        latest_damage = None
        for number in damage_numbers:  # Changed from reversed() to regular order
            if isinstance(number, DamageNumber):
                if hasattr(number, 'amount') and isinstance(number.amount, (int, float)):
                    latest_damage = number.amount
                    print(f"Found damage number: {latest_damage}")
                    break
        
        print("\nTurn End Debug Info:")
        print(f"Enemy last_damage_dealt: {current_boss.last_damage_dealt}")
        print(f"Damage notification shows: {latest_damage}")
        print(f"Current combo count: {blood_reaper.combo_count}")
        
        # Use both checks for damage
        if current_boss.last_damage_dealt or (latest_damage is not None and latest_damage > 0):
            blood_reaper.combo_count = 0
            blood_reaper.was_hit = True
            blood_reaper.should_combo = False
            print(f">>> Enemy dealt damage - Next turn will be basic attack")
            print(f">>> Combo reset to: {blood_reaper.combo_count}")
        else:
            blood_reaper.was_hit = False
            blood_reaper.should_combo = True
            blood_reaper.combo_count += 1
            print(">>> Enemy missed/blocked - Enabling combo for next turn")
            print(f">>> New combo count: {blood_reaper.combo_count}")
    
    # Reset tracking variables    
    current_boss.last_damage_dealt = False
    
    current_turn = "player"
    enemy_has_attacked = False
    turn_switch_time = pygame.time.get_ticks()
    start_turn_notification()
    
    player_turn_counter += 1
    enemy_turn_counter += 1
    round_counter += 1  # Increment round counter
    
    # Energy recovery every 2 rounds
    if round_counter % 2 == 0:
        blood_reaper.target_energy = min(blood_reaper.max_energy, blood_reaper.target_energy + 10)
        current_boss.target_energy = min(current_boss.max_energy, current_boss.target_energy + 10)
    
    # Existing turn energy regen
    if player_turn_counter >= 6:
        blood_reaper.target_energy = min(blood_reaper.max_energy, blood_reaper.target_energy + 15)
        player_turn_counter = 0
    
    if enemy_turn_counter >= 3:
        current_boss.target_energy = min(current_boss.max_energy, current_boss.target_energy + 15)
        enemy_turn_counter = 0

# Main game loop
run = True
while run:
    clock.tick(fps)
    draw_background()
    draw_panel()
    now = pygame.time.get_ticks()  # Add this line to define 'now'

    for character in [blood_reaper, current_boss]:
        character.update()
        character.draw()

    # Update UI element positions using scale_pos() for coordinates
    blood_reaper.draw_health_bar_panel(*scale_pos(250, 790))  # Changed from 350 to 250
    blood_reaper.draw_energy_bar_panel(*scale_pos(250, 810))  # Changed from 350 to 250
    current_boss.draw_health_bar_panel(*scale_pos(1150, 790))
    current_boss.draw_energy_bar_panel(*scale_pos(1150, 810))
    current_boss.draw_skill_icons()  # Add this line

    draw_turn_text()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Input hanya berlaku saat giliran player dan BloodReaper belum mati
        if current_turn == "player":
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_s and not blood_reaper.attacking 
                    and not blood_reaper.is_dead
                    and not (hasattr(current_boss, 'using_ultimate') and current_boss.using_ultimate)):
                    # Debug before attack
                    print("\nPlayer Attack Debug:")
                    print("BloodReaper initiating attack...")
                    print(f"Baphomet HP before attack: {current_boss.current_health}/{current_boss.max_hp}")
                    print(f"Current damage numbers in list: {len(damage_numbers)}")
                    print("Current damage numbers:")
                    for dmg in damage_numbers:
                        print(f"- Amount: {dmg.amount}, Position: ({dmg.x}, {dmg.y})")
                    
                    blood_reaper.attack(current_boss)
                    
                    # Move debug prints after a small delay to ensure damage numbers are created
                    pygame.time.delay(50)  # Add small delay
                    
                    # Debug after attack
                    print("\nAfter Attack Debug:")
                    print(f"Current damage numbers list length: {len(damage_numbers)}")
                    print(f"Baphomet HP after attack: {current_boss.current_health}/{current_boss.max_hp}")
                    print("\nDamage Numbers Debug:")
                    print("All current damage numbers:")
                    for i, dmg in enumerate(damage_numbers):
                        print(f"Number {i+1}:")
                        print(f"- Amount: {dmg.amount}")
                        print(f"- Position: ({dmg.x}, {dmg.y})")
                        print(f"- Color: {dmg.color}")
                        print(f"- Lifetime: {dmg.lifetime}")
                    
                    current_turn = "enemy"
                    enemy_has_attacked = False
                    turn_switch_time = pygame.time.get_ticks()
                    start_turn_notification()

    # Giliran musuh hanya jika BloodReaper belum mati
    if current_turn == "enemy" and not current_boss.is_dead:
        if now - turn_switch_time > turn_switch_delay:
            if not current_boss.attacking and not enemy_has_attacked:
                current_boss.attack(blood_reaper)
                enemy_has_attacked = True

            if not current_boss.attacking and enemy_has_attacked:
                switch_turns()

    # Update and draw damage numbers and combo texts
    for number in damage_numbers[:]:
        # Add debug print with proper type checking
        if isinstance(number, DamageNumber):
            print(f"Drawing damage number: {number.amount} at ({number.x}, {number.y})")
        elif isinstance(number, ComboText):
            print(f"Drawing combo text: {number.text} at ({number.x}, {number.y})")
        
        number.update()
        number.draw(screen)
        
        # Removal check with proper type checking
        if isinstance(number, DamageNumber) and number.lifetime <= 0:
            print(f"Removing damage number: {number.amount}")
            damage_numbers.remove(number)
        elif isinstance(number, ComboText) and number.lifetime <= 0:
            print(f"Removing combo text: {number.text}")
            damage_numbers.remove(number)
    
    pygame.display.update()

pygame.quit()