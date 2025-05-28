import pygame
import random
from boss import Boss
from game_data import screen, scale_pos, damage_numbers, DamageNumber
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from bloodreaper import BloodReaper

# Initialize pygame mixer before loading sounds 
pygame.mixer.init()

# Import sound effects
bab_sfx = pygame.mixer.Sound('Assets/SFX/BA_B.wav')  # Add Baphomet's basic attack sound
idleb_sfx = pygame.mixer.Sound('Assets/SFX/Idle_B.wav')  # Baphomet's idle sound
deathb_sfx = pygame.mixer.Sound('Assets/SFX/Death_B.wav')  # Baphomet's death sound

class Baphomet(Boss):
    def __init__(self, x, y, scale, player=None):
        # Set position before super().__init__
        self.pos_x = x
        self.pos_y = y
        super().__init__(x, y, max_hp=1000, strength=50, potion=3, name="Baphomet", scale=scale)
        
        # Add energy system attributes
        self.max_energy = 500  # Same as DeathSentry's system
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350
        self.energy_ratio = self.max_energy / self.energy_bar_length
        self.basic_attack_cost = 20  # Same cost as DeathSentry

        # Basic attributes
        self.player = player
        self.entity_type = "boss"
        self.is_dying = False
        self.is_dead = False
        self.attacking = False
        self.attack_applied = False

        # Add this for basic attack icon
        ICON_SCALE = 0.1
        self.icon_base_x = 1360  # Changed from 1350 to 1400 to move right
        self.icon_base_y = 870
        self.icon_spacing = 120
        self.basic_attack_icon = pygame.image.load('img\Baphomet\Skill_icon\BasicAttack_B.png').convert_alpha()
        self.basic_attack_icon = pygame.transform.scale(self.basic_attack_icon, 
            (int(self.basic_attack_icon.get_width() * ICON_SCALE), 
             int(self.basic_attack_icon.get_height() * ICON_SCALE)))
        self.skill_icons_alpha = {'basic': 128}

        # Initialize animation variables
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.action = 0

        # Load animations last
        self.load_animations(scale)

        # Add idle sound properties
        self.idle_sound = idleb_sfx
        self.idle_sound_playing = False
        self.idle_sound_channel = None

        # Add combo tracking
        self.last_damage_dealt = False
        self.damage_done = 0  # Add this to track damage amount like DeathSentry

    def load_animations(self, scale):
        self.animation_list = []  # Reset animation list
        
        def load_animation(path, prefix, frame_count):
            temp_list = []
            for i in range(frame_count):
                img_path = f'img/Baphomet/{path}/{prefix}_{i+1}.png'
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            return temp_list

        # Load all animations in correct order
        self.animation_list.append(load_animation('Idle', 'demon_idle', 6))       # index 0
        self.animation_list.append(load_animation('Attack', 'demon_cleave', 15))  # index 1
        self.animation_list.append(load_animation('Death', 'demon_death', 22))    # index 2

        # Set initial image and rect
        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos_x, self.pos_y)

    def calculate_rage_multiplier(self):
        # Calculate damage multiplier based on missing health percentage
        health_percent = (self.current_health / self.max_hp) * 100
        # Reduced multiplier to max 1.25x damage at low health (was 2x)
        multiplier = 0.5 + ((100 - health_percent) / 100)  # Changed from /100 to /400
        return multiplier

    def attack(self, target):
        self.last_damage_dealt = False
        if not self.attacking and not self.is_dying and not self.is_dead:
            if self.current_energy >= self.basic_attack_cost:
                # Stop idle sound when starting attack
                if self.idle_sound_playing and self.idle_sound_channel:
                    self.idle_sound_channel.stop()
                    self.idle_sound_playing = False

                self.attacking = True
                self.attack_applied = False
                self.frame_index = 0
                self.action = 1
                self.attack_target = target
                self.target_energy = max(0, self.target_energy - self.basic_attack_cost)
                pygame.mixer.Sound.play(bab_sfx)
                return True
        return False

    def take_damage(self, amount):
        # Stop idle sound when hit
        if self.idle_sound_playing and self.idle_sound_channel:
            self.idle_sound_channel.stop()
            self.idle_sound_playing = False
            
        # Set hit state and play hit sound
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        self.alpha = 128  # 50% opacity when hit
        # Only play Baphomet's hit sound
        # Calculate damage
        damage_dealt = super().take_damage(amount)
        self.last_damage_dealt = (damage_dealt > 0)
        
        # Create damage number
        if damage_dealt > 0:
            new_damage = DamageNumber(
                900,
                150,
                str(damage_dealt),
                (255, 0, 0),
                font_size=20,
                velocity=-2,
                lifetime=30
            )
            damage_numbers.append(new_damage)
            
        return damage_dealt

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Handle hit state opacity
        if self.is_hit:
            if current_time - self.hit_time >= 250:  # 0.25s flash duration
                self.alpha = 255
                self.is_hit = False

        # Death check
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2
            self.frame_index = 0
            # Stop idle sound when dying starts
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False
            pygame.mixer.Sound.play(deathb_sfx)
            return

        # Handle death animation
        if self.is_dying or self.is_dead:
            if current_time - self.update_time > animation_cooldown:
                if self.is_dying:
                    if self.frame_index < len(self.animation_list[2]) - 1:
                        self.frame_index += 1
                        self.rect.y += 0  # Fall effect
                    else:
                        self.is_dying = False
                        self.is_dead = True
                        self.frame_index = len(self.animation_list[2]) - 1
                self.update_time = current_time
            self.image = self.animation_list[2][self.frame_index]
            return

        # Handle idle sound - now checks for hit state
        if self.action == 0 and not self.is_dead and not self.is_dying and not self.attacking and not self.is_hit:
            if not self.idle_sound_playing:
                self.idle_sound_channel = pygame.mixer.find_channel()
                if self.idle_sound_channel:
                    self.idle_sound_channel.play(self.idle_sound, loops=-1)
                    self.idle_sound_playing = True
        else:
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False

        # Handle attack animation and damage
        if self.action == 1:  # Attack animation
            animation_cooldown = 1000 // len(self.animation_list[1])  # Distribute 1000ms across all frames
            if current_time - self.update_time > animation_cooldown:
                self.frame_index += 1
                self.update_time = current_time
                
                # Apply damage near middle of attack animation
                if not self.attack_applied and self.frame_index == 7:
                    if hasattr(self, "attack_target"):
                        # Calculate base damage with rage multiplier
                        base_damage = int(self.strength * self.calculate_rage_multiplier())
                        # Apply damage and get actual damage dealt back
                        damage_dealt = self.attack_target.take_damage(base_damage)
                        self.last_damage_dealt = (damage_dealt > 0)
                        
                        # Show actual damage dealt with proper colors
                        damage_numbers.append(DamageNumber(
                            self.attack_target.rect.centerx,
                            self.attack_target.rect.y - 50,
                            damage_dealt if damage_dealt > 0 else "Miss!",
                            (255, 255, 255) if damage_dealt == 1 else (255, 0, 0) if damage_dealt > 0 else (255, 255, 255),
                            font_size=20,
                            lifetime=30
                        ))

                        # Print debug message after damage number created
                        if damage_dealt > 0:
                            print(f"Enemy dealt {base_damage} damage!")
                        
                        # Update player state
                        if hasattr(self.attack_target, 'entity_type') and self.attack_target.entity_type == "player":
                            if damage_dealt > 0:
                                self.attack_target.was_hit = True
                                self.attack_target.combo_count = 0
                                self.attack_target.should_combo = False
                    
                    self.attack_applied = True

                if self.frame_index >= len(self.animation_list[1]):
                    self.action = 0
                    self.attacking = False
                    self.attack_applied = False
        else:
            animation_cooldown = 150  # Normal animation speed for other actions

        # Update animation frames
        if current_time - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = current_time
            
            # Make sure damage numbers are visible
            if hasattr(self, 'last_damage_taken'):
                damage_numbers.append(DamageNumber(
                    self.rect.centerx,
                    self.rect.y - 50,
                    str(self.last_damage_taken),
                    (255, 255, 255),
                    lifetime=90
                ))
                delattr(self, 'last_damage_taken')

            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0
                if self.action == 1:  # After attack animation
                    self.action = 0
                    self.attacking = False

        # Update current frame
        if (self.action < len(self.animation_list) and 
            self.frame_index < len(self.animation_list[self.action])):
            self.image = self.animation_list[self.action][self.frame_index]

        # Update health and stats
        self.update_health()
        self.update_energy()

    def draw_skill_icons(self):
        if self.is_dead or self.is_dying:
            return

        # Update basic attack icon opacity
        target_alpha = 255 if self.attacking else 128
        current = self.skill_icons_alpha['basic']
        
        if current < target_alpha:
            self.skill_icons_alpha['basic'] = min(current + 15, target_alpha)
        elif current > target_alpha:
            self.skill_icons_alpha['basic'] = max(current - 15, target_alpha)

        # Draw only basic attack icon
        temp_surface = self.basic_attack_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['basic'])
        scaled_pos = scale_pos(self.icon_base_x, self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)
