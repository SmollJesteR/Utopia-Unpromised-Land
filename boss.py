import pygame
import random
from entity import Entity
from game_data import screen, font_ui, damage_numbers, DamageNumber
# Import at top level to avoid circular import
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from battle import BloodReaper

# Initialize pygame mixer before loading sounds
pygame.mixer.init()

# Remove player hit sounds, only keep boss-specific sounds
boss1_sfx = pygame.mixer.Sound('Assets/SFX/BA_DS.wav')
deathboss1_sfx = pygame.mixer.Sound('Assets/SFX/Death_DS.wav')

class Boss(Entity):
    def __init__(self, x, y, max_health, max_strength, name, scale, skip_animation=False):
        super().__init__(x, y, max_health, max_strength, name, scale, skip_animation=skip_animation)
        self.entity_type = "boss"
        self.last_damage_dealt = False
        self.damage_done = 0

    def load_animations(self, scale):
        self.animation_list = []  # Reset animation list first
        
        def load_animation(path, frame_count):
            temp_list = []
            for i in range(frame_count):
                img = pygame.image.load(f'img/{self.name}/{path}/{i+1}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            return temp_list

        # Load animations in correct order
        self.animation_list.append(load_animation('Idle', 12))      # index 0
        self.animation_list.append(load_animation('Attack', 8))     # index 1
        self.animation_list.append(load_animation('Death', 14))     # index 2

        # Set initial image and rect
        self.image = self.animation_list[0][0]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def attack(self, target):
        if not self.attacking and self.current_energy >= 20:
            self.attacking = True
            self.attack_applied = False
            self.action = 1
            self.attack_target = target
            self.target_energy = max(0, self.target_energy - 20)
            # Only play boss attack sound, remove monster_sfx
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
                base_damage = self.max_strength
                if hasattr(self, "attack_target") and self.attack_target:
                    damage_done = self.attack_target.take_damage(base_damage)
                    self.damage_done = base_damage
                    self.last_damage_dealt = (damage_done > 0)
                    
                    # Show damage number
                    damage_numbers.append(DamageNumber(
                        self.attack_target.rect.centerx,
                        self.attack_target.rect.y - 50,
                        "MISS!" if damage_done == 0 else base_damage,
                        (255, 255, 255) if damage_done == 0 else (255, 0, 0)
                    ))

                    # Use hasattr to check for player attributes
                    if self.last_damage_dealt and hasattr(self.attack_target, 'entity_type'):
                        if self.attack_target.entity_type == "player":
                            self.attack_target.was_hit = True
                            self.attack_target.combo_count = 0
                            self.attack_target.should_combo = False
                            print(f"Enemy dealt {self.damage_done} damage!")
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
            
        base_damage = self.max_strength * 2 if random.random() < 0.35 else self.max_strength
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
            missing_health = self.max_health - self.target_health
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
            # Calculate speed based on total health difference and 0.5 second duration
            health_diff = self.current_health - self.target_health
            transition_step = (health_diff / 20)  # 30 frames = 0.5 second at 60fps
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