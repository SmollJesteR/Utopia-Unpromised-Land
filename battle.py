import pygame
import random
from entity import Entity
from boss import Boss
from deathsentry import DeathSentry
from bloodreaper import BloodReaper
from game_data import (screen, scale_pos, font_ui, damage_numbers, 
                      DamageNumber, DESIGN_WIDTH, scale_factor, ComboText)
from baphomet import Baphomet
from cyclops import Cyclops  # Import Cyclops
from doomcultist import DoomCultist  # Add this import
from medusa import Medusa
from ashenknight import AshenKnight  # Add this import

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
background_winter_img = pygame.image.load('img/Background/Map.png').convert_alpha()
background_hell_img = pygame.image.load('img/Background/Hell_Map.png').convert_alpha()
background_mountain_img = pygame.image.load('img/Background/Mountain_Map.png').convert_alpha()
background_castle_img = pygame.image.load('img/Background/Castle_Map.png').convert_alpha()
background_lair_img = pygame.image.load('img/Background/Lair_Map.png').convert_alpha()
# Scale images to fit the design resolution
panel_img = pygame.image.load('img/Background/Panel.png').convert_alpha()
font_ui = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", int(20 * scale_factor))  # Scale font size

# Define UI elements in design coordinates (1920x1080 space)
attack_icon_rect = pygame.Rect(350, 820, 64, 64)  # Original coordinates and size

# Modify the draw functions to use scaling
def draw_background():
    # Draw to game surface first at original resolution
    if BOSS_TYPE == 1:  # DeathSentry
        game_surface.blit(background_winter_img, (0, 0))
    elif BOSS_TYPE == 2:  # Baphomet
        game_surface.blit(background_hell_img, (0, 0))
    elif BOSS_TYPE == 3:  # Cyclops
        game_surface.blit(background_mountain_img, (0, 0))
    elif BOSS_TYPE == 4:
        game_surface.blit(background_castle_img, (0, 0))
    elif BOSS_TYPE == 5:  # Medusa
        game_surface.blit(background_lair_img, (0, 0))  # Use the same background for Medusa        
    
    # Scale and draw to main screen with proper positioning
    scaled_surface = pygame.transform.scale(game_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (padding_x, padding_y))

def draw_panel():
    # Draw panel to game surface first
    game_surface.blit(panel_img, (0, 0))
    # Scale and draw to main screen
    scaled_surface = pygame.transform.scale(game_surface, (screen_width, screen_height))
    screen.blit(scaled_surface, (padding_x, padding_y))

# Change player character selection (add this near BloodReaper initialization)
PLAYER_TYPE = 2  # 1 for BloodReaper, 2 for AshenKnight

if PLAYER_TYPE == 1:
    player = BloodReaper(int(500 * scale_factor), int(500 * scale_factor), scale=4.2 * scale_factor)
elif PLAYER_TYPE == 2:
    player = AshenKnight(int(500 * scale_factor), int(500 * scale_factor), scale=7.2 * scale_factor)

# Update boss type selection
BOSS_TYPE = 1 # Add Medusa as type 5

# Update boss creation
if BOSS_TYPE == 1:
    current_boss = DeathSentry(int(1400 * scale_factor), int(420 * scale_factor), 
                              scale=8.5 * scale_factor, player=player)
elif BOSS_TYPE == 2:
    current_boss = Baphomet(int(1400 * scale_factor), int(120 * scale_factor),
                           scale=7 * scale_factor, player=player)                              
elif BOSS_TYPE == 3:
    current_boss = Cyclops(int(1450 * scale_factor), int(420 * scale_factor),
                          scale=9 * scale_factor, player=player)
elif BOSS_TYPE == 4:
    current_boss = DoomCultist(int(1100 * scale_factor), int(250 * scale_factor),
                              scale=9 * scale_factor, player=player)
