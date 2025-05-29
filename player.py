import pygame
pygame.mixer.init()

# Add sound effects specific to Entity class
death_sfx = {
    "BloodReaper": pygame.mixer.Sound('Assets/SFX/Death_BR.wav'),
    "DeathSentry": pygame.mixer.Sound('Assets/SFX/Death_DS.wav')
}

class Player():
    def __init__(self, x, y, max_health, max_strength, name, scale, skip_animation=False):
        self.name = name
        self.max_health = max_health
        self.hp = max_health
        self.max_strength = max_strength
        self.alive = True
        self.animation_list = []
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

        self.target_health = max_health
        self.current_health = max_health
        self.health_bar_length = 350  
        self.health_ratio = self.max_health / self.health_bar_length
        self.health_change_speed = 0.2

        self.max_energy = 100
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350
        self.energy_ratio = self.max_energy / self.energy_bar_length
        self.energy_change_speed = 2

        # Only load animations if not skipped
        if not skip_animation:
            self.load_animations(scale)

        # Initialize other attributes
        self.is_dying = False
        self.is_dead = False
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.attacking = False
        self.attack_applied = False
        self.player_type = "player"
        self.immunity_turns = 0
        self.alpha = 255
        self.hit_time = 0
        self.is_hit = False
        self.combo_count = 0
        self.should_combo = False
        self.last_hit_successful = False
        self.can_combo = False

    def load_animations(self, scale):
        """Load animations for the player."""
        temp_list = []
        for i in range(8 if self.name == "BloodReaper" else 9):
            img = pygame.image.load(f'img/{self.name}/Idle/{i+1}.png')
            img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            temp_list.append(img)
        self.animation_list.append(temp_list)

    def update_health(self):
        self.target_health = max(0, min(self.target_health, self.max_health))

    def update_energy(self):
        self.target_energy = max(0, min(self.target_energy, self.max_energy))

    def take_damage(self, amount):
        """Base damage handling for all entities"""
        if self.immunity_turns > 0:
            return 0

        # Set hit state
        self.is_hit = True
        self.hit_time = pygame.time.get_ticks()
        self.alpha = 128  # Set to 50% opacity when hit
        
        # Update health
        self.target_health = max(0, self.target_health - amount)
        return amount  # Return actual damage dealt

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Update opacity fade back
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
            # Play death sound based on player type
            if self.name in death_sfx:
                pygame.mixer.Sound.play(death_sfx[self.name])
            return

        # Handle death animation
        if self.is_dying or self.is_dead:
            if current_time - self.update_time > animation_cooldown:
                self.update_time = current_time
                if self.frame_index < len(self.animation_list[2]) - 1:
                    self.frame_index += 1
                    self.rect.y += 5
                else:
                    self.is_dead = True
                    self.is_dying = False
            self.image = self.animation_list[2][self.frame_index]
            return

        # Handle regular animation updates
        if current_time - self.update_time > animation_cooldown:
            self.update_time = current_time
            self.frame_index += 1

            # Reset frame index if it exceeds animation length
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 1:  # Attack animation finished
                    self.action = 0  # Return to idle
                    self.attacking = False
                    self.attack_applied = False
                self.frame_index = 0

            # Update current image
            self.image = self.animation_list[self.action][self.frame_index]

        # Handle attack damage application
        if self.action == 1 and not self.attack_applied and self.frame_index == len(self.animation_list[1]) - 2:
            if hasattr(self, "attack_target") and self.attack_target:
                self.apply_attack_damage()

        # Update stats
        if not self.is_dead:
            self.update_health()
            self.update_energy()

