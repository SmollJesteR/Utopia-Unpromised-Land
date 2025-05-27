import pygame
import random
from boss import Boss
from game_data import screen, scale_pos, damage_numbers, DamageNumber
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from bloodreaper import BloodReaper

pygame.mixer.init()

# Sound effects
monster_sfx = pygame.mixer.Sound('Assets/SFX/MA.wav')
bam_sfx = pygame.mixer.Sound('Assets/SFX/BA_M.wav')
idlem_sfx = pygame.mixer.Sound('Assets/SFX/Idle_M.wav')
deathm_sfx = pygame.mixer.Sound('Assets/SFX/Death_M.wav')
medusahit_sfx = pygame.mixer.Sound('Assets/SFX/MA_M.wav')  # Use Cyclops hit sound temporarily

class Medusa(Boss):
    def __init__(self, x, y, scale, player=None):
        self.pos_x = x
        self.pos_y = y
        super().__init__(x, y, max_hp=800, strength=10, potion=3, name="Medusa", scale=scale)
        
        # Energy system attributes
        self.max_energy = 150
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350
        self.energy_ratio = self.max_energy / self.energy_bar_length
        self.basic_attack_cost = 20

        # Basic attributes
        self.player = player
        self.original_player_strength = None  # Add this to store original strength
        self.entity_type = "boss"
        self.is_dying = False
        self.is_dead = False
        self.attacking = False
        self.attack_applied = False
        
        # Turn counter for passive
        self.turn_counter = 0
        self.curse_active = False

        # Basic attack icon
        ICON_SCALE = 0.1
        self.icon_base_x = 1360
        self.icon_base_y = 870
        self.icon_spacing = 120
        self.basic_attack_icon = pygame.image.load('img/Medusa/Skill_icon/BasicAttack_M.png').convert_alpha()
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
        self.idle_sound = idlem_sfx
        self.idle_sound_playing = False
        self.idle_sound_channel = None

        # Combo tracking
        self.last_damage_dealt = False  # Add this for combo tracking

    def load_animations(self, scale):
        self.animation_list = []
        
        def load_animation(path, frame_count):
            temp_list = []
            for i in range(frame_count):
                img_path = f'img/Medusa/{path}/{i+1}.png'
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
        self.last_damage_dealt = False  # Reset damage flag at start

        # Update turn counter and check for curse activation
        self.turn_counter += 1
        self.curse_active = (self.turn_counter % 2 == 0)  # Every second turn

        if not self.attacking and not self.is_dying and not self.is_dead:
            if self.current_energy >= self.basic_attack_cost:
                # Apply curse effect
                if self.curse_active and self.player:
                    # Store original strength only if not already stored
                    if self.original_player_strength is None:
                        self.original_player_strength = self.player.strength
                    self.player.strength = int(self.original_player_strength * 0.5)  # Use original strength for calculation
                    damage_numbers.append(DamageNumber(
                        self.player.rect.centerx,
                        self.player.rect.y - 50,
                        "CURSED!",
                        (128, 0, 128),  # Purple color for curse
                        font_size=20,
                        lifetime=60
                    ))
                elif not self.curse_active and self.original_player_strength is not None:
                    # Reset strength when curse ends
                    self.player.strength = self.original_player_strength
                    self.original_player_strength = None  # Clear stored value
                    damage_numbers.append(DamageNumber(
                        self.player.rect.centerx,
                        self.player.rect.y - 50,
                        "CURSE LIFTED!",
                        (0, 255, 0),  # Green color for curse lift
                        font_size=20,
                        lifetime=60
                    ))

                # Stop idle sound when attacking
                if self.idle_sound_playing and self.idle_sound_channel:
                    self.idle_sound_channel.stop()
                    self.idle_sound_playing = False
                
                self.attacking = True
                self.attack_applied = False
                self.frame_index = 0
                self.action = 1
                self.attack_target = target
                self.target_energy = max(0, self.target_energy - self.basic_attack_cost)
                pygame.mixer.Sound.play(monster_sfx)
                pygame.mixer.Sound.play(bam_sfx)
                return True
        return False

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

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Handle idle sound with proper state checks
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

        # Handle hit state opacity - should be at start of update
        if self.is_hit:
            if current_time - self.hit_time >= 250:  # 0.25s duration
                self.alpha = 255  # Restore to full opacity
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
            pygame.mixer.Sound.play(deathm_sfx)
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
            # Update frame index
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
                    if not self.attack_applied and self.frame_index == 4:
                        if hasattr(self, "attack_target"):
                            # Apply normal damage 
                            damage_done = self.attack_target.take_damage(self.strength)
                            self.last_damage_dealt = (damage_done > 0)  # Track if damage was dealt
                            
                            # Create damage number
                            damage_numbers.append(DamageNumber(
                                self.attack_target.rect.centerx,
                                self.attack_target.rect.y - 50,
                                self.strength if damage_done > 0 else "Miss!",
                                (255, 0, 0) if damage_done > 0 else (255, 255, 255),
                                font_size=20,
                                velocity=-2,
                                lifetime=30
                            ))
                            
                            # Update player combo state
                            if hasattr(self.attack_target, 'entity_type') and self.attack_target.entity_type == "player":
                                if damage_done > 0:
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

        # Reset curse effect after one turn
        if self.curse_active and hasattr(self.player, 'original_strength'):
            # Reset player's strength back to original value on next turn
            if self.turn_counter % 2 == 1:  # On odd turns (after curse turn)
                self.player.strength = self.player.original_strength
                delattr(self.player, 'original_strength')
                damage_numbers.append(DamageNumber(
                    self.player.rect.centerx,
                    self.player.rect.y - 50,
                    "CURSE LIFTED!",
                    (0, 255, 0),  # Green color for curse lift
                    font_size=20,
                    lifetime=60
                ))

    def take_damage(self, amount):
        # Stop idle sound when hit
        if self.idle_sound_playing and self.idle_sound_channel:
            self.idle_sound_channel.stop()
            self.idle_sound_playing = False
            
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        self.alpha = 128

        # Play hit sound effect
        pygame.mixer.Sound.play(medusahit_sfx)
        
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
