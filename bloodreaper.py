import pygame
import random
from player import Player
from deathsentry import DeathSentry
from baphomet import Baphomet  # Add this import
from cyclops import Cyclops  # Add this import
from doomcultist import DoomCultist  # Add DoomCultist import
from game_data import screen, damage_numbers, ComboText, DamageNumber, font_ui, scale_pos  # Add scale_pos import here
from medusa import Medusa  # Add this import at the top with other imports

# Import sound effects
attack_sfx = pygame.mixer.Sound('Assets/SFX/BA.wav')
bloodreaperhit_sfx = pygame.mixer.Sound('Assets/SFX/MA.wav')  # Add hit sound here
deathbloodreaper_sfx = pygame.mixer.Sound('Assets/SFX/Death_BR.wav')
deathsentryshieldhit_sfx = pygame.mixer.Sound('Assets/SFX/MA_SHIELD_DS.wav')
basiccombo_sfx = pygame.mixer.Sound('Assets/SFX/combo2,3,.wav')
morecombo_sfx = pygame.mixer.Sound('Assets/SFX/combo4,-.wav')
idlebr_sfx = pygame.mixer.Sound('Assets/SFX/Idle_BR.wav')
baphemothit_sfx = pygame.mixer.Sound('Assets/SFX/MA_B.wav')  # Add Baphomet's hit sound
cyclopshit_sfx = pygame.mixer.Sound('Assets/SFX/MA_C.wav')  # Add Cyclops' hit sound
cyclopsdodgehit_sfx = pygame.mixer.Sound('Assets/SFX/MA_DODGE_C.wav')  # Add Cyclops' dodge hit sound
deathsentryhit_sfx = pygame.mixer.Sound('Assets/SFX/MA_DS.wav')  # Add DeathSentry's hit sound
bloodreaperheal_sfx = pygame.mixer.Sound('Assets/SFX/Heal_BR.wav')  # Add BloodReaper's heal sound

pygame.mixer.init()  # Add this line

