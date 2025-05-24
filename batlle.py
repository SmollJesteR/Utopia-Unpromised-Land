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

clock = pygame.time.Clock()
fps = 60

screen_width = 1920
screen_height = 1080
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Battle Sequence")

background_img = pygame.image.load('img/Background/Map.png').convert_alpha()
panel_img = pygame.image.load('img/Background/Panel.png').convert_alpha()
font_ui = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", 20)

# Define attack icon rect (example position and size, adjust as needed)
attack_icon_rect = pygame.Rect(350, 820, 64, 64)  # x, y, width, height

current_turn = "player"  # giliran "player" atau "enemy"
enemy_has_attacked = False

turn_switch_delay = 1500  # jeda milidetik antar giliran
turn_switch_time = 0
font_turn = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", 36)

turn_notification_img = pygame.image.load('img/Background/TurnNotification.png').convert_alpha()
turn_notification_duration = 5000  # durasi notifikasi tampil (ms)
turn_notification_start = 0  # waktu mulai notifikasi (ms)

player_turn_counter = 0
enemy_turn_counter = 0

# Add combo counter variables
combo_counter = 0
combo_text_duration = 1000  # 1 second
combo_text_start = 0

def draw_background():
    screen.blit(background_img, (0, 0))

def draw_panel():
    screen.blit(panel_img, (0, 0))

def start_turn_notification():
    global turn_notification_start
    turn_notification_start = pygame.time.get_ticks()

