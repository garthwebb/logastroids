"""Explosion sprite class."""
import pygame
from constants import WINDOW_WIDTH, WINDOW_HEIGHT


class Explosion(pygame.sprite.Sprite):
    """Explosion that keeps drifting and spinning with the destroyed asteroid."""

    def __init__(self, broken_sheets, x, y, rotation_angle, rotation_speed, vx, vy, frame_hold=4):
        super().__init__()
        self.broken_sheets = broken_sheets  # list of directional sheets
        self.frame_hold = frame_hold
        self.tick = 0
        self.frame_index = 0
        self.rotation = rotation_angle
        self.rotation_speed = rotation_speed
        self.x = float(x)
        self.y = float(y)
        self.vx = vx
        self.vy = vy
        self.image = None
        self.rect = None
        self._set_image()

    def _set_image(self):
        sheet = self.broken_sheets[self.frame_index]
        num_frames = len(sheet)
        dir_index = int((self.rotation / 360.0) * num_frames) % num_frames
        self.image = sheet[dir_index]
        if self.rect:
            center = self.rect.center
            self.rect = self.image.get_rect(center=center)
        else:
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def update(self):
        # Drift forward with preserved velocity
        self.x += self.vx
        self.y += self.vy
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0
        if self.rect:
            self.rect.center = (int(self.x), int(self.y))

        # Keep spinning to animate directional shards
        self.rotation = (self.rotation + self.rotation_speed) % 360

        self.tick += 1
        if self.tick % self.frame_hold == 0:
            self.frame_index += 1
            if self.frame_index >= len(self.broken_sheets):
                self.kill()
                return
            self._set_image()
        else:
            # Update frame for current rotation even within the same explosion stage
            self._set_image()