class BloodReaper(Player):
    def __init__(self, x, y, scale, strength_level=0, energy_level=0, health_level=0):
        # Store position attributes first
        self.pos_x = x
        self.pos_y = y
        
        # Calculate stat bonuses based on tree levels
        base_strength = 10
        bonus_strength = strength_level * 10
        self.total_strength = max(1, base_strength + bonus_strength)
        base_health = 100
        bonus_health = health_level * 10
        total_health = max(1, base_health + bonus_health)
        base_energy = 100
        bonus_energy = energy_level * 10
        total_energy = max(1, base_energy + bonus_energy)

        # Initialize with combined base + bonus stats
        super().__init__(x, y, 
                        max_health=total_health,  # Use total health with minimum 1
                        max_strength=self.total_strength,
                        name="BloodReaper", 
                        scale=scale)
        
        # Initialize damage multiplier system 
        self.base_strength = self.total_strength
        self.max_strength = self.base_strength
        self.damage_multiplier = 1
        self.has_attacked = False  # Add this line to fix the error
        
        # Store capped energy
        self.max_energy = total_energy
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350
        self.energy_ratio = self.max_energy / self.energy_bar_length
        self.energy_change_speed = 1  # Add energy change speed

        # Reset combo system
        self.entity_type = "player"        
        self.combo_count = 0
        self.was_hit = True
        self.last_hit_successful = False
        self.should_combo = False

        # Initialize idle sound properly
        self.idle_sound = pygame.mixer.Sound('Assets/SFX/Idle_BR.wav')
        self.idle_sound_playing = False
        self.idle_sound_channel = None
        
        # Add these lines
        self.death_sound = pygame.mixer.Sound('Assets/SFX/Death_BR.wav')
        self.update_time = pygame.time.get_ticks()
        
        # Add basic attack icon with larger scale
        ICON_SCALE = 0.1  # Changed from 0.1 to 0.25 for larger icon
        # Icon positions setup
        self.icon_base_x = 450  # Ubah posisi dasar ke kiri
        self.icon_base_y = 870  # Y tetap sama
        self.icon_spacing = 120
        self.basic_attack_icon = pygame.image.load('img/BloodReaper/Skill_icon/BasicAttack_BR.png').convert_alpha()
        self.basic_attack_icon = pygame.transform.scale(self.basic_attack_icon, 
            (int(self.basic_attack_icon.get_width() * ICON_SCALE), 
             int(self.basic_attack_icon.get_height() * ICON_SCALE)))
        
        # Initialize skill_icons_alpha with both 'basic' and 'heal' keys
        self.skill_icons_alpha = {'basic': 128, 'heal': 128}  # Tambahkan kedua kunci dari awal

        # Add heal skill properties
        self.using_heal = False
        self.heal_applied = False 
        self.heal_amount = 30
        self.heal_energy_cost = 20

        self.heal_icon = pygame.image.load('img/BloodReaper/Skill_icon/Heal_BR.png').convert_alpha()
        self.heal_icon = pygame.transform.scale(self.heal_icon,
            (int(self.heal_icon.get_width() * ICON_SCALE),
             int(self.heal_icon.get_height() * ICON_SCALE)))

        # Add damage reduction attributes (set to False by default)
        self.damage_reduction_active = False
        self.damage_reduction_turns = 0
        
        self.load_animations(scale)  # Call load_animations after all attributes are set

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
        self.animation_list.append(load_animation('Idle', 8))      # index 0
        self.animation_list.append(load_animation('Attack', 6))    # index 1 
        self.animation_list.append(load_animation('Death', 6))     # index 2

        # Set initial image and rect
        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = (self.pos_x, self.pos_y)  # Now pos_x and pos_y are available

    def attack(self, target):
        # Check if target is dead before allowing attack
        if isinstance(target, (DeathSentry, Baphomet, Cyclops, DoomCultist)) and (target.is_dead or target.is_dying):
            return
            
        # Add check for DoomCultist ultimate animation
        if isinstance(target, DoomCultist) and (target.using_ultimate or target.using_skill):
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

    def draw(self):
        """Draw the player's current image to the screen with opacity"""
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

        # Calculate health bar width
        health_bar_width = int(max(0, self.current_health / self.health_ratio))
        health_bar = pygame.Rect(x, y, health_bar_width, 15)

        # Health bar transition 
        if self.current_health > self.target_health:  # Taking damage
            health_diff = self.current_health - self.target_health
            transition_step = (health_diff / 20)
            self.current_health = max(self.target_health, self.current_health - transition_step)
            # Batasi transition width agar tidak melewati bar
            transition_width = min(
                int((self.current_health - self.target_health) / self.health_ratio),
                self.health_bar_length - health_bar_width
            )
            transition_color = (255, 255, 0)
        elif self.current_health < self.target_health:  # Healing
            self.current_health = min(self.target_health, self.current_health + 1)
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)

        # Create transition bar with width yang sudah dibatasi
        transition_bar = pygame.Rect(x + health_bar_width, y, max(0, transition_width), 15)
        
        # Draw bars
        pygame.draw.rect(screen, (255, 0, 0), health_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.health_bar_length, 15), 4)

    def draw_energy_bar_panel(self, x, y):
        transition_color = (200, 200, 0)
        transition_width = 0
        
        # Calculate energy bar width first
        energy_bar_width = int(self.current_energy / self.energy_ratio)
        energy_bar = pygame.Rect(x, y, energy_bar_width, 15)

        if self.current_energy < self.target_energy:
            self.current_energy += self.energy_change_speed
            if self.current_energy > self.target_energy:
                self.current_energy = self.target_energy
            # Batasi transition width agar tidak melewati bar
            transition_width = min(
                int((self.target_energy - self.current_energy) / self.energy_ratio),
                self.energy_bar_length - energy_bar_width
            )
            transition_color = (200, 200, 0)
        elif self.current_energy > self.target_energy:
            self.current_energy -= self.energy_change_speed
            if self.current_energy < self.target_energy:
                self.current_energy = self.target_energy
            # Batasi transition width agar tidak melewati bar
            transition_width = min(
                int((self.current_energy - self.target_energy) / self.energy_ratio),
                self.energy_bar_length - energy_bar_width
            )
            transition_color = (255, 255, 0)

        transition_bar = pygame.Rect(x + energy_bar_width, y, transition_width, 15)

        pygame.draw.rect(screen, (255, 255, 0), energy_bar)
        pygame.draw.rect(screen, transition_color, transition_bar)
        pygame.draw.rect(screen, (255,255,255), (x, y, self.energy_bar_length, 15), 4)

    def apply_attack_damage(self):
        # Only apply combo multiplier if player hasn't been hit
        combo_multiplier = 1
        if not self.was_hit:
            combo_multiplier = 1 + (self.combo_count * 0.5)
            
        # Calculate damage first without multiplier
        base_damage = self.max_strength
        damage_total = int(base_damage * combo_multiplier)
        # --- PATCH: cek jika Cyclops miss, jangan apply damage dua kali ---
        # Hanya panggil take_damage sekali, dan gunakan hasilnya
        damage_done = self.attack_target.take_damage(damage_total)

        # Only increase multiplier after confirming damage was dealt
        if damage_done > 0:
            if not self.has_attacked:
                # First hit stays at base damage
                self.has_attacked = True
            else:
                # Double strength for next attack
                self.max_strength *= 2

        # Only multiply strength after first successful hit
        if self.has_attacked and damage_done > 0:
            self.damage_multiplier *= 2
            self.max_strength = self.base_strength * self.damage_multiplier
            damage_numbers.append(DamageNumber(
                self.rect.centerx - 100,
                self.rect.y - 0,
                f"STRENGTH X 2!",
                (255, 165, 0),
                font_size=20,
                lifetime=45
            ))
        
        self.has_attacked = True  # Mark first attack as done
        
        # --- PATCH: hapus pemanggilan take_damage kedua, gunakan damage_done dari atas ---
        # Update this section to handle all boss types including Medusa
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
            self.attack_target.rect.centerx - 30,
            self.attack_target.rect.y - 30,
            "MISS!" if damage_done == 0 else damage_total,
            (255, 255, 255) if damage_done == 0 else (255, 0, 0)
        ))
        
        # Apply lifesteal if damage was dealt
        if damage_done > 0:
            missing_health = self.max_health - self.target_health
            if missing_health > 0:
                heal_amount = min(int(damage_done * 0.20), missing_health)
                if heal_amount > 0:
                    self.target_health += heal_amount
                    damage_numbers.append(DamageNumber(
                        self.rect.centerx,
                        self.rect.y - 50,
                        heal_amount,
                        (0, 255, 0)
                    ))
            self.target_energy = min(self.max_energy, self.target_energy + 15)
        
        self.attack_applied = True

    def take_damage(self, amount, attacker=None):  # Add optional attacker parameter
        # Play BloodReaper hit sound first before any other operations
        pygame.mixer.Sound.play(bloodreaperhit_sfx)
        
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        self.alpha = 128
        
        # Add damage number visualization
        damage_numbers.append(DamageNumber(
            self.rect.centerx,
            self.rect.y - 50,
            str(amount),
            (255, 0, 0),  # Red color for damage
            font_size=20,
            lifetime=30
        ))
        
        self.target_health -= amount
        return amount

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Add heal timing reset
        if self.using_heal and current_time - getattr(self, 'heal_time', 0) > 500:  # 500ms duration
            self.using_heal = False
            self.skill_icons_alpha['heal'] = 128  # Reset heal icon opacity
            self.heal_applied = True

        # Stop idle sound immediately if dying or dead
        if (self.is_dying or self.is_dead) and self.idle_sound_playing:
            if self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False

        # Handle opacity restoration with 250ms duration
        if self.is_hit and current_time - self.hit_time >= 250:  # Changed from 500 to 250
            self.is_hit = False
            self.alpha = 255  # Restore to full opacity after 0.3s
            
        # Death handling - set opacity to 50% when dying starts
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2
            self.frame_index = 0
            self.alpha = 128  # Set to 50% opacity when dying
            pygame.mixer.Sound.play(self.death_sound)
            return

        # Reset hit state at start of each update
        if self.is_hit and current_time - self.hit_time >= 250:
            self.is_hit = False
            self.alpha = 255
            self.hit_time = 0

        # Handle death first
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2  # Death animation
            self.frame_index = 0
            self.alpha = 255  # Reset opacity when dying starts
            pygame.mixer.Sound.play(self.death_sound)
            return

        # Handle death animation with proper falling
        if self.is_dying or self.is_dead:
            if current_time - self.update_time > animation_cooldown:
                if self.is_dying:
                    if self.frame_index < len(self.animation_list[2]) - 1:
                        self.frame_index += 1
                        self.rect.y += 5  # Move down 5 pixels with each death frame
                    else:
                        self.is_dying = False
                        self.is_dead = True
                        # Keep last frame
                        self.frame_index = len(self.animation_list[2]) - 1
                self.update_time = current_time
            
            # Always show current death frame
            self.image = self.animation_list[2][self.frame_index]
            return

        # Handle idle sound for living character
        if self.action == 0 and not self.is_dead and not self.is_dying:
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
            self.update_time = current_time
            self.frame_index += 1

            # Handle attack animation and damage
            if self.action == 1:  # Attack animation
                if not self.attack_applied and self.frame_index == 4:
                    if hasattr(self, "attack_target") and self.attack_target:
                        self.apply_attack_damage()
                if self.frame_index >= len(self.animation_list[1]):
                    self.frame_index = 0
                    self.action = 0
                    self.attacking = False
                    self.attack_applied = False
            # Handle other animations
            elif self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0

            # Update current frame
            if (self.action < len(self.animation_list) and 
                self.frame_index < len(self.animation_list[self.action])):
                self.image = self.animation_list[self.action][self.frame_index]

        # Remove this section since strength updates are handled in apply_attack_damage
        # The old passive skill update code is removed to avoid duplicate multiplier stacking

        # ...rest of existing code...

    def use_heal(self):
        if not self.using_heal and not self.is_dead and self.current_energy >= self.heal_energy_cost:
            self.using_heal = True
            self.heal_applied = False
            self.heal_time = pygame.time.get_ticks()  # Track when heal started
            self.target_energy = max(0, self.target_energy - self.heal_energy_cost)
            
            # Apply heal
            self.target_health = min(self.max_health, self.target_health + self.heal_amount)
            
            # Show heal notification
            damage_numbers.append(DamageNumber(
                self.rect.x + 100,
                self.rect.y,
                f"+{self.heal_amount}",
                (0, 255, 0),
                font_size=20,
                lifetime=45
            ))
            
            pygame.mixer.Sound.play(bloodreaperheal_sfx)  # Changed from bloodreaperhit_sfx
            return True
        return False

    def draw_skill_icons(self):
        if self.is_dead or self.is_dying:
            return

        # Update icon alphas
        target_alpha_basic = 255 if self.attacking else 128
        target_alpha_heal = 255 if self.using_heal else 128  # Add this line

        # Update both alphas
        for skill_type, target in [('basic', target_alpha_basic), ('heal', target_alpha_heal)]:
            current = self.skill_icons_alpha[skill_type]
            if current < target:
                self.skill_icons_alpha[skill_type] = min(current + 15, target)
            elif current > target:
                self.skill_icons_alpha[skill_type] = max(current - 15, target)

        # Draw basic attack icon (paling kiri)
        temp_surface = self.basic_attack_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['basic'])
        scaled_pos = scale_pos(self.icon_base_x, self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)

        # Draw heal icon (jauh ke kanan)
        temp_surface = self.heal_icon.copy()
        temp_surface.set_alpha(self.skill_icons_alpha['heal'])  # Use heal alpha value
        scaled_pos = scale_pos(self.icon_base_x + 30 + (self.icon_spacing * 2), self.icon_base_y)
        screen.blit(temp_surface, scaled_pos)
