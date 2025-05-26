import pygame
import random

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

class DamageNumber:
    def __init__(self, x, y, amount, color, font_size=26, velocity=-2, lifetime=30):
        self.font = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", font_size)
        self.x = x
        self.y = y
        self.amount = amount
        self.color = color
        self.lifetime = lifetime  # Customizable duration
        self.alpha = 255
        self.velocity_y = velocity  # Customizable upward speed
        # Add slower fade for initial damage
        self.is_initial_damage = isinstance(amount, int) and amount == 20
        self.fade_rate = 4 if not self.is_initial_damage else 2  # Slower fade for initial damage

    def update(self):
        self.y += self.velocity_y
        self.lifetime -= 1
        if self.lifetime < 30:  # start fading out in the last 30 frames
            self.alpha = max(0, self.alpha - self.fade_rate)

    def draw(self, screen):
        text_surface = self.font.render(str(self.amount), True, self.color)
        text_surface.set_alpha(self.alpha)
        screen.blit(text_surface, (self.x, self.y))

damage_numbers = []

class ComboText:
    def __init__(self, x, y, combo_count):
        self.font = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", 32)
        self.x = x
        self.y = y
        # Only show combo text if combo_count is 2 or greater
        self.text = f"Combo {combo_count}!" if combo_count >= 2 else ""
        # Change color based on combo count - gold for 2-3, red for 4+
        self.color = (255, 0, 0) if combo_count >= 4 else (255, 215, 0)  # Red for 4+ combos, gold otherwise
        self.alpha = 255
        self.lifetime = 60

    def update(self):
        self.lifetime -= 1
        if self.lifetime < 30:
            self.alpha = max(0, self.alpha - 8)

    def draw(self, screen):
        text_surface = self.font.render(self.text, True, self.color)
        text_surface.set_alpha(self.alpha)
        screen.blit(text_surface, (self.x, self.y))

