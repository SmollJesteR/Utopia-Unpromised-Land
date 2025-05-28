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
boss1_sfx = pygame.mixer.Sound('Assets/SFX/BA_DS.wav')
deathboss1_sfx = pygame.mixer.Sound('Assets/SFX/Death_DS.wav')
skillboss1_sfx = pygame.mixer.Sound('Assets/SFX/Skill_DS.wav')
ultimateboss1_sfx = pygame.mixer.Sound('Assets/SFX/Ultimate_DS.wav')
deathsentryattack_sfx = pygame.mixer.Sound('Assets/SFX/MA.wav')  # Rename to be more specific
idleds_sfx = pygame.mixer.Sound('Assets/SFX/Idle_DS.wav')

class DeathSentry(Boss):
    def __init__(self, x, y, scale, player=None):  # Add player parameter
        # Set position variables before super().__init__
        self.pos_x = x
        self.pos_y = y
        super().__init__(x, y, max_hp=2000, strength=30, potion=3, name="DeathSentry", scale=scale)
        
        self.max_energy = 500  # Changed from 1 to 500
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
                img = pygame.image.load(f'img/{self.name}/{path}/{i+1}.png').convert_alpha()
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
            'basic': 255,
            'skill': 255,
            'ultimate': 255
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

        self.player = player  # Store player reference
        self.load_animations(scale)  # Load animations after storing player reference

    def load_animations(self, scale):
        self.animation_list = []  # Reset animation list
        
        def load_animation(path, frame_count):
            temp_list = []
            for i in range(frame_count):
                img = pygame.image.load(f'img/{self.name}/{path}/{i+1}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            return temp_list

        # Load animations in correct order
        self.animation_list.append(load_animation('Idle', 9))      # index 0
        self.animation_list.append(load_animation('Attack', 8))    # index 1 
        self.animation_list.append(load_animation('Death', 14))    # index 2
        self.animation_list.append(load_animation('Skill', 7))     # index 3
        self.animation_list.append(load_animation('Ultimate', 14))  # index 4

        # Set initial image and rect using stored position
        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos_x, self.pos_y)  # Now pos_x and pos_y will exist

    def attack(self, target):
        self.last_damage_dealt = False  # Reset damage flag
        if not self.is_dying and not self.is_dead:
            # Add energy check for basic attack
            basic_attack_cost = 20
            if not self.attacking and not self.using_skill and not self.using_ultimate:
                self.attack_target = target
                health_percent = (self.target_health / self.max_hp) * 100
                
                if health_percent < 50 and self.current_energy >= self.ultimate_energy_cost:
                    self.active_skill = 'ultimate'
                    self.use_ultimate(target)
                elif self.current_energy >= self.skill_energy_cost and random.random() < 0.3:
                    self.active_skill = 'skill'
                    self.use_skill()
                elif self.current_energy >= basic_attack_cost:
                    self.active_skill = 'basic'
                    self.attacking = True
                    self.attack_applied = False
                    self.action = 1
                    self.frame_index = 0
                    self.target_energy = max(0, self.target_energy - basic_attack_cost)
                    pygame.mixer.Sound.play(boss1_sfx)  # Only play boss attack sound, remove monster_sfx

    def take_damage(self, amount):
        # Stop idle sound when hit
        if self.idle_sound_playing and self.idle_sound_channel:
            self.idle_sound_channel.stop()
            self.idle_sound_playing = False

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
            
        # Return actual damage dealt
        return super().take_damage(amount)

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
            if self.player:  # Check if player reference exists
                self.player.should_combo = False  # Reset combo potential during immunity
            return True
        return False

    def use_ultimate(self, target: Any):
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
            self.rect.centerx -= 1050  # Changed from 1000 to 1200 to move more left
            self.rect.centery -= 30
            
            # Apply initial burst damage and create damage number
            if hasattr(self, "attack_target") and self.attack_target:
                damage_done = self.attack_target.take_damage(self.initial_ultimate_damage)
                self.last_damage_dealt = (damage_done > 0)
                
                # Update player combat state
                if hasattr(self.attack_target, 'entity_type') and self.attack_target.entity_type == "player":
                    self.attack_target.combo_count = 0
                    self.attack_target.should_combo = False
                    
            # Reset sequence variables
            self.damage_ticks = 0
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
            and not self.attacking and not self.is_hit):  # Add not self.is_hit check
            if not self.idle_sound_playing:
                self.idle_sound_channel = pygame.mixer.find_channel()
                if self.idle_sound_channel:
                    self.idle_sound_channel.play(self.idle_sound, loops=-1)
                    self.idle_sound_playing = True
        else:
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False

        # Update opacity fade back with 250ms duration
        if self.is_hit:
            if current_time - self.hit_time >= 250:  # Changed from 500 to 250
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
                    self.active_skill = None  # Reset active skill

            self.image = self.animation_list[3][self.frame_index]
            return

        # Handle ultimate animation
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
                self.active_skill = None  # Reset active skill
                return

            self.image = self.animation_list[4][self.frame_index]
            return

        # Handle attack animation
        if self.action == 1:
            if not self.attack_applied and self.frame_index == 4:
                if hasattr(self, "attack_target"):
                    # Apply damage and get actual dealt amount
                    damage_amount = self.strength
                    damage_dealt = self.attack_target.take_damage(damage_amount)
                    self.last_damage_dealt = (damage_dealt > 0)
                    
                    # Create single damage notification
                    if hasattr(self.attack_target, 'damage_reduction_active') and self.attack_target.damage_reduction_active:
                        # Let target handle shield notification
                        pass
                    else:
                        # Only show damage number if not shielded
                        damage_numbers.append(DamageNumber(
                            self.attack_target.rect.centerx,
                            self.attack_target.rect.y - 50,
                            damage_dealt,
                            (255, 0, 0),
                            font_size=20,
                            lifetime=30
                        ))

                    self.attack_applied = True

        # Handle basic attack end
        if self.action == 1 and self.frame_index >= len(self.animation_list[1]) - 1:
            self.action = 0
            self.attacking = False
            self.attack_applied = False
            self.active_skill = None  # Reset active skill

        # Handle other animations normally
        super().update()

        # Update stats
        if not self.is_dead:
            self.update_health()
            self.update_energy()

    def show_next_damage_number(self):
        if hasattr(self, "attack_target"):
            pygame.mixer.Sound.play(monster_sfx)
            
            # Let target handle damage reduction
            damage_done = self.attack_target.take_damage(10)
            self.last_damage_dealt = (damage_done > 0)
            
            if damage_done > 0 and hasattr(self.attack_target, 'entity_type'):
                if self.attack_target.entity_type == "player":
                    self.attack_target.combo_count = 0
                    self.attack_target.should_combo = False
            
            # Increment vertical position for each damage number
            self.damage_number_index += 1

    def draw_skill_icons(self):
        if self.is_dead or self.is_dying:
            return

        # Update icon opacities based on active skill
        for skill_type in self.skill_icons_alpha:
            target = 255 if self.active_skill == skill_type else 128
            current = self.skill_icons_alpha[skill_type]
            
            if current < target:
                self.skill_icons_alpha[skill_type] = min(current + self.alpha_transition_speed, target)
            elif current > target:
                self.skill_icons_alpha[skill_type] = max(current - self.alpha_transition_speed, target)

        # Draw icons with updated opacities
        base_x = self.icon_base_x
        y = self.icon_base_y
        spacing = self.icon_spacing
        
        # Helper function to draw icon with current opacity
        def draw_icon(surface, x, y, skill_type):
            temp_surface = surface.copy()
            temp_surface.set_alpha(self.skill_icons_alpha[skill_type])
            scaled_pos = scale_pos(x, y)
            screen.blit(temp_surface, scaled_pos)
        
        draw_icon(self.basic_attack_icon, base_x - spacing, y, 'basic')
        draw_icon(self.skill_icon, base_x, y, 'skill')
        draw_icon(self.ultimate_icon, base_x + spacing, y, 'ultimate')