import pygame
import random
from player import Player
from deathsentry import DeathSentry
from baphomet import Baphomet
from cyclops import Cyclops
from doomcultist import DoomCultist
from medusa import Medusa
from game_data import screen, damage_numbers, ComboText, DamageNumber, font_ui, scale_pos

pygame.mixer.init()

# Import sound effects
attack_sfx = pygame.mixer.Sound('Assets/SFX/BA_AK.wav')
deathashenknight_sfx = pygame.mixer.Sound('Assets/SFX/Death_AK.wav')
deathsentryshieldhit_sfx = pygame.mixer.Sound('Assets/SFX/MA_SHIELD_DS.wav')
basiccombo_sfx = pygame.mixer.Sound('Assets/SFX/combo2,3,.wav')
morecombo_sfx = pygame.mixer.Sound('Assets/SFX/combo4,-.wav')
idleak_sfx = pygame.mixer.Sound('Assets/SFX/Idle_AK.wav')
baphemothit_sfx = pygame.mixer.Sound('Assets/SFX/MA_B.wav')
cyclopshit_sfx = pygame.mixer.Sound('Assets/SFX/MA_C.wav')
deathsentryhit_sfx = pygame.mixer.Sound('Assets/SFX/MA_DS.wav')
ashenknighthit_sfx = pygame.mixer.Sound('Assets/SFX/MA_AK.wav')  # Add hit sound here
ashenknightskill_sfx = pygame.mixer.Sound('Assets/SFX/Skill_AK.wav')  # Add kill sound here
ashenknightshieldhit_sfx = pygame.mixer.Sound('Assets/SFX/MA_SHIELD_AK.wav')  # Add shield hit sound here
ashenknightultimate_sfx = pygame.mixer.Sound('Assets/SFX/Ultimate_AK.wav')  # Add ultimate sound here
ashenknightheal_sfx = pygame.mixer.Sound('Assets/SFX/Heal_AK.wav')  # Add heal sound here

class AshenKnight(Player):
    def __init__(self, x, y, scale, strength_level=0, energy_level=0, health_level=0):
        self.pos_x = x
        self.pos_y = y

        # Calculate stat bonuses based on tree levels
        base_strength = 60
        bonus_strength = strength_level * 10
        # Ensure total strength doesn't go below 1
        total_strength = max(1, base_strength + bonus_strength)
        
        base_health = 120
        bonus_health = health_level * 10
        # Ensure total health doesn't go below 1
        total_health = max(1, base_health + bonus_health)
        
        base_energy = 300
        bonus_energy = energy_level * 10
        # Ensure total energy doesn't go below 1
        total_energy = max(1, base_energy + bonus_energy)
        
        # Initialize with capped stats
        super().__init__(x, y, 
                        max_health=total_health,
                        max_strength=total_strength,
                        name="AshenKnight", 
                        scale=scale)
        
        # Store capped energy
        self.max_energy = total_energy
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350  # Same visual bar length as BloodReaper
        self.energy_ratio = self.max_energy / self.energy_bar_length  # Calculate ratio
        self.energy_change_speed = 1  # Add energy change speed like BloodReaper

        # Core combat attributes
        self.entity_type = "player"
        self.combo_count = 0
        self.was_hit = True
        self.last_hit_successful = False
        self.should_combo = False
        self.attacking = False
        self.attack_applied = False
        self.attack_target = None  # Add this line to store reference to attacker/target

        # Sound setup
        self.idle_sound = idleak_sfx
        self.idle_sound_playing = False
        self.idle_sound_channel = None
        self.death_sound = deathashenknight_sfx
        self.update_time = pygame.time.get_ticks()

        # Icon setup - samakan dengan DoomCultist
        ICON_SCALE = 0.1
        self.icon_base_x = 460  # Tetap di kiri karena player
        self.icon_base_y = 870  # Samakan dengan DoomCultist
        self.icon_spacing = 120  # Samakan spacing dengan DoomCultist
        
        # Load both basic attack and skill icons
        self.basic_attack_icon = pygame.image.load('img/AshenKnight/Skill_icon/BasicAttack_AK.png').convert_alpha()
        self.skill_icon = pygame.image.load('img/AshenKnight/Skill_icon/Skill_AK.png').convert_alpha()  # Temporarily use BR skill icon
        
        # Scale both icons
        self.basic_attack_icon = pygame.transform.scale(self.basic_attack_icon, 
            (int(self.basic_attack_icon.get_width() * ICON_SCALE), 
             int(self.basic_attack_icon.get_height() * ICON_SCALE)))
        self.skill_icon = pygame.transform.scale(self.skill_icon,
            (int(self.skill_icon.get_width() * ICON_SCALE),
             int(self.skill_icon.get_height() * ICON_SCALE)))
             
        # Add ultimate properties
        self.using_ultimate = False
        self.ultimate_applied = False
        self.ultimate_energy_cost = self.max_energy // 2  # Half of max energy
        
        # Load ultimate icon
        self.ultimate_icon = pygame.image.load('img/AshenKnight/Skill_icon/Ultimate_AK.png').convert_alpha()
        self.ultimate_icon = pygame.transform.scale(self.ultimate_icon,
            (int(self.ultimate_icon.get_width() * ICON_SCALE),
             int(self.ultimate_icon.get_height() * ICON_SCALE)))
        
        # Add heal skill properties
        self.using_heal = False
        self.heal_applied = False
        self.heal_amount = 30
        self.heal_energy_cost = 20
        
        # Load heal icon (using ultimate icon temporarily)
        self.heal_icon = pygame.image.load('img/AshenKnight/Skill_icon/Heal_AK.png').convert_alpha()
        self.heal_icon = pygame.transform.scale(self.heal_icon,
            (int(self.heal_icon.get_width() * ICON_SCALE),
             int(self.heal_icon.get_height() * ICON_SCALE)))
        
        self.skill_icons_alpha = {'basic': 128, 'skill': 128, 'ultimate': 128, 'heal': 128}

        # Animation loading
        self.load_animations(scale)

        # Hit state
        self.alpha = 255
        self.hit_time = 0
        self.is_hit = False

        # Add damage reduction skill attributes
        self.using_skill = False
        self.skill_applied = False
        self.damage_reduction_active = False
        self.damage_reduction_turns = 0
        self.skill_energy_cost = 30
        self.skill_animation_loaded = False

        # Load skill animation
        temp_list = []
        for i in range(7):
            img_path = f'img/AshenKnight/Skill/{i+1}.png'
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)  # index 3 for skill animation

        # Load Ultimate animation
        temp_list = []
        for i in range(7):  # 7 frames for ultimate
            img_path = f'img/AshenKnight/Ultimate/{i+1}.png'
            img = pygame.image.load(img_path).convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)  # index 4 for ultimate animation

        # Add this to track if ultimate was blocked
        self.blocked_ultimate = False

    def load_animations(self, scale):
        self.animation_list = []
        
        def load_animation(path, frame_count):
            temp_list = []
            for i in range(frame_count):
                img_path = f'img/AshenKnight/{path}/{i+1}.png'
                img = pygame.image.load(img_path).convert_alpha()
                
                # Apply smaller scale for attack frames 5 and 6
                if path == 'Attack' and i in [4, 5]:  # Frames 5 and 6
                    adjusted_scale = scale * 0.95  # Reduce scale by 20%
                    img = pygame.transform.scale(img, (int(img.get_width() * adjusted_scale), 
                                                     int(img.get_height() * adjusted_scale)))
                else:
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), 
                                                     int(img.get_height() * scale)))
                temp_list.append(img)
            return temp_list

        # Load animations in order
        self.animation_list.append(load_animation('Idle', 9))      # index 0
        self.animation_list.append(load_animation('Attack', 6))    # index 1
        self.animation_list.append(load_animation('Death', 6))     # index 2

        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos_x, self.pos_y)

        # Add custom positions for attack frames 5 and 6
        self.attack_frame_positions = {
            4: {"offset_x": 30, "offset_y": +20},  # Frame 5 (index 4)
            5: {"offset_x": 30, "offset_y": +20}   # Frame 6 (index 5)
        }

    def draw(self):
        """Draw the player's current image to the screen with opacity"""
        temp_surface = self.image.copy()
        temp_surface.fill((255, 255, 255, self.alpha), special_flags=pygame.BLEND_RGBA_MULT)
        screen.blit(temp_surface, self.rect)

    def draw_health_bar_panel(self, x, y):
        transition_width = 0
        transition_color = (255, 0, 0)

        # Draw name
        name_text = font_ui.render(self.name.replace("_", " "), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + self.health_bar_length // 2, y - 25))
        screen.blit(name_text, name_rect)

        # Calculate health bar
        health_bar_width = int(max(0, self.current_health / self.health_ratio))
        health_bar = pygame.Rect(x, y, health_bar_width, 15)

        # Handle transitions
        if self.current_health > self.target_health:
            health_diff = self.current_health - self.target_health
            transition_step = (health_diff / 20)
            self.current_health = max(self.target_health, self.current_health - transition_step)
            # Batasi transition width agar tidak melewati bar
            transition_width = min(
                int((self.current_health - self.target_health) / self.health_ratio),
                self.health_bar_length - health_bar_width
            )
            transition_color = (255, 255, 0)
        elif self.current_health < self.target_health:
            self.current_health = min(self.target_health, self.current_health + 1)
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)

        # Draw bars dengan width yang sudah dibatasi
        transition_bar = pygame.Rect(x + health_bar_width, y, max(0, transition_width), 15)
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

    def draw_skill_icons(self):
        if self.is_dead or self.is_dying:
            return

        # Update basic attack icon alpha
        target_alpha_basic = 255 if self.attacking else 128
        target_alpha_skill = 255 if self.using_skill else 128
        target_alpha_ultimate = 255 if self.using_ultimate else 128
        target_alpha_heal = 255 if self.using_heal else 128

        # Update all icon alphas
        for skill_type, target in [('basic', target_alpha_basic), ('skill', target_alpha_skill), 
                                 ('ultimate', target_alpha_ultimate), ('heal', target_alpha_heal)]:
            current = self.skill_icons_alpha[skill_type]
            if current < target:
                self.skill_icons_alpha[skill_type] = min(current + 15, target)
            elif current > target:
                self.skill_icons_alpha[skill_type] = max(current - 15, target)

        # Draw basic attack icon
        temp_surface = self.basic_attack_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['basic'])
        scaled_pos = scale_pos(self.icon_base_x - self.icon_spacing, self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)

        # Draw skill icon
        temp_surface = self.skill_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['skill'])
        scaled_pos = scale_pos(self.icon_base_x, self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)

        # Draw ultimate icon  
        temp_surface = self.ultimate_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['ultimate'])
        scaled_pos = scale_pos(self.icon_base_x + self.icon_spacing, self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)

        # Draw heal icon (setelah ultimate)
        temp_surface = self.heal_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['heal'])
        scaled_pos = scale_pos(self.icon_base_x + 20 + (self.icon_spacing * 2), self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)
        
    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Add heal timing reset
        if self.using_heal and current_time - getattr(self, 'heal_time', 0) > 500:  # 500ms duration
            self.using_heal = False
            self.skill_icons_alpha['heal'] = 128  # Reset heal icon opacity
            self.heal_applied = True

        # Handle opacity restoration
        if self.is_hit and current_time - self.hit_time >= 250:
            self.is_hit = False
            self.alpha = 255

        # Handle death state
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2  # Death animation
            self.frame_index = 0
            pygame.mixer.Sound.play(self.death_sound)
            return

        if self.is_dying or self.is_dead:
            if current_time - self.update_time > animation_cooldown:
                if self.is_dying:
                    if self.frame_index < len(self.animation_list[2]) - 1:
                        self.frame_index += 1
                        self.rect.y += 5
                    else:
                        self.is_dying = False
                        self.is_dead = True
                        self.frame_index = len(self.animation_list[2]) - 1
                self.update_time = current_time
            self.image = self.animation_list[2][self.frame_index]
            return

        # Handle idle sound
        if self.action == 0 and not self.is_dead and not self.is_dying and not self.attacking:
            if not self.idle_sound_playing:
                self.idle_sound_channel = pygame.mixer.find_channel()
                if self.idle_sound_channel:
                    self.idle_sound_channel.play(self.idle_sound, loops=-1)
                    self.idle_sound_playing = True
        else:
            if self.idle_sound_playing and self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False

        # Handle animation updates
        if current_time - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = current_time

            # Handle skill animation first
            if self.action == 3:  # Skill animation
                if not self.skill_applied:
                    # If at last frame, reset animation
                    if self.frame_index >= len(self.animation_list[3]):
                        self.frame_index = 0
                        self.action = 0  # Return to idle
                        self.using_skill = False
                        self.skill_applied = True
                    else:
                        self.image = self.animation_list[3][self.frame_index]
                return

            # Handle ultimate animation
            if self.action == 4:  # Ultimate animation
                if not self.ultimate_applied and self.frame_index == 4:  # Apply heal at middle of animation
                    self.target_health = self.max_health  # Full heal
                    self.ultimate_applied = True
                    damage_numbers.append(DamageNumber(
                        self.rect.x + 60,
                        self.rect.y,
                        "FULL HEAL!",
                        (0, 255, 0),  # Green color
                        font_size=20,
                        lifetime=45
                    ))

                if self.frame_index >= len(self.animation_list[4]):
                    self.frame_index = 0
                    self.action = 0
                    self.using_ultimate = False
                    return

            # Handle attack animation and custom positions
            if self.action == 1:  # Attack animation
                if not self.attack_applied and self.frame_index == 4:
                    if hasattr(self, "attack_target"):
                        self.apply_attack_damage()
                
                # Apply custom positions for specific attack frames
                if self.frame_index in self.attack_frame_positions:
                    offset = self.attack_frame_positions[self.frame_index]
                    saved_center = self.rect.center
                    self.rect.centerx = saved_center[0] + offset["offset_x"]
                    self.rect.centery = saved_center[1] + offset["offset_y"]
                else:
                    self.rect.center = (self.pos_x, self.pos_y)
                        
                if self.frame_index >= len(self.animation_list[1]):
                    self.frame_index = 0
                    self.action = 0
                    self.attacking = False
                    self.attack_applied = False
                    self.rect.center = (self.pos_x, self.pos_y)  # Reset position
            # Handle other animations
            elif self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

            # Update current frame
            if (self.action < len(self.animation_list) and 
                self.frame_index < len(self.animation_list[self.action])):
                self.image = self.animation_list[self.action][self.frame_index]

    def attack(self, target):
        # Check if target is dead before allowing attack
        if isinstance(target, (DeathSentry, Baphomet, Cyclops, DoomCultist, Medusa)) and (target.is_dead or target.is_dying):
            return
            
        # Check immunity and death state before allowing attack
        if self.is_dead or self.is_dying or self.immunity_turns > 0:
            return
            
        if not self.attacking and self.current_energy >= 20:
            self.attacking = True
            self.attack_applied = False
            self.frame_index = 0  # Reset frame index when starting attack
            self.action = 1  # Set to attack animation
            self.attack_target = target
            self.target_energy = max(0, self.target_energy - 20)
            pygame.mixer.Sound.play(attack_sfx)

    def take_damage(self, amount, attacker=None):  # Add attacker parameter
        if not self.is_dead:
            self.is_hit = True
            self.hit_time = pygame.time.get_ticks()
            self.alpha = 128
            
            # Store attacker reference
            self.attack_target = attacker

            # Check if damage is from DeathSentry ultimate
            if (self.attack_target and hasattr(self.attack_target, 'using_ultimate') and 
                self.attack_target.using_ultimate and 
                isinstance(self.attack_target, DeathSentry)):
                if self.damage_reduction_active:
                    self.blocked_ultimate = True
                    actual_damage = 1
                    pygame.mixer.Sound.play(ashenknightshieldhit_sfx)
                    damage_numbers.append(DamageNumber(
                        self.rect.centerx,
                        self.rect.y,
                        f"{actual_damage}",
                        (255, 255, 255),
                        font_size=20,
                        lifetime=45
                    ))
                    return actual_damage

            if self.damage_reduction_active:
                # Play shield hit sound when damage reduced
                pygame.mixer.Sound.play(ashenknightshieldhit_sfx)
                actual_damage = 1
            else:
                # Play regular hit sound when not shielded
                pygame.mixer.Sound.play(ashenknighthit_sfx)
                actual_damage = amount
            
            # Show damage numbers only once
            damage_numbers.append(DamageNumber(
                self.rect.centerx,
                self.rect.y - 50,
                str(actual_damage),
                (255, 255, 255) if self.damage_reduction_active else (255, 0, 0),
                font_size=20,
                lifetime=30
            ))
            
            self.target_health -= actual_damage
            return actual_damage
        return 0

    def use_skill(self):
        if not self.using_skill and not self.is_dead and self.current_energy >= self.skill_energy_cost:
            self.using_skill = True
            self.skill_applied = False
            self.action = 3  # Skill animation index
            self.frame_index = 0
            self.target_energy = max(0, self.target_energy - self.skill_energy_cost)
            self.damage_reduction_active = True
            self.damage_reduction_turns = 2  # Set duration to 2 turns
            
            damage_numbers.append(DamageNumber(
                self.rect.x + 10,
                self.rect.y,
                "SHIELD ACTIVATED!",
                (0, 255, 255),
                font_size=20,
                lifetime=45
            ))
            pygame.mixer.Sound.play(ashenknightskill_sfx)
            return True
        return False

    def use_ultimate(self):
        if not self.using_ultimate and not self.is_dead and self.current_energy >= self.ultimate_energy_cost:
            self.using_ultimate = True
            self.ultimate_applied = False
            self.action = 4  # Ultimate animation index
            self.frame_index = 0
            self.target_energy = max(0, self.target_energy - self.ultimate_energy_cost)
            pygame.mixer.Sound.play(ashenknightultimate_sfx)
            return True
        return False

    def use_heal(self):
        if not self.using_heal and not self.is_dead and self.current_energy >= self.heal_energy_cost:
            self.using_heal = True 
            self.heal_applied = False  # Changed from True to False
            self.heal_time = pygame.time.get_ticks()  # Add heal time tracking
            self.target_energy = max(0, self.target_energy - self.heal_energy_cost)
            
            # Apply heal
            self.target_health = min(self.max_health, self.target_health + self.heal_amount)
            
            # Show heal notification
            damage_numbers.append(DamageNumber(
                self.rect.x + 140,
                self.rect.y,
                f"+{self.heal_amount}",
                (0, 255, 0),  # Green color
                font_size=20,
                lifetime=45
            ))
            
            # Changed from ashenknightskill_sfx to ashenknightheal_sfx
            pygame.mixer.Sound.play(ashenknightheal_sfx)
            return True
        return False

    def apply_attack_damage(self):
        # Only apply combo multiplier if player hasn't been hit
        combo_multiplier = 1
        if not self.was_hit:
            combo_multiplier = 1 + (self.combo_count * 0.5)
            
        base_damage = self.max_strength * 2 if random.random() < 0.35 else self.max_strength
        total_damage = int(base_damage * combo_multiplier)
        damage_done = self.attack_target.take_damage(total_damage)
        
        # Update this section to handle all boss types
        if isinstance(self.attack_target, (DeathSentry, Baphomet, Cyclops, DoomCultist, Medusa)):
            if damage_done == 0:
                if isinstance(self.attack_target, Cyclops):
                    # Don't play shield hit sound for Cyclops dodge
                    pass
                else:
                    pygame.mixer.Sound.play(deathsentryshieldhit_sfx)
                self.combo_count = 0
                self.should_combo = False
            else:
                # Play appropriate hit sound based on boss type
                if isinstance(self.attack_target, DeathSentry):
                    pygame.mixer.Sound.play(deathsentryhit_sfx)
                elif isinstance(self.attack_target, Baphomet):
                    pygame.mixer.Sound.play(baphemothit_sfx)
                elif isinstance(self.attack_target, (Cyclops, DoomCultist, Medusa)):
                    pygame.mixer.Sound.play(cyclopshit_sfx)
                
                # Add combo text and sound effects
                if not self.was_hit and self.combo_count > 0:
                    next_combo = self.combo_count + 1
                    if next_combo >= 2:
                        combo_text = ComboText(
                            self.rect.centerx - 100,
                            self.rect.centery - 150,
                            next_combo
                        )
                        damage_numbers.append(combo_text)
                        
                        if next_combo in [2, 3]:
                            pygame.mixer.Sound.play(basiccombo_sfx)
                        elif next_combo >= 4:
                            pygame.mixer.Sound.play(morecombo_sfx)

        # Show damage number
        damage_numbers.append(DamageNumber(
            self.attack_target.rect.centerx - 60,
            self.attack_target.rect.y - 10,
            "MISS!" if damage_done == 0 else total_damage,
            (255, 255, 255) if damage_done == 0 else (255, 0, 0)
        ))
        
        self.attack_applied = True

    def show_damage_number(self, target, damage):
        dmg_number = DamageNumber(str(damage), target.rect.centerx, target.rect.centery - 50)
        damage_numbers.append(dmg_number)

    def play_attack_sound(self):
        if self.death_sound.get_num_channels() == 0:
            self.death_sound.play()

    def play_hurt_sound(self):
        if self.idle_sound_channel is not None:
            self.idle_sound_channel.stop()
        channel = random.choice([0, 1, 2])
        sound = pygame.mixer.Sound(f'Assets/SFX/Hurt_BR_{channel}.wav')
        sound.play()

    def die(self):
        self.is_dead = True
        self.can_move = False
        self.death_sound.play()
        self.alpha = 255
        # Additional death logic here (e.g., playing death animation)

    def update_position(self):
        # Smooth position transition
        if not self.is_dead:
            self.rect.centerx = int(self.pos_x)
            self.rect.centery = int(self.pos_y)

    def play_idle_sound(self):
        if not self.idle_sound_playing:
            self.idle_sound_playing = True
            self.idle_sound_channel = self.idle_sound.play(-1)
            self.idle_sound_channel.set_volume(0.3)

    def stop_idle_sound(self):
        if self.idle_sound_channel is not None:
            self.idle_sound_channel.stop()
            self.idle_sound_playing = False

    def handle_energy_regeneration(self):
        if self.current_energy < self.max_energy:
            self.current_energy += 0.1  # Regenerate energy over time
            if self.current_energy > self.max_energy:
                self.current_energy = self.max_energy
        elif self.current_energy > self.max_energy:
            self.current_energy = self.max_energy

    def update_animation(self):
        # Animation updating logic
        if self.attacking:
            self.play_attack_animation()
        elif self.is_dead:
            self.play_death_animation()
        else:
            self.play_idle_animation()

    def play_attack_animation(self):
        # Play attack animation
        self.action = 1
        self.update_frame_index(6, 100)

    def play_death_animation(self):
        # Play death animation
        self.action = 2
        self.update_frame_index(6, 100)

    def play_idle_animation(self):
        # Play idle animation
        self.action = 0
        self.update_frame_index(9, 100)

    def update_frame_index(self, frame_count, speed):
        # Update the frame index for animations
        if pygame.time.get_ticks() - self.update_time > speed:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= frame_count:
                self.frame_index = 0

        self.image = self.animation_list[self.action][self.frame_index]
