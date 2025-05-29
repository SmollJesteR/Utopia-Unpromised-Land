import pygame
import random
from boss import Boss
from game_data import screen, scale_pos, damage_numbers, DamageNumber
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from bloodreaper import BloodReaper

pygame.mixer.init()

# Sound effects - use DoomCultist-specific sounds only
bad_sfx = pygame.mixer.Sound('Assets/SFX/BA_D.wav')
idled_sfx = pygame.mixer.Sound('Assets/SFX/Idle_D.wav')
skilld_sfx = pygame.mixer.Sound('Assets/SFX/Skill_D.wav')
deathd_sfx = pygame.mixer.Sound('Assets/SFX/Death_D.wav')
doomculthit_sfx = pygame.mixer.Sound('Assets/SFX/MA_D.wav')
ultimated_sfx = pygame.mixer.Sound('Assets/SFX/Ultimate_D.wav') 

class DoomCultist(Boss):
    def __init__(self, x, y, scale, player=None):
        self.pos_x = x
        self.pos_y = y
        super().__init__(x, y, max_health=650, max_strength=10, name="DoomCultist", scale=scale)
        
        # Energy system attributes
        self.max_energy = 250
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350
        self.energy_ratio = self.max_energy / self.energy_bar_length
        self.basic_attack_cost = 20

        # Basic attributes
        self.player = player
        self.entity_type = "boss"
        self.is_dying = False
        self.is_dead = False
        self.attacking = False
        self.attack_applied = False
        
        # Turn counter for passive
        self.turn_counter = 0
        self.is_rage_turn = False

        # Icon setup
        ICON_SCALE = 0.1
        self.icon_base_x = 1360
        self.icon_base_y = 870
        self.icon_spacing = 120
        
        # Load all skill icons
        self.basic_attack_icon = pygame.image.load('img/DoomCultist/Skill_icon/BasicAttack_D.png').convert_alpha()
        self.skill_icon = pygame.image.load('img/DoomCultist/Skill_icon/Skill_D.png').convert_alpha()  # Temporarily use basic attack icon
        self.ultimate_icon = pygame.image.load('img/DoomCultist/Skill_icon/Ultimate_D.png').convert_alpha()  # Tambahkan ultimate icon
        
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
             
        self.skill_icons_alpha = {'basic': 128, 'skill': 128, 'ultimate': 128}  # Tambahkan ultimate alpha

        # Animation variables
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.action = 0

        # Load animations
        self.load_animations(scale)

        # Sound properties
        self.idle_sound = idled_sfx
        self.idle_sound_playing = False
        self.idle_sound_channel = None

        # Add skill properties
        self.using_skill = False
        self.skill_applied = False
        self.skill_energy_cost = 30
        self.skill_damage = 25  # Changed from 50 to 25
        self.skill_chance = 0.5  # Changed from 1 to 0.5 for 50% chance

        # Add ultimate properties
        self.using_ultimate = False
        self.ultimate_applied = False
        self.ultimate_energy_cost = 50
        self.ultimate_damage = 50  # Changed from 100 to 50
        self.ultimate_hp_threshold = 0.5  # Change to 50% HP threshold
        
        # Animation loading for ultimate
        temp_list = []
        for i in range(16):
            img_path = f'img/DoomCultist/Ultimate/{i+1}.png'
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)  # index 3 for ultimate animation

        # Add damage reduction attributes
        self.damage_reduction_active = False
        self.damage_reduction_turns = 0
        
        # Add turn action tracking
        self.action_taken_this_turn = False

    def load_animations(self, scale):
        self.animation_list = []
        
        # Animation setup
        def load_animation(path, frame_count):
            temp_list = []
            for i in range(frame_count):
                img_path = f'img/DoomCultist/{path}/{i+1}.png'
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            return temp_list

        # Load animations including death
        self.animation_list.append(load_animation('Idle', 8))     # index 0
        self.animation_list.append(load_animation('Attack', 8))   # index 1
        self.animation_list.append(load_animation('Skill', 9))    # index 2
        self.animation_list.append(load_animation('Ultimate', 16))  # index 3
        self.animation_list.append(load_animation('Death', 10))   # index 4 - Add death animation

    def attack(self, target):
        # Check if already acted this turn
        if self.action_taken_this_turn:
            return False
            
        self.last_damage_dealt = False
        if not self.attacking and not self.using_skill and not self.using_ultimate and not self.is_dying and not self.is_dead:
            # Check ultimate first if HP below threshold and have enough energy
            hp_percent = self.current_health / self.max_health
            if hp_percent <= self.ultimate_hp_threshold and self.current_energy >= self.ultimate_energy_cost:
                self.action_taken_this_turn = True
                self.target_energy = max(0, self.target_energy - self.ultimate_energy_cost)
                return self.use_ultimate(target)
                
            # Check skill first - check energy untuk skill
            if self.current_energy >= self.skill_energy_cost and random.random() < 0.3:
                self.action_taken_this_turn = True
                self.target_energy = max(0, self.target_energy - self.skill_energy_cost)
                return self.use_skill(target)
                
            # Only do basic attack if we haven't used skill or ultimate
            if self.current_energy >= self.basic_attack_cost and not self.action_taken_this_turn:
                self.action_taken_this_turn = True
                # Update turn counter and check for rage turn
                self.turn_counter += 1
                self.is_rage_turn = (self.turn_counter % 2 == 0)

                if self.idle_sound_playing and self.idle_sound_channel:
                    self.idle_sound_channel.stop()
                    self.idle_sound_playing = False
                
                self.attacking = True
                self.attack_applied = False
                self.frame_index = 0
                self.action = 1
                self.attack_target = target
                self.target_energy = max(0, self.target_energy - self.basic_attack_cost)
                pygame.mixer.Sound.play(bad_sfx)
                return True
        return False

    def use_skill(self, target):
        if self.current_energy >= self.skill_energy_cost:
            self.using_skill = True
            self.skill_applied = False
            self.frame_index = 0
            self.action = 2  # Skill animation index
            self.attack_target = target
            pygame.mixer.Sound.play(skilld_sfx)  # Use same sound for now
            return True
        return False

    def use_ultimate(self, target):
        if self.current_energy >= self.ultimate_energy_cost:
            self.using_ultimate = True
            self.ultimate_applied = False
            self.frame_index = 0
            self.action = 3  # Ultimate animation index
            self.attack_target = target
            self.target_energy = max(0, self.target_energy - self.ultimate_energy_cost)
            
            # Store original position and calculate target position
            self.original_pos = self.rect.center
            # Move position up by adding offset to y position
            self.rect.center = (target.rect.centerx + 30, target.rect.centery - 150)  # Offset y by -100 to move up
            
            pygame.mixer.Sound.play(ultimated_sfx)  # Use basic attack sound temporarily
            return True
        return False

    def take_damage(self, amount):
        # Stop idle sound when hit
        if self.idle_sound_playing and self.idle_sound_channel:
            self.idle_sound_channel.stop()
            self.idle_sound_playing = False
            
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        self.alpha = 128

        # Play DoomCultist specific hit sound
        pygame.mixer.Sound.play(doomculthit_sfx)
        
        # Handle damage reduction when damage reduction is active
        damage_dealt = 1 if self.damage_reduction_active else amount
        self.target_health -= damage_dealt
        self.last_damage_dealt = (damage_dealt > 0)
        
        if damage_dealt > 0:
            new_damage = DamageNumber(
                925,
                100,
                str(damage_dealt),
                (255, 255, 255) if self.damage_reduction_active else (255, 0, 0),
                font_size=20,
                velocity=-2,
                lifetime=30
            )
            damage_numbers.append(new_damage)
            
        return damage_dealt

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Handle idle sound
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

        # Handle hit state opacity
        if self.is_hit:
            if current_time - self.hit_time >= 250:
                self.alpha = 255
                self.is_hit = False

        # Handle death check
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 4  # Use death animation
            self.frame_index = 0
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False
            pygame.mixer.Sound.play(deathd_sfx)
            return

        # Handle death animation
        if self.is_dying or self.is_dead:
            if self.is_dying and current_time - self.update_time > animation_cooldown:
                self.frame_index += 1
                self.update_time = current_time
                
                if self.frame_index >= len(self.animation_list[4]):
                    self.frame_index = len(self.animation_list[4]) - 1  # Stay on last frame
                    self.is_dying = False
                    self.is_dead = True
                
                self.image = self.animation_list[4][self.frame_index]
            return

        # Handle animations
        if current_time - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = current_time

            # Handle attack animation
            if self.action == 1:
                if self.frame_index >= len(self.animation_list[1]):
                    self.frame_index = 0
                    self.action = 0
                    self.attacking = False
                    self.attack_applied = False
                else:
                    # Apply damage at middle frame
                    if not self.attack_applied and self.frame_index == 4:
                        if hasattr(self, "attack_target"):
                            actual_strength = self.max_strength * 2 if self.is_rage_turn else self.max_strength
                            if self.attack_target.damage_reduction_active:
                                actual_strength = 1
                            damage_dealt = self.attack_target.take_damage(actual_strength)
                            self.last_damage_dealt = (damage_dealt > 0)

                            # Update player combat state
                            if hasattr(self.attack_target, 'entity_type') and self.attack_target.entity_type == "player":
                                if damage_dealt > 0:
                                    self.attack_target.was_hit = True
                                    self.attack_target.combo_count = 0
                                    self.attack_target.should_combo = False
                        
                        self.attack_applied = True
                
                self.image = self.animation_list[1][self.frame_index]
            
            # Handle skill animation
            elif self.action == 2:
                if self.frame_index >= len(self.animation_list[2]):
                    self.frame_index = 0
                    self.action = 0
                    self.using_skill = False
                    self.skill_applied = False
                else:
                    # Apply skill damage at middle frame
                    if not self.skill_applied and self.frame_index == 4:
                        if hasattr(self, "attack_target"):
                            # Check if target has damage reduction before applying it
                            has_reduction = (hasattr(self.attack_target, 'damage_reduction_active') and 
                                          self.attack_target.damage_reduction_active)
                            actual_damage = 1 if has_reduction else self.skill_damage
                            damage_dealt = self.attack_target.take_damage(actual_damage)
                            self.last_damage_dealt = (damage_dealt > 0)
                            
                            damage_numbers.append(DamageNumber(
                                self.attack_target.rect.centerx,
                                self.attack_target.rect.y - 50,
                                str(damage_dealt),
                                (255, 255, 255) if damage_dealt == 1 else (255, 0, 0),
                                font_size=20,
                                lifetime=30
                            ))

                            # Update player combat state
                            if hasattr(self.attack_target, 'entity_type') and self.attack_target.entity_type == "player":
                                if damage_dealt > 0:
                                    self.attack_target.was_hit = True
                                    self.attack_target.combo_count = 0
                                    self.attack_target.should_combo = False
                        self.skill_applied = True

                self.image = self.animation_list[2][self.frame_index]
            
            # Handle ultimate animation
            elif self.action == 3:
                if self.frame_index >= len(self.animation_list[3]):
                    # Reset position and state when animation ends
                    self.frame_index = 0
                    self.action = 0
                    self.using_ultimate = False
                    self.ultimate_applied = False
                    self.rect.center = self.original_pos
                else:
                    # Apply damage at specific frame
                    if not self.ultimate_applied and self.frame_index == 8:
                        if hasattr(self, "attack_target"):
                            actual_damage = 1 if self.attack_target.damage_reduction_active else self.ultimate_damage
                            damage_dealt = self.attack_target.take_damage(actual_damage)
                            self.last_damage_dealt = (damage_dealt > 0)
                            
                            # Update player combat state if damage dealt
                            if hasattr(self.attack_target, 'entity_type') and self.attack_target.entity_type == "player":
                                if damage_dealt > 0:
                                    self.attack_target.was_hit = True
                                    self.attack_target.combo_count = 0
                                    self.attack_target.should_combo = False
                                
                            damage_numbers.append(DamageNumber(
                                self.attack_target.rect.centerx,
                                self.attack_target.rect.y - 50,
                                damage_dealt if damage_dealt > 0 else "Miss!",
                                (255, 255, 255) if damage_dealt == 1 else (255, 0, 0) if damage_dealt > 0 else (255, 255, 255),
                                font_size=20,
                                lifetime=30
                            ))
                        self.ultimate_applied = True
                
                self.image = self.animation_list[3][self.frame_index]
            
            # Handle idle animation
            else:
                if self.frame_index >= len(self.animation_list[0]):
                    self.frame_index = 0
                self.image = self.animation_list[0][self.frame_index]

        # Update stats
        self.update_health()
        self.update_energy()

        # Reset action flag when animations complete
        if self.action == 0 and not self.attacking and not self.using_skill and not self.using_ultimate:
            self.action_taken_this_turn = False

    def draw_skill_icons(self):
        if self.is_dead or self.is_dying:
            return

        # Update all icon alphas
        target_basic = 255 if self.attacking else 128
        target_skill = 255 if self.using_skill else 128
        target_ultimate = 255 if self.using_ultimate else 128
        
        for skill_type, target in [('basic', target_basic), ('skill', target_skill), ('ultimate', target_ultimate)]:
            current = self.skill_icons_alpha[skill_type]
            if current < target:
                self.skill_icons_alpha[skill_type] = min(current + 15, target)
            elif current > target:
                self.skill_icons_alpha[skill_type] = max(current - 15, target)

        # Draw all icons
        base_x = self.icon_base_x
        y = self.icon_base_y
        spacing = self.icon_spacing
        
        # Draw basic attack icon
        temp_surface = self.basic_attack_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['basic'])
        scaled_pos = scale_pos(base_x - spacing, y)
        screen.blit(temp_surface, scaled_pos)

        # Draw skill icon
        temp_surface = self.skill_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['skill']) 
        scaled_pos = scale_pos(base_x, y)
        screen.blit(temp_surface, scaled_pos)

        # Draw ultimate icon
        temp_surface = self.ultimate_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['ultimate'])
        scaled_pos = scale_pos(base_x + spacing, y)
        screen.blit(temp_surface, scaled_pos)