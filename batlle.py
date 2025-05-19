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

def draw_background():
    screen.blit(background_img, (0, 0))

def draw_panel():
    screen.blit(panel_img, (0, 0))

class Entity():
    def _init_(self, x, y, max_hp, strength, potion, name, scale):
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
        animation_cooldown = 100
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
    def _init_(self, x, y, scale):
        super()._init_(x, y, max_hp=900, strength=40, potion=3, name="BloodReaper", scale=scale)
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

    def update(self):
        try:
            super().update()

            if self.attacking:
                if self.frame_index == len(self.animation_list[1]) - 1:
                    if not self.attack_applied:
                        base_damage = self.strength * (2 if self.double_attack else 1)

                        if hasattr(self, "attack_target") and self.attack_target:
                            self.attack_target.take_damage(base_damage)

                            self.target_health = min(self.max_hp, self.target_health + int(base_damage * 0.1))

                            if self.bleed_level > 0 and hasattr(self.attack_target, "apply_bleed"):
                                self.attack_target.apply_bleed(self.bleed_level)

                            self.attack_applied = True

                if self.attack_applied and self.frame_index == len(self.animation_list[1]) - 1:
                    self.action = 0
                    self.attacking = False
                    self.frame_index = 0
        except Exception as e:
            print("Update Error:", e)


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
    def _init_(self, x, y, max_hp, strength, potion, name, scale):
        self.name = name
        self.max_hp = max_hp
        self.hp = max_hp
        self.strength = strength
        self.potion = potion
        self.alive = True
        self.animation_list = []
        self.action = 2
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

    def update(self):
        animation_cooldown = 100
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
    
    def take_damage(self, amount):
        self.target_health -= amount




# Buat karakter dan musuh
BloodReaper = BloodReaper(501, 500, scale=2.7)
DoomCultist = Entity(1086, 350, 480, 10, 3, "DoomCultist", scale=4.5)
Medusa = Entity(1520, 350, 520, 8, 3, "Medusa", scale=4.5)
Cyclops = Entity(1086, 350, 450, 7, 3, "Cyclops", scale=4.5)
DeathSentry = Boss(1300, 400, 800, 20, 3, "DeathSentry", scale=8.5)

run = True
while run:
    clock.tick(fps)
    draw_background()
    draw_panel()

    for character in [BloodReaper, DeathSentry]:
        character.update()
        character.draw()
    

    # Tampilkan bar Blood Reaper (bisa dimodifikasi)
    BloodReaper.draw_health_bar_panel(x=350, y=790)
    BloodReaper.draw_energy_bar_panel(x=350, y=810)
    attack_icon_rect = pygame.Rect(350, 840, 64, 64)  # (x, y, width, height)



    DeathSentry.draw_health_bar_panel(x=1200, y=790)
    DeathSentry.draw_energy_bar_panel(x=1200, y=810)


    # Tampilkan bar Doom Cultist (hanya tampil, tidak bisa dimodifikasi)
    # DoomCultist.draw_health_bar_panel(x=1200, y=790)
    # DoomCultist.draw_energy_bar_panel(x=1200, y=810)

    # Cyclops.draw_health_bar_panel(x=1200, y=870)
    # Cyclops.draw_energy_bar_panel(x=1200, y=890)
    
    for event in pygame.event.get():
         if event.type == pygame.QUIT:
            run = False

         elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                BloodReaper.target_health -= 200
            elif event.key == pygame.K_UP:
                BloodReaper.target_health += 200
            elif event.key == pygame.K_LEFT:
                BloodReaper.target_energy -= 20
            elif event.key == pygame.K_RIGHT:
                BloodReaper.target_energy += 20
            elif event.key == pygame.K_s:
                BloodReaper.attack(DeathSentry)
     
         elif event.type == pygame.MOUSEBUTTONDOWN:
            if attack_icon_rect.collidepoint(pygame.mouse.get_pos()):
                BloodReaper.attack(DeathSentry)

    pygame.display.update()

pygame.quit()