elif BOSS_TYPE == 5:  # Add Medusa
    current_boss = Medusa(int(1450 * scale_factor), int(180 * scale_factor),
                         scale=8 * scale_factor, player=player)

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
        if player.is_dead:
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
    
    # Handle AshenKnight's damage reduction duration at start of turn
    if isinstance(player, AshenKnight) and player.damage_reduction_active:
        if player.damage_reduction_turns > 0:  # Only decrement if turns remain
            if not (isinstance(current_boss, DeathSentry) and current_boss.using_ultimate):
                # Don't decrement shield during ultimate to maintain consistency
                player.damage_reduction_turns -= 1
            if player.damage_reduction_turns <= 0:
                player.damage_reduction_active = False
                damage_numbers.append(DamageNumber(
                    player.rect.centerx,
                    player.rect.y - 50,
                    "SHIELD OFF",
                    (255, 255, 255),
                    font_size=20,
                    lifetime=60
                ))

    # Handle DeathSentry's shield duration
    if isinstance(current_boss, DeathSentry) and current_boss.immunity_hits > 0:
        current_boss.immunity_turns += 1
        if current_boss.immunity_turns >= 3:  # Changed from 2 to 3 - Shield breaks after 3 turns
            current_boss.immunity_hits = 0
            current_boss.immunity_turns = 0
            damage_numbers.append(DamageNumber(
                current_boss.rect.centerx,
                current_boss.rect.y - 50,
                "SHIELD BREAK",
                (255, 255, 255),
                font_size=20,
                lifetime=60
            ))
    
    # Handle combo logic when enemy turn ends
    if current_turn == "enemy":
        # Debug info before checking damage
        print("\nDamage Check Debug:")
        
        # Get the actual damage number from the most recent DamageNumber
        latest_damage = None
        for number in damage_numbers:
            if isinstance(number, DamageNumber):
                try:
                    if hasattr(number, 'amount'):
                        if isinstance(number.amount, (int, float)):
                            latest_damage = number.amount
                            print(f"Found numeric damage: {latest_damage}")
                        else:
                            print(f"Found text message: {number.amount}")
                except UnicodeEncodeError:
                    print("Found special effect message")
                    
        print("\nTurn End Debug Info:")
        print(f"Enemy dealt damage: {current_boss.last_damage_dealt}")
        print(f"Last damage amount: {latest_damage}")
        print(f"Combo counter: {player.combo_count}")
        
        # Use both checks for damage
        if current_boss.last_damage_dealt or (latest_damage is not None and latest_damage > 0):
            player.combo_count = 0
            player.was_hit = True
            player.should_combo = False
            print(f">>> Enemy dealt damage - Next turn will be basic attack")
            print(f">>> Combo reset to: {player.combo_count}")
        else:
            player.was_hit = False
            player.should_combo = True
            player.combo_count += 1
            print(">>> Enemy missed/blocked - Enabling combo for next turn")
            print(f">>> New combo count: {player.combo_count}")
    
    # Reset tracking variables    
    current_boss.last_damage_dealt = False
    
    # Only switch turns if neither player nor boss is dead
    if not player.is_dead and not current_boss.is_dead:
        current_turn = "player"
        enemy_has_attacked = False
        turn_switch_time = pygame.time.get_ticks()
        start_turn_notification()
        
        # Increment turn counters
        player_turn_counter += 1
        enemy_turn_counter += 1
        round_counter += 1
        
        # Energy recovery every 2 rounds
        if round_counter % 2 == 0:
            player.target_energy = min(player.max_energy, player.target_energy + 10)
            current_boss.target_energy = min(current_boss.max_energy, current_boss.target_energy + 10)
        
        # Regular turn energy regen
        if player_turn_counter >= 6:
            player.target_energy = min(player.max_energy, player.target_energy + 15)
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

    for character in [player, current_boss]:
        character.update()
        character.draw()

    # Update UI element positions using scale_pos() for coordinates
    player.draw_health_bar_panel(*scale_pos(250, 790))  # Changed from 350 to 250
    player.draw_energy_bar_panel(*scale_pos(250, 810))  # Changed from 350 to 250
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
                if event.key == pygame.K_a and not player.attacking:
                    print("\n=== Basic Attack Debug ===")
                    print(f"Player Energy: {player.current_energy}/{player.max_energy}")
                    print(f"Enemy Health: {current_boss.current_health}/{current_boss.max_hp}")
                    print(f"Current Combo Count: {player.combo_count}")
                    if hasattr(player, 'damage_reduction_active'):
                        print(f"Shield Active: {player.damage_reduction_active}")
                        if player.damage_reduction_active:
                            print(f"Shield Turns Left: {player.damage_reduction_turns}")
                    
                    player.attack(current_boss)
                    
                    # Post-attack debug
                    pygame.time.delay(50)
                    print("\n=== After Attack ===")
                    print(f"Enemy Health After Attack: {current_boss.current_health}/{current_boss.max_hp}")
                    print(f"Player Energy After Attack: {player.current_energy}/{player.max_energy}")
                    
                    current_turn = "enemy"
                    enemy_has_attacked = False
                    turn_switch_time = pygame.time.get_ticks()
                    start_turn_notification()

                # Add check for AshenKnight before checking skill usage
                elif (event.key == pygame.K_s and isinstance(player, AshenKnight) 
                      and not player.using_skill 
                      and not player.is_dead 
                      and player.current_energy >= player.skill_energy_cost):
                    print("\n=== Skill Activation Debug ===")
                    print(f"Player Energy: {player.current_energy}/{player.max_energy}")
                    print("Activating Damage Reduction Shield")
                    print(f"Shield Duration: {player.damage_reduction_turns} turns")
                    print(f"Energy Cost: {player.skill_energy_cost}")
                    
                    player.use_skill()
                    
                    # Post-skill debug
                    print("\n=== After Skill Use ===")
                    print(f"Shield Active: {player.damage_reduction_active}")
                    print(f"Player Energy After Skill: {player.current_energy}/{player.max_energy}")
                    
                    current_turn = "enemy"
                    enemy_has_attacked = False
                    turn_switch_time = pygame.time.get_ticks()
                    start_turn_notification()

    # Giliran musuh hanya jika BloodReaper belum mati
    if current_turn == "enemy" and not current_boss.is_dead and not player.is_dead:  # Add check for player.is_dead
        if now - turn_switch_time > turn_switch_delay:
            if not current_boss.attacking and not enemy_has_attacked:
                current_boss.attack(player)
                enemy_has_attacked = True

            if not current_boss.attacking and enemy_has_attacked:
                switch_turns()

    # Update this section in the main loop
    for number in damage_numbers[:]:
        # Only print debug messages for actual damage numbers or important effects
        if isinstance(number, DamageNumber):
            try:
                # Skip debug output for shield status messages
                if not str(number.amount).startswith("SHIELD"):
                    if isinstance(number.amount, str):
                        print(f"Special message: {number.amount}")
                    else:
                        print(f"Damage dealt: {number.amount}")
            except UnicodeEncodeError:
                print("Special effect triggered")
        elif isinstance(number, ComboText):
            print(f"Combo: {number.text}")
            
        number.update()
        number.draw(screen)
        
        if isinstance(number, DamageNumber) and number.lifetime <= 0:
            try:
                # Only show removal message for actual damage
                if not str(number.amount).startswith("SHIELD"):
                    print(f"Removed damage number: {number.amount}")
            except UnicodeEncodeError:
                pass
            damage_numbers.remove(number)
        elif isinstance(number, ComboText) and number.lifetime <= 0:
            print(f"Removed combo: {number.text}")
            damage_numbers.remove(number)
    
    player.draw_skill_icons()    
    pygame.display.update()

pygame.quit()