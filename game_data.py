import pygame

# Initialize pygame and mixer first
pygame.init()
pygame.mixer.init()

# Screen setup
screen_info = pygame.display.Info()
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080

scale_x = screen_info.current_w / DESIGN_WIDTH
scale_y = screen_info.current_h / DESIGN_HEIGHT
scale_factor = min(scale_x, scale_y)

screen_width = int(DESIGN_WIDTH * scale_factor)
screen_height = int(DESIGN_HEIGHT * scale_factor)
padding_x = (screen_info.current_w - screen_width) // 2
padding_y = (screen_info.current_h - screen_height) // 2

screen = pygame.display.set_mode((screen_info.current_w, screen_info.current_h))
font_ui = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", int(20 * scale_factor))

def scale_pos(x, y):
    return (int(x * scale_factor) + padding_x, 
            int(y * scale_factor) + padding_y)

# Damage number handling
damage_numbers = []

class DamageNumber:
    def __init__(self, x, y, amount, color, font_size=26, velocity=-2, lifetime=30):
        self.font = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", font_size)
        self.x = x
        self.y = y
        self.amount = amount
        self.color = color
        self.lifetime = lifetime
        self.alpha = 255
        self.velocity_y = velocity
        self.is_initial_damage = isinstance(amount, int) and amount == 20
        self.fade_rate = 4 if not self.is_initial_damage else 2

    def update(self):
        self.y += self.velocity_y
        self.lifetime -= 1
        if self.lifetime < 30:
            self.alpha = max(0, self.alpha - self.fade_rate)

    def draw(self, screen):
        text_surface = self.font.render(str(self.amount), True, self.color)
        text_surface.set_alpha(self.alpha)
        screen.blit(text_surface, (self.x, self.y))

class ComboText:
    def __init__(self, x, y, combo_count):
        self.font = pygame.font.Font("Assets/Font/PressStart2P-Regular.ttf", 32)
        self.x = x
        self.y = y
        self.text = f"Combo {combo_count}!" if combo_count >= 2 else ""
        # Change color based on combo count - gold for 2-3, red for 4+
        self.color = (255, 0, 0) if combo_count >= 4 else (255, 215, 0)
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
