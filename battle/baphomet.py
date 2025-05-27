    def update(self):
        animation_cooldown = 150
        current_time = pygame.time.get_ticks()

        # Stop idle sound if dying or dead
        if (self.is_dying or self.is_dead) and self.idle_sound_playing:
            if self.idle_sound_channel:
                self.idle_sound_channel.stop()
                self.idle_sound_playing = False

        # ...existing code for hit state and death handling...

        # Handle idle sound when in idle animation
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

        # ...rest of existing update code...
