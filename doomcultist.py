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
deathd_sfx = pygame.mixer.Sound('Assets/SFX/Death_D.wav')
doomculthit_sfx = pygame.mixer.Sound('Assets/SFX/MA_D.wav')

class DoomCultist(Boss):
    def __init__(self, x, y, scale, player=None):
        self.pos_x = x
        self.pos_y = y
        super().__init__(x, y, max_hp=500, strength=20, potion=3, name="DoomCultist", scale=scale)
        
        # Energy system attributes
        self.max_energy = 100
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

        # Basic attack icon
        ICON_SCALE = 0.1
        self.icon_base_x = 1360
        self.icon_base_y = 870
        self.icon_spacing = 120
        self.basic_attack_icon = pygame.image.load('img/DoomCultist/Skill_icon/BasicAttack_D.png').convert_alpha()
        self.basic_attack_icon = pygame.transform.scale(self.basic_attack_icon, 
            (int(self.basic_attack_icon.get_width() * ICON_SCALE), 
             int(self.basic_attack_icon.get_height() * ICON_SCALE)))
        self.skill_icons_alpha = {'basic': 128}

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

    def load_animations(self, scale):
        self.animation_list = []
        
        def load_animation(path, frame_count):
            temp_list = []
            for i in range(frame_count):
                img_path = f'img/DoomCultist/{path}/{i+1}.png'
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            return temp_list

        # Load animations
        self.animation_list.append(load_animation('Idle', 8))    # index 0
        self.animation_list.append(load_animation('Attack', 8))  # index 1

        # Set initial image
        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos_x, self.pos_y)

    def attack(self, target):
        self.last_damage_dealt = False
        if not self.attacking and not self.is_dying and not self.is_dead:
            if self.current_energy >= self.basic_attack_cost:
                # Update turn counter and check for rage turn
                self.turn_counter += 1
                self.is_rage_turn = (self.turn_counter % 2 == 0)  # Every second turn

                if self.idle_sound_playing and self.idle_sound_channel:
                    self.idle_sound_channel.stop()
                    self.idle_sound_playing = False
                
                self.attacking = True
                self.attack_applied = False
                self.frame_index = 0
                self.action = 1
                self.attack_target = target
                self.target_energy = max(0, self.target_energy - self.basic_attack_cost)
                pygame.mixer.Sound.play(bad_sfx)  # Only play DoomCultist attack sound
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
        
        damage_dealt = super().take_damage(amount)
        self.last_damage_dealt = (damage_dealt > 0)
        
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
            self.action = 0  # Use idle animation for death
            self.frame_index = 0
            self.death_start_time = current_time
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False
            pygame.mixer.Sound.play(deathd_sfx)
            return

        # Handle death animation with fade out
        if self.is_dying or self.is_dead:
            if self.is_dying:
                fade_progress = (current_time - self.death_start_time) / 2000
                self.alpha = max(0, int(255 * (1 - fade_progress)))
                
                if fade_progress >= 1:
                    self.is_dying = False
                    self.is_dead = True
                    self.alpha = 0
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
                            # Calculate damage considering rage state
                            actual_strength = self.strength * 2 if self.is_rage_turn else self.strength
                            damage_dealt = self.attack_target.take_damage(actual_strength)
                            self.last_damage_dealt = (damage_dealt > 0)
                            
                            # Hapus bagian ini yang memainkan monster_sfx
                            # if damage_dealt > 0:
                            #     pygame.mixer.Sound.play(monster_sfx)
                            
                            # Show damage number
                            damage_numbers.append(DamageNumber(
                                self.attack_target.rect.centerx,
                                self.attack_target.rect.y - 50,
                                damage_dealt if damage_dealt > 0 else "Miss!",
                                (255, 0, 0) if damage_dealt > 0 else (255, 255, 255),
                                font_size=20,
                                lifetime=30
                            ))

                            # Update player combat state
                            if hasattr(self.attack_target, 'entity_type') and self.attack_target.entity_type == "player":
                                if damage_dealt > 0:
                                    self.attack_target.was_hit = True
                                    self.attack_target.combo_count = 0
                                    self.attack_target.should_combo = False
                        
                        self.attack_applied = True
                
                self.image = self.animation_list[1][self.frame_index]
            
            # Handle idle animation
            else:
                if self.frame_index >= len(self.animation_list[0]):
                    self.frame_index = 0
                self.image = self.animation_list[0][self.frame_index]

        # Update stats
        self.update_health()
        self.update_energy()

    def draw_skill_icons(self):
        if self.is_dead or self.is_dying:
            return

        target_alpha = 255 if self.attacking else 128
        current = self.skill_icons_alpha['basic']
        
        if current < target_alpha:
            self.skill_icons_alpha['basic'] = min(current + 15, target_alpha)
        elif current > target_alpha:
            self.skill_icons_alpha['basic'] = max(current - 15, target_alpha)

        temp_surface = self.basic_attack_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['basic'])
        scaled_pos = scale_pos(self.icon_base_x, self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)