def draw_turn_text():
    now = pygame.time.get_ticks()
    if now - turn_notification_start < turn_notification_duration:
        notif_x = screen_width // 2
        notif_y = (screen_height // 2) - 470

        notif_rect = turn_notification_img.get_rect(center=(notif_x, notif_y))
        screen.blit(turn_notification_img, notif_rect)

        if current_turn == "player":
            text = font_turn.render("Your Turn!", True, (0, 255, 0))
        else:
            text = font_turn.render("Enemy Turn!", True, (255, 0, 0))

        text_rect = text.get_rect(center=(notif_x, notif_y))
        screen.blit(text, text_rect)

class DamageNumber:
    def __init__(self, x, y, amount, color, font_size=26, velocity=-2, lifetime=60):
        self.font = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", font_size)
        self.x = x
        self.y = y
        self.amount = amount
        self.color = color
        self.lifetime = lifetime  # Customizable duration
        self.alpha = 255
        self.velocity_y = velocity  # Customizable upward speed

    def update(self):
        self.y += self.velocity_y
        self.lifetime -= 1
        if self.lifetime < 30:  # start fading out in the last 30 frames
            self.alpha = max(0, self.alpha - 8)

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
        self.text = f"Combo {combo_count}!"
        self.color = (255, 215, 0)  # Gold color
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
        self.health_change_speed = 10

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

        # Add death animation loading for DeathSentry
        if name == "DeathSentry":
            temp_list = []
            for i in range(14):# Only load 4 death frames
                img = pygame.image.load(f'img/{self.name}/Death/{i+1}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        # Add skill animation loading for DeathSentry
        if name == "DeathSentry":
            temp_list = []
            for i in range(7):  # Load 7 skill frames
                img = pygame.image.load(f'img/{self.name}/Skill/{i+1}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
        
        # Add ultimate animation loading for DeathSentry
        if name == "DeathSentry":
            temp_list = []
            for i in range(14):
                img = pygame.image.load(f'img/{self.name}/Ultimate/{i+1}.png')
                img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 150
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0

        self.update_health()
        self.update_energy()

    def draw(self):
        screen.blit(self.image, self.rect)

    def draw_health_bar_panel(self, x, y):
        transition_width = 0
        transition_color = (255, 0, 0)

        # Nama karakter
        name_text = font_ui.render(self.name.replace("_", " "), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + self.health_bar_length // 2, y - 25))
        screen.blit(name_text, name_rect)

        # Transisi health
        if self.current_health < self.target_health:
            self.current_health += self.health_change_speed
            if self.current_health > self.target_health:
                self.current_health = self.target_health
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)
        elif self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            if self.current_health < self.target_health:
                self.current_health = self.target_health
            transition_width = int((self.current_health - self.target_health) / self.health_ratio)
            transition_color = (255, 255, 0)

        health_bar_width = int(self.current_health / self.health_ratio)
        health_bar = pygame.Rect(x, y, health_bar_width, 15)
        transition_bar = pygame.Rect(x + health_bar_width, y, transition_width, 15)

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

    def update_health(self):
        self.target_health = max(0, min(self.target_health, self.max_hp))

    def update_energy(self):
        self.target_energy = max(0, min(self.target_energy, self.max_energy))

    def take_damage(self, amount):
        self.target_health -= amount
        return amount  # Return damage dealt

class BloodReaper(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, max_hp=100, strength=300, potion=3, name="BloodReaper", scale=scale)
        self.max_energy = 200  # Change to match DeathSentry
        self.target_energy = self.max_energy
        self.current_energy = self.max_energy
        self.energy_bar_length = 350
        self.energy_ratio = self.max_energy / self.energy_bar_length

        self.defense = 10
        self.agility = 35
        self.bleed_level = 0
        self.total_hp_lost = 0
        self.bleed_upgrade = False
        self.double_attack = False
        self.attacking = False
        self.attack_applied = False

        self.evasion_chance = self.agility / 100
        self.critical_chance = self.agility / 100

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

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        global combo_counter  # Single global declaration at start of method
        animation_cooldown = 150
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            if self.action == 1:
                self.action = 0
                self.attacking = False
                self.attack_applied = False

        # Lakukan damage sekali saat frame terakhir animasi attack
        if self.action == 1:
            if not self.attack_applied and self.frame_index == len(self.animation_list[1]) - 1:
                if random.random() < self.critical_chance:
                    base_damage = self.strength * 2
                    critical_hit = True
                else:
                    base_damage = self.strength
                    critical_hit = False

                # Apply combo multiplier if combo exists
                if combo_counter > 0:  # Changed from > 1 to > 0
                    base_damage = int(base_damage * 1.5)  # Apply 50% bonus damage
                
                if hasattr(self, "attack_target") and self.attack_target:
                    damage_done = self.attack_target.take_damage(base_damage)
                    heal_amount = int(base_damage * 0.20)
                    self.target_health = min(self.max_hp, self.target_health + heal_amount)
                    # Add energy when getting healed from lifesteal
                    self.target_energy = min(self.max_energy, self.target_energy + 15)
                    
                    # Add damage number
                    damage_numbers.append(DamageNumber(
                        self.attack_target.rect.centerx, 
                        self.attack_target.rect.y,
                        damage_done,
                        (255, 0, 0)
                    ))
                    # Add heal number
                    damage_numbers.append(DamageNumber(
                        self.rect.centerx,
                        self.rect.y,
                        heal_amount,
                        (0, 255, 0)
                    ))

                    # Combo system (removed duplicate global declaration)
                    combo_counter += 1
                    if combo_counter > 1:
                        damage_numbers.append(ComboText(
                            self.rect.centerx - 100,
                            self.rect.y - 50,
                            combo_counter
                        ))

                self.attack_applied = True

    def take_damage(self, amount):
        damage_taken = max(0, amount - self.defense)
        self.target_health -= damage_taken
        return damage_taken

    def attack(self, target):
        if not self.attacking and self.current_energy >= 20:
            self.attacking = True
            self.attack_applied = False
            self.action = 1
            self.attack_target = target
            self.frame_index = 0
            self.target_energy = max(0, self.target_energy - 20)  # Consume 20 stamina
            pygame.mixer.Sound.play(attack_sfx)
            
    def use_skill(self, skill_name):
        if skill_name == "Blood Sacrifice":
            bonus = int((self.max_hp - self.target_health) * 0.2)
            self.strength += bonus
        elif skill_name == "Activate Bleed":
            self.bleed_level = 1

    def apply_bleed(self, stacks):
        self.bleed_level = min(7 if self.bleed_upgrade else 3, self.bleed_level + stacks)

    def bleed_effect(self, target):
        if self.bleed_level > 0:
            bleed_damage = int(5 + self.bleed_level * 2)
            target.take_damage(bleed_damage)
            if self.bleed_upgrade:
                self.target_health = min(self.max_hp, self.target_health + int(bleed_damage * 0.1))

    def apply_upgrade(self, option):
        if option == "ATK+7":
            self.strength += 7
        elif option == "AGI+7":
            self.agility += 7
        elif option == "HP+10":
            self.max_hp += 10
        elif option == "Upgrade Life Steal":
            pass  # Bisa ditambahkan multiplier heal
        elif option == "Upgrade Blood Sacrifice":
            pass
        elif option == "Unlock Bleed":
            self.bleed_level = 1
        elif option == "Bleed+%":
            pass
        elif option == "Blood Frenzy":
            self.bleed_upgrade = True
        elif option == "Double Trouble":
            self.double_attack = True

class Boss(Entity):
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
                    # Add damage number
                    damage_numbers.append(DamageNumber(
                        self.attack_target.rect.centerx,
                        self.attack_target.rect.y,
                        damage_done,
                        (255, 0, 0)
                    ))

                    # Reset combo when player gets hit
                    global combo_counter
                    combo_counter = 0  

                self.attack_applied = True

                # Tandai musuh sudah menyerang (jika variabel global digunakan)
                global enemy_has_attacked
                enemy_has_attacked = True

        self.update_health()
        self.update_energy()

  # Tandai sudah menyerang


    def draw(self):
        screen.blit(self.image, self.rect)

    def draw_health_bar_panel(self, x, y):
        transition_width = 0
        transition_color = (255, 0, 0)

        # Nama karakter
        name_text = font_ui.render(self.name.replace("_", " "), True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(x + self.health_bar_length // 2, y - 25))
        screen.blit(name_text, name_rect)

        # Transisi health
        if self.current_health < self.target_health:
            self.current_health += self.health_change_speed
            if self.current_health > self.target_health:
                self.current_health = self.target_health
            transition_width = int((self.target_health - self.current_health) / self.health_ratio)
            transition_color = (0, 255, 0)
        elif self.current_health > self.target_health:
            self.current_health -= self.health_change_speed
            if self.current_health < self.target_health:
                self.current_health = self.target_health
            transition_width = int((self.current_health - self.target_health) / self.health_ratio)
            transition_color = (255, 255, 0)

        health_bar_width = int(self.current_health / self.health_ratio)
        health_bar = pygame.Rect(x, y, health_bar_width, 15)
        transition_bar = pygame.Rect(x + health_bar_width, y, transition_width, 15)

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

    def update_health(self):
        self.target_health = max(0, min(self.target_health, self.max_hp))

    def update_energy(self):
        self.target_energy = max(0, min(self.target_energy, self.max_energy))
    
    def take_damage(self, amount):
        damage_taken = amount  # No defense for boss, can be modified if needed
        self.target_health -= damage_taken
        return damage_taken

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
        self.immunity_turns = 0
        self.using_skill = False
        self.skill_applied = False
        self.skill_energy_cost = 45

        self.using_ultimate = False
        self.ultimate_applied = False
        self.ultimate_energy_cost = 75
        self.ultimate_damage = 50  # Changed from 75 to 50 to accommodate 5x10 damage
        self.ultimate_start_time = 0  # Add this line to track when ultimate starts
        self.damage_numbers_delay = 1000  # 1 second delay for damage numbers
        self.damage_number_spacing = 40  # Increased vertical spacing between numbers
        self.ultimate_damage_shown = False  # Add flag to track if damage numbers have been shown

        # New variables for staggered damage number display
        self.damage_number_delay = 200  # Delay between each number appearing (ms)
        self.damage_number_index = 0  # Track which number we're showing
        self.next_damage_number_time = 0  # When to show next number

    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Check when to show next damage number during ultimate
        if self.using_ultimate and self.damage_number_index < 5:
            if current_time - self.ultimate_start_time >= 1000:  # Wait initial 1 second
                if current_time >= self.next_damage_number_time:
                    self.show_next_damage_number()
                    self.damage_number_index += 1
                    self.next_damage_number_time = current_time + self.damage_number_delay

        if self.using_skill:
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.animation_list[3]):  # Skill animation
                    self.frame_index = 0
                    self.action = 0
                    self.using_skill = False
                    self.skill_applied = False
            self.image = self.animation_list[3][self.frame_index]
            return

        if self.using_ultimate:
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.animation_list[4]):  # Ultimate animation
                    self.frame_index = 0
                    self.action = 0
                    self.using_ultimate = False
                    self.ultimate_applied = False
                    # Return to original position after ultimate
                    self.rect.center = self.original_pos
            self.image = self.animation_list[4][self.frame_index]
            return

        # Check if health is 0 and death animation hasn't started
        if self.target_health <= 0 and not self.is_dying and not self.is_dead:
            self.is_dying = True
            self.action = 2  # Switch to death animation
            self.frame_index = 0
            pygame.mixer.Sound.play(deathboss1_sfx)  # Play death sound when starting to die
            
        if self.is_dying:
            # Handle death animation
            if pygame.time.get_ticks() - self.update_time > animation_cooldown:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= 4:  # Hardcode 4 frames since we know the count
                    self.frame_index = 3  # Stay on last frame
                    self.is_dead = True
                    self.is_dying = False
            self.image = self.animation_list[2][self.frame_index]
        else:
            # Normal update for other states
            super().update()

    def attack(self, target):
        if not self.is_dying and not self.is_dead:
            # Check for ultimate condition first
            health_percent = (self.target_health / self.max_hp) * 100
            if health_percent < 50 and self.current_energy >= self.ultimate_energy_cost:
                self.use_ultimate(target)
            # Then check for skill
            elif self.current_energy >= self.skill_energy_cost and random.random() < 0.3:
                self.use_skill()
            else:
                super().attack(target)

    def use_skill(self):
        self.using_skill = True
        self.skill_applied = False
        self.action = 3  # Index for skill animation
        self.frame_index = 0
        self.target_energy = max(0, self.target_energy - self.skill_energy_cost)
        self.immunity_turns = 2
        pygame.mixer.Sound.play(skillboss1_sfx)

    def use_ultimate(self, target):
        self.using_ultimate = True
        self.ultimate_applied = False
        self.ultimate_damage_shown = False  # Reset flag
        self.action = 4  # Index for ultimate animation
        self.frame_index = 0
        self.ultimate_start_time = pygame.time.get_ticks()  # Record start time
        
        # Store original position
        self.original_pos = self.rect.center
        # Move to center screen for ultimate - Ubah angka untuk mengatur posisi
        self.rect.center = (screen_width // 2 - 1100, screen_height // 2 - 250)  # Sesuaikan nilai -100 dan -200
        
        self.attack_target = target
        self.target_energy = max(0, self.target_energy - self.ultimate_energy_cost)
        
        if self.image in self.animation_list[4]:
            self.image = pygame.transform.flip(self.image, True, False)

        pygame.mixer.Sound.play(monster_sfx)
        pygame.mixer.Sound.play(ultimateboss1_sfx) # Add ultimate sound effect
        # Remove the immediate damage numbers display
        if hasattr(self, "attack_target"):
            self.attack_target.take_damage(self.ultimate_damage)
        
        # New: Initialize damage number display variables
        self.damage_number_index = 0
        self.next_damage_number_time = self.ultimate_start_time + 1000  # Start after 1 second

    def show_next_damage_number(self):
        if hasattr(self, "attack_target"):
            start_y = self.attack_target.rect.y - 100
            damage_numbers.append(DamageNumber(
                self.attack_target.rect.centerx,
                start_y + (self.damage_number_index * 40),
                10,
                (255, 255, 0),
                font_size=26,
                velocity=-2,
                lifetime=120
            ))

    def take_damage(self, amount):
        if self.immunity_turns > 0:
            return 0  # No damage taken while immune
        if not self.is_dying and not self.is_dead:
            return super().take_damage(amount)
        return 0

# Buat karakter dan musuh
BloodReaper = BloodReaper(501, 500, scale=4.2)
DeathSentry = DeathSentry(1300, 400, scale=8.5)

def switch_turns():
    global current_turn, enemy_has_attacked, turn_switch_time, player_turn_counter, enemy_turn_counter
    current_turn = "player"
    enemy_has_attacked = False
    turn_switch_time = pygame.time.get_ticks()
    start_turn_notification()
    
    player_turn_counter += 1
    enemy_turn_counter += 1
    
    if player_turn_counter >= 6:
        BloodReaper.target_energy = min(BloodReaper.max_energy, BloodReaper.target_energy + 15)
        player_turn_counter = 0
    
    if enemy_turn_counter >= 3:
        DeathSentry.target_energy = min(DeathSentry.max_energy, DeathSentry.target_energy + 15)
        enemy_turn_counter = 0
        if DeathSentry.immunity_turns > 0:
            DeathSentry.immunity_turns -= 1

# Main game loop
run = True
while run:
    clock.tick(fps)
    draw_background()
    draw_panel()

    for character in [BloodReaper, DeathSentry]:
        character.update()
        character.draw()

    BloodReaper.draw_health_bar_panel(x=350, y=790)
    BloodReaper.draw_energy_bar_panel(x=350, y=810)
    DeathSentry.draw_health_bar_panel(x=1200, y=790)
    DeathSentry.draw_energy_bar_panel(x=1200, y=810)

    draw_turn_text()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        # Input hanya berlaku saat giliran player
        if current_turn == "player":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_s and not BloodReaper.attacking:
                    BloodReaper.attack(DeathSentry)
                    current_turn = "enemy"
                    enemy_has_attacked = False
                    turn_switch_time = pygame.time.get_ticks()
                    start_turn_notification()

    # Giliran musuh menyerang otomatis setelah delay
    now = pygame.time.get_ticks()
    if current_turn == "enemy":
        if now - turn_switch_time > turn_switch_delay:
            if not DeathSentry.attacking and not enemy_has_attacked:
                DeathSentry.attack(BloodReaper)
                enemy_has_attacked = True

            if not DeathSentry.attacking and enemy_has_attacked:
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
