import pygame

class DisplayManager:
    def __init__(self, design_width=1920, design_height=1080):
        self.design_width = design_width
        self.design_height = design_height
        
        info = pygame.display.Info()
        self.user_width = info.current_w
        self.user_height = info.current_h
        
        self.scale_x = self.user_width / self.design_width
        self.scale_y = self.user_height / self.design_height
        self.scale_factor = min(self.scale_x, self.scale_y)
        
        self.screen_width = int(self.design_width * self.scale_factor)
        self.screen_height = int(self.design_height * self.scale_factor)
        
        self.offset_x = (self.user_width - self.screen_width) // 2
        self.offset_y = (self.user_height - self.screen_height) // 2

    def scale_pos(self, x, y):
        return (int(x * self.scale_factor) + self.offset_x,
                int(y * self.scale_factor) + self.offset_y)
                
    def scale_surface(self, surface):
        scaled_w = int(surface.get_width() * self.scale_factor)
        scaled_h = int(surface.get_height() * self.scale_factor)
        return pygame.transform.smoothscale(surface, (scaled_w, scaled_h))
