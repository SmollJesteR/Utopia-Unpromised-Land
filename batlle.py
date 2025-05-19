import pygame

pygame.init()

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
attack_icon_rect = pygame.Rect(350, 900, 64, 64)  # x, y, width, height

current_turn = "player"  # giliran "player" atau "enemy"
enemy_has_attacked = False

turn_switch_delay = 1500  # jeda milidetik antar giliran
turn_switch_time = 0
font_turn = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", 40)

def draw_background():
    screen.blit(background_img, (0, 0))

def draw_panel():
    screen.blit(panel_img, (0, 0))

def draw_turn_text():
    if current_turn == "player":
        text = font_turn.render("Your Turn !", True, (0, 255, 0))  # hijau terang
    else:
        text = font_turn.render("Enemy Turn !", True, (255, 0, 0))  # merah terang
    rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
    screen.blit(text, rect)


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
        for i in range(8):
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
        pygame.draw.rect(screen, (255, 255, 255), (x, y, self.health_bar_length, 15), 4)

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
        pygame.draw.rect(screen, (255, 255, 255), (x, y, self.energy_bar_length, 15), 4)

    def update_health(self):
        self.target_health = max(0, min(self.target_health, self.max_hp))

    def update_energy(self):
        self.target_energy = max(0, min(self.target_energy, self.max_energy))

class BloodReaper(Entity):
    def __init__(self, x, y, scale):
        super().__init__(x, y, max_hp=100, strength=70, potion=3, name="BloodReaper", scale=scale)
        self.defense = 10
        self.agility = 25
        self.bleed_level = 0
        self.total_hp_lost = 0
        self.bleed_upgrade = False
        self.double_attack = False
        self.attacking = False
        self.attack_applied = False

    def take_damage(self, amount):
        damage_taken = max(0, amount - self.defense)
        self.target_health -= damage_taken
        self.total_hp_lost += damage_taken
        return damage_taken

    def attack(self, target):
        if not self.attacking:
            self.attacking = True
            self.attack_applied = False
            self.action = 1  # Switch to attack animation
            self.attack_target = target  # Save reference to apply damage later
            self.frame_index = 0  
          
    def update(self):
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
                base_damage = self.strength * (2 if self.double_attack else 1)
                if hasattr(self, "attack_target") and self.attack_target:
                    self.attack_target.take_damage(base_damage)
                self.attack_applied = True


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

class Boss():
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

        self.attacking = False
        self.attack_applied = False

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


        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def attack(self, target):
        if not self.attacking:
            self.attacking = True
            self.attack_applied = False
            self.action = 1
            self.attack_target = target

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
                    self.attack_target.take_damage(base_damage)
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
        pygame.draw.rect(screen, (255, 255, 255), (x, y, self.health_bar_length, 15), 4)

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
        pygame.draw.rect(screen, (255, 255, 255), (x, y, self.energy_bar_length, 15), 4)

    def update_health(self):
        self.target_health = max(0, min(self.target_health, self.max_hp))

    def update_energy(self):
        self.target_energy = max(0, min(self.target_energy, self.max_energy))
    
    def take_damage(self, amount):
        self.target_health -= amount

# Buat karakter dan musuh
BloodReaper = BloodReaper(501, 500, scale=2.7)
DoomCultist = Entity(1086, 350, 480, 10, 3, "DoomCultist", scale=4.5)
Medusa = Entity(1520, 350, 520, 8, 3, "Medusa", scale=4.5)
Cyclops = Entity(1086, 350, 450, 7, 3, "Cyclops", scale=4.5)
DeathSentry = Boss(1300, 400, 500, 30, 3, "DeathSentry", scale=8.5)

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

    # Giliran musuh menyerang otomatis setelah delay
    now = pygame.time.get_ticks()
    if current_turn == "enemy":
        if now - turn_switch_time > turn_switch_delay:
            if not DeathSentry.attacking and not enemy_has_attacked:
                DeathSentry.attack(BloodReaper)
                enemy_has_attacked = True

            if not DeathSentry.attacking and enemy_has_attacked:
                current_turn = "player"
                enemy_has_attacked = False
                turn_switch_time = now

    pygame.display.update()



pygame.quit()




    # Tampilkan bar Doom Cultist (hanya tampil, tidak bisa dimodifikasi)
    # DoomCultist.draw_health_bar_panel(x=1200, y=790)
    # DoomCultist.draw_energy_bar_panel(x=1200, y=810)

    # Cyclops.draw_health_bar_panel(x=1200, y=870)
    # Cyclops.draw_energy_bar_panel(x=1200, y=890)