class Entity():
    def __init__(self, x, y, max_hp, strength, potion, name, scale):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potion = potion
        self.alive = True
        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        self.target_health = max_hp
        self.current_health = max_hp
        self.health_bar_length = 350  
        self.health_ratio = self.max_hp / self.health_bar_length
        self.health_change_speed = 0.2  # Adjusted for smoother 1-second transition

        self.max_energy = 100
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350
        self.energy_ratio = self.max_energy / self.energy_bar_length
        self.energy_change_speed = 2

        # load idle animation
        temp_list = []
        for i in range(8 if name == "BloodReaper" else 9):
            img = pygame.image.load(f'img/{self.name}/Idle/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load attack animation
        temp_list = []
        for i in range(6 if name == "BloodReaper" else 8):
            img = pygame.image.load(f'img/{self.name}/Attack/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load death animation
        temp_list = []
        for i in range(6):  # BloodReaper death animation has 6 frames
            img = pygame.image.load(f'img/{self.name}/Death/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # Initialize attributes for death state
        self.is_dying = False
        self.is_dead = False

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

        self.attacking = False
        self.attack_applied = False

        self.entity_type = "entity"  # Add this line

        self.immunity_turns = 0  # Add immunity counter

        self.alpha = 255  # Add this for opacity control
        self.hit_time = 0  # Add this to track when hit
        self.is_hit = False  # Add this to track hit state

        # Add base combo attributes for all entities
        self.combo_count = 0
        self.should_combo = False
        self.last_hit_successful = False
        self.can_combo = False  # New flag to track if combo is possible

    def attack(self, target):
        # Check if target is dead before allowing attack
        if isinstance(target, DeathSentry) and (target.is_dead or target.is_dying):
            return
            
        # Check immunity and death state before allowing attack
        if self.is_dead or self.is_dying or self.immunity_turns > 0:
            return
            
        if not self.attacking and self.current_energy >= 20:
            self.attacking = True
            self.attack_applied = False
            self.frame_index = 0  # Reset frame index when starting attack
            self.action = 1
            self.attack_target = target
            self.target_energy = max(0, self.target_energy - 20)
            if self.entity_type == "player":
                pygame.mixer.Sound.play(attack_sfx)

    def take_damage(self, amount):
        if self.immunity_turns > 0:
            return 0  # Return 0 damage if immune

        # Set hit state
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        self.alpha = 128  # Set to 50% opacity when hit
        
        self.target_health -= amount
        return amount

        return super().take_damage(amount)  # Return damage taken when no shield        

    def update_health(self):
        """Update health values within bounds"""
        self.target_health = max(0, min(self.target_health, self.max_hp))

    def update_energy(self):
        """Update energy values within bounds"""
        self.target_energy = max(0, min(self.target_energy, self.max_energy))

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Update opacity fade back for hit state first
        if self.is_hit:
            if current_time - self.hit_time >= 500:
                self.alpha = 255
                self.is_hit = False
            else:
                self.alpha = 128

        # Check for death first
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2
            self.frame_index = 0
            self.original_y = self.rect.y
            pygame.mixer.Sound.play(deathbloodreaper_sfx)
            return

        # Handle death animation with downward movement
        if self.is_dying or self.is_dead:
            if current_time - self.update_time > animation_cooldown:
                if self.is_dying:
                    if self.frame_index < len(self.animation_list[2]) - 1:
                        self.frame_index += 1
                        # Move down 5 pixels each frame during death animation
                        self.rect.y += 5  # Changed from 20 to 5
                    else:
                        self.is_dead = True
                        self.is_dying = False
            self.image = self.animation_list[2][self.frame_index]
            return

        # Safety check for animation indices
        if self.action >= len(self.animation_list):
            self.action = 0
            self.frame_index = 0
            
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            if self.action == 1:  # If attack animation finished
                self.action = 0   # Return to idle
                self.attacking = False
                self.attack_applied = False

        # Handle animation updates
        if current_time - self.update_time > animation_cooldown:
            self.update_time = current_time
            self.frame_index += 1

            # Handle different animation states
            if self.is_dying:
                if self.frame_index >= len(self.animation_list[2]):
                    self.frame_index = len(self.animation_list[2]) - 1
                    self.is_dead = True
                    self.is_dying = False
            elif self.action == 1:  # Attack animation
                if self.frame_index >= len(self.animation_list[1]):
                    self.frame_index = 0
                    self.action = 0
                    self.attacking = False
                    self.attack_applied = False
            else:  # Idle animation
                if self.frame_index >= len(self.animation_list[0]):
                    self.frame_index = 0

        # Update current frame safely
        if (self.action < len(self.animation_list) and 
            self.frame_index < len(self.animation_list[self.action])):
            self.image = self.animation_list[self.action][self.frame_index]

        # Handle attack damage
        if self.action == 1 and not self.attack_applied and self.frame_index == len(self.animation_list[1]) - 2:
            if hasattr(self, "attack_target") and self.attack_target:
                self.apply_attack_damage()

        # Update stats directly
        if not self.is_dead:
            self.update_health()
            self.update_energy()

    def apply_attack_damage(self):
        # Only apply combo if player hasn't been hit
        combo_multiplier = 1
        if not self.was_hit:
            combo_multiplier = 1 + (self.combo_count * 0.5)
            
        base_damage = self.strength * 2 if random.random() < 0.35 else self.strength
        total_damage = int(base_damage * combo_multiplier)
        damage_done = self.attack_target.take_damage(total_damage)
        
        if isinstance(self.attack_target, DeathSentry):
            if damage_done == 0:
                pygame.mixer.Sound.play(deathsentryshieldhit_sfx)
                self.combo_count = 0
                self.should_combo = False
            else:
                # Only show combo if player hasn't been hit this turn
                pygame.mixer.Sound.play(deathsentryhit_sfx)
                if not self.was_hit and self.combo_count > 0:
                    next_combo = self.combo_count + 1
                    if next_combo >= 2:
                        combo_text = ComboText(
                            self.rect.centerx - 100,  # Changed from -50 to -100 to shift left
                            self.rect.centery - 150,
                            next_combo
                        )
                        damage_numbers.append(combo_text)
                        if next_combo in [2, 3]:
                            pygame.mixer.Sound.play(basiccombo_sfx)
                        elif next_combo >= 4:
                            pygame.mixer.Sound.play(morecombo_sfx)

        # Only apply lifesteal if damage was dealt and health isn't full
        if damage_done > 0 and isinstance(self, BloodReaper):
            missing_health = self.max_hp - self.target_health
            if missing_health > 0:
                heal_amount = min(int(damage_done * 0.20), missing_health)  # Cap healing at missing health
                if heal_amount > 0:
                    self.target_health += heal_amount
                    # Only show healing number if actually healed
                    damage_numbers.append(DamageNumber(
                        self.rect.centerx,
                        self.rect.y - 50,
                        heal_amount,
                        (0, 255, 0)
                    ))
                    
            # Energy gain happens regardless of healing
            self.target_energy = min(self.max_energy, self.target_energy + 15)
        
        self.attack_applied = True

    def draw(self):
        """Draw the entity's current image to the screen with opacity"""
        temp_surface = self.image.copy()
        temp_surface.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(temp_surface, self.rect)

    def draw_health_bar_panel(self, x, y):
        transition_width = 0
        transition_color = (255, 0, 0)

        # Character name
        name_text = font_ui.render(self.name.replace("_", " "), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + self.health_bar_length // 2, y - 25))
        screen.blit(name_text, name_rect)

        # Calculate health bar width first
        health_bar_width = int(max(0, self.current_health / self.health_ratio))
        health_bar = pygame.Rect(x, y, health_bar_width, 15)

        # Health bar transition 
        if self.current_health > self.target_health:  # Taking damage
            # Calculate speed based on total health difference and desired duration
            health_diff = self.current_health - self.target_health
            transition_step = (health_diff / 60)  # 60 frames = 1 second at 60fps
            self.current_health = max(self.target_health, 
                                    self.current_health - transition_step)
            transition_width = int((self.current_health - self.target_health) / self.health_ratio)
            transition_color = (255, 255, 0)
            
        elif self.current_health < self.target_health:  # Healing
            self.current_health = min(self.target_health, self.current_health + 1)
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)

        # Create transition bar with clamped width
        transition_bar = pygame.Rect(x + health_bar_width, y, max(0, transition_width), 15)
        
        # Draw the bars
        pygame.draw.rect(screen, (255, 0, 0), health_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.health_bar_length, 15), 4)

    def draw_energy_bar_panel(self, x, y):
        transition_color = (200, 200, 0)
        transition_width = 0

        if self.current_energy < self.target_energy:
            self.current_energy += self.energy_change_speed
            if self.current_energy > self.target_energy:
                self.current_energy = self.target_energy
            transition_width = int((self.target_energy - self.current_energy) / self.energy_ratio)
            transition_color = (200, 200, 0)
        elif self.current_energy > self.target_energy:
            self.current_energy -= self.energy_change_speed
            if self.current_energy < self.target_energy:
                self.current_energy = self.target_energy
            transition_width = int((self.current_energy - self.target_energy) / self.energy_ratio)
            transition_color = (255, 255, 0)

        energy_bar_width = int(self.current_energy / self.energy_ratio)
        energy_bar = pygame.Rect(x, y, energy_bar_width, 15)
        transition_bar = pygame.Rect(x + energy_bar_width, y, transition_width, 15)

        pygame.draw.rect(screen, (255, 255, 0), energy_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.energy_bar_length, 15), 4)

class BloodReaper(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, max_hp=100, strength=75, potion=3, name="BloodReaper", scale=scale)
        self.entity_type = "player"  
        self.load_animations(scale)
        self.immunity_turns = 0
        
        # Reset combo system
        self.combo_count = 0
        self.was_hit = True  # Start as True so combo won't activate until next turn
        self.last_hit_successful = False
        self.should_combo = False

        self.idle_sound = idlebr_sfx
        self.idle_sound_playing = False
        self.idle_sound_channel = None

    def load_animations(self, scale):
        # load idle animation
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Idle/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load attack animation
        temp_list = []
        for i in range(6):
            img = pygame.image.load(f'img/{self.name}/Attack/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # Load death animation for BloodReaper
        temp_list = []
        for i in range(6):
            img = pygame.image.load(f'img/{self.name}/Death/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Handle idle sound effect
        if self.action == 0 and not self.is_dead and not self.is_dying:  # If in idle animation
            if not self.idle_sound_playing:
                self.idle_sound_channel = pygame.mixer.find_channel()
                if self.idle_sound_channel:
                    self.idle_sound_channel.play(self.idle_sound, loops=-1)
                    self.idle_sound_playing = True
        else:
            # Stop sound if not in idle animation
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False

        # Update opacity fade back
        if self.is_hit:
            if current_time - self.hit_time >= 500:  # Changed to 500ms to match DeathSentry
                self.alpha = 255
                self.is_hit = False
            else:
                self.alpha = 128

        # Check for death first
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2
            self.frame_index = 0
            self.original_y = self.rect.y
            pygame.mixer.Sound.play(deathbloodreaper_sfx)
            return

        # Handle death animation with downward movement
        if self.is_dying or self.is_dead:
            if current_time - self.update_time > animation_cooldown:
                if self.is_dying:
                    if self.frame_index < len(self.animation_list[2]) - 1:
                        self.frame_index += 1
                        # Move down 5 pixels each frame during death animation
                        self.rect.y += 5  # Changed from 20 to 5
                    else:
                        self.is_dead = True
                        self.is_dying = False
            self.image = self.animation_list[2][self.frame_index]
            return

        # Safety check for animation indices
        if self.action >= len(self.animation_list):
            self.action = 0
            self.frame_index = 0
            
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            if self.action == 1:  # If attack animation finished
                self.action = 0   # Return to idle
                self.attacking = False
                self.attack_applied = False

        # Handle animation updates
        if current_time - self.update_time > animation_cooldown:
            self.update_time = current_time
            self.frame_index += 1

            # Handle different animation states
            if self.is_dying:
                if self.frame_index >= len(self.animation_list[2]):
                    self.frame_index = len(self.animation_list[2]) - 1
                    self.is_dead = True
                    self.is_dying = False
            elif self.action == 1:  # Attack animation
                if self.frame_index >= len(self.animation_list[1]):
                    self.frame_index = 0
                    self.action = 0
                    self.attacking = False
                    self.attack_applied = False
            else:  # Idle animation
                if self.frame_index >= len(self.animation_list[0]):
                    self.frame_index = 0

        # Update current frame safely
        if (self.action < len(self.animation_list) and 
            self.frame_index < len(self.animation_list[self.action])):
            self.image = self.animation_list[self.action][self.frame_index]

        # Handle attack damage
        if self.action == 1 and not self.attack_applied and self.frame_index == len(self.animation_list[1]) - 2:
            if hasattr(self, "attack_target") and self.attack_target:
                self.apply_attack_damage()

        # Update stats directly
        if not self.is_dead:
            self.update_health()
            self.update_energy()

    def apply_attack_damage(self):
        # Only apply combo multiplier if player hasn't been hit at all
        combo_multiplier = 1
        if not self.was_hit:
            combo_multiplier = 1 + (self.combo_count * 0.5)
            
        base_damage = self.strength * 2 if random.random() < 0.35 else self.strength
        total_damage = int(base_damage * combo_multiplier)
        damage_done = self.attack_target.take_damage(total_damage)
        
        if isinstance(self.attack_target, DeathSentry):
            if damage_done == 0:
                pygame.mixer.Sound.play(deathsentryshieldhit_sfx)
                self.combo_count = 0
                self.should_combo = False
            else:
                # Only show combo if player hasn't been hit this turn
                pygame.mixer.Sound.play(deathsentryhit_sfx)
                if not self.was_hit and self.combo_count > 0:
                    next_combo = self.combo_count + 1
                    if next_combo >= 2:
                        combo_text = ComboText(
                            self.rect.centerx - 100,  # Changed from -50 to -100 to shift left
                            self.rect.centery - 150,
                            next_combo
                        )
                        damage_numbers.append(combo_text)
                        if next_combo in [2, 3]:
                            pygame.mixer.Sound.play(basiccombo_sfx)
                        elif next_combo >= 4:
                            pygame.mixer.Sound.play(morecombo_sfx)

        # Show damage number for enemy (remove duplicate and adjust position)
        damage_numbers.append(DamageNumber(
            self.attack_target.rect.centerx - 30,  # Changed from -40 to -100 to shift further left
            self.attack_target.rect.y - 30,
            "Miss!" if damage_done == 0 else total_damage,
            (255, 255, 255) if damage_done == 0 else (255, 0, 0)
        ))
        
        # Only apply lifesteal if damage was dealt and health isn't full
        if damage_done > 0 and isinstance(self, BloodReaper):
            missing_health = self.max_hp - self.target_health
            if missing_health > 0:
                heal_amount = min(int(damage_done * 0.20), missing_health)  # Cap healing at missing health
                if heal_amount > 0:
                    self.target_health += heal_amount
                    # Only show healing number if actually healed
                    damage_numbers.append(DamageNumber(
                        self.rect.centerx,
                        self.rect.y - 50,
                        heal_amount,
                        (0, 255, 0)
                    ))
                    
            # Energy gain happens regardless of healing
            self.target_energy = min(self.max_energy, self.target_energy + 15)
        
        self.attack_applied = True

    def draw(self):
        """Draw the entity's current image to the screen with opacity"""
        temp_surface = self.image.copy()
        temp_surface.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(temp_surface, self.rect)

    def draw_health_bar_panel(self, x, y):
        transition_width = 0
        transition_color = (255, 0, 0)

        # Character name
        name_text = font_ui.render(self.name.replace("_", " "), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + self.health_bar_length // 2, y - 25))
        screen.blit(name_text, name_rect)

        # Calculate health bar width first
        health_bar_width = int(max(0, self.current_health / self.health_ratio))
        health_bar = pygame.Rect(x, y, health_bar_width, 15)

        # Health bar transition 
        if self.current_health > self.target_health:  # Taking damage
            # Calculate speed based on total health difference and desired duration
            health_diff = self.current_health - self.target_health
            transition_step = (health_diff / 60)  # 60 frames = 1 second at 60fps
            self.current_health = max(self.target_health, 
                                    self.current_health - transition_step)
            transition_width = int((self.current_health - self.target_health) / self.health_ratio)
            transition_color = (255, 255, 0)
            
        elif self.current_health < self.target_health:  # Healing
            self.current_health = min(self.target_health, self.current_health + 1)
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)

        # Create transition bar with clamped width
        transition_bar = pygame.Rect(x + health_bar_width, y, max(0, transition_width), 15)
        
        # Draw the bars
        pygame.draw.rect(screen, (255, 0, 0), health_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.health_bar_length, 15), 4)

    def draw_energy_bar_panel(self, x, y):
        transition_color = (200, 200, 0)
        transition_width = 0

        if self.current_energy < self.target_energy:
            self.current_energy += self.energy_change_speed
            if self.current_energy > self.target_energy:
                self.current_energy = self.target_energy
            transition_width = int((self.target_energy - self.current_energy) / self.energy_ratio)
            transition_color = (200, 200, 0)
        elif self.current_energy > self.target_energy:
            self.current_energy -= self.energy_change_speed
            if self.current_energy < self.target_energy:
                self.current_energy = self.target_energy
            transition_width = int((self.current_energy - self.target_energy) / self.energy_ratio)
            transition_color = (255, 255, 0)

        energy_bar_width = int(self.current_energy / self.energy_ratio)
        energy_bar = pygame.Rect(x, y, energy_bar_width, 15)
        transition_bar = pygame.Rect(x + energy_bar_width, y, transition_width, 15)

        pygame.draw.rect(screen, (255, 255, 0), energy_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.energy_bar_length, 15), 4)

class Boss(Entity):
    def __init__(self, x, y, max_hp, strength, potion, name, scale):
        super().__init__(x, y, max_hp, strength, potion, name, scale)
        self.entity_type = "boss"
        self.last_damage_dealt = False  # Track damage dealt flag
        self.damage_done = 0  # Add new variable to track damage amount

    def load_animations(self, scale):
        # load idle animation
        temp_list = []
        for i in range(12):
            img = pygame.image.load(f'img/{self.name}/Idle/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # load attack animation
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Attack/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        temp_list = []
        for i in range(14):
            img = pygame.image.load(f'img/{self.name}/Death/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

    def attack(self, target):
        if not self.attacking and self.current_energy >= 20:
            self.attacking = True
            self.attack_applied = False
            self.action = 1
            self.attack_target = target
            self.target_energy = max(0, self.target_energy - 20)
            pygame.mixer.Sound.play(monster_sfx)
            pygame.mixer.Sound.play(boss1_sfx)  

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Check for death first
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2  # Death animation index
            self.frame_index = 0
            pygame.mixer.Sound.play(deathboss1_sfx)
            return

        # Handle death animation first
        if self.is_dying or self.is_dead:
            if current_time - self.update_time > animation_cooldown:
                if self.is_dying:
                    if self.frame_index < len(self.animation_list[2]) - 1:
                        self.frame_index += 1
                    else:
                        self.is_dead = True
                        self.is_dying = False
            self.image = self.animation_list[2][self.frame_index]
            return

        if self.action < len(self.animation_list):
            frames = self.animation_list[self.action]
            if self.frame_index >= len(frames):
                self.frame_index = 0
            self.image = frames[self.frame_index]
        else:
            # Jika action invalid, reset ke idle
            self.action = 0
            self.frame_index = 0
            self.image = self.animation_list[0][0]

        # Update frame jika cooldown terpenuhi
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        # Jika animasi attack selesai, kembalikan ke idle dan reset status
        if self.action == 1 and self.frame_index >= len(self.animation_list[1]):
            self.frame_index = 0
            self.action = 0
            self.attacking = False
            self.attack_applied = False

        # Lakukan damage sekali di frame terakhir animasi attack
        if self.action == 1:
            if (not self.attack_applied) and (self.frame_index == len(self.animation_list[1]) - 1):
                base_damage = self.strength
                if hasattr(self, "attack_target") and self.attack_target:
                    damage_done = self.attack_target.take_damage(base_damage)
                    self.damage_done = base_damage  # Change this to track base damage instead of returned value
                    self.last_damage_dealt = (damage_done > 0)
                    
                    # Show damage number
                    damage_numbers.append(DamageNumber(
                        self.attack_target.rect.centerx,
                        self.attack_target.rect.y - 50,
                        "Miss!" if damage_done == 0 else base_damage,
                        (255, 255, 255) if damage_done == 0 else (255, 0, 0)
                    ))

                    if self.last_damage_dealt and isinstance(self.attack_target, BloodReaper):
                        self.attack_target.was_hit = True
                        self.attack_target.combo_count = 0
                        self.attack_target.should_combo = False
                        print(f"Enemy dealt {self.damage_done} damage!") # Debug print
                self.attack_applied = True

        # Call parent class methods for stat updates
        self.update_health()
        self.update_energy()

    def apply_attack_damage(self):
        # Only apply combo multiplier for player entities
        if hasattr(self, 'entity_type') and self.entity_type == "player":
            combo_multiplier = 1 + (self.combo_count * 0.5)  # Each combo adds 50% damage
        else:
            combo_multiplier = 1  # No combo multiplier for non-player entities
            
        base_damage = self.strength * 2 if random.random() < 0.35 else self.strength
        total_damage = int(base_damage * combo_multiplier)
        damage_done = self.attack_target.take_damage(total_damage)
        
        # Track hit success and handle combo setup
        if isinstance(self.attack_target, DeathSentry):
            if damage_done == 0:
                pygame.mixer.Sound.play(deathsentryshieldhit_sfx)
                self.combo_count = 0
                self.should_combo = False
            else:
                pygame.mixer.Sound.play(deathsentryhit_sfx)
                self.last_damage_dealt = damage_done > 0  # Track if damage was dealt
                damage_numbers.append(DamageNumber(
                    self.attack_target.rect.centerx,
                    self.attack_target.rect.y,
                    damage_done,
                    (255, 0, 0)
                ))
                
                if damage_done > 0 and isinstance(self.attack_target, BloodReaper):
                    self.attack_target.combo_count = 0  # Reset combo
                    self.attack_target.should_combo = False

        # Only apply lifesteal if damage was dealt and health isn't full
        if damage_done > 0 and isinstance(self, BloodReaper):
            missing_health = self.max_hp - self.target_health
            if missing_health > 0:
                heal_amount = min(int(damage_done * 0.20), missing_health)  # Cap healing at missing health
                if heal_amount > 0:
                    self.target_health += heal_amount
                    # Only show healing number if actually healed
                    damage_numbers.append(DamageNumber(
                        self.rect.centerx,
                        self.rect.y - 50,
                        heal_amount,
                        (0, 255, 0)
                    ))
                    
            # Energy gain happens regardless of healing
            self.target_energy = min(self.max_energy, self.target_energy + 15)
        
        self.attack_applied = True

    def draw(self):
        """Draw the entity's current image to the screen with opacity"""
        temp_surface = self.image.copy()
        temp_surface.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(temp_surface, self.rect)

    def draw_health_bar_panel(self, x, y):
        transition_width = 0
        transition_color = (255, 0, 0)

        # Character name
        name_text = font_ui.render(self.name.replace("_", " "), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + self.health_bar_length // 2, y - 25))
        screen.blit(name_text, name_rect)

        # Calculate health bar width first
        health_bar_width = int(max(0, self.current_health / self.health_ratio))
        health_bar = pygame.Rect(x, y, health_bar_width, 15)

        # Health bar transition 
        if self.current_health > self.target_health:  # Taking damage
            # Calculate speed based on total health difference and desired duration
            health_diff = self.current_health - self.target_health
            transition_step = (health_diff / 60)  # 60 frames = 1 second at 60fps
            self.current_health = max(self.target_health, 
                                    self.current_health - transition_step)
            transition_width = int((self.current_health - self.target_health) / self.health_ratio)
            transition_color = (255, 255, 0)
            
        elif self.current_health < self.target_health:  # Healing
            self.current_health = min(self.target_health, self.current_health + 1)
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)

        # Create transition bar with clamped width
        transition_bar = pygame.Rect(x + health_bar_width, y, max(0, transition_width), 15)
        
        # Draw the bars
        pygame.draw.rect(screen, (255, 0, 0), health_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.health_bar_length, 15), 4)

    def draw_energy_bar_panel(self, x, y):
        transition_color = (200, 200, 0)
        transition_width = 0

        if self.current_energy < self.target_energy:
            self.current_energy += self.energy_change_speed
            if self.current_energy > self.target_energy:
                self.current_energy = self.target_energy
            transition_width = int((self.target_energy - self.current_energy) / self.energy_ratio)
            transition_color = (200, 200, 0)
        elif self.current_energy > self.target_energy:
            self.current_energy -= self.energy_change_speed
            if self.current_energy < self.target_energy:
                self.current_energy = self.target_energy
            transition_width = int((self.current_energy - self.target_energy) / self.energy_ratio)
            transition_color = (255, 255, 0)

        energy_bar_width = int(self.current_energy / self.energy_ratio)
        energy_bar = pygame.Rect(x, y, energy_bar_width, 15)
        transition_bar = pygame.Rect(x + energy_bar_width, y, transition_width, 15)

        pygame.draw.rect(screen, (255, 255, 0), energy_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.energy_bar_length, 15), 4)

class DeathSentry(Boss):
    def __init__(self, x, y, scale):
        super().__init__(x, y, max_hp=2000, strength=30, potion=3, name="DeathSentry", scale=scale)
        self.max_energy = 500  # Total energy points
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350  # Visual bar length in pixels
        self.energy_ratio = self.max_energy / self.energy_bar_length
        self.is_dying = False
        self.is_dead = False
        self.attacking = False  # Add this line
        self.attack_applied = False  # Add this line
        self.immunity_turns = 0  # Change this to immunity_hits
        self.immunity_hits = 0  # Number of hits the shield can take
        self.max_immunity_hits = 2  # Maximum number of hits shield can take
        self.using_skill = False
        self.skill_applied = False
        self.skill_energy_cost = 45

        self.using_ultimate = False
        self.ultimate_applied = False
        self.ultimate_energy_cost = 75
        self.ultimate_damage = 70  # Total damage (20 initial + 5x10)
        self.initial_ultimate_damage = 20  # Initial burst damage
        self.ultimate_duration = 2000  # Duration in milliseconds (2 seconds)
        self.ultimate_start_time = 0   # When ultimate starts
        self.damage_numbers_delay = 1000  # 1 second delay for damage numbers
        self.damage_number_spacing = 40  # Increased vertical spacing between numbers
        self.ultimate_damage_shown = False  # Add flag to track if damage numbers have been shown

        # New variables for staggered damage number display
        self.damage_number_delay = 200  # Delay between each number appearing (ms)
        self.damage_number_index = 0  # Track which number we're showing
        self.next_damage_number_time = 0  # When to show next number

        # Load DeathSentry specific animations
        # Load death animation first before other animations
        temp_list = []
        for i in range(14):
            img = pygame.image.load(f'img/{self.name}/Death/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)  # This becomes index 2

        # Then load skill and ultimate animations
        # Skill animation (index 3)
        temp_list = []
        for i in range(7):  # Load 7 skill frames
            img = pygame.image.load(f'img/{self.name}/Skill/{i+1}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # Ultimate animation (index 4)  
        temp_list = []
        for i in range(14):  # Load 14 ultimate frames
            img = pygame.image.load(f'img/{self.name}/Ultimate/{i+1}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        # Load animations in correct order
        self.animation_list = []  # Reset animation list
        
        # Helper function untuk load dan scale image
        def load_animation(path, frame_count):
            temp_list = []
            for i in range(frame_count):
                img = pygame.image.load(f'img/{self.name}/{path}/{i+1}.png')
                # Set posisi yang sama untuk semua animasi
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            return temp_list

        # Load semua animasi dengan posisi yang konsisten
        self.animation_list.append(load_animation('Idle', 9))      # index 0
        self.animation_list.append(load_animation('Attack', 8))    # index 1 
        self.animation_list.append(load_animation('Death', 14))    # index 2
        self.animation_list.append(load_animation('Skill', 7))     # index 3
        self.animation_list.append(load_animation('Ultimate', 14))  # index 4

        # Set posisi awal
        self.image = self.animation_list[0][0]  # Idle frame pertama
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.original_pos = self.rect.center  # Simpan posisi original

        # Add icon position attributes
        self.icon_base_x = 1350
        self.icon_base_y = 870
        self.icon_spacing = 120

        # Add active skill tracking
        self.active_skill = None
        
        # Add variables for icon state tracking with smooth transitions
        self.skill_icons_target_alpha = {
            'basic': 128,
            'skill': 128,
            'ultimate': 128
        }
        self.skill_icons_alpha = {
            'basic': 128,
            'skill': 128,
            'ultimate': 128
        }
        self.alpha_transition_speed = 15  # Speed of fade transition

        # Load and scale skill icons
        ICON_SCALE = 0.1
        self.basic_attack_icon = pygame.image.load('img/DeathSentry/Skill_icon/BasicAttack_DS.png').convert_alpha()
        self.skill_icon = pygame.image.load('img/DeathSentry/Skill_icon/Skill_DS.png').convert_alpha()
        self.ultimate_icon = pygame.image.load('img/DeathSentry/Skill_icon/Ultimate_DS.png').convert_alpha()
        
        # Scale icons
        self.basic_attack_icon = pygame.transform.scale(self.basic_attack_icon, 
            (int(self.basic_attack_icon.get_width() * ICON_SCALE), 
             int(self.basic_attack_icon.get_height() * ICON_SCALE)))
        self.skill_icon = pygame.transform.scale(self.skill_icon, 
            (int(self.skill_icon.get_width() * ICON_SCALE), 
             int(self.skill_icon.get_height() * ICON_SCALE)))
        self.ultimate_icon = pygame.transform.scale(self.ultimate_icon, 
            (int(self.ultimate_icon.get_width() * ICON_SCALE), 
             int(self.ultimate_icon.get_height() * ICON_SCALE)))

        # Add damage sequence tracking variables
        self.damage_sequence_started = False
        self.damage_sequence_complete = False
        self.damage_ticks = 0
        self.max_damage_ticks = 5
        
        # Add other needed sequence variables
        self.damage_number_index = 0
        self.next_damage_number_time = 0

        self.death_animation_duration = 5000  # 2 seconds death animation
        self.death_frame_delay = self.death_animation_duration / 14  # 14 frames spread over 2 seconds

        # Add idle sound attributes
        self.idle_sound = idleds_sfx
        self.idle_sound_playing = False
        self.idle_sound_channel = None

    def attack(self, target):
        self.last_damage_dealt = False
        if not self.is_dying and not self.is_dead:
            if not self.attacking and not self.using_skill and not self.using_ultimate:
                # Check for ultimate condition first
                health_percent = (self.target_health / self.max_hp) * 100
                if health_percent < 50 and self.current_energy >= self.ultimate_energy_cost:
                    self.active_skill = 'ultimate'
                    self.use_ultimate(target)
                # Then check for skill with increased probability
                elif self.current_energy >= self.skill_energy_cost and random.random() < 0.3:
                    self.active_skill = 'skill'
                    self.use_skill()
                    self.attack_target = target
                else:
                    self.active_skill = 'basic'
                    super().attack(target)

    def take_damage(self, amount):
        if self.immunity_hits > 0:
            self.immunity_hits -= 1
            return 0  # No damage taken while shield active
            
        # Set hit state when actually taking damage
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        self.alpha = 128  # 50% opacity
        
        # Shield breaks after taking max hits
        if self.immunity_hits <= 0:
            self.immunity_turns = 0  # Reset immunity turns
            
        return super().take_damage(amount)  # Return damage taken when no shield        

    def use_skill(self):
        if len(self.animation_list) > 3:
            self.using_skill = True
            self.skill_applied = False
            self.action = 3
            self.frame_index = 0
            self.target_energy = max(0, self.target_energy - self.skill_energy_cost)
            pygame.mixer.Sound.play(skillboss1_sfx)
            
            # Set immunity without dealing damage
            self.immunity_hits = self.max_immunity_hits  # Reset shield hits to maximum
            blood_reaper.should_combo = False  # Reset combo potential during immunity
            return True
        return False

    def use_ultimate(self, target):
        if len(self.animation_list) > 4:
            self.using_ultimate = True
            self.ultimate_applied = False
            self.action = 4  # Ultimate animation index
            self.frame_index = 0
            self.attack_target = target
            self.target_energy = max(0, self.target_energy - self.ultimate_energy_cost)
            pygame.mixer.Sound.play(ultimateboss1_sfx)
            pygame.mixer.Sound.play(monster_sfx)  # Add hit sound for initial damage
            
            # Store original position and create offset for ultimate animation
            self.original_pos = self.rect.center
            self.rect.centerx -= 1150  # Changed from 1000 to 1200 to move more left
            self.rect.centery -= 60
            
            # Apply initial burst damage and create damage number
            if hasattr(self, "attack_target") and self.attack_target:
                damage_done = self.attack_target.take_damage(self.initial_ultimate_damage)
                self.last_damage_dealt = (damage_done > 0)
                self.initial_damage_done = True  # Add this flag to prevent duplicate damage
                
                if isinstance(self.attack_target, BloodReaper) and damage_done > 0:
                    self.attack_target.combo_count = 0
                    self.attack_target.should_combo = False
                
                damage_numbers.append(DamageNumber(
                    self.attack_target.rect.centerx,
                    self.attack_target.rect.y - 50,
                    self.initial_ultimate_damage,
                    (255, 0, 0),
                    lifetime=120  # Increased from 90 to 120 for longer fade
                ))
            
            # Reset sequence variables
            self.damage_number_index = 0
            self.ultimate_start_time = pygame.time.get_ticks()
            self.next_damage_number_time = self.ultimate_start_time + 500
            return True
        return False

    def update_health(self):
        """Update health values within bounds"""
        self.target_health = max(0, min(self.target_health, self.max_hp))

    def update_energy(self):
        """Update energy values within bounds"""
        self.target_energy = max(0, min(self.target_energy, self.max_energy))

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Handle idle sound effect first - must be at the start of update
        if (self.action == 0 and not self.is_dead and not self.is_dying 
            and not self.using_skill and not self.using_ultimate 
            and not self.attacking):  # Add check for not attacking
            if not self.idle_sound_playing:
                self.idle_sound_channel = pygame.mixer.find_channel()
                if self.idle_sound_channel:
                    self.idle_sound_channel.play(self.idle_sound, loops=-1)
                    self.idle_sound_playing = True
        else:
            # Stop sound if not in idle state
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False

        # Update opacity fade back first
        if self.is_hit:
            if current_time - self.hit_time >= 500:
                self.alpha = 255
                self.is_hit = False

        # Check for death first
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2
            self.frame_index = 0
            self.original_y = self.rect.y
            pygame.mixer.Sound.play(deathboss1_sfx)
            return

        # Handle death animation with slower movement
        if self.is_dying or self.is_dead:
            frame_delay = 1000 / len(self.animation_list[2])  # 3000ms / number of frames for even timing
            if current_time - self.update_time > frame_delay:  # Use longer frame delay
                if self.is_dying:
                    if self.frame_index < len(self.animation_list[2]) - 1:
                        self.frame_index += 1
                        self.rect.y += 5  # Slower downward movement
                    else:
                        self.is_dead = True
                        self.is_dying = False
                self.update_time = current_time
            self.image = self.animation_list[2][self.frame_index]
            return

        # Handle skill animation
        if self.using_skill:
            # Make sure alpha is restored during skill
            self.alpha = 255
            
            if current_time - self.update_time > animation_cooldown:
                self.update_time = current_time
                self.frame_index += 1
                
                if self.frame_index >= len(self.animation_list[3]):
                    self.frame_index = 0
                    self.action = 0
                    self.using_skill = False
                    self.skill_applied = False

            self.image = self.animation_list[3][self.frame_index]
            return

        # Handle ultimate animation with delayed initial damage
        if self.using_ultimate:
            self.alpha = 255
            elapsed = current_time - self.ultimate_start_time
            progress = min(1.0, elapsed / self.ultimate_duration)
            
            # Remove this section since we now handle initial damage in use_ultimate()
            # if not hasattr(self, 'initial_damage_done') and elapsed >= 500:
            #     self.initial_damage_done = True
            #     if hasattr(self, "attack_target"):
            #         damage_done = self.attack_target.take_damage(self.initial_ultimate_damage)
            #         damage_numbers.append(DamageNumber(...))

            # Calculate which frame to show based on progress
            total_frames = len(self.animation_list[4])
            self.frame_index = min(int(progress * total_frames), total_frames - 1)
            
            # Apply damage at specific points during the animation
            if not self.damage_sequence_started and progress >= 0.5:
                self.damage_sequence_started = True
                self.damage_ticks = 0
                self.next_damage_number_time = current_time + 200

            # Apply damage if sequence started
            if self.damage_sequence_started and not self.damage_sequence_complete:
                if current_time >= self.next_damage_number_time and self.damage_ticks < self.max_damage_ticks:
                    self.show_next_damage_number()
                    self.damage_ticks += 1
                    self.next_damage_number_time = current_time + 200

                if self.damage_ticks >= self.max_damage_ticks:
                    self.damage_sequence_complete = True

            # End ultimate after duration
            if elapsed >= self.ultimate_duration:
                self.action = 0
                self.using_ultimate = False
                self.ultimate_applied = True
                self.damage_sequence_started = False
                self.damage_sequence_complete = False
                self.damage_ticks = 0
                self.rect.center = self.original_pos
                return

            self.image = self.animation_list[4][self.frame_index]
            return

        # Handle other animations normally
        super().update()

        # Update stats
        if not self.is_dead:
            self.update_health()
            self.update_energy()

    def show_next_damage_number(self):
        if hasattr(self, "attack_target"):
            start_y = self.attack_target.rect.y - 100
            pygame.mixer.Sound.play(monster_sfx)  # Play hit sound for each damage tick
            
            # Initial burst (20) has already been applied in use_ultimate()
            # So here we only deal the 10 damage ticks
            damage_amount = 10
            lifetime = 90  # Increased from 60 to 90 for more consistent fade timing
            
            damage_done = self.attack_target.take_damage(damage_amount)
            self.last_damage_dealt = (damage_done > 0)
            
            if isinstance(self.attack_target, BloodReaper) and damage_done > 0:
                self.attack_target.combo_count = 0
                self.attack_target.should_combo = False
            
            # Increment damage_number_index to stack numbers vertically
            self.damage_number_index += 1
            
            damage_numbers.append(DamageNumber(
                self.attack_target.rect.centerx,
                start_y + (self.damage_number_index * 40),
                damage_amount,
                (255, 255, 0),
                font_size=20,
                velocity=-2,
                lifetime=90  # Increased from 60 to 90 for more consistent fade timing
            ))

    def draw_skill_icons(self):
        if self.is_dead or self.is_dying:
            return

        # Use class variables for positioning
        base_x = self.icon_base_x
        y = self.icon_base_y
        spacing = self.icon_spacing
        
        # Helper function to draw icon with current opacity
        def draw_icon(surface, x, y, skill_type):
            temp_surface = surface.copy()
            temp_surface.set_alpha(self.skill_icons_alpha[skill_type])
            scaled_pos = scale_pos(x, y)
            screen.blit(temp_surface, scaled_pos)
        
        # Draw all icons with their current opacity states
        draw_icon(self.basic_attack_icon, base_x - spacing, y, 'basic')
        draw_icon(self.skill_icon, base_x, y, 'skill')
        draw_icon(self.ultimate_icon, base_x + spacing, y, 'ultimate')

# Create character instances - MOVED DOWN here after all class definitions
blood_reaper = BloodReaper(int(501 * scale_factor), int(500 * scale_factor), scale=4.2 * scale_factor)
death_sentry = DeathSentry(int(1400 * scale_factor), int(400 * scale_factor), scale=8.5 * scale_factor)  # Changed x from 1300 to 1400

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
        elif death_sentry.is_dead:
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
        # Get the latest damage number
        latest_damage = None
        for number in damage_numbers:
            if isinstance(number, DamageNumber):
                if number.amount != "Miss!":  # Only consider numeric damage values
                    latest_damage = number.amount
        
        print("\nTurn End Debug Info:")
        print(f"Enemy last_damage_dealt: {death_sentry.last_damage_dealt}")
        print(f"Damage notification shows: {latest_damage}")
        print(f"Current combo count: {blood_reaper.combo_count}")
        
        # Check actual damage dealt based on damage numbers
        if latest_damage is None or latest_damage == 0 or latest_damage == "Miss!":
            blood_reaper.was_hit = False
            blood_reaper.should_combo = True
            blood_reaper.combo_count += 1
            print(">>> Enemy missed/blocked - Enabling combo for next turn")
            print(f">>> New combo count: {blood_reaper.combo_count}")
        else:
            blood_reaper.combo_count = 0
            blood_reaper.was_hit = True
            blood_reaper.should_combo = False
            print(f">>> Enemy dealt {latest_damage} damage - Next turn will be basic attack")
            print(f">>> Combo reset to: {blood_reaper.combo_count}")
            
    # Reset tracking variables    
    death_sentry.last_damage_dealt = False
    
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
        death_sentry.target_energy = min(death_sentry.max_energy, death_sentry.target_energy + 10)
    
    # Existing turn energy regen
    if player_turn_counter >= 6:
        blood_reaper.target_energy = min(blood_reaper.max_energy, blood_reaper.target_energy + 15)
        player_turn_counter = 0
    
    if enemy_turn_counter >= 3:
        death_sentry.target_energy = min(death_sentry.max_energy, death_sentry.target_energy + 15)
        enemy_turn_counter = 0

# Main game loop
run = True
while run:
    clock.tick(fps)
    draw_background()
    draw_panel()
    now = pygame.time.get_ticks()  # Add this line to define 'now'

    for character in [blood_reaper, death_sentry]:
        character.update()
        character.draw()

    # Update UI element positions using scale_pos() for coordinates
    blood_reaper.draw_health_bar_panel(*scale_pos(250, 790))  # Changed from 350 to 250
    blood_reaper.draw_energy_bar_panel(*scale_pos(250, 810))  # Changed from 350 to 250
    death_sentry.draw_health_bar_panel(*scale_pos(1150, 790))
    death_sentry.draw_energy_bar_panel(*scale_pos(1150, 810))
    death_sentry.draw_skill_icons()  # Add this line

    draw_turn_text()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Input hanya berlaku saat giliran player dan BloodReaper belum mati
        if current_turn == "player":
            if event.type == pygame.KEYDOWN:
                # Add check for DeathSentry ultimate
                if (event.key == pygame.K_s and not blood_reaper.attacking 
                    and not blood_reaper.is_dead
                    and not death_sentry.using_ultimate):  # Add this condition
                    blood_reaper.attack(death_sentry)
                    current_turn = "enemy"
                    enemy_has_attacked = False
                    turn_switch_time = pygame.time.get_ticks()
                    start_turn_notification()

    # Giliran musuh hanya jika BloodReaper belum mati
    if current_turn == "enemy" and not death_sentry.is_dead:
        if now - turn_switch_time > turn_switch_delay:
            if not death_sentry.attacking and not enemy_has_attacked:
                death_sentry.attack(blood_reaper)
                enemy_has_attacked = True

            if not death_sentry.attacking and enemy_has_attacked:
                switch_turns()

    # Update and draw damage numbers and combo texts
    for number in damage_numbers[:]:
        number.update()
        number.draw(screen)
        if isinstance(number, DamageNumber) and number.lifetime <= 0:
            damage_numbers.remove(number)
        elif isinstance(number, ComboText) and number.lifetime <= 0:
            damage_numbers.remove(number)
    
    pygame.display.update()

pygame.quit